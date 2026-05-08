---
name: StudioFlow — Architecture Studio CRM
description: CRM/BizDev app pentru HERTZ Studio (arhitectură + design). PRD v5.0 final, implementare neîncepută. 2 HTML + manifest + sw.js, offline, IndexedDB.
type: project
originSessionId: 6fd381b6-95a2-442f-b17c-51eabe076b26
---
# StudioFlow — Architecture Studio CRM

**Client:** HERTZ Studio — Str. Spătarului nr. 36, S2, București (owner/architect-chief, solo user)  
**PRD:** v5.0 final — salvat la `C:\Users\admin\Desktop\StudioFlow PRD v5.0.md`  
**Status:** PRD complet, implementare neîncepută

## Stack
- 2 fișiere HTML: `app.html` (app) + `offer.html` (renderer ofertă print)
- `manifest.json` + `sw.js` (PWA)
- Vanilla JS ES6+ · IndexedDB · File System Access API · Canvas API · Chart.js bundled
- Zero server · Zero npm runtime · Offline-first · Chrome/Edge recomandat

## 10 Module (ordinea de build)
```
Sprint 1 (MVP):  F8 Foundation → F0 Setup+Import → F2 Lead+Scoring → F3 Pipeline Kanban
Sprint 2:        F1 Calculator+Price Intelligence → F4 Activity Cadence → F9 Today View
Sprint 3:        F5a Portfolio Manager → F5 Offer Generator → F6 Client 360
Sprint 4:        F7 Intelligence Layer → PWA (manifest + sw.js)
```

## Date cheie HERTZ (din documente analizate)
- Conversion rate: 62.9% (2019) → 19.6% (2025) → 5.2% (2026 parțial)
- ~25–30 oferte/an · 5 surse lead · 2 tipuri ofertă (Discovery Brief + Proiectare Generală)
- Scoring: 14 criterii 0–10 · Hot≥105 · Warm 70–104 · Cold<70
- Calculator ARH: T1-T6, 7 faze, 10 condiții speciale, gamma bands
- Calculator INT: T1-T6, 10 faze, 8 condiții speciale, gamma bands diferite

## Arhitectura critică (rezolvată în v5.0)
- **Data schema:** 8 entități (Studio, Client, Lead, Offer, Activity, Portfolio, RateCard, SystemSettings)
- **offer.html ↔ app.html:** URL param `?offerId=X` + sessionStorage fallback → IndexedDB read
- **Learning Loop:** rule-based (nu ML), calibrare manuală după n=20/50 debriefuri
- **Price Intelligence:** activ la n≥30 deals per categorie (insufficient_data sub prag)
- **Capacity Go/No-Go:** weeklyCapacityHours + activeProjectsLimit în Studio entity
- **Browser:** Chrome/Edge full · Firefox/Safari = core app OK, auto-backup fallback manual

## KPIs target
- Conversion rate: de la 19.6% → ≥35% în 12 luni
- Timp per ofertă: ≤2h (de la ~4h manual)
- Follow-up coverage: 100% (de la ~0% structurat)

**Why:** HERTZ urmărește oprit tendința de scădere a conversiei + eficiență operațională  
**How to apply:** La implementare, respectă ordinea de build Sprint 1→4; nu schimba stack-ul fără confirmare
