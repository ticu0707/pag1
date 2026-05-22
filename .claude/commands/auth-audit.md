---
description: Audit Authentication & Authorization — verifică 22 reguli critice (Supabase Auth, RLS/Storage, Middleware, Session Security, Server Actions, HTML Vanilla). Raportează BLOCKER / ATENȚIE / OK fără a modifica codul. Bazat pe ghid-auth-authorization-v4.md.
---

# /auth-audit — Audit Authentication & Authorization

**Scopul:** Analizează fișierele unui proiect pentru greșeli critice de autentificare și autorizare și raportează BLOCKER / ATENȚIE / OK per regulă. Bazat pe ghid-auth-authorization-v4.md.

---

## PASUL 1 — Identifică directorul

**Dacă $ARGUMENTS conține o cale** (ex: `/auth-audit Desktop/vibe-budget`):
Lucrează în: `C:\Users\admin\$ARGUMENTS`

**Dacă $ARGUMENTS este gol:**
Întreabă utilizatorul: `Pe care proiect rulăm auth-auditul? (ex: Desktop/vibe-budget)`
Sau dacă există context clar din sesiune, folosește directorul curent.

---

## PASUL 2 — Detectează tipul de proiect și găsește fișierele relevante

Rulează în paralel cu Glob:
- `next.config.ts` sau `next.config.js` (rădăcina proiectului) → prezență = Next.js
- `middleware.ts` sau `middleware.js` (rădăcina sau src/)
- `**/*.ts` și `**/*.tsx` (exclude node_modules, .next, dist, .git)
- `**/*.html` și `**/*.js` (exclude node_modules, dist) → prezență exclusivă = HTML Vanilla
- `**/*.sql` sau `supabase/migrations/**` (SQL migrations)
- `.env.local` (rădăcina proiectului)
- `package.json` (rădăcina proiectului)

**Tip proiect detectat:**
- `next.config.*` prezent → **Next.js** (rulează categoriile A, B, C, D, E; F marchează `— (Next.js project)`)
- Doar fișiere `.html` / `.js`, fără `next.config.*` → **HTML Vanilla** (rulează A parțial, B, D, F; C marchează `— (fără middleware)`)
- Ambele → **Mix** (rulează tot)

Dacă nu găsești niciun fișier TS/TSX și niciun HTML: raportează `EROARE: director gol sau cale greșită` și oprește.

Notează: Tip proiect: [Next.js / HTML Vanilla / Mix] + [N] TS/TSX + [M] HTML/JS + [migrations SQL: DA/NU] + [middleware: DA/NU] + [.env.local: DA/NU]

---

## PASUL 3 — Rulează verificările pe 6 categorii

### CATEGORIA A — SUPABASE AUTH SETUP

*Se aplică dacă există `@supabase/ssr` sau `@supabase/supabase-js` în package.json.*
*Dacă Supabase absent: marchează toată categoria cu `— (Supabase negăsit în proiect)`*

**A1 — getUser() vs getSession() pe server**
Grep pentru `getSession()` în fișierele `.ts` și `.tsx` din `app/`, `actions/`, `lib/` (exclude `lib/supabase/client.ts` — acolo e OK).
- `getSession()` găsit în context server (Server Component, Server Action, middleware, route handler) → **BLOCKER** (JWT din cookie nevalidat criptografic cu serverul; atacatorul poate manipula cookie-ul și trece de orice `if (session)`. Fix: înlocuiește cu `await supabase.auth.getUser()`)
- Absent în context server → **OK**

**A2 — exchangeCodeForSession în callback OAuth**
Glob pentru `**/auth/callback/route.ts` sau `**/auth/callback/route.tsx`.
Dacă fișierul există, grep pentru `exchangeCodeForSession`.
- Callback există dar `exchangeCodeForSession` absent → **BLOCKER** (codul OAuth nu e schimbat pe token securizat cu verificare PKCE; sesiunea nu se creează. Fix: adaugă `await supabase.auth.exchangeCodeForSession(code)`)
- Callback există și `exchangeCodeForSession` prezent → **OK**
- Nu există callback → **OK** (nu e obligatoriu dacă nu folosești OAuth)

