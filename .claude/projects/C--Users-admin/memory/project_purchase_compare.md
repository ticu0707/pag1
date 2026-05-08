---
name: PurchaseCompare
description: Tool offline comparare oferte furnizori — 2 fișiere HTML, fără dependențe externe, lead magnet gratuit
type: project
originSessionId: 1b5a6505-ecd2-40a1-b4c8-f79314e19df0
---
PurchaseCompare este funcțional și testat de utilizator (2026-04-29).

**Fișiere:** `Desktop/purchase-compare/purchase-compare.html` + `landing.html`

**Why:** Lead magnet offline pentru retail/HoReCa/distribuție mică — compară oferte furnizori cu scoring ponderat, export PDF via window.print().

**Arhitectură:** IIFE modules sub namespace `PC` (același pattern ca DSF.*) — 9 module: PC.calc, PC.score, PC.validate, PC.settings, PC.suppliers, PC.storage, PC.results, PC.export, PC.app. Storage: sessionStorage (cheie `pc_session`).

**Bug-uri fixate în sesiune:**
- `readForm()`: `?? -1` nu prindea empty string → NaN în calcule; fixat cu `|| '0'`
- Câmp dată: `type="date"` afișa MM/DD/YYYY (locale US) → înlocuit cu text input `zz/ll/aaaa` + `type="date"` invizibil suprapus pe iconița 📅 pentru calendar nativ

**How to apply:** Dacă se revine la acest proiect, aplicația rulează complet offline din browser (dublu-click pe HTML). Nu necesită server, build sau dependențe.
