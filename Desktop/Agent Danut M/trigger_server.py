"""
SM Writer — trigger_server.py
Mini server local pentru dashboard-ul de aprobare.

Pornire (se face automat de pipeline la PASUL 7):
  python3 scripts/trigger_server.py

Ascultă pe localhost:7734.
La verde: scrie trigger.json în rădăcina proiectului + printează TRIGGER: la stdout.
Monitor-ul agentului preia triggerul și rulează scripts/publish.py.

IMPORTANT: Rulează din rădăcina proiectului sm-writer, nu din alt folder.
"""
from http.server import HTTPServer, BaseHTTPRequestHandler
import json, pathlib

TRIGGER_FILE = pathlib.Path('trigger.json')

class Handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self._cors()
        self.end_headers()

    def do_POST(self):
        length = int(self.headers.get('Content-Length', 0))
        body = json.loads(self.rfile.read(length)) if length else {}

        action = body.get('action', '')
        notes  = body.get('notes', '')

        if action == 'publish':
            TRIGGER_FILE.write_text(json.dumps(body, ensure_ascii=False, indent=2))
            schedule = body.get('schedule', {})
            fb = schedule.get('facebook', 'now')
            li = schedule.get('linkedin',  'now')
            print(f'TRIGGER:verde:fb={fb}:li={li}', flush=True)

        elif action == 'review' and notes:
            print(f'TRIGGER:return:{notes}', flush=True)

        else:
            print(f'TRIGGER:unknown:{action}', flush=True)

        self.send_response(200)
        self._cors()
        self.end_headers()
        self.wfile.write(b'ok')

    def _cors(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')

    def log_message(self, *a):
        pass  # fără zgomot în stdout

print('SM-WRITER-TRIGGER-SERVER:ready', flush=True)
HTTPServer(('127.0.0.1', 7734), Handler).serve_forever()