**A3 — Open Redirect Prevention în callback**
Citește fișierul callback (`app/auth/callback/route.ts`).
Verifică dacă parametrul `next` (sau similar) e validat cu pattern `next.startsWith('/')` + `!next.startsWith('//')` sau echivalent.
- Callback există, `next` e folosit ca redirect destination, validare absent → **BLOCKER** (atacatorul trimite `?next=https://evil.com` și primește token-ul după redirect. Fix: `const safeNext = next.startsWith('/') && !next.startsWith('//') ? next : '/dashboard'`)
- Validare prezentă sau `next` absent → **OK**

**A4 — Cookie security attributes (httpOnly + sameSite)**
Grep pentru `sameSite` sau `httpOnly` în fișierele din `lib/supabase/` sau fișiere cu `createServerClient`.
- `httpOnly: true` absent din setarea cookie → **ATENȚIE** (JS client poate citi token-ul din cookie; XSS fură sesiunea)
- `sameSite: 'strict'` în loc de `'lax'` → **ATENȚIE** (strict rupe OAuth redirects — Google/GitHub redirect înapoi nu trimite cookie-ul)
- `httpOnly: true` și `sameSite: 'lax'` prezente → **OK**

**A5 — Env vars validate la startup**
Grep pentru `envSchema` sau `z.object` în fișiere din `lib/env` sau similar.
Dacă nu există validare centralizată, numără apariții de `process.env.NEXT_PUBLIC_SUPABASE` sau `process.env.SUPABASE` în fișierele proiectului.
- Zero validare Zod și mai mult de 3 accesări directe `process.env.SUPABASE*` → **ATENȚIE** (variabilă `.env` lipsă = `undefined` silențios la runtime, crash greu de depanat. Fix: creează `lib/env.ts` cu Zod schema care validează la startup)
- Există validare sau mai puțin de 4 accesări → **OK**

---

### CATEGORIA B — RLS & STORAGE

*Se aplică dacă există fișiere SQL (migrations) sau referințe la `storage.objects` în proiect.*
*Dacă SQL și storage complet absente: marchează cu `— (SQL/Storage negăsite)` dar notează că RLS trebuie verificat manual în Supabase Dashboard.*

**B1 — UPDATE policies cu WITH CHECK**
Grep pentru `FOR UPDATE` în fișierele `.sql` din `supabase/migrations/` sau oriunde în proiect.
Pentru fiecare politică `FOR UPDATE`, verifică dacă există `WITH CHECK` în același bloc.
- `FOR UPDATE` cu `USING` dar fără `WITH CHECK` → **ATENȚIE** (permite schimbarea user_id la altul — "furt" de înregistrare. Fix: adaugă `WITH CHECK (user_id = auth.uid())` sau equivalent)
- Toate `FOR UPDATE` au `WITH CHECK` sau nu există UPDATE policies → **OK**

**B2 — TO authenticated în politici**
Grep pentru `CREATE POLICY` în fișierele SQL.
Verifică ce procent au `TO authenticated` explicit.
- Politici fără `TO authenticated` → **ATENȚIE** (fără `TO authenticated`, politica se aplică și rolului `anon` — utilizatori neautentificați pot fi afectați sau exploata politica. Fix: adaugă `TO authenticated` la fiecare politică pentru date utilizator)
- Toate au `TO authenticated` sau nu există politici → **OK**

**B3 — user_roles / audit_log blocate la mutații directe**
Grep pentru `user_roles` și `audit_log` în fișierele SQL.
Dacă tabelele există, verifică prezența `WITH CHECK (false)` pe INSERT/UPDATE/DELETE.
- `user_roles` sau `audit_log` există în SQL dar fără `WITH CHECK (false)` pe mutații → **BLOCKER** (oricine poate face `INSERT INTO user_roles VALUES (auth.uid(), 'admin')` — privilege escalation trivial. Fix: adaugă politici block pe INSERT/UPDATE/DELETE cu `WITH CHECK (false)` sau `USING (false)`)
- Politici block prezente sau tabele inexistente → **OK**

