---
description: Audit offline-first — verifică 12 reguli critice (localStorage, IndexedDB, Service Worker, PWA) în fișierele proiectului. Raportează BLOCKER / ATENȚIE / OK fără a modifica codul.
---

# /offline-audit — Audit Offline-First Architecture

**Scopul:** Analizează fișierele proiectului pentru probleme de offline-first architecture și raportează BLOCKER / ATENȚIE / OK per regulă. Bazat pe ghid-offline-first-architecture-v1.md.

---

## PASUL 1 — Identifică directorul

**Dacă $ARGUMENTS conține o cale** (ex: `/offline-audit Desktop/cashpulse`):
Lucrează în: `C:\Users\admin\$ARGUMENTS`

**Dacă $ARGUMENTS este gol:**
Întreabă utilizatorul: `Pe care proiect rulăm auditul? (ex: Desktop/cashpulse)`
Sau dacă există context clar din sesiune, folosește directorul curent.

---

## PASUL 2 — Găsește fișierele relevante

Rulează în paralel cu Glob:
- `*.html` în directorul proiectului
- `*.js` în directorul proiectului (exclude node_modules, .next, dist, .git)
- `sw.js` sau `service-worker.js` (rădăcina proiectului)
- `manifest.json` sau `manifest.webmanifest` (rădăcina sau public/)

Dacă nu găsești niciun fișier HTML sau JS: raportează `EROARE: director gol sau cale greșită` și oprește.

Notează ce ai găsit: [N] HTML + [M] JS + sw.js: DA/NU + manifest.json: DA/NU

---

## PASUL 3 — Rulează verificările pe 4 categorii

### CATEGORIA A — LocalStorage

*Rulează verificările A dacă găsești `localStorage` în orice fișier.*

**A1 — QuotaExceededError tratat**
Grep pentru `localStorage\.setItem` în fișierele proiectului.
Dacă găsești apeluri `setItem`:
- Verifică dacă există `try` + `catch` care învelește apelul.
- `catch` există dar fără `QuotaExceededError` → **ATENȚIE** (erorile de stocare plin sunt ignorate silențios)
- Niciun `try/catch` în același fișier unde există `setItem` → **BLOCKER**
- `catch` cu `QuotaExceededError` sau mesaj user → **OK**

**A2 — JSON.parse cu fallback**
Grep pentru `JSON\.parse\(localStorage\.getItem`.
- Pattern fără `?? ` și fără `try/catch` → **ATENȚIE** (crash garantat la JSON corupt sau localStorage gol)
- Are fallback: `JSON.parse(... ?? '[]')` sau `try/catch` → **OK**

**A3 — Key namespacing**
Grep pentru `localStorage\.setItem\(['"]` și `localStorage\.getItem\(['"]`.
Uită-te la cheile folosite. Caută dacă există o constantă PREFIX definită sau dacă cheile au un prefix consistent (ex: `cashpulse_`, `APP_`).
- Chei bare fără prefix: `'items'`, `'data'`, `'state'` → **ATENȚIE** (coliziuni între proiecte sau versiuni diferite)
- Chei cu prefix constant sau variabilă PREFIX → **OK**

**A4 — Schema versioning**
Grep pentru `_schema_version` sau `STORAGE_VERSION` sau `_db_version` sau `migrations`.
- Nu există niciun mecanism de versioning → **ATENȚIE** (schimbările de structură vor corupe date existente)
- Există → **OK**

---

### CATEGORIA B — IndexedDB

*Rulează verificările B doar dacă găsești `indexedDB.open` sau `new Dexie` în fișiere.*
Dacă nu există niciun IndexedDB: marchează toată categoria cu `— (IndexedDB negăsit)`

**B1 — onversionchange apelat în onsuccess** *(cel mai critic — blochează upgrade DB)*
Grep pentru `onversionchange` sau `versionchange` sau `setupVersionChangeHandler`.

Scenariul de risc: funcția e *definită* dar nu e *apelată* în blocul `onsuccess`.
- Grep pentru `onsuccess` și verifică dacă în acel bloc există un apel la funcția/handler-ul de versionchange.
- Handler definit dar nechemat în `onsuccess` → **BLOCKER** (alte tab-uri blochează silențios upgrade-ul DB)
- Nu există niciun handler `onversionchange` → **BLOCKER**
- Handler apelat explicit în `onsuccess`: `db.onversionchange = () => db.close()` sau `setupVersionChangeHandler(db)` → **OK**

**B2 — onblocked handler**
Grep pentru `\.onblocked` în vecinătatea unui `indexedDB.open`.
- Nu există → **ATENȚIE** (utilizatorul nu primește niciun feedback când upgrade-ul e blocat)
- Există → **OK**

**B3 — Dexie: ALL stores declarate la fiecare version()**
Grep pentru `.version(` în fișierele cu Dexie.
Dacă există version(2) sau mai mare, citește toate apelurile `.version(N).stores({...})`.
- version(2+) declară stores diferite fără să le repete pe cele din version(1) → **BLOCKER** (Dexie șterge stores nedeclarate la upgrade)
- Toate version-urile repetă toate stores → **OK**
- Există o singură versiune → **OK** (nu e cazul de upgrade încă)

**B4 — Persistent storage solicitat**
Grep pentru `navigator\.storage` sau `storage\.persist` sau `initPersistentStorage`.
- Nu există → **ATENȚIE** (browserul poate evicat datele IndexedDB sub presiune de memorie, fără avertizare)
- Există → **OK**

---

### CATEGORIA C — Service Worker

*Rulează verificările C doar dacă există sw.js sau `serviceWorker` în fișiere.*
Dacă nu există niciun SW: marchează toată categoria cu `— (Service Worker negăsit)`

