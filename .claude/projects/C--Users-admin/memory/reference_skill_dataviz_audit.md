---
name: reference-skill-dataviz-audit
description: "Skill /dataviz-audit — audit static data visualization pe 16 reguli (Chart.js/Canvas/Recharts/ECharts/Date/Robustness); acoperă HTML Vanilla + Next.js; BLOCKER/ATENȚIE/OK"
metadata:
  node_type: memory
  type: reference
  originSessionId: a3fd517a-f93d-4269-830f-cf60e6caed19
---

Skill `/dataviz-audit` — audit static de cod pentru proiecte cu grafice și vizualizări de date.

**Locație fișier:** `C:\Users\admin\.claude\commands\dataviz-audit.md`

**Invocare:** `/dataviz-audit Desktop/cashpulse` (cu cale) sau `/dataviz-audit` (întreabă)

**Ce face:** Detectează automat librăriile prezente (Chart.js, Canvas, Recharts, ECharts), tipul de proiect (HTML Vanilla / Next.js / mix), și raportează BLOCKER / ATENȚIE / OK pentru 16 reguli pe 6 categorii. Nu modifică cod — doar raportează.

**Detectare automată:**
- Chart.js: `new Chart(` sau `Chart.register(`
- Canvas API: `getContext('2d')`
- Recharts: `from 'recharts'`
- ECharts: `from 'echarts'` sau `echarts-for-react`
- Tip proiect: `next.config.*` → Next.js; doar `*.html` → HTML Vanilla

**Cele 16 reguli:**

- **A. Chart.js** (3 reguli)
  - A1: `destroy()` în useEffect cleanup — **BLOCKER** dacă absent (Canvas already in use)
  - A2: `chart.update()` vs `destroy+new Chart` pentru update date — **ATENȚIE**
  - A3: `maintainAspectRatio: false` fără container height — **ATENȚIE**

- **B. Canvas API** (4 reguli)
  - B1: `devicePixelRatio` în canvas setup — **ATENȚIE** (blur Retina)
  - B2: `ctx.beginPath()` înainte de fiecare shape — **BLOCKER** dacă absent
  - B3: `cancelAnimationFrame` în cleanup — **BLOCKER** dacă absent (memory leak rAF)
  - B4: `ctx.save()` + `ctx.restore()` echilibrate — **ATENȚIE**

- **C. Recharts** (4 reguli — Next.js)
  - C1: `'use client'` sau `dynamic ssr:false` — **BLOCKER** (window is not defined)
  - C2: `ResponsiveContainer` cu height explicit — **BLOCKER** (0px înălțime)
  - C3: Formatters cu `useCallback` — **ATENȚIE** (re-render la keystroke)
  - C4: `isAnimationActive={false}` pe live data — **INFO**

- **D. Date & Timezone** (2 reguli)
  - D1: `new Date('YYYY-MM-DD')` fără `T00:00:00` — **ATENȚIE** (timezone bug UTC-x)
  - D2: `Date` objects ca props Server→Client — **BLOCKER** (Next.js)

- **E. Robustness** (2 reguli)
  - E1: `beginAtZero: true` pe bar charts — **ATENȚIE** (lie factor vizual)
  - E2: `ChartErrorBoundary` prezent — **ATENȚIE** (Next.js cu date externe)

- **F. ECharts** (2 reguli — Next.js)
  - F1: `dynamic ssr:false` — **BLOCKER** dacă absent
  - F2: `progressive` rendering pe datasets mari — **INFO**

**Ordinea fix-urilor la BLOCKER:** B3 (rAF leak) > A1 (Chart.js destroy) > C1 (Recharts SSR) > C2 (ResponsiveContainer height) > B2 (beginPath) > D2 (Date server→client) > F1 (ECharts SSR)

**Proiecte țintă:** CashPulse · Daily Sales Flash · MenuMix Matrix · StudioFlow Intelligence · Vibe Budget · ERP Financiar · Clinică Medicală · orice proiect cu grafice

**How to apply:** Înainte de orice deploy pe proiect cu charts, sau când apar bug-uri vizuale/de rendering — rulează `/dataviz-audit [proiect]` pentru diagnostic rapid.

**Legat de:** [[reference-skill-nextjs-audit]], [[reference-skill-offline-audit]], [[project_ghid_data_viz]]