**B4 — getPublicUrl() pentru fișiere private**
Grep pentru `.getPublicUrl(` în fișierele `.ts` și `.tsx`.
- `.getPublicUrl(` găsit → verifică dacă bucket-ul referit sugerează conținut privat (cuvinte cheie: `documents`, `private`, `medical`, `financial`, `contracts`, `files`, `uploads`, `records`)
- Bucket cu nume sensibil + `getPublicUrl()` → **BLOCKER** (URL permanent public la oricine — documente medicale/financiare expuse. Fix: înlocuiește cu `createSignedUrl(path, 3600)`)
- Bucket generic sau absent → **ATENȚIE** (verifică manual că bucket-ul e într-adevăr public)
- `getPublicUrl` absent → **OK**

**B5 — SECURITY DEFINER cu SQL dinamic**
Grep pentru `SECURITY DEFINER` în fișierele SQL.
Pentru fiecare funcție cu SECURITY DEFINER, verifică prezența `||` (string concat) sau `EXECUTE` sau `format(` cu variabile în apropiere.
- SECURITY DEFINER + SQL dinamic cu `||` sau `EXECUTE format(` → **BLOCKER** (SQL injection cu privilegii postgres — cel mai sever tip de injection posibil. Fix: folosește SQL static parametrizat; NICIODATĂ string interpolation în SECURITY DEFINER)
- SECURITY DEFINER cu SQL static sau absent → **OK**

---

### CATEGORIA C — MIDDLEWARE & SECURITY HEADERS

*Se aplică EXCLUSIV pentru proiecte Next.js. Dacă HTML Vanilla: marchează toată categoria cu `— (fără middleware Next.js)`*

**C1 — Matcher negativ în middleware**
Citește fișierul `middleware.ts` sau `middleware.js`.
Verifică câmpul `matcher` din `export const config`.
- Matcher pozitiv (ex: `['/dashboard/:path*', '/admin/:path*']` sau `['/api/:path*']`) → **BLOCKER** (rutele nelistate sunt complet neprotejate — un endpoint `/api/admin/users` adăugat fără a actualiza matcher-ul e public. Fix: înlocuiește cu matcher negativ: `'/((?!_next/static|_next/image|favicon.ico|robots.txt|public/).*)'`)
- Matcher absent (middleware fără config) → **ATENȚIE** (implicit: tot, dar include și static assets — ineficient)
- Matcher negativ cu `(?!` prezent → **OK**

**C2 — Security headers în next.config**
Citește `next.config.ts` sau `next.config.js`.
Verifică prezența funcției `headers()` cu: `X-Frame-Options`, `X-Content-Type-Options`, `Content-Security-Policy`.
- Funcția `headers()` complet absentă → **ATENȚIE** (vulnerabil la clickjacking, MIME sniffing, XSS via iframe. Fix: adaugă blocul `headers()` cu cele 5 headere de securitate din S15 al ghidului)
- `headers()` există dar lipsesc 2+ headere → **ATENȚIE** (protecție parțială — listează headerele lipsă)
- Toate 3+ prezente → **OK**

**C3 — Webhook signature verification**
Glob pentru fișiere cu `webhook` în cale: `**/webhook*`, `**/webhooks*`.
Dacă există route handlers de webhook, grep pentru `timingSafeEqual` sau `crypto.timingSafeEqual`.
- Webhook route există dar `timingSafeEqual` absent → **BLOCKER** (comparare naivă a semnăturilor e vulnerabilă la timing attacks — atacatorul poate ghici HMAC-ul bit cu bit. Fix: `crypto.timingSafeEqual(Buffer.from(signature), Buffer.from(expectedSig))`)
- `timingSafeEqual` prezent sau webhook absent → **OK**

**C4 — Route Handlers fără Origin validation**
Glob pentru `**/route.ts` (exclude `auth/callback`).
Grep pentru `POST` handler în fișierele găsite.
Verifică dacă cel puțin un Route Handler POST verifică `request.headers.get('origin')` sau `request.headers.get('Origin')`.
- Există Route Handlers POST dar niciun `Origin` header check → **ATENȚIE** (Route Handlers nu au protecție CSRF automată ca Server Actions — un request cross-site poate executa mutații. Fix: adaugă `const origin = request.headers.get('origin'); if (origin !== process.env.NEXT_PUBLIC_APP_URL) return NextResponse.json({ error: 'Forbidden' }, { status: 403 })`)
- Cel puțin unul verifică Origin sau nu există Route Handlers POST → **OK**

