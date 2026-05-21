---
name: reference-skill-offline-audit
description: "Skill /offline-audit — audit static offline-first pe 12 reguli (localStorage, IndexedDB, SW, PWA); locație, utilizare, reguli acoperite"
metadata: 
  node_type: memory
  type: reference
  originSessionId: a3fd517a-f93d-4269-830f-cf60e6caed19
---

Skill `/offline-audit` — audit static de cod pentru proiecte offline-first.

**Locație fișier:** `C:\Users\admin\.claude\commands\offline-audit.md`

**Invocare:** `/offline-audit Desktop/cashpulse` (cu cale) sau `/offline-audit` (întreabă)

**Ce face:** Citește fișierele proiectului (HTML + JS + sw.js + manifest.json) și raportează BLOCKER / ATENȚIE / OK pentru 12 reguli pe 4 categorii. Nu modifică cod — doar raportează.

**Cele 12 reguli:**

- **A. LocalStorage** (4 reguli)
  - A1: `localStorage.setItem` învelit în `try/catch` cu `QuotaExceededError`
  - A2: `JSON.parse(localStorage.getItem(...))` cu fallback (`?? ` sau `try/catch`)
  - A3: Key namespacing — prefix constant (ex: `cashpulse_`, `APP_`)
  - A4: Schema versioning — mecanism de migrare la schimbarea structurii

- **B. IndexedDB** (4 reguli — dacă există `indexedDB.open` sau `new Dexie`)
  - B1: `onversionchange` handler apelat în `onsuccess` (nu doar definit) — **cel mai critic**
  - B2: `onblocked` handler prezent
  - B3: Dexie — toate stores declarate la fiecare `version()` (nu doar la prima)
  - B4: `navigator.storage.persist()` apelat la startup

- **C. Service Worker** (3 reguli — dacă există sw.js)
  - C1: sw.js în rădăcina proiectului (scope corect)
  - C2: `skipWaiting()` coordonat cu `postMessage` (nu bare)
  - C3: Cel puțin o strategie de caching definită

- **D. PWA / Manifest** (3 reguli — dacă există manifest.json)
  - D1: Icon cu `"purpose": "maskable"` separat de `"any"`
  - D2: `start_url` și `display` prezente
  - D3: `beforeinstallprompt` (informativ — opțional)

**Verdict:** BLOCKER ✗ (cel puțin un blocker) / ATENȚIE ⚠ (zero blockere, atenții) / CLEAN ✓

**Ordinea fix-urilor la BLOCKER:** B1 > B3 > A1 (impact descrescător)

**Proiecte țintă:** CashPulse · FollowUp Board · PurchaseCompare · Reorder Radar · InvoiceChaser · Daily Sales Flash · MenuMix Matrix · StudioFlow

**How to apply:** Înainte de orice deploy pe proiect offline-first, sau când apar bug-uri de date pierdute / stocare coruptă — rulează `/offline-audit [proiect]` pentru diagnostic rapid.

**Legat de:** [[project-ghid-offline-first]]
