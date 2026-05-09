---
name: StudioFlow — Architecture Studio CRM
description: CRM/BizDev app pentru HERTZ Studio (arhitectură + design). PRD v6.0 final. M1–M7 implementate și commituite. Urmează M8 sf-f4 Activity Cadence.
type: project
originSessionId: 6fd381b6-95a2-442f-b17c-51eabe076b26
---
# StudioFlow — Architecture Studio CRM

**Client:** HERTZ Studio — Str. Spătarului nr. 36, S2, București (owner/architect-chief, solo user)  
**PRD:** v6.0 final — salvat la `C:\Users\admin\Desktop\StudioFlow PRD v6.0.md`  
**Status (2026-05-09):** M1–M14 implementate + commituite; commituri nepush-uite pe main

## Module implementate
| Modul | Commit | Conținut |
|-------|--------|----------|
| M1–M4 | `444633a` | HTML shell + CSS + sf-utils/db/state/router/ui + sf-f8 Foundation + sf-f0 Setup Wizard |
| M5 | `a30edba` | sf-f2 Lead Capture + Scoring live + Go/No-Go + Win Probability |
| M5 fix | `f285317` | 5 bug-uri M1–M4: toast dismiss, KPI CSS, modal CSS |
| M6 | `7d144e9` | sf-f3 Pipeline Kanban (6 coloane, filtre, stage age, terminal drops) |
| M6 audit | `fa093bf` | 5 bug-uri: null guards în handleTerminalStageDrop/markLeadWon/_confirmWon/_confirmLost + pipeTotal scope fix |
| M7 | `70314dd` | sf-f1 Calculator ARH/INT + Price Intelligence (295 linii) |
| M8 | `5904470` | sf-f4 Activity CRUD + Cadence + CADENCE_TEMPLATES |
| M9 | `399a28d` | sf-f9 Today View 4 secțiuni + notificări desktop + PWA Badge |
| M10 | `c145642` | sf-f3-dnd Drag-and-Drop Kanban (event delegation) |
| M11 | `b4d286b` | sf-f5a Portfolio Manager (grid, upload, compress, DnD reorder) |
| M12 | `deed1b5` | sf-f5 Offer Generator + offer.html renderer (9 secțiuni, print) |
| M13 | `80f765e` | sf-f6 Client 360 view + LTV + re-engagement |
| M14 | `66ed1ef` | sf-f7 Intelligence Dashboard — 6 panouri Canvas pură + Debrief dialog + CSV export |
| M15 | `8597bbf` | sf-f10 Settings — 7 secțiuni + 2 bug fixes (portfolio store + logoBlob sanitize) |
| M16 | `7efb419` | sf-export Export/Import public API — importFromBackup + exportLeadsCSV (65 ins, 44 del) |
| M17 | `79f3ed7` | sf-shortcuts Keyboard Shortcuts (N/L/1-9/?/Esc/Ctrl+B+S) + manifest.json final SVG icons |

## Urmează (sesiunea viitoare)
- **Sprint 4 COMPLET** — toate modulele M1–M17 implementate și commituite local
- **Push la origin/main** — 52 commit-uri locale nepush-uite
- **Testare end-to-end în browser** — verificare golden path complet
- **Deploy** — opțional: Netlify / GitHub Pages pentru acces offline

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