---

### CATEGORIA D — SESSION & PASSWORD SECURITY

**D1 — Password change fără session revocation**
Grep pentru `updateUser` cu `password` în fișierele `.ts` / `.tsx`.
Pattern: `updateUser({` sau `updateUser({ password` sau `updateUser({\s*password`.
Dacă găsești, verifică dacă în același fișier sau acțiune există apel la `signOut.*scope.*others` sau `admin.signOut(.*'others')` sau `adminSupabase.auth.admin.signOut`.
- `updateUser({ password` fără `signOut` cu scope 'others' în proximity → **BLOCKER** (sesiunile active pe alte device-uri rămân valide cu parola veche — atacatorul care știa parola veche menține accesul. Fix: după `updateUser({ password })`, apelează `await adminSupabase.auth.admin.signOut(user.id, 'others')`)
- Password change cu revocation prezentă sau pattern absent → **OK**

**D2 — signOut() fără scope explicit**
Grep pentru `auth.signOut()` sau `signOut()` (fără parametri) sau `signOut({})` în fișierele `.ts` / `.tsx`.
- `signOut()` fără `{ scope: '...' }` → **ATENȚIE** (default scope e 'local' — delogarea nu revocă sesiunile de pe alte device-uri; utilizatorul crede că e delogat global dar alte sesiuni rămân active. Fix: folosește scope explicit: `signOut({ scope: 'local' })` pentru delogare device-curent sau `scope: 'global'` pentru toate device-urile)
- Toate `signOut` au scope explicit → **OK**

**D3 — Magic link URL logat în server logs**
Grep pentru `console.log` în fișierele `.ts` / `.tsx` server-side.
Verifică dacă în proximity de `signInWithOtp` sau `generateLink` există `console.log` cu variabile de tip URL sau link.
Pattern suspect: `console.log(.*[Uu]rl|.*[Ll]ink|.*[Tt]oken|.*[Mm]agic)` în fișiere server-side cu OTP.
- Pattern găsit → **ATENȚIE** (magic link conține token sensibil — dacă e logat, oricine cu acces la logs poate uzurpa sesiunea. Fix: loghează doar `'Magic link sent to ' + email`, niciodată URL-ul complet)
- Absent → **OK**

---

### CATEGORIA E — SERVER ACTIONS & RATE LIMITING

*Se aplică dacă există `'use server'` sau fișiere în `actions/`.*
*Dacă absent: marchează toată categoria cu `— (Server Actions negăsite)`*

**E1 — Server Action fără auth check**
Glob pentru fișiere cu `'use server'` sau din `actions/`.
Grep pentru `supabase.from(` sau `.insert(` sau `.update(` sau `.delete(` în aceste fișiere.
Pentru fiecare fișier cu mutații DB, verifică prezența `getUser()` sau `auth.getUser()` înainte de mutație.
- Fișier cu `'use server'` care face mutații DB fără `getUser()` → **BLOCKER** (Server Action fără autentificare — oricine poate apela acțiunea direct din browser console. Fix: adaugă `const { data: { user } } = await supabase.auth.getUser(); if (!user) return { error: 'Unauthorized' }` ca primă operație)
- Toate acțiunile cu mutații verifică auth sau nu există → **OK**

**E2 — Rate limiting absent**
Grep pentru `rateLimit` sau `@upstash/ratelimit` sau `redis` în fișierele `.ts` / `.tsx` sau `package.json`.
Verifică dacă există Server Actions cu operații sensibile (auth, submit, send, upload, approve).
- Server Actions sensibile există dar fără niciun mecanism de rate limiting → **ATENȚIE** (brute force pe login/signup/submit posibil; 1000 cereri/secundă fără cost. Fix: adaugă Upstash Redis ratelimit sau middleware-level rate limiting)
- Rate limiting prezent sau Server Actions absente → **OK**

