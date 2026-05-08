---
name: CashPulse
description: Tool gratuit forecast cash-flow 13 săptămâni pentru IMM-uri românești — status implementare completă
type: project
originSessionId: d7e8781f-ec1c-4763-8bab-c6b63b289187
---
Aplicație completă, implementată și commitată local (branch main, nepushed).

**Why:** Lead magnet gratuit pentru proprietari de IMM, construiește autoritate subtilă pentru creator. Descărcabil, rulează offline, fără cont/API/server.

**Fișiere:**
- `C:\Users\admin\Desktop\cashpulse\app\cashpulse.html` — aplicația dev (Chart.js extern din assets/)
- `C:\Users\admin\Desktop\cashpulse\dist\cashpulse.html` — bundle self-contained (253KB, Chart.js inline)
- `C:\Users\admin\Desktop\cashpulse\dist\cashpulse.zip` — pachet final pentru download (82KB)
- `C:\Users\admin\Desktop\cashpulse\landing\index.html` — landing page de download

**Stack:** Single HTML file, CSS + JS inline, Chart.js v4.4.4 bundled local, LocalStorage persistență.

**Template-uri (calibrate să arate deficit):**
- HoReCa: soldInitial 12000, cheltuieliFixe 9500 → deficit realist săpt 11
- Retail: soldInitial 15000, cheltuieliFixe 13000 → deficit realist săpt 10
- Servicii: încasări lunare (săpt 4,8,12), cheltuieliFixe 6000 → deficit realist săpt 6

**Features implementate (toate 10 module):** wizard 3 pași, selectare industrie, motor calcul forecast, grafic Chart.js bare colorate (albastru/roșu), alertă cash gap + runway, scenarii pesimist/realist/optimist (±20%), LocalStorage auto-save + restore modal, tooltips educaționale, export PDF (window.print), bundle ZIP.

**Server local:** `node -e "http.createServer(...).listen(8080)"` din `cashpulse/`
- App: http://localhost:8080/dist/cashpulse.html
- Landing: http://localhost:8080/landing/index.html

**How to apply:** Proiect complet — dacă utilizatorul revine, probabil vrea să distribuie (hosting landing page) sau să adauge funcționalități noi.
