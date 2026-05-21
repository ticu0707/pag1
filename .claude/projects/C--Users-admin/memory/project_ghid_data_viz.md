---
name: project_ghid_data_viz
description: "Ghid Data Visualization v1.0 COMPLET (18 secțiuni, 5 Bloc-uri): Chart.js, Canvas API, Recharts, D3 utilities, ECharts, SVG vs Canvas decision, timezone pitfall, spring physics, cross-filtering, Error Boundary, 24 greșeli"
metadata:
  node_type: memory
  type: project
  originSessionId: a3fd517a-f93d-4269-830f-cf60e6caed19
---

Ghid Skill 7 — Data Visualization v1.0 COMPLET, salvat la Desktop/Vibe-Coding/ghid-data-visualization-v1.md

**Why:** Aproape fiecare proiect din curs are grafice (CashPulse, Daily Sales Flash, MenuMix, StudioFlow Intelligence, Vibe Budget). Ghidul acoperă Chart.js avansat, Canvas API pur (deja în StudioFlow), Recharts pentru Next.js (nou), D3 utilities standalone și ECharts pentru big data.

**How to apply:** Referință la orice sesiune cu grafice — în special SVG vs Canvas decizie (Sec 0.2), timezone pitfall (Sec 12.1), data transitions fără destroy (Sec 5.1), ChartShell + Error Boundary (Sec 11.1-11.2), cross-filtering (Sec 10.5), stable references Recharts (Sec 10.1), 24 greșeli (Sec 14).

## Structură

18 secțiuni (0–17) în 5 Blocuri:
- Bloc 0: Principii (chart type decision, Tufte, SVG vs Canvas vs WebGL, ColorBrewer, Okabe-Ito, WCAG AA corect, dark mode, D3 utilities)
- Bloc 1: Chart.js (setup, theme switching, axis formatters, gradient fill, data labels, external tooltip, data transitions, live streaming, ring buffer, decimation LTTB)
- Bloc 2: Canvas API (HiDPI, beginPath pitfall, text rendering, ResizeObserver, hit testing, touch events passive:false, zoom/pan transform matrix, spring physics, OffscreenCanvas)
- Bloc 3: Recharts (hydration mismatch explicat, dynamic import, responsive config, ComposedChart, syncId, Brush, cross-filtering, ChartShell, Error Boundary, small multiples, export PNG/SVG/PDF)
- Bloc 4: Date & Performance (groupByMonth cu d3-array, axis formatters universali, timezone pitfall, Server+Client pattern, React Query/SWR, overplotting, ECharts Next.js, 24 greșeli, accesibilitate reală)

## Concepte Cheie Adăugate față de alte ghiduri

- `SVG vs Canvas vs WebGL` — decizie de arhitectură ÎNAINTE de library
- `timezone pitfall` — `new Date('2026-01-15')` = UTC midnight → wrong day în UTC-x; fix: `+ 'T00:00:00'`
- `beginPath()` pitfall Canvas — shape-urile anterioare se contopesc fără beginPath
- `spring physics` — animații naturale (k=0.12, d=0.85) vs easing simplu
- `ChartErrorBoundary` — React Error Boundary dedicat pentru grafice
- `ChartShell` — wrapper loading/empty/error reusabil
- `cross-filtering` — click pe o bară filtrează toate graficele din dashboard
- `useCallback([])` pe formatters Recharts — previne re-render complet la orice keystroke
- `contrastRatio()` — formula WCAG AA completă (nu aproximarea cu 0.179)
- `external tooltip` Chart.js — portal custom în afara canvas
- `ComposedChart` Recharts — Bar + Line + Area în același grafic
- `syncId` — tooltipuri sincronizate multi-chart
- `React Query/SWR` integration cu charts
- `ECharts WebGL` — `scatterGL` + `progressive` rendering pentru 100k+ puncte

[[project_ghid_nextjs]] [[project_ghid_offline_first]] [[project_erp_financiar]] [[project_vibe_budget]] [[project_cashpulse]] [[project_studioflow]]
