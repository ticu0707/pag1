---
name: StudioFlow — Architecture Studio CRM
description: CRM/BizDev app pentru HERTZ Studio (arhitectură + design). PRD v6.0 final, implementare neîncepută. 4 fișiere (app.html, offer.html, manifest.json, sw.js), offline, IndexedDB.
type: project
originSessionId: 6fd381b6-95a2-442f-b17c-51eabe076b26
---
# StudioFlow — Architecture Studio CRM

**Client:** HERTZ Studio — Str. Spătarului nr. 36, S2, București (owner/architect-chief, solo user)  
**PRD:** v6.0 final — salvat la `C:\Users\admin\Desktop\StudioFlow PRD v6.0.md`  
**Status:** PRD complet (v6.0), implementare neîncepută

## Stack
- 4 fișiere: `app.html` + `offer.html` + `manifest.json` + `sw.js`
- Vanilla JS ES6+ · IndexedDB (DB class wrapper 50 linii) · Chart.js bundled · Canvas API
- CSS Custom Properties (Design System complet) · File System Access API
- Zero server · Zero npm runtime · Offline-first · Chrome/Edge recomandat

## 12 Module (ordinea de build)
```
Sprint 1 (MVP):   F8 Foundation → F0 Setup+Import → F2 Lead+Scoring → F3 Pipeline Kanban
Sprint 2:         F1 Calculator+Price Intelligence → F4 Activity Cadence → F9 Today View + F3 drag-drop
Sprint 3:         F5a Portfolio Manager → F5 Offer Generator → F6 Client 360
Sprint 4 (Final): F7 Intelligence Layer → F10 Settings → PWA + Export/Import complet
```

## Date cheie HERTZ
- Conversion rate: 62.9% (2019) → 19.6% (2025) → 5.2% (2026 parțial)
- ~25–30 oferte/an · 5 surse lead · 2 tipuri ofertă (Discovery Brief + Proiectare Generală)
- Scoring: 14 criterii 0–10 · Hot≥105 · Warm 70–104 · Cold<70 · max=140
- Calculator ARH: T1-T6, 7 faze, 10 condiții speciale, gamma bands
- Calculator INT: T1-T6, 10 faze, 8 condiții speciale (estimate în PRD, verificare Excel necesară)

## Arhitectura critică (v6.0)
- **Data schema:** 8 entități (Studio, Client, Lead, Offer, Activity, Portfolio, RateCard, SystemSettings)
- **DB Wrapper:** `class DB { get/put/delete/getAll/getAllByIndex/putBulk/count }` — 50 linii
- **Module-level state:** `AppState = { db, backupFolderHandle, ... }` — backupFolderHandle NU în IndexedDB
- **offer.html ↔ app.html:** URL param `?offerId=X` + sessionStorage fallback → IndexedDB read
- **Design System:** CSS Custom Properties (--sf-primary #1C3557, --sf-accent #C9963A, warm off-white bg)
- **Navigation:** Left sidebar 240px + hash routing + top bar
- **offerCode:** counter `lastOfferCodeSeq` în Settings (monoton, nu count by year)
- **estimatedEndDate:** pe Lead — necesar pentru Go/No-Go capacity check (activ dacă status=won + endDate>today)
- **Learning Loop:** rule-based, calibrare manuală la n=20/n=50 debriefuri
- **Price Intelligence:** activ la n≥30 per categorie (insufficient_data sub prag)
- **INT special conditions:** 8 condiții estimate — VERIFICARE necesară față de Calculator Excel

## KPIs target
- Conversion rate: de la 19.6% → ≥35% în 12 luni
- Timp per ofertă: ≤2h (de la ~4h manual)
- Follow-up coverage: 100% (de la ~0% structurat)

**Why:** HERTZ urmărește oprirea tendinței de scădere a conversiei + eficiență operațională  
**How to apply:** La implementare, respectă ordinea de build Sprint 1→4; nu schimba stack-ul fără confirmare; verifică INT special conditions față de Excel înainte de implementare F1
