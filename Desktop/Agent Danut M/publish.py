"""
SM Writer — publish.py
Publică un brief finalizat pe Facebook și LinkedIn via Zernio.
Se apelează automat de agent după ce utilizatorul apasă verde în dashboard.

Utilizare:
  python3 scripts/publish.py output/2026-05-24/raspundere-output-ai/

Citește din folderul brief-ului:
  facebook-text.md    → textul postului Facebook
  linkedin-text.md    → textul postului LinkedIn
  facebook-image.png  → imaginea Facebook (1080×1350)
  linkedin-image.png  → imaginea LinkedIn (1200×627)

Citește din rădăcina proiectului:
  trigger.json        → schedule (fb/li: "now" sau "2026-05-28T10:00:00")

Scrie în folderul brief-ului:
  publicare.md        → URL-urile postărilor publicate

Credențiale: macOS Keychain
  zernio-api-key, zernio-fb-account-id, zernio-linkedin-account-id

NOTE: câmpurile corecte pentru presign sunt `filename` și `contentType` (nu camelCase).
"""
import sys, json, subprocess, pathlib
from urllib.request import urlopen, Request
from urllib.error import HTTPError


def keychain(service):
    import os
    r = subprocess.run(
        ['security', 'find-generic-password', '-a', os.environ.get('USER', ''), '-s', service, '-w'],
        capture_output=True, text=True
    )
    return r.stdout.strip() if r.returncode == 0 else None


def zernio_req(api_key, url, body):
    data = json.dumps(body).encode()
    req = Request(url, data=data, headers={
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    })
    with urlopen(req) as r:
        return json.loads(r.read())


def presign(api_key, filename):
    resp = zernio_req(api_key, 'https://zernio.com/api/v1/media/presign', {
        'filename': filename,
        'contentType': 'image/png'
    })
    if 'uploadUrl' not in resp:
        raise RuntimeError(f'Presign eșuat: {resp}')
    return resp['uploadUrl'], resp['publicUrl']


def upload_image(upload_url, image_path):
    data = pathlib.Path(image_path).read_bytes()
    req = Request(upload_url, data=data, method='PUT',
                  headers={'Content-Type': 'image/png'})
    with urlopen(req) as r:
        if r.status not in (200, 204):
            raise RuntimeError(f'Upload HTTP {r.status}')


def create_post(api_key, caption, public_url, platform, account_id, schedule_time):
    body = {
        'content': caption,
        'mediaItems': [{'url': public_url, 'type': 'image'}],
        'platforms': [{'platform': platform, 'accountId': account_id}],
    }
    if schedule_time == 'now':
        body['publishNow'] = True
    else:
        body['scheduledFor'] = schedule_time  # ISO 8601, ex: "2026-05-28T10:00:00"

    resp = zernio_req(api_key, 'https://zernio.com/api/v1/posts', body)
    platforms = resp.get('post', {}).get('platforms', [{}])
    return platforms[0].get('platformPostUrl', '') if platforms else ''


def main():
    if len(sys.argv) < 2:
        print('Utilizare: python3 scripts/publish.py output/AAAA-LL-ZZ/slug-brief/')
        sys.exit(1)

    folder = pathlib.Path(sys.argv[1])
    if not folder.exists():
        print(f'EROARE: Folderul {folder} nu există.')
        sys.exit(1)

    # Citește schedule din trigger.json (rădăcina proiectului)
    schedule = {'facebook': 'now', 'linkedin': 'now'}
    trigger_file = pathlib.Path('trigger.json')
    if trigger_file.exists():
        t = json.loads(trigger_file.read_text())
        schedule = t.get('schedule', schedule)

    # Credențiale
    api_key   = keychain('zernio-api-key')
    fb_acct   = keychain('zernio-fb-account-id')
    li_acct   = keychain('zernio-linkedin-account-id')

    missing = [s for s, v in [
        ('zernio-api-key', api_key),
        ('zernio-fb-account-id', fb_acct),
        ('zernio-linkedin-account-id', li_acct)
    ] if not v]
    if missing:
        print(f'EROARE: Chei lipsă în Keychain: {", ".join(missing)}')
        print('Adaugă cu: security add-generic-password -U -a "$USER" -s SERVICIU -w CHEIE')
        sys.exit(1)

    results = {}

    for platform, img_name, acct, sched_key in [
        ('facebook', 'facebook-image.png', fb_acct,  'facebook'),
        ('linkedin', 'linkedin-image.png', li_acct,  'linkedin'),
    ]:
        caption   = (folder / f'{platform}-text.md').read_text().strip()
        img_path  = folder / img_name
        sched     = schedule.get(sched_key, 'now')

        print(f'[{platform.upper()}] Presign…')
        upload_url, public_url = presign(api_key, img_name)

        print(f'[{platform.upper()}] Upload imagine…')
        upload_image(upload_url, str(img_path))

        print(f'[{platform.upper()}] Creare post (schedule: {sched})…')
        post_url = create_post(api_key, caption, public_url, platform, acct, sched)
        results[platform] = post_url
        print(f'POSTED [{platform.upper()}]: {post_url}')

    # Scrie publicare.md
    slug = folder.name
    date = folder.parent.name
    (folder / 'publicare.md').write_text(
        f'# Publicare: {slug} — {date}\n\n'
        f'## Facebook\nPOSTED: {results.get("facebook", "—")}\n\n'
        f'## LinkedIn\nPOSTED: {results.get("linkedin", "—")}\n'
    )
    print(f'\nSalvat: {folder}/publicare.md')


if __name__ == '__main__':
    main()