**C1 — Locația sw.js (scope)**
Verifică unde se află sw.js (din Glob de la Pasul 2).
- `sw.js` în rădăcina proiectului → **OK** (scope = tot site-ul)
- `sw.js` într-un subfolder (`/js/sw.js`, `/src/sw.js`, `/assets/sw.js`) → **ATENȚIE** (scope limitat — controlează doar path-urile de sub acel folder)

**C2 — skipWaiting coordonat**
Grep pentru `skipWaiting` în sw.js.
- Există `skipWaiting()` → verifică dacă există și `postMessage` sau notificare user în același fișier sau în fișierele JS principale.
- `skipWaiting()` fără niciun `postMessage` și fără notificare → **ATENȚIE** (update activat silențios poate corupe state activ)
- `skipWaiting()` cu `postMessage` coordonat sau banner de reload → **OK**
- Nu există `skipWaiting` → **OK** (comportament standard — SW așteaptă)

**C3 — Strategie de caching definită**
Grep pentru `cache\.put` sau `caches\.open` sau `CacheFirst` sau `NetworkFirst` sau `StaleWhileRevalidate` sau `event\.respondWith`.
- Există SW dar nu există nicio strategie → **ATENȚIE** (SW interceptează cereri dar nu face nimic util offline)
- Există cel puțin o strategie → **OK**

---

### CATEGORIA D — PWA / Manifest

*Rulează verificările D doar dacă există manifest.json.*
Dacă nu există manifest: marchează toată categoria cu `— (manifest.json negăsit)`

Citește manifest.json pentru D1 și D2.

**D1 — Maskable icon**
Verifică câmpul `icons` din manifest.json.
- Există o singură intrare sau nicio intrare cu `"purpose": "maskable"` → **ATENȚIE** (icon apare tăiat pe Android — safe zone 60%)
- Există cel puțin una cu `"purpose": "any"` și una separată cu `"purpose": "maskable"` → **OK**

**D2 — start_url și display**
Verifică prezența `start_url` și `display` (valori acceptate: `"standalone"`, `"fullscreen"`, `"minimal-ui"`).
- Lipsesc ambele sau unul dintre ele → **ATENȚIE** (instalarea PWA nu funcționează corect)
- Ambele prezente → **OK**

**D3 — beforeinstallprompt (informativ)**
Grep pentru `beforeinstallprompt` în fișierele JS/HTML.
- Găsit → **INFO: implementat** (buton instalare custom activ)
- Nu găsit → **INFO: neimplementat** (opțional — browserul afișează prompt automat)

---

## PASUL 4 — Raportează în formatul exact de mai jos

```
=== OFFLINE-AUDIT: [director / proiect] ===
Fișiere analizate: [N] HTML + [M] JS + [sw.js: DA/NU] + [manifest.json: DA/NU]

── A. LOCALSTORAGE ──────────────────────────
  [✓/✗/!] A1 QuotaExceededError tratat     [status + detaliu fișier:linie dacă problemă]
  [✓/!]   A2 JSON.parse cu fallback        [status + detaliu]
  [✓/!]   A3 Key namespacing               [status + chei bare găsite dacă problemă]
  [✓/!]   A4 Schema versioning             [status]

── B. INDEXEDDB ─────────────────────────────
  [✓/✗]   B1 onversionchange în onsuccess  [status + fișier:linie dacă BLOCKER]
  [✓/!]   B2 onblocked handler             [status]
  [✓/✗]   B3 Dexie: ALL stores per version [status + detaliu dacă BLOCKER]
  [✓/!]   B4 navigator.storage.persist     [status]
  (sau: — IndexedDB/Dexie negăsite în proiect)

── C. SERVICE WORKER ────────────────────────
  [✓/!]   C1 Locație sw.js (scope)         [OK: rădăcină / ATENȚIE: subfolder path]
  [✓/!]   C2 skipWaiting coordonat         [status + fișier:linie dacă problemă]
  [✓/!]   C3 Strategie caching definită    [status]
  (sau: — Service Worker negăsit în proiect)

── D. PWA / MANIFEST ────────────────────────
  [✓/!]   D1 Maskable icon                 [status]
  [✓/!]   D2 start_url + display           [status]
  [i]     D3 beforeinstallprompt           [Implementat / Neimplementat (opțional)]
  (sau: — manifest.json negăsit)

══════════════════════════════════════════════
BLOCKER-e: [N]  |  ATENȚIE: [M]  |  OK: [K]

VERDICT: [BLOCKER ✗ / ATENȚIE ⚠ / CLEAN ✓]

Fix-uri necesare (BLOCKER-e în ordinea impactului):
  1. [B1/B3/A1] descriere exactă + linie de cod de adăugat
  2. ...
```

---

## Reguli de verdict

| Condiție | Verdict |
|---|---|
| Cel puțin un BLOCKER | **BLOCKER ✗** — oprești și listezi fix-ul complet |
| Zero BLOCKER-e, cel puțin un ATENȚIE | **ATENȚIE ⚠** — informezi, utilizatorul decide |
| Toate OK sau INFO | **CLEAN ✓** |

---

## Note de execuție

- **Nu modifica niciun fișier** — doar raportezi; utilizatorul decide ce și când fixează
- **Specifică întotdeauna fișier + linie** pentru BLOCKER și ATENȚIE — nu raporta vag
- **Ordinea fix-urilor la BLOCKER**: B1 (onversionchange) > B3 (Dexie stores) > A1 (QuotaExceededError) — cel mai mare impact primul
- **Categoria lipsă** (fără IndexedDB, SW sau manifest): marchează cu `—` și explică în paranteză — nu raporta ca eroare
- **Proiecte HTML Vanilla cu Dexie CDN**: `Dexie` e global (window.Dexie) — pattern `new Dexie(` e același, regulile B3 se aplică identic