**E3 — Server Action chain incomplet (auth→RBAC→Zod)**
Grep pentru fișiere cu `'use server'` care conțin `.insert(` sau `.update(` sau `.delete(`.
Verifică prezența TUTUROR în același fișier: `getUser()` + (`canDo` sau `hasPermission` sau rol check din DB) + `z.object` sau `.safeParse(` sau `.parse(`.
- Acțiuni cu mutații sensibile fără toate 3 componente → **ATENȚIE** (lanțul complet: auth → RBAC → validare Zod — lipsa oricăruia lasă un vector de atac. Notează ce lipsește: auth / RBAC / Zod)
- Toate 3 prezente sau acțiuni simple (CRUD personal fără RBAC) → **OK**

---

### CATEGORIA F — HTML VANILLA SECURITY

*Se aplică EXCLUSIV pentru proiecte HTML Vanilla (fișiere `.html` / `.js` fără next.config).*
*Pentru Next.js: marchează toată categoria cu `— (Next.js project — F nu se aplică)`*

**F1 — innerHTML cu date utilizator**
Grep pentru `innerHTML\s*=` sau `\.innerHTML\s*=` în fișierele `.js` și `.html`.
Pentru fiecare apariție, verifică dacă valoarea e o variabilă sau expresie (nu string literal hardcodat).
- `element.innerHTML = variabila` sau `el.innerHTML = getData()` sau similar → **BLOCKER** (XSS garantat dacă variabila conține input utilizator sau date din API. Fix: înlocuiește cu `element.textContent = variabila` sau folosește `DOMPurify.sanitize()` dacă HTML e strict necesar)
- Doar string literale hardcodate sau `textContent` → **OK**

**F2 — Subresource Integrity pe scripturi CDN**
Grep pentru `<script` cu `http://` sau `https://` (CDN extern) în fișierele `.html`.
Verifică dacă atributul `integrity=` e prezent pe scripturile CDN găsite.
- Script CDN fără `integrity=` → **ATENȚIE** (CDN compromis = cod malițios rulat în browser-ul tuturor utilizatorilor. Fix: generează hash SHA-384 via `openssl dgst -sha384 -binary file.js | openssl base64 -A` și adaugă `integrity="sha384-[HASH]" crossorigin="anonymous"`)
- Toate CDN-urile au `integrity=` sau nu există CDN scripts → **OK**

---

## PASUL 4 — Raportează în formatul exact de mai jos

```
=== AUTH-AUDIT: [director / proiect] ===
Tip proiect: [Next.js / HTML Vanilla / Mix]
Fișiere analizate: [N] TS/TSX + [M] HTML/JS + [migrations SQL: DA/NU] + [middleware: DA/NU] + [.env.local: DA/NU]

── A. SUPABASE AUTH SETUP ───────────────────────
  [✓/✗]   A1 getUser() (nu getSession()) server    [status + fișier:linie dacă BLOCKER]
  [✓/✗]   A2 exchangeCodeForSession în callback    [status + detaliu dacă BLOCKER]
  [✓/✗]   A3 Open redirect prevention              [status + fișier:linie dacă BLOCKER]
  [✓/!]   A4 Cookie: httpOnly + sameSite lax        [status + ce lipsește dacă ATENȚIE]
  [✓/!]   A5 Env vars validate cu Zod              [status]
  (sau: — Supabase negăsit în proiect)

── B. RLS & STORAGE ─────────────────────────────
  [✓/!]   B1 UPDATE policies cu WITH CHECK         [status + fișier:linie dacă ATENȚIE]
  [✓/!]   B2 TO authenticated în politici          [status + câte lipsesc dacă ATENȚIE]
  [✓/✗]   B3 user_roles/audit_log blocate          [status + tabel neprotejat dacă BLOCKER]
  [✓/✗/!] B4 getPublicUrl() pentru private         [status + fișier:linie dacă problemă]
  [✓/✗]   B5 SECURITY DEFINER SQL static           [status + funcție afectată dacă BLOCKER]
  (sau: — SQL/Storage negăsite, verificare manuală necesară în Dashboard)

── C. MIDDLEWARE & SECURITY HEADERS ─────────────
  [✓/✗]   C1 Matcher negativ în middleware         [status + tip matcher găsit dacă BLOCKER]
  [✓/!]   C2 Security headers în next.config       [status + headere lipsă dacă ATENȚIE]
  [✓/✗]   C3 Webhook signature timingSafeEqual     [status + fișier dacă BLOCKER]
  [✓/!]   C4 Route Handlers cu Origin validation   [status + număr handlers neprotejați]
  (sau: — fără middleware Next.js)

── D. SESSION & PASSWORD SECURITY ───────────────
  [✓/✗]   D1 Password change + session revocation  [status + fișier:linie dacă BLOCKER]
  [✓/!]   D2 signOut() cu scope explicit           [status + fișier:linie dacă ATENȚIE]
  [✓/!]   D3 Magic link URL absent din logs        [status + fișier:linie dacă ATENȚIE]

── E. SERVER ACTIONS & RATE LIMITING ────────────
  [✓/✗]   E1 Server Action cu auth check           [status + fișier dacă BLOCKER]
  [✓/!]   E2 Rate limiting prezent                 [status]
  [✓/!]   E3 Chain auth→RBAC→Zod complet           [status + ce lipsește pe fișier dacă ATENȚIE]
  (sau: — Server Actions negăsite)

── F. HTML VANILLA SECURITY ─────────────────────
  [✓/✗]   F1 innerHTML absent cu date dinamice     [status + fișier:linie dacă BLOCKER]
  [✓/!]   F2 SRI pe scripturi CDN                  [status + scripturi fără integrity dacă ATENȚIE]
  (sau: — Next.js project — F nu se aplică)

══════════════════════════════════════════════════
BLOCKER-e: [N]  |  ATENȚIE: [M]  |  OK: [K]

VERDICT: [BLOCKER ✗ / ATENȚIE ⚠ / CLEAN ✓]

Fix-uri necesare (BLOCKER-e în ordinea impactului):
  1. [A1/B3/C1/...] descriere exactă + codul exact de adăugat/modificat
  2. ...

Verificări manuale necesare (nu detectabile static):
  - RLS ENABLE ROW LEVEL SECURITY activat pe toate tabelele → Supabase Dashboard → Table Editor
  - `.env.local` și `.env*.local` în `.gitignore` → `git log -S 'SUPABASE_SERVICE_ROLE'`
  - TypeScript types generate din DB schema → `npx supabase gen types typescript --local`
  - MFA recovery codes hashuite în DB (nu stocate plain text)
  - Backup-uri criptate activate → Supabase Dashboard → Settings → Backups
  - Incident response plan documentat (cine / ce / în cât timp per tip de incident)
```

---

## Reguli de verdict

| Condiție | Verdict |
|---|---|
| Cel puțin un BLOCKER | **BLOCKER ✗** — listezi fix-ul complet pentru fiecare |
| Zero BLOCKER-e, cel puțin un ATENȚIE | **ATENȚIE ⚠** — informezi, utilizatorul decide |
| Toate OK sau INFO | **CLEAN ✓** |

---

## Note de execuție

- **Nu modifica niciun fișier** — doar raportezi; utilizatorul decide ce și când fixează
- **Specifică întotdeauna fișier + linie** pentru BLOCKER și ATENȚIE — nu raporta vag
- **Ordinea fix-urilor la BLOCKER**: A1 (getSession) > A2 (exchangeCode) > A3 (open redirect) > B3 (privilege escalation) > B5 (SECURITY DEFINER) > B4 (getPublicUrl) > C1 (matcher) > C3 (webhook HMAC) > D1 (password+sessions) > E1 (Server Action auth) > F1 (innerHTML) — impactul de securitate primul
- **Categoria SQL fără fișiere locale**: e normal să nu existe SQL în repo dacă migrările sunt în Supabase Dashboard — notează că verificarea B1/B2/B3 trebuie făcută manual în Dashboard → SQL Editor
- **Proiecte fără Supabase**: categoria A marchează `— (Supabase negăsit)`, B marchează `— (Supabase negăsit)`, continuă cu C, D, E, F
- **Proiecte HTML Vanilla cu Supabase CDN**: A1, A2, A3 se aplică în fișierele `.js`; caută `supabase.auth.getSession()` în context non-client — în Vanilla tot e client, deci A1 e mai puțin relevant; notează `— (Vanilla: getSession OK în browser)`
- **Proiecte fără Server Actions** (fără `'use server'` sau `actions/`): categoria E marchează `— (Server Actions negăsite)` — nu e eroare
