# Ghid 7 — Data Visualization (Chart.js · Canvas API · Recharts)
### v1.0 Final — Producție-ready, 0.1%

**Stack acoperit:** Chart.js 4 · react-chartjs-2 · Canvas 2D API · Recharts 2 · D3 utilities standalone · ECharts · Next.js 14+ App Router

---

## TL;DR — 3 reguli dacă nu citești nimic altceva

1. **Alege instrumentul potrivit**: Recharts (SVG) pentru < 1k elemente interactive; Canvas pentru 1k–100k; WebGL/ECharts pentru 100k+. Nu există "cel mai bun tool" — există "potrivit pentru sarcina dată"
2. **Culori non-negociabile**: Okabe-Ito pentru daltonism-safe, ColorBrewer pentru scale secvențiale/divergente — testează cu Chrome DevTools → Rendering → Deuteranopia înainte de orice deploy
3. **Date tranziționează, nu se teleportează**: `chart.update()` cu animație activă, niciodată `chart.destroy()` + reconstrucție; Canvas: interpolează `oldValue → newValue` cu spring physics în rAF loop

---

## Learning Map

★ = Must-know | ★★ = Important | ★★★ = Avansat

| # | Secțiune | Nivel |
|---|---|---|
| 0 | Chart type decision tree + Tufte + **SVG vs Canvas vs WebGL** | ★ |
| 1 | Culori — ColorBrewer · Okabe-Ito · dark mode · **WCAG corect** · **daltonism testing** | ★ |
| 2 | D3 Utilities standalone (scale · array · interpolate) | ★★ |
| 3 | Chart.js — setup · register · react-chartjs-2 · **theme switching** | ★ |
| 4 | Chart.js — **axis formatters** · multi-axis · **gradient fill** · **data labels** · **external tooltip** · click API | ★★ |
| 5 | Chart.js — **data transitions** · live streaming · ring buffer · decimation | ★★ |
| 6 | Canvas — HiDPI · primitives · **text rendering** · **beginPath pitfall** · **ResizeObserver** | ★★ |
| 7 | Canvas — hit testing · **touch events** · **zoom/pan cu transform matrix** | ★★★ |
| 8 | Canvas — **data transitions cu spring physics** · rAF · OffscreenCanvas | ★★★ |
| 9 | Recharts — setup · **de ce hydration fail** · dynamic import · **responsive config** | ★ |
| 10 | Recharts — custom tooltip · syncId · **ComposedChart** · Brush · **cross-filtering** | ★★ |
| 11 | Recharts — **loading/empty/error** · **Error Boundary** · small multiples · export | ★★ |
| 12 | Data transforms + **axis formatters universali** + **timezone pitfall** | ★★ |
| 13 | Server+Client pattern + Supabase + overplotting + **React Query** + export PDF | ★★ |
| 14 | 24 greșeli comune (8 Data Viz + 16 Tehnice) | ★ |
| 15 | Performanță: tiers · decimation · **ECharts în Next.js** · React profiling | ★★ |
| 16 | Accesibilitate reală — table fallback · SVG title/desc · WCAG · pattern fills | ★★ |
| 17 | Decision tree complet · comparison table · checklist pre-deploy · Quick Reference Card | ★ |

---

## BLOC 0 — Principii Fundamentale

### Secțiunea 0 — Chart Type Decision + Tufte + SVG vs Canvas vs WebGL

#### 0.1 Decizie chart type

```
ÎNTREABĂ: "Ce vrea utilizatorul să observe?"

Comparație categorii          → BAR (nu pie, niciodată)
Tendință în timp              → LINE / AREA
Compoziție ≤ 5 categorii      → PIE / DOUGHNUT (cu etichete explicite cu valori)
Distribuție valori            → HISTOGRAM / BOX PLOT / VIOLIN
Relație 2 variabile           → SCATTER PLOT
Flux / tranziții între stări  → SANKEY / ALLUVIAL
Ierarhie cu proporții         → TREEMAP
Date geografice               → CHOROPLETH / deck.gl
Progres față de target        → BULLET CHART (nu gauge — Tufte)
Trend rapid inline            → SPARKLINE (area 40px, fără axe, fără tooltip)
Comparație multi-metrici      → RADAR CHART (max 6 axe — altfel ilegibil)
```

**Principii Tufte adaptate pentru web:**
- **Data-ink ratio maxim**: fiecare pixel de cerneală reprezintă o dată. Griduri groase, umbre 3D, fundaluri colorate, gradiente decorative = chartjunk — elimină tot
- **Lie factor**: `(schimbare vizuală) / (schimbare dată)` trebuie să fie 1.0. Axa Y care nu pornește de la 0 pe bar chart = minciună vizuală deliberată
- **Small multiples**: 6 grafice mici identice, fiecare cu un subset de date > 1 grafic complex cu 6 serii suprapuse
- **Context obligatoriu**: `5.200 RON` fără comparație față de luna trecută sau față de target nu informează — derutează
- **Etichetele directe bat legenda**: când poți, pune eticheta direct pe linie/bară în loc de legendă separată

**Reguli hard:**
- Pie/Doughnut: maximum 5 categorii, cu etichete cu valori și procente
- Bar chart: Y pornește întotdeauna de la 0
- Dual Y axis: NUMAI pentru unități incomparabile (RON + %), cu notă explicită pe grafic
- 3D charts: NICIODATĂ — distorsionează percepția proporțiilor cu 40–60%

#### 0.2 SVG vs Canvas vs WebGL — decizia de arhitectură

Iei această decizie ÎNAINTE să alegi library-ul:

| Criteriu | SVG / Recharts | Canvas 2D | WebGL / ECharts |
|---|---|---|---|
| DOM nodes | 1 per element | 0 | 0 |
| Accesibilitate nativă | ✓ Screen reader natural | ✗ ARIA manual | ✗ |
| Scalare vectorială | ✓ Perfect la orice zoom | ✗ Pixelat la zoom | ✗ |
| Export SVG/PDF vectorial | ✓ Nativ | ✗ PNG only | ✗ |
| Performanță @ 1k | ✓ OK | ✓ Bine | ✓ |
| Performanță @ 10k | ✗ Lag vizibil | ✓ Bine | ✓ |
| Performanță @ 100k+ | ✗ Freeze | ✗ Lag | ✓ |
| Text rendering | ✓ Nativ, scalabil | ✗ Mediocru, pixelat | ✗ |
| CSS theming / dark mode | ✓ CSS variables | ✗ Manual în JS | ✗ Manual |
| Customizare completă | ✗ Limitată de API | ✓ Pixel perfect | Medie |
| Interactivitate built-in | ✓ CSS hover, focus | ✗ Manual (hit testing) | Rigidă |

```
Regula practică:

< 1.000 elemente, interactivitate bogată  → Recharts (SVG)
1.000 – 100.000 elemente                 → Chart.js sau Canvas pur
> 100.000 elemente                        → ECharts (WebGL renderer)
Date geografice @ scară                  → deck.gl
```

---

### Secțiunea 1 — Culori pentru Date

#### 1.1 ColorBrewer — palate validate perceptual

```javascript
// Calitativ — categorii distincte, fără ordine implicită
export const CB_QUALITATIVE_8 = [
  '#4e79a7', '#f28e2b', '#e15759', '#76b7b2',
  '#59a14f', '#edc948', '#b07aa1', '#ff9da7'
]

// Secvențial — de la mic la mare (intensitate, densitate, temperatură)
export const CB_BLUES_5  = ['#eff3ff', '#bdd7e7', '#6baed6', '#2171b5', '#084594']
export const CB_GREENS_5 = ['#f7fcf5', '#c7e9c0', '#74c476', '#238b45', '#00441b']

// Divergent — cu centru neutru (profit/pierdere, temperatură vs medie, NPS)
export const CB_RDYLGN_7 = ['#d73027', '#fc8d59', '#fee08b', '#ffffbf', '#d9ef8b', '#91cf60', '#1a9850']
export const CB_RDBU_7   = ['#b2182b', '#ef8a62', '#fddbc7', '#f7f7f7', '#d1e5f0', '#67a9cf', '#2166ac']
```

#### 1.2 Okabe-Ito — singura paletă daltonism-safe garantată

```javascript
// Okabe & Ito (2008) — testată pe toate tipurile de deficiențe de vedere
export const OKABE_ITO = {
  orange:    '#E69F00',
  skyBlue:   '#56B4E9',
  green:     '#009E73',
  yellow:    '#F0E442',
  blue:      '#0072B2',
  vermilion: '#D55E00',
  purple:    '#CC79A7',
  black:     '#000000'
}
export const OI_PALETTE = Object.values(OKABE_ITO)  // pentru .map() automat
```

#### 1.3 Contrast WCAG AA — formula completă

```javascript
// WCAG 2.1: contrast ratio minim 4.5:1 (text normal), 3:1 (text mare / UI)
// GREȘEALĂ COMUNĂ: formula simplificată cu prag 0.179 dă fals pozitiv
// (#808080 pe alb: L = 0.2159 > 0.179 → "OK", dar contrast real = 3.9:1, sub AA)

function relativeLuminance(hex) {
  const r = parseInt(hex.slice(1, 3), 16) / 255
  const g = parseInt(hex.slice(3, 5), 16) / 255
  const b = parseInt(hex.slice(5, 7), 16) / 255
  const lin = c => c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4)
  return 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b)
}

export function contrastRatio(hex1, hex2) {
  const L1 = relativeLuminance(hex1)
  const L2 = relativeLuminance(hex2)
  return (Math.max(L1, L2) + 0.05) / (Math.min(L1, L2) + 0.05)
}

// Returnează culoarea cu contrast REAL mai mare față de fundal
export function getTextColorForBg(hexBg) {
  return contrastRatio(hexBg, '#000000') >= contrastRatio(hexBg, '#ffffff')
    ? '#000000'
    : '#ffffff'
}
```

#### 1.4 Dark mode — paleta adaptată

```javascript
// globals.css — schimbare automată cu tema
// :root { --chart-bg: #ffffff; --chart-grid: #e2e8f0; --chart-text: #1e293b; }
// .dark  { --chart-bg: #0f172a; --chart-grid: #1e293b; --chart-text: #e2e8f0; }

// ColorBrewer pe dark mode — capătul întunecat devine start, deschisul = vârf
export const CB_BLUES_5_DARK = ['#084594', '#2171b5', '#6baed6', '#bdd7e7', '#eff3ff']
// Divergentele (RdYlGn, RdBu) funcționează pe ambele teme fără modificare

// Chart.js — dark mode global (aplici o singură dată la inițializare)
Chart.defaults.color       = 'var(--chart-text)'
Chart.defaults.borderColor = 'var(--chart-grid)'
```

#### 1.5 Testare daltonism — obligatoriu pre-deploy

```
Chrome DevTools → Rendering (tab jos) → Emulate vision deficiencies:
  - Deuteranopia  (cel mai frecvent: 6% bărbați — roșu/verde indistincte)
  - Protanopia    (roșu absent)
  - Tritanopia    (albastru/galben)

Dacă seriile tale sunt roșu + verde → ÎNLOCUIEȘTE cu:
  OKABE_ITO.vermilion (#D55E00) + OKABE_ITO.green (#009E73)

Tool online alternativ: color-blindness.com/coblis-color-blindness-simulator/
```

#### 1.6 Pattern fills — backup accesibil pentru culori

```javascript
// Canvas — hatching pentru print alb-negru sau daltonism sever
export function createHatchPattern(ctx, color, angle = 45) {
  const size = 8
  const pat = document.createElement('canvas')
  pat.width = pat.height = size
  const pc = pat.getContext('2d')
  pc.strokeStyle = color
  pc.lineWidth = 1.5
  pc.beginPath()
  if (angle === 45) {
    pc.moveTo(0, size);       pc.lineTo(size, 0)
    pc.moveTo(-size/2, size/2); pc.lineTo(size/2, -size/2)
    pc.moveTo(size/2, 3*size/2); pc.lineTo(3*size/2, size/2)
  } else {  // 135°
    pc.moveTo(0, 0); pc.lineTo(size, size)
  }
  pc.stroke()
  return ctx.createPattern(pat, 'repeat')
}

// Recharts — SVG <pattern> în <defs>:
// <defs>
//   <pattern id="hatch1" width="8" height="8" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
//     <line x1="0" y1="0" x2="0" y2="8" stroke="#4e79a7" strokeWidth="1.5"/>
//   </pattern>
// </defs>
// <Bar fill="url(#hatch1)" />
```

---

### Secțiunea 2 — D3 Utilities Standalone

#### 2.1 Instalare selectivă

```bash
# D3 complet = 150kB. Instalezi NUMAI modulele necesare:
npm install d3-scale d3-array d3-color d3-interpolate d3-scale-chromatic
```

#### 2.2 d3-scale — mapping domain → range

```javascript
import { scaleLinear, scaleBand, scaleTime, scaleLog, scaleOrdinal } from 'd3-scale'

// Y axis — valori numerice
const yScale = scaleLinear()
  .domain([0, maxValue])   // input: date reale
  .range([height, 0])      // output: pixeli (Y inversat pe canvas!)
  .nice()                  // rotunjește la valori "frumoase": 97 → 100

// X axis — categorii (bare)
const xScale = scaleBand()
  .domain(labels)          // ['Ian', 'Feb', 'Mar', ...]
  .range([0, width])
  .padding(0.2)            // 20% spațiu între bare

// X axis — timp
const timeScale = scaleTime()
  .domain([new Date('2026-01-01'), new Date('2026-06-30')])
  .range([0, width])

// Utilizare pe Canvas:
const barX = xScale('Ian')             // → pixel X de start
const barW = xScale.bandwidth()        // → lățimea barei
const barY = yScale(5200)              // → pixel Y pentru valoarea 5200
const barH = height - barY             // → înălțimea barei

// IMPORTANT: scale.invert() — pixel → valoare dată (pentru hover/brush)
const hoverValue = yScale.invert(mouseY)   // → valoarea numerică la poziția mouse
const hoverDate  = timeScale.invert(mouseX) // → Date la poziția mouse

// Ticks automat pentru axe:
yScale.ticks(5)      // → [0, 2000, 4000, 6000, 8000, 10000]
timeScale.ticks(6)   // → [Date(Ian), Date(Feb), ...]
```

#### 2.3 d3-array — transformări de date

```javascript
import { extent, group, rollup, sum, bin, ascending, descending } from 'd3-array'

// extent — min și max simultan (evită două Math.min/max separate)
const [minVal, maxVal] = extent(transactions, d => d.amount)

// group — grupare fără agregare
const byMonth = group(transactions, d => d.month)
// → Map { 'Ian' => [{...}, {...}], 'Feb' => [{...}], ... }

// rollup — grupare CU agregare (cel mai folosit)
const totalByCategory = rollup(
  transactions,
  v => sum(v, d => d.amount),
  d => d.category
)
// → Map { 'Mâncare' => 1200, 'Transport' => 450, ... }

// rollup cu 2 nivele de grupare
const byMonthAndCat = rollup(
  transactions,
  v => sum(v, d => d.amount),
  d => d.month,    // nivel 1
  d => d.category  // nivel 2
)
// → Map { 'Ian' => Map { 'Mâncare' => 450, 'Transport' => 120 }, ... }

// bin — pentru histogramă
const binner = bin().value(d => d.amount).thresholds(10)
const bins = binner(transactions)
// → [{ x0: 0, x1: 100, length: 5 }, ...]

data.sort((a, b) => descending(a.value, b.value))  // descrescător
data.sort((a, b) => ascending(a.date, b.date))      // crescător
```

#### 2.4 d3-scale-chromatic — palate dinamice

```javascript
import { interpolateBlues, interpolateRdYlGn, schemeTableau10 } from 'd3-scale-chromatic'
import { quantize } from 'd3-interpolate'
import { scaleSequential } from 'd3-scale'

// Generare N culori dintr-un interpolator
function makeSequentialPalette(n, interpolator = interpolateBlues) {
  return quantize(t => interpolator(t * 0.8 + 0.1), n)  // 0.1–0.9 evită extremele
}
const blues5 = makeSequentialPalette(5, interpolateBlues)
// → ['#c6dbef', '#9ecae1', '#6baed6', '#3182bd', '#08519c']

// Scale cu culori — pentru heatmap
const colorScale = scaleSequential(interpolateRdYlGn).domain([minVal, maxVal])
const color = colorScale(value)  // → hex string

// Paletă calitativă Tableau (10 culori)
const colors = schemeTableau10
```

---

## BLOC 1 — Chart.js

### Secțiunea 3 — Setup + Register + react-chartjs-2 + Theme Switching

#### 3.1 Instalare

```bash
npm install chart.js react-chartjs-2 chartjs-adapter-date-fns
# chartjs-adapter-date-fns — necesar pentru TimeScale cu Date objects
```

#### 3.2 Register — înregistrezi NUMAI ce folosești

```typescript
// lib/chart-setup.ts — importat o singură dată în layout sau _app
import {
  Chart,
  CategoryScale, LinearScale, TimeScale, LogarithmicScale,
  BarElement, LineElement, PointElement, ArcElement,
  Title, Tooltip, Legend, Filler
} from 'chart.js'
import 'chartjs-adapter-date-fns'

Chart.register(
  CategoryScale, LinearScale, TimeScale, LogarithmicScale,
  BarElement, LineElement, PointElement, ArcElement,
  Title, Tooltip, Legend, Filler
)
```

#### 3.3 react-chartjs-2 — pattern complet cu useRef

```tsx
'use client'
import { useRef } from 'react'
import { Bar } from 'react-chartjs-2'
import type { ChartData, ChartOptions } from 'chart.js'
import '@/lib/chart-setup'

interface Props {
  data: { month: string; income: number; expenses: number }[]
}

export function IncomeExpenseChart({ data }: Props) {
  const chartRef = useRef<import('chart.js').Chart<'bar'> | null>(null)

  const chartData: ChartData<'bar'> = {
    labels: data.map(d => d.month),
    datasets: [
      { label: 'Venituri',   data: data.map(d => d.income),   backgroundColor: OKABE_ITO.skyBlue },
      { label: 'Cheltuieli', data: data.map(d => d.expenses), backgroundColor: OKABE_ITO.vermilion }
    ]
  }

  const options: ChartOptions<'bar'> = {
    responsive: true,
    maintainAspectRatio: true,
    aspectRatio: 2,
    plugins: {
      legend: { position: 'top' },
      tooltip: { mode: 'index', intersect: false }
    },
    scales: { y: { beginAtZero: true } }
  }

  return <Bar ref={chartRef} data={chartData} options={options} />
}
```

#### 3.4 Theme switching la runtime — fără destroy/recreate

```typescript
// Când utilizatorul comută dark/light mode, actualizezi defaults și refreshezi
export function applyChartTheme(isDark: boolean) {
  const text = isDark ? '#e2e8f0' : '#1e293b'
  const grid = isDark ? '#1e293b' : '#e2e8f0'

  Chart.defaults.color       = text
  Chart.defaults.borderColor = grid

  // Actualizează toate graficele active
  Chart.instances && Object.values(Chart.instances).forEach(chart => {
    // Actualizare scale
    Object.values(chart.options.scales ?? {}).forEach((scale: any) => {
      if (scale.ticks) scale.ticks.color = text
      if (scale.grid)  scale.grid.color  = grid
    })
    chart.update('none')  // fără animație la schimbarea temei
  })
}

// Utilizare în useEffect (ascultă preferința de sistem):
useEffect(() => {
  const mq = window.matchMedia('(prefers-color-scheme: dark)')
  applyChartTheme(mq.matches)
  const handler = (e: MediaQueryListEvent) => applyChartTheme(e.matches)
  mq.addEventListener('change', handler)
  return () => mq.removeEventListener('change', handler)
}, [])
```

---

### Secțiunea 4 — Axis Formatters + Multi-axis + Gradient + Data Labels + External Tooltip

#### 4.1 Axis formatters — pentru producție

```typescript
const options: ChartOptions<'bar'> = {
  scales: {
    y: {
      beginAtZero: true,
      ticks: {
        // Numere compacte pe axă
        callback(value) {
          const n = Number(value)
          if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M RON`
          if (n >= 1_000)     return `${(n / 1_000).toFixed(0)}k RON`
          return `${n} RON`
        }
      }
    },
    x: {
      ticks: {
        callback(value, index) {
          const dateStr = this.getLabelForValue(index)
          return new Intl.DateTimeFormat('ro-RO', { month: 'short', year: '2-digit' }).format(new Date(dateStr))
        }
      }
    }
  },
  plugins: {
    tooltip: {
      callbacks: {
        label(ctx) {
          const n = ctx.parsed.y
          return `${ctx.dataset.label}: ${new Intl.NumberFormat('ro-RO', {
            style: 'currency', currency: 'RON', maximumFractionDigits: 0
          }).format(n)}`
        }
      }
    }
  }
}
```

#### 4.2 Multi-axis (Y stânga + Y dreapta)

```typescript
const options: ChartOptions = {
  scales: {
    yRevenue: {
      type: 'linear',
      position: 'left',
      title: { display: true, text: 'Venituri (RON)' },
      ticks: { callback: v => `${(Number(v)/1000).toFixed(0)}k` }
    },
    yMargin: {
      type: 'linear',
      position: 'right',
      min: 0, max: 100,
      title: { display: true, text: 'Marjă (%)' },
      grid: { drawOnChartArea: false },  // nu suprapune gridurile
      ticks: { callback: v => `${v}%` }
    }
  }
}

datasets: [
  { label: 'Venituri', data: [...], yAxisID: 'yRevenue' },
  { label: 'Marjă %',  data: [...], yAxisID: 'yMargin', type: 'line' }
]
```

#### 4.3 Gradient fill pe Area chart

```typescript
// Gradient-ul se creează în callback — nu la nivel de variabilă modulară
// (canvas dimensions nu sunt disponibile la import time)
const options: ChartOptions<'line'> = {
  plugins: {
    // Creare gradient în beforeLayout (o singură dată per resize)
  }
}

// Pattern corect — în useEffect după creare chart:
useEffect(() => {
  const chart = chartRef.current
  if (!chart) return
  const ctx = chart.ctx
  const gradient = ctx.createLinearGradient(0, 0, 0, chart.height)
  gradient.addColorStop(0,   'rgba(14, 165, 233, 0.4)')   // albastru opac sus
  gradient.addColorStop(0.7, 'rgba(14, 165, 233, 0.05)')  // transparent jos
  gradient.addColorStop(1,   'rgba(14, 165, 233, 0)')

  chart.data.datasets[0].backgroundColor = gradient
  chart.update('none')
}, [])  // creezi gradientul o singură dată după mount
```

#### 4.4 Data labels pe elemente

```bash
npm install chartjs-plugin-datalabels
```

```typescript
import ChartDataLabels from 'chartjs-plugin-datalabels'

// Înregistrare globală (sau per-chart):
Chart.register(ChartDataLabels)

const options: ChartOptions<'bar'> = {
  plugins: {
    datalabels: {
      anchor: 'end',
      align: 'top',
      formatter: (value) => value >= 1000 ? `${(value/1000).toFixed(0)}k` : value,
      font: { size: 11, weight: 'bold' },
      color: ctx => getTextColorForBg(
        ctx.dataset.backgroundColor as string ?? '#ffffff'
      )
    }
  }
}
```

#### 4.5 External tooltip — portal custom în afara canvas

```typescript
// Util când tooltip-ul trebuie să conțină date suplimentare sau markup complex
function createExternalTooltip(chart: Chart) {
  let tooltipEl = document.getElementById('chart-tooltip')
  if (!tooltipEl) {
    tooltipEl = document.createElement('div')
    tooltipEl.id = 'chart-tooltip'
    tooltipEl.className = 'absolute bg-white border border-slate-200 rounded-lg shadow-lg p-3 text-sm pointer-events-none z-50 transition-opacity'
    document.body.appendChild(tooltipEl)
  }
  return tooltipEl
}

const externalTooltipHandler = (context: { chart: Chart; tooltip: TooltipModel<'bar'> }) => {
  const { chart, tooltip } = context
  const el = createExternalTooltip(chart)

  if (tooltip.opacity === 0) {
    el.style.opacity = '0'
    return
  }

  // Populare conținut
  el.innerHTML = `
    <p class="font-semibold text-slate-700 mb-1">${tooltip.title[0]}</p>
    ${tooltip.dataPoints.map(dp => `
      <p style="color: ${dp.dataset.borderColor}">
        ${dp.dataset.label}: ${Number(dp.raw).toLocaleString('ro-RO')} RON
      </p>
    `).join('')}
  `

  // Poziționare cu clamp (nu overflow viewport)
  const { offsetLeft, offsetTop } = chart.canvas
  const rect = chart.canvas.getBoundingClientRect()
  let left = offsetLeft + tooltip.caretX + 10
  let top  = offsetTop  + tooltip.caretY - el.offsetHeight / 2

  // Clamp la marginile ferestrei
  left = Math.min(left, window.innerWidth  - el.offsetWidth  - 16)
  top  = Math.min(top,  window.innerHeight - el.offsetHeight - 16)
  left = Math.max(left, 8)
  top  = Math.max(top, 8)

  el.style.left    = `${left + window.scrollX}px`
  el.style.top     = `${top  + window.scrollY}px`
  el.style.opacity = '1'
  el.style.position = 'absolute'
}

const options: ChartOptions = {
  plugins: {
    tooltip: {
      enabled: false,  // dezactivezi tooltip-ul built-in
      external: externalTooltipHandler
    }
  }
}
```

#### 4.6 Click API corect — getElementsAtEventForMode

```typescript
useEffect(() => {
  const canvas = canvasRef.current
  if (!canvas) return

  function handleClick(e: MouseEvent) {
    const chart = chartRef.current
    if (!chart) return
    const elements = chart.getElementsAtEventForMode(
      e, 'nearest', { intersect: true }, false
    )
    if (!elements.length) return
    const { datasetIndex, index } = elements[0]
    const value = chart.data.datasets[datasetIndex].data[index]
    const label = chart.data.labels?.[index]
    onBarClick?.({ value, label, datasetIndex, index })
  }

  canvas.addEventListener('click', handleClick)
  return () => canvas.removeEventListener('click', handleClick)
}, [onBarClick])
```

#### 4.7 Custom Plugin — linie de threshold

```typescript
const thresholdPlugin: Plugin<'bar'> = {
  id: 'thresholdLine',
  afterDraw(chart) {
    const { ctx, scales: { y }, chartArea: { left, right } } = chart
    const yPos = y.getPixelForValue(5000)

    ctx.save()
    ctx.beginPath()
    ctx.moveTo(left, yPos)
    ctx.lineTo(right, yPos)
    ctx.strokeStyle = OKABE_ITO.vermilion
    ctx.lineWidth = 2
    ctx.setLineDash([6, 3])
    ctx.stroke()
    ctx.fillStyle = OKABE_ITO.vermilion
    ctx.font = '11px system-ui'
    ctx.textBaseline = 'bottom'
    ctx.fillText('Target: 5.000 RON', right - 130, yPos - 4)
    ctx.restore()
  }
}
Chart.register(thresholdPlugin)
```

---

### Secțiunea 5 — Data Transitions + Live Streaming + Decimation

#### 5.1 Data transitions — update corect, nu destroy

```typescript
// ✗ GREȘIT — distruge și recreează la fiecare update (flickering + pierde starea animației)
useEffect(() => {
  chartRef.current?.destroy()
  chartRef.current = new Chart(canvas, { data: newData, ... })
}, [data])

// ✓ CORECT — actualizezi în-place, Chart.js animează tranziția
useEffect(() => {
  const chart = chartRef.current
  if (!chart) return

  chart.data.labels                = newData.map(d => d.month)
  chart.data.datasets[0].data      = newData.map(d => d.income)
  chart.data.datasets[1].data      = newData.map(d => d.expenses)

  chart.update()          // cu animație implicită 300ms
  // chart.update('none') // fără animație — pentru refresh frecvent
}, [data])
```

#### 5.2 Live streaming — ring buffer pattern

```typescript
const MAX_POINTS = 60  // fereastră de 60 de puncte vizibile

export function useLiveChart(
  chartRef: RefObject<Chart | null>,
  fetchFn: () => number,
  intervalMs = 1000
) {
  useEffect(() => {
    const chart = chartRef.current
    if (!chart) return

    const id = setInterval(() => {
      const now   = new Date()
      const value = fetchFn()

      chart.data.labels!.push(now)
      chart.data.datasets[0].data.push(value)

      // Ring buffer — elimină cel mai vechi când depășim MAX_POINTS
      if (chart.data.labels!.length > MAX_POINTS) {
        chart.data.labels!.shift()
        chart.data.datasets[0].data.shift()
      }

      chart.update('none')  // fără animație pentru live data
    }, intervalMs)

    return () => clearInterval(id)
  }, [chartRef, fetchFn, intervalMs])
}
```

#### 5.3 Decimation LTTB — pentru datasets mari

```typescript
const options: ChartOptions<'line'> = {
  parsing: false,       // datele sunt deja { x, y } — skip parsing
  normalized: true,     // datele sunt sortate crescător după x
  animation: false,
  plugins: {
    decimation: {
      enabled: true,
      algorithm: 'lttb',  // Largest Triangle Three Buckets — cel mai bun vizual
      samples: 500,       // reduce la max 500 puncte vizibile
      threshold: 1000     // activează dacă > 1000 puncte
    }
  }
}
```

---

## BLOC 2 — Canvas API

### Secțiunea 6 — HiDPI + Text + beginPath Pitfall + ResizeObserver

#### 6.1 Setup HiDPI — obligatoriu

```typescript
export function setupCanvas(
  canvas: HTMLCanvasElement,
  width: number,
  height: number
): CanvasRenderingContext2D {
  const dpr = window.devicePixelRatio ?? 1
  canvas.width  = Math.floor(width  * dpr)
  canvas.height = Math.floor(height * dpr)
  canvas.style.width  = `${width}px`
  canvas.style.height = `${height}px`
  const ctx = canvas.getContext('2d')!
  ctx.scale(dpr, dpr)
  return ctx
}
```

#### 6.2 beginPath() — cel mai comun bug Canvas

```javascript
// ✗ GREȘIT — uitați de beginPath(), toate shape-urile se contopesc
ctx.fillStyle = 'blue'
ctx.rect(10, 10, 50, 50)
ctx.fill()

ctx.fillStyle = 'red'
ctx.rect(70, 10, 50, 50)
ctx.fill()  // Ambele dreptunghiuri devin roșii — path-ul anterior nu a fost resetat!

// ✓ CORECT — beginPath() înainte de fiecare shape nou
ctx.beginPath()
ctx.fillStyle = 'blue'
ctx.rect(10, 10, 50, 50)
ctx.fill()

ctx.beginPath()
ctx.fillStyle = 'red'
ctx.rect(70, 10, 50, 50)
ctx.fill()

// REGULĂ: clearRect la fiecare frame + beginPath la fiecare shape
function draw() {
  ctx.clearRect(0, 0, width, height)  // NU canvas.width = canvas.width (resetează transform!)
  bars.forEach(bar => {
    ctx.beginPath()  // OBLIGATORIU înainte de fiecare shape
    ctx.fillStyle = bar.color
    ctx.rect(bar.x, bar.y, bar.w, bar.h)
    ctx.fill()
  })
}
```

#### 6.3 Text rendering pe Canvas

```javascript
// 1. Setează font complet (size + family) — ÎNTOTDEAUNA
ctx.font = '12px system-ui, -apple-system, sans-serif'

// 2. textBaseline — afectează poziționarea verticală
ctx.textBaseline = 'middle'  // centrat față de y (cel mai predictibil)
ctx.textBaseline = 'top'     // y = top al textului
ctx.textBaseline = 'bottom'  // y = bottom al textului

// 3. Pixel alignment pentru text clar
const x = Math.round(barX + barW / 2)  // aliniere pe pixel întreg
const y = Math.round(barY - 8)

// 4. Truncare cu ellipsis pentru etichete lungi
function truncateText(ctx, text, maxWidth) {
  if (ctx.measureText(text).width <= maxWidth) return text
  let t = text
  while (ctx.measureText(t + '…').width > maxWidth && t.length > 0) {
    t = t.slice(0, -1)
  }
  return t + '…'
}

// 5. Etichete axă X rotite (pentru date lungi)
function drawRotatedLabel(ctx, text, x, y, angleDeg = -45) {
  ctx.save()
  ctx.translate(x, y)
  ctx.rotate(angleDeg * Math.PI / 180)
  ctx.textAlign    = 'right'
  ctx.textBaseline = 'middle'
  ctx.fillText(text, 0, 0)
  ctx.restore()
}

// 6. Linie de 1px clară — aliniere pe jumătate de pixel
const px = (v) => Math.round(v) + 0.5
ctx.moveTo(px(x1), px(y1))
ctx.lineTo(px(x2), px(y2))
```

#### 6.4 ResizeObserver responsive cu debounce și cleanup

```tsx
'use client'
import { useRef, useEffect, useCallback } from 'react'

export function useResizableCanvas(
  drawFn: (ctx: CanvasRenderingContext2D, w: number, h: number) => void
) {
  const canvasRef    = useRef<HTMLCanvasElement>(null)
  const containerRef = useRef<HTMLDivElement>(null)
  const rafRef       = useRef<number | null>(null)

  const redraw = useCallback(() => {
    const canvas    = canvasRef.current
    const container = containerRef.current
    if (!canvas || !container) return
    const { width, height } = container.getBoundingClientRect()
    const ctx = setupCanvas(canvas, width, height)
    drawFn(ctx, width, height)
  }, [drawFn])

  useEffect(() => {
    const observer = new ResizeObserver(() => {
      // Debounce cu rAF — maxim un redraw per frame
      if (rafRef.current) cancelAnimationFrame(rafRef.current)
      rafRef.current = requestAnimationFrame(redraw)
    })
    if (containerRef.current) observer.observe(containerRef.current)
    redraw()  // draw inițial

    return () => {
      observer.disconnect()
      if (rafRef.current) cancelAnimationFrame(rafRef.current)
    }
  }, [redraw])

  return { canvasRef, containerRef }
}
```

---

### Secțiunea 7 — Hit Testing + Touch Events + Zoom/Pan

#### 7.1 Hit testing universal — HiDPI-aware

```typescript
export function getCanvasPos(
  canvas: HTMLCanvasElement,
  e: MouseEvent | Touch
): { x: number; y: number } {
  const rect = canvas.getBoundingClientRect()
  const dpr  = window.devicePixelRatio ?? 1
  return {
    x: (e.clientX - rect.left) * (canvas.width / rect.width)  / dpr,
    y: (e.clientY - rect.top)  * (canvas.height / rect.height) / dpr
  }
}

// Hit test pe dreptunghi
export function hitRect(px: number, py: number, rx: number, ry: number, rw: number, rh: number) {
  return px >= rx && px <= rx + rw && py >= ry && py <= ry + rh
}

// Hit test pe cerc
export function hitCircle(px: number, py: number, cx: number, cy: number, r: number) {
  return Math.hypot(px - cx, py - cy) <= r
}
```

#### 7.2 Touch events — mobile-first

```typescript
function addInteractionListeners(
  canvas: HTMLCanvasElement,
  onHover: (pos: { x: number; y: number } | null) => void,
  onClick: (pos: { x: number; y: number }) => void
) {
  // Mouse
  canvas.addEventListener('mousemove', e => onHover(getCanvasPos(canvas, e)))
  canvas.addEventListener('mouseleave', () => onHover(null))
  canvas.addEventListener('click', e => onClick(getCanvasPos(canvas, e)))

  // Touch — IMPORTANT: passive: false necesar pentru preventDefault
  canvas.addEventListener('touchstart', e => {
    if (e.touches.length !== 1) return
    e.preventDefault()  // previne scroll accidental
    onClick(getCanvasPos(canvas, e.touches[0]))
  }, { passive: false })

  canvas.addEventListener('touchmove', e => {
    if (e.touches.length !== 1) return
    e.preventDefault()
    onHover(getCanvasPos(canvas, e.touches[0]))
  }, { passive: false })

  canvas.addEventListener('touchend', () => onHover(null))
}
```

#### 7.3 Zoom și pan — cu transform matrix

```typescript
interface ViewTransform { scale: number; offsetX: number; offsetY: number }

export function useCanvasZoomPan(
  canvasRef: RefObject<HTMLCanvasElement>,
  onTransformChange: (t: ViewTransform) => void
) {
  const transform   = useRef<ViewTransform>({ scale: 1, offsetX: 0, offsetY: 0 })
  const isDragging  = useRef(false)
  const lastPos     = useRef({ x: 0, y: 0 })

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return
    const handlers: [string, EventListenerOrEventListenerObject, AddEventListenerOptions?][] = []

    const add = (event: string, fn: EventListener, opts?: AddEventListenerOptions) => {
      canvas.addEventListener(event, fn, opts)
      handlers.push([event, fn, opts])
    }

    add('wheel', ((e: WheelEvent) => {
      e.preventDefault()
      const { x, y } = getCanvasPos(canvas, e as unknown as MouseEvent)
      const delta = e.deltaY < 0 ? 1.1 : 0.9
      const t = transform.current
      t.offsetX = x - delta * (x - t.offsetX)
      t.offsetY = y - delta * (y - t.offsetY)
      t.scale   = Math.max(0.5, Math.min(10, t.scale * delta))
      onTransformChange({ ...t })
    }) as EventListener, { passive: false })

    add('mousedown', ((e: MouseEvent) => {
      isDragging.current = true
      lastPos.current    = getCanvasPos(canvas, e)
    }) as EventListener)

    add('mousemove', ((e: MouseEvent) => {
      if (!isDragging.current) return
      const pos = getCanvasPos(canvas, e)
      transform.current.offsetX += pos.x - lastPos.current.x
      transform.current.offsetY += pos.y - lastPos.current.y
      lastPos.current = pos
      onTransformChange({ ...transform.current })
    }) as EventListener)

    add('mouseup', (() => { isDragging.current = false }) as EventListener)

    add('dblclick', (() => {
      transform.current = { scale: 1, offsetX: 0, offsetY: 0 }
      onTransformChange({ ...transform.current })
    }) as EventListener)

    return () => handlers.forEach(([e, fn, opts]) => canvas.removeEventListener(e, fn, opts))
  }, [canvasRef, onTransformChange])

  return transform
}

// Utilizare în draw():
// ctx.save()
// ctx.setTransform(t.scale, 0, 0, t.scale, t.offsetX, t.offsetY)
// drawChart(ctx)
// ctx.restore()
```

---

### Secțiunea 8 — Data Transitions pe Canvas + Spring Physics + OffscreenCanvas

#### 8.1 Spring physics — animație naturală

```typescript
interface AnimBar {
  current: number
  target:  number
  velocity: number
}

export class AnimatedBarChart {
  private bars:  AnimBar[] = []
  private rafId: number | null = null

  constructor(
    private ctx: CanvasRenderingContext2D,
    private width: number,
    private height: number
  ) {}

  updateData(values: number[]) {
    values.forEach((v, i) => {
      if (this.bars[i]) {
        this.bars[i].target = v
      } else {
        this.bars.push({ current: 0, target: v, velocity: 0 })  // enter: pornește de la 0
      }
    })
    // Exit: bare în plus → target = 0
    for (let i = values.length; i < this.bars.length; i++) {
      this.bars[i].target = 0
    }
    this.start()
  }

  private start() {
    if (this.rafId) cancelAnimationFrame(this.rafId)
    const animate = () => {
      let settled = true
      const SPRING  = 0.12   // rigiditate — mai mare = mai rapid
      const DAMPING = 0.85   // amortizare — mai mic = mai mult bounce

      this.bars.forEach(bar => {
        const force   = (bar.target - bar.current) * SPRING
        bar.velocity  = (bar.velocity + force) * DAMPING
        bar.current  += bar.velocity
        if (Math.abs(bar.velocity) > 0.1 || Math.abs(bar.target - bar.current) > 0.1) {
          settled = false
        }
      })

      this.draw()
      if (!settled) this.rafId = requestAnimationFrame(animate)
      else          this.rafId = null
    }
    this.rafId = requestAnimationFrame(animate)
  }

  private draw() {
    const { ctx, width, height, bars } = this
    ctx.clearRect(0, 0, width, height)
    const maxVal   = Math.max(...bars.map(b => b.target), 1)
    const barWidth = (width / bars.length) * 0.7
    const gap      = (width / bars.length) * 0.3

    bars.forEach((bar, i) => {
      const barH = (bar.current / maxVal) * (height - 40)
      const x    = i * (barWidth + gap) + gap / 2
      const y    = height - barH - 20

      ctx.beginPath()
      ctx.fillStyle = OI_PALETTE[i % OI_PALETTE.length]
      ctx.roundRect(x, y, barWidth, barH, [4, 4, 0, 0])
      ctx.fill()
    })
  }

  destroy() {
    if (this.rafId) cancelAnimationFrame(this.rafId)
  }
}
```

#### 8.2 Easing functions pentru animații UI

```typescript
export const easing = {
  linear:    (t: number) => t,
  easeOut:   (t: number) => 1 - Math.pow(1 - t, 3),
  easeIn:    (t: number) => t * t * t,
  easeInOut: (t: number) => t < 0.5 ? 4*t*t*t : 1 - Math.pow(-2*t + 2, 3) / 2,
}

export function animateValue(
  from: number, to: number, duration: number,
  easingFn: (t: number) => number,
  onUpdate: (v: number) => void,
  onComplete?: () => void
) {
  const start = performance.now()
  const frame = (now: number) => {
    const t = Math.min((now - start) / duration, 1)
    onUpdate(from + (to - from) * easingFn(t))
    if (t < 1) requestAnimationFrame(frame)
    else onComplete?.()
  }
  requestAnimationFrame(frame)
}
```

#### 8.3 OffscreenCanvas — rendering pe worker thread

```javascript
// main.ts
const offscreen = canvas.transferControlToOffscreen()
const worker    = new Worker(new URL('./chart-worker.ts', import.meta.url))
worker.postMessage({ type: 'init', canvas: offscreen }, [offscreen])

worker.postMessage({ type: 'update', data: newData })

// chart-worker.ts
let ctx: OffscreenCanvasRenderingContext2D
self.onmessage = (e) => {
  if (e.data.type === 'init') {
    ctx = e.data.canvas.getContext('2d')!
    renderInitial(ctx)
  }
  if (e.data.type === 'update') {
    renderUpdate(ctx, e.data.data)  // nu blochează main thread
  }
}
```

---

## BLOC 3 — Recharts

### Secțiunea 9 — Setup + Hydration + Dynamic Import + Responsive Config

#### 9.1 De ce apare hydration mismatch — explicație completă

```
PROBLEMA:
Recharts apelează window.innerWidth și alte Browser API-uri în timpul render.
Pe server (Next.js SSR), window nu există → valori diferite sau eroare.
React compară HTML server vs client → HYDRATION MISMATCH.

SIMPTOM: "Warning: Prop `width` did not match. Server: '0'. Client: '1200'"
         Sau: "window is not defined" în build

SOLUȚIE 1 — dynamic import cu ssr: false (recomandată)
```

```tsx
// components/charts/index.ts — re-export cu lazy loading
import dynamic from 'next/dynamic'

export const RevenueChart = dynamic(
  () => import('./RevenueChart'),
  { ssr: false, loading: () => <ChartSkeleton height={300} /> }
)
// Poți importa RevenueChart în Server Components fără 'use client'

// SOLUȚIE 2 — mounted flag (când ai nevoie de control fin)
'use client'
const [mounted, setMounted] = useState(false)
useEffect(() => setMounted(true), [])
if (!mounted) return <ChartSkeleton height={300} />
return <RevenueChart data={data} />
```

#### 9.2 ResponsiveContainer — regula înălțimii

```tsx
// ✗ GREȘIT — ResponsiveContainer nu știe înălțimea, grafic = 0px
<div>
  <ResponsiveContainer width="100%">
    <BarChart>...</BarChart>
  </ResponsiveContainer>
</div>

// ✓ CORECT — înălțime explicită pe container sau pe ResponsiveContainer
<div style={{ height: 300 }}>
  <ResponsiveContainer width="100%" height="100%">
    <BarChart>...</BarChart>
  </ResponsiveContainer>
</div>
```

#### 9.3 Responsive config — mobil vs desktop

```tsx
'use client'
import { useEffect, useState } from 'react'

function useBreakpoint() {
  const [mobile, setMobile] = useState(false)
  useEffect(() => {
    const mq      = window.matchMedia('(max-width: 640px)')
    setMobile(mq.matches)
    const handler = (e: MediaQueryListEvent) => setMobile(e.matches)
    mq.addEventListener('change', handler)
    return () => mq.removeEventListener('change', handler)
  }, [])
  return mobile
}

export function AdaptiveChart({ data }) {
  const isMobile = useBreakpoint()

  return (
    <ResponsiveContainer width="100%" height={isMobile ? 200 : 350}>
      <BarChart
        data={data}
        margin={isMobile ? { top: 4, right: 4, bottom: 20, left: 0 } : { top: 8, right: 24, bottom: 40, left: 16 }}
      >
        <XAxis
          dataKey="month"
          tick={{ fontSize: isMobile ? 10 : 12 }}
          tickFormatter={isMobile ? m => m.slice(0, 3) : m => m}  // 'Ianuarie' → 'Ian'
          interval={isMobile ? 1 : 0}  // pe mobile: afișează fiecare al doilea tick
        />
        <YAxis
          width={isMobile ? 36 : 60}
          tickFormatter={isMobile ? v => `${(v/1000).toFixed(0)}k` : v => `${v} RON`}
        />
        <Tooltip
          // Pe mobile: tooltip simplificat fără dataset label
          formatter={(v: number) => isMobile ? v.toLocaleString('ro-RO') : `${v.toLocaleString('ro-RO')} RON`}
        />
        <Bar dataKey="value" fill={OKABE_ITO.skyBlue} />
      </BarChart>
    </ResponsiveContainer>
  )
}
```

---

### Secțiunea 10 — Custom Tooltip + syncId + ComposedChart + Brush + Cross-filtering

#### 10.1 Custom Tooltip — referință stabilă cu useCallback

```tsx
'use client'
import { useCallback } from 'react'
import type { TooltipProps } from 'recharts'

// useCallback cu [] — referință stabilă, previne re-render complet Recharts la orice keystroke
export function useRONTooltip() {
  const fmt = new Intl.NumberFormat('ro-RO', { style: 'currency', currency: 'RON', maximumFractionDigits: 0 })

  return useCallback(({ active, payload, label }: TooltipProps<number, string>) => {
    if (!active || !payload?.length) return null
    return (
      <div className="bg-white border border-slate-200 rounded-lg shadow-lg p-3 text-sm">
        <p className="font-semibold text-slate-700 mb-2">{label}</p>
        {payload.map((entry, i) => (
          <p key={i} style={{ color: entry.color }}>
            {entry.name}: {fmt.format(entry.value ?? 0)}
          </p>
        ))}
      </div>
    )
  }, [fmt])
}

// Utilizare — formatter stabil:
export function RevenueChart({ data }) {
  const TooltipContent = useRONTooltip()
  const fmtK = useCallback((v: number) => v >= 1000 ? `${(v/1000).toFixed(0)}k` : String(v), [])

  return (
    <BarChart data={data}>
      <YAxis tickFormatter={fmtK} />
      <Tooltip content={TooltipContent} />
      <Bar dataKey="value" fill={OKABE_ITO.skyBlue} />
    </BarChart>
  )
}
```

#### 10.2 syncId — tooltipuri sincronizate multi-chart

```tsx
const SYNC = 'monthly-dashboard'

<div className="grid grid-cols-2 gap-4">
  <ResponsiveContainer height={200}>
    <AreaChart data={incomeData} syncId={SYNC}>
      <Area dataKey="income" stroke={OKABE_ITO.skyBlue} fill={OKABE_ITO.skyBlue} fillOpacity={0.15} />
      <XAxis dataKey="month" /><YAxis /><Tooltip />
    </AreaChart>
  </ResponsiveContainer>

  <ResponsiveContainer height={200}>
    <BarChart data={expenseData} syncId={SYNC}>
      <Bar dataKey="expenses" fill={OKABE_ITO.vermilion} />
      <XAxis dataKey="month" /><YAxis /><Tooltip />
    </BarChart>
  </ResponsiveContainer>
</div>
```

#### 10.3 ComposedChart — Bar + Line + Area în același grafic

```tsx
// Foarte comun în dashboarduri financiare: bare pentru venituri/cheltuieli, linie pentru trend
import { ComposedChart, Bar, Line, Area, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts'

export function FinancialComposedChart({ data }) {
  const fmtRON = useCallback(
    (v: number) => new Intl.NumberFormat('ro-RO', { maximumFractionDigits: 0 }).format(v) + ' RON',
    []
  )

  return (
    <ResponsiveContainer width="100%" height={350}>
      <ComposedChart data={data} margin={{ top: 8, right: 24, bottom: 8, left: 16 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
        <XAxis dataKey="month" />
        <YAxis yAxisId="left"  orientation="left"  tickFormatter={v => `${(v/1000).toFixed(0)}k`} />
        <YAxis yAxisId="right" orientation="right" tickFormatter={v => `${v}%`} />
        <Tooltip formatter={fmtRON} />
        <Legend />

        {/* Bare — venituri și cheltuieli pe axa stângă */}
        <Bar     yAxisId="left"  dataKey="income"   name="Venituri"   fill={OKABE_ITO.skyBlue}   radius={[3,3,0,0]} />
        <Bar     yAxisId="left"  dataKey="expenses" name="Cheltuieli" fill={OKABE_ITO.vermilion}  radius={[3,3,0,0]} />

        {/* Linie — marjă pe axa dreaptă */}
        <Line    yAxisId="right" dataKey="margin"   name="Marjă %"    stroke={OKABE_ITO.orange}   strokeWidth={2} dot={false} />

        {/* Area opțional — pentru profit cumulat */}
        <Area    yAxisId="left"  dataKey="cumProfit" name="Profit cumulat" fill={OKABE_ITO.green}
                 stroke={OKABE_ITO.green} fillOpacity={0.1} strokeWidth={1.5} />
      </ComposedChart>
    </ResponsiveContainer>
  )
}
```

#### 10.4 Brush — selecție interval temporal

```tsx
<AreaChart data={data}>
  <Area dataKey="value" />
  <XAxis dataKey="date" />
  <YAxis />
  <Tooltip />
  <Brush
    dataKey="date"
    height={30}
    stroke="#94a3b8"
    startIndex={data.length - 30}  // ultimele 30 selectate implicit
    onChange={({ startIndex, endIndex }) => {
      onRangeChange?.(data.slice(startIndex, (endIndex ?? data.length - 1) + 1))
    }}
  />
</AreaChart>
```

#### 10.5 Cross-filtering — pattern complet

```tsx
'use client'
import { useState, useMemo } from 'react'

export function CrossFilterDashboard({ transactions }) {
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null)
  const [selectedMonth,    setSelectedMonth]    = useState<string | null>(null)

  const filtered = useMemo(() => transactions.filter(t => {
    if (selectedCategory && t.category !== selectedCategory) return false
    if (selectedMonth    && t.month    !== selectedMonth)    return false
    return true
  }), [transactions, selectedCategory, selectedMonth])

  const byCategory = useMemo(() =>
    Array.from(rollup(filtered, v => sum(v, d => d.amount), d => d.category),
      ([category, total]) => ({ category, total })
    ).sort((a, b) => b.total - a.total),
    [filtered]
  )

  const byMonth = useMemo(() =>
    Array.from(rollup(filtered, v => sum(v, d => d.amount), d => d.month),
      ([month, total]) => ({ month, total })
    ),
    [filtered]
  )

  const toggle = (setter: (v: string | null) => void, current: string | null, val: string) =>
    setter(current === val ? null : val)

  return (
    <div>
      <div className="flex gap-2 text-sm text-slate-500 mb-4">
        {filtered.length} tranzacții
        {selectedCategory && ` · ${selectedCategory}`}
        {selectedMonth    && ` · ${selectedMonth}`}
        {(selectedCategory || selectedMonth) && (
          <button onClick={() => { setSelectedCategory(null); setSelectedMonth(null) }}
            className="text-blue-600 hover:underline ml-2">
            Resetează
          </button>
        )}
      </div>

      <ResponsiveContainer width="100%" height={200}>
        <BarChart data={byCategory}>
          <Bar dataKey="total" onClick={d => toggle(setSelectedCategory, selectedCategory, d.category)} cursor="pointer">
            {byCategory.map(d => (
              <Cell key={d.category}
                fill={!selectedCategory || selectedCategory === d.category ? OKABE_ITO.skyBlue : '#e2e8f0'}
                opacity={selectedCategory && selectedCategory !== d.category ? 0.4 : 1} />
            ))}
          </Bar>
          <XAxis dataKey="category" /><YAxis /><Tooltip />
        </BarChart>
      </ResponsiveContainer>

      <ResponsiveContainer width="100%" height={200}>
        <BarChart data={byMonth}>
          <Bar dataKey="total" onClick={d => toggle(setSelectedMonth, selectedMonth, d.month)} cursor="pointer">
            {byMonth.map(d => (
              <Cell key={d.month}
                fill={!selectedMonth || selectedMonth === d.month ? OKABE_ITO.green : '#e2e8f0'}
                opacity={selectedMonth && selectedMonth !== d.month ? 0.4 : 1} />
            ))}
          </Bar>
          <XAxis dataKey="month" /><YAxis /><Tooltip />
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}
```

---

### Secțiunea 11 — Loading/Empty/Error + Error Boundary + Small Multiples + Export

#### 11.1 Loading, empty și error states — ChartShell pattern

```tsx
// components/ChartShell.tsx
interface ChartShellProps {
  isLoading?: boolean
  error?: Error | null
  isEmpty?: boolean
  emptyMessage?: string
  height?: number
  children: React.ReactNode
}

export function ChartShell({ isLoading, error, isEmpty, emptyMessage = 'Nicio dată disponibilă', height = 300, children }: ChartShellProps) {
  if (isLoading) return <ChartSkeleton height={height} />
  if (error)     return <ChartError   message={error.message} height={height} />
  if (isEmpty)   return <ChartEmpty   message={emptyMessage}  height={height} />
  return <>{children}</>
}

function ChartSkeleton({ height }: { height: number }) {
  return (
    <div style={{ height }} className="animate-pulse flex items-end gap-2 p-4 bg-slate-50 rounded-lg">
      {[60, 40, 80, 50, 70, 45, 90, 55].map((h, i) => (
        <div key={i} className="bg-slate-200 rounded flex-1" style={{ height: `${h}%` }} />
      ))}
    </div>
  )
}

function ChartEmpty({ message, height }: { height: number; message: string }) {
  return (
    <div style={{ height }}
      className="flex flex-col items-center justify-center gap-2 text-slate-400 border-2 border-dashed border-slate-200 rounded-lg">
      <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
        <path d="M3 3v18h18M7 16l4-4 4 4 4-4" />
      </svg>
      <p className="text-sm">{message}</p>
    </div>
  )
}

function ChartError({ message, height }: { height: number; message: string }) {
  return (
    <div style={{ height }} className="flex flex-col items-center justify-center gap-2 text-red-400 bg-red-50 rounded-lg">
      <p className="text-sm font-medium">Eroare la încărcarea datelor</p>
      <p className="text-xs text-slate-400 max-w-xs text-center">{message}</p>
    </div>
  )
}
```

#### 11.2 Chart Error Boundary — un grafic spart nu crapă pagina

```tsx
'use client'
import { Component, type ReactNode } from 'react'

interface Props { children: ReactNode; height?: number; name?: string }
interface State { hasError: boolean; error: Error | null }

export class ChartErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props)
    this.state = { hasError: false, error: null }
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error }
  }

  componentDidCatch(error: Error, info: React.ErrorInfo) {
    console.error(`Chart "${this.props.name}" crashed:`, error, info)
    // Trimite la Sentry/monitoring: Sentry.captureException(error)
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{ height: this.props.height ?? 300 }}
          className="flex items-center justify-center bg-slate-50 rounded-lg border border-slate-200">
          <p className="text-sm text-slate-400">
            Graficul "{this.props.name ?? 'necunoscut'}" nu s-a putut afișa
          </p>
        </div>
      )
    }
    return this.props.children
  }
}

// Utilizare — învelești orice chart sensibil:
<ChartErrorBoundary name="Revenue Chart" height={300}>
  <RevenueChart data={data} />
</ChartErrorBoundary>
```

#### 11.3 Small multiples — aceeași scală Y pe toate

```tsx
export function SmallMultiplesGrid({ categories }: { categories: { name: string; data: { month: string; value: number }[] }[] }) {
  // CRITIC: scală Y uniformă pe TOATE graficele — altfel comparația e falsă
  const maxValue = useMemo(
    () => Math.max(...categories.flatMap(c => c.data.map(d => d.value))),
    [categories]
  )

  return (
    <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
      {categories.map(({ name, data }) => (
        <div key={name} className="bg-white rounded-lg p-3 border">
          <h4 className="text-xs font-semibold text-slate-600 mb-1">{name}</h4>
          <ResponsiveContainer width="100%" height={80}>
            <AreaChart data={data} margin={{ top: 2, right: 2, bottom: 0, left: 0 }}>
              <YAxis domain={[0, maxValue]} hide />
              <Tooltip formatter={(v: number) => [`${v} RON`, name]} />
              <Area type="monotone" dataKey="value"
                stroke={OKABE_ITO.skyBlue} fill={OKABE_ITO.skyBlue} fillOpacity={0.15}
                strokeWidth={1.5} dot={false} isAnimationActive={false} />
            </AreaChart>
          </ResponsiveContainer>
          <p className="text-xs text-slate-500 text-right mt-1">
            {data.at(-1)?.value.toLocaleString('ro-RO')} RON
          </p>
        </div>
      ))}
    </div>
  )
}
```

#### 11.4 Export PNG, SVG, PDF

```tsx
'use client'
import { useRef, useCallback } from 'react'

export function useChartExport(filename = 'chart') {
  const containerRef = useRef<HTMLDivElement>(null)

  // PNG dintr-un canvas nativ
  const exportCanvasPNG = useCallback((canvas: HTMLCanvasElement) => {
    const a = document.createElement('a')
    a.download = `${filename}.png`
    a.href     = canvas.toDataURL('image/png', 1.0)
    a.click()
  }, [filename])

  // PNG dintr-un Recharts SVG (via html2canvas)
  const exportPNG = useCallback(async () => {
    const el = containerRef.current
    if (!el) return
    const { default: html2canvas } = await import('html2canvas')
    const canvas = await html2canvas(el, { backgroundColor: '#ffffff', scale: 2, logging: false })
    const a = document.createElement('a')
    a.download = `${filename}.png`
    a.href     = canvas.toDataURL('image/png', 1.0)
    a.click()
  }, [filename])

  // SVG vectorial (Recharts) — calitate perfectă pentru print
  const exportSVG = useCallback(() => {
    const svg = containerRef.current?.querySelector('svg')
    if (!svg) return
    const data = new XMLSerializer().serializeToString(svg)
    const blob = new Blob([data], { type: 'image/svg+xml' })
    const url  = URL.createObjectURL(blob)
    const a    = document.createElement('a')
    a.download = `${filename}.svg`
    a.href     = url
    a.click()
    URL.revokeObjectURL(url)
  }, [filename])

  // PDF cu jsPDF — testat pe Safari
  const exportPDF = useCallback(async () => {
    const el = containerRef.current
    if (!el) return
    const [{ default: html2canvas }, { default: jsPDF }] = await Promise.all([
      import('html2canvas'),
      import('jspdf')
    ])
    const canvas  = await html2canvas(el, { backgroundColor: '#ffffff', scale: 2, logging: false })
    const imgData = canvas.toDataURL('image/png', 1.0)
    const pdf     = new jsPDF({
      orientation: canvas.width > canvas.height ? 'landscape' : 'portrait',
      unit: 'px',
      format: [canvas.width / 2, canvas.height / 2]
    })
    pdf.addImage(imgData, 'PNG', 0, 0, canvas.width / 2, canvas.height / 2)
    pdf.save(`${filename}.pdf`)
  }, [filename])

  return { containerRef, exportCanvasPNG, exportPNG, exportSVG, exportPDF }
}
```

---

## BLOC 4 — Date & Performance

### Secțiunea 12 — Data Transforms + Axis Formatters Universali + Timezone Pitfall

#### 12.1 Timezone pitfall — bug critic în dashboarduri financiare

```typescript
// PROBLEMA: new Date('2026-01-15') parsează ca UTC midnight
// → în timezone-uri UTC-x (ex: UTC-5), devine 2026-01-14 la ora 19:00
// → pe axă apare "14 Ian" în loc de "15 Ian" — bug subtil, greu de repro

// ✗ GREȘIT:
const d = new Date('2026-01-15')  // UTC midnight → wrong day în UTC-x

// ✓ CORECT — explicit local time:
const d = new Date('2026-01-15T00:00:00')  // fără Z → interpretare locală

// ✓ CORECT — cu date-fns (recomandat):
import { parseISO, startOfDay } from 'date-fns'
const d = parseISO('2026-01-15')  // safe în toate timezone-urile

// ✓ CORECT — pentru grouping pe zi (ignoră ora):
const dateKey = (isoString: string) => isoString.slice(0, 10)  // '2026-01-15'
// Evită new Date() în totul în transformări de date — lucrează cu string-uri ISO

// Regula practică:
// - Stochezi în Supabase ca timestamptz
// - Transmiți server→client ca string ISO: t.created_at (string, nu Date)
// - Grupezi pe zi cu: t.created_at.slice(0, 10)
// - Convertești la Date NUMAI în momentul afișării pe axă
```

#### 12.2 Axis formatters — biblioteca completă

```typescript
// lib/formatters.ts — importat în orice proiect

export const fmtCompact = (v: number, unit = '') => {
  if (Math.abs(v) >= 1_000_000) return `${(v / 1_000_000).toFixed(1)}M${unit}`
  if (Math.abs(v) >= 1_000)     return `${(v / 1_000).toFixed(0)}k${unit}`
  return `${v}${unit}`
}

export const fmtRON = (v: number) =>
  new Intl.NumberFormat('ro-RO', { style: 'currency', currency: 'RON', maximumFractionDigits: 0 }).format(v)

export const fmtEUR = (v: number) =>
  new Intl.NumberFormat('ro-RO', { style: 'currency', currency: 'EUR', maximumFractionDigits: 2 }).format(v)

export const fmtPct = (v: number) =>
  new Intl.NumberFormat('ro-RO', { style: 'percent', maximumFractionDigits: 1 }).format(v)  // 0.156 → "15.6%"

export const fmtDelta = (v: number, unit = 'RON') =>
  `${v > 0 ? '+' : ''}${v.toLocaleString('ro-RO')} ${unit}`

export const fmtMonthShort = (iso: string) =>
  new Intl.DateTimeFormat('ro-RO', { month: 'short' }).format(new Date(iso + 'T00:00:00'))

export const fmtMonthYear = (iso: string) =>
  new Intl.DateTimeFormat('ro-RO', { month: 'short', year: '2-digit' }).format(new Date(iso + 'T00:00:00'))

export const fmtDay = (iso: string) =>
  new Intl.DateTimeFormat('ro-RO', { day: 'numeric', month: 'short' }).format(new Date(iso + 'T00:00:00'))

// Utilizare:
// <YAxis tickFormatter={v => fmtCompact(v, ' RON')} />
// <Tooltip formatter={(v: number) => [fmtRON(v), 'Venituri']} />
// <XAxis dataKey="date" tickFormatter={fmtMonthShort} />
```

#### 12.3 Data transforms — pattern complet

```typescript
// lib/data-transforms.ts
import { group, rollup, sum, extent } from 'd3-array'

export interface Transaction {
  id: string; date: string; amount: number; category: string
}

// Venituri/cheltuieli per lună
export function groupByMonth(txns: Transaction[]) {
  const order = ['Ian','Feb','Mar','Apr','Mai','Iun','Iul','Aug','Sep','Oct','Nov','Dec']
  const byMonth = rollup(
    txns,
    v => ({
      income:   sum(v.filter(t => t.amount > 0), t => t.amount),
      expenses: sum(v.filter(t => t.amount < 0), t => Math.abs(t.amount)),
      net:      sum(v, t => t.amount)
    }),
    t => new Intl.DateTimeFormat('ro-RO', { month: 'short' }).format(new Date(t.date + 'T00:00:00'))
  )
  return order.filter(m => byMonth.has(m)).map(month => ({ month, ...byMonth.get(month)! }))
}

// Cheltuieli per categorie
export function groupByCategory(txns: Transaction[]) {
  return Array.from(
    rollup(txns, v => sum(v, t => Math.abs(t.amount)), t => t.category),
    ([category, total]) => ({ category, total })
  ).sort((a, b) => b.total - a.total)
}

// Trend ultimele 30 de zile — pentru sparkline sau area
export function last30Days(txns: Transaction[]) {
  const today = new Date()
  const days = Array.from({ length: 30 }, (_, i) => {
    const d = new Date(today)
    d.setDate(d.getDate() - (29 - i))
    return d.toISOString().slice(0, 10)
  })
  const byDay = rollup(txns, v => sum(v, t => t.amount), t => t.date.slice(0, 10))
  return days.map(date => ({
    date,
    label: fmtDay(date),
    value: byDay.get(date) ?? 0
  }))
}
```

---

### Secțiunea 13 — Server+Client Pattern + Supabase + Overplotting + React Query + Export PDF

#### 13.1 Pattern corect Next.js — fetch pe server, chart pe client

```tsx
// app/(dashboard)/analytics/page.tsx — Server Component
import 'server-only'
import { createServerClient } from '@/lib/supabase/server'
import { groupByMonth, groupByCategory } from '@/lib/data-transforms'
import { AnalyticsDashboard } from './AnalyticsDashboard'

export default async function AnalyticsPage() {
  const supabase = createServerClient()
  const { data: { user }, error: authError } = await supabase.auth.getUser()
  if (authError || !user) redirect('/login')

  const { data: txns, error } = await supabase
    .from('transactions').select('*')
    .eq('user_id', user.id)
    .gte('date', `${new Date().getFullYear()}-01-01`)
  if (error) throw error

  // Transformări pe server — clientul primește date pre-agregate, nu raw
  return (
    <AnalyticsDashboard
      monthlyData={groupByMonth(txns ?? [])}
      categoryData={groupByCategory(txns ?? [])}
    />
  )
}
```

```tsx
// AnalyticsDashboard.tsx — Client Component
'use client'
export function AnalyticsDashboard({ monthlyData, categoryData }) {
  return (
    <div className="grid grid-cols-2 gap-6">
      <ChartErrorBoundary name="Revenue">
        <ChartShell isEmpty={!monthlyData.length}>
          <RevenueChart data={monthlyData} />
        </ChartShell>
      </ChartErrorBoundary>
      <ChartErrorBoundary name="Categories">
        <ChartShell isEmpty={!categoryData.length}>
          <CategoryChart data={categoryData} />
        </ChartShell>
      </ChartErrorBoundary>
    </div>
  )
}
```

#### 13.2 React Query / SWR — integrare cu charts

```tsx
// React Query — pattern pentru charts cu refresh automat
'use client'
import { useQuery } from '@tanstack/react-query'

async function fetchMonthlyData(userId: string) {
  const res = await fetch(`/api/analytics/monthly?userId=${userId}`)
  if (!res.ok) throw new Error('Failed to fetch')
  return res.json()
}

export function LiveRevenueChart({ userId }: { userId: string }) {
  const { data, isLoading, error } = useQuery({
    queryKey: ['monthly-analytics', userId],
    queryFn: () => fetchMonthlyData(userId),
    refetchInterval: 30_000,  // refresh la 30s
    staleTime:       10_000,  // consider fresh 10s
  })

  return (
    <ChartShell
      isLoading={isLoading}
      error={error as Error}
      isEmpty={!data?.length}
      height={300}
    >
      <RevenueChart data={data!} />
    </ChartShell>
  )
}

// SWR — alternativă mai simplă
import useSWR from 'swr'
const { data, isLoading, error } = useSWR(
  `/api/analytics/monthly?userId=${userId}`,
  url => fetch(url).then(r => r.json()),
  { refreshInterval: 30_000 }
)
```

#### 13.3 Overplotting — soluții pentru scatter cu date dense

```javascript
// PROBLEMA: 5.000 puncte pe scatter → suprapunere, distribuția devine invizibilă

// SOLUȚIE 1 — Alpha transparency (cel mai simplu)
datasets: [{
  backgroundColor: 'rgba(14, 165, 233, 0.15)',  // opacity 15%
  pointRadius: 3,
  borderWidth: 0
}]

// SOLUȚIE 2 — Jitter (pentru date categoriale)
function jitter(value: number, amount = 0.3): number {
  return value + (Math.random() - 0.5) * amount
}

// SOLUȚIE 3 — Sampling pentru preview rapid (nu distorsionează tendința)
function sampleEvenly<T>(data: T[], maxPoints = 2000): T[] {
  if (data.length <= maxPoints) return data
  const step = data.length / maxPoints
  return Array.from({ length: maxPoints }, (_, i) => data[Math.floor(i * step)])
}

// SOLUȚIE 4 — LTTB (Largest-Triangle-Three-Buckets) — păstrează shape-ul
// Disponibil în Chart.js cu decimation plugin (Secțiunea 5.3)
// Sau manual: npm install downsample
import { LTTB } from 'downsample'
const sampled = LTTB(data.map(d => [d.x, d.y]), 500)
```

---

## BLOC 5 — Producție

### Secțiunea 14 — 24 Greșeli Comune

#### GV — Data Visualization (8 greșeli de concept)

```
GV1: PIE CU PREA MULTE CATEGORII
Problemă: Pie/Doughnut cu 8+ categorii — unghiurile nu mai pot fi comparate vizual
Fix: Bar chart orizontal sortate descendent + "Top 5 + Altele"

GV2: TRUNCAREA AXEI Y PE BAR CHART
Problemă: Y pornește de la 4.000 → bara de 4.500 pare de 5x mai mare decât 4.100
Fix: beginAtZero: true OBLIGATORIU pe bar. Pe line/area: acceptabil cu notă explicită.

GV3: DUAL Y AXIS FĂRĂ JUSTIFICARE
Problemă: Orice 2 serii par corelate pe dual Y (manipulare vizuală facilă)
Fix: NUMAI pentru unități incomparabile (RON vs %) cu notă explicită pe grafic

GV4: ROȘU + VERDE = INVIZIBIL PENTRU 6% DINTRE BĂRBAȚI
Problemă: Deuteranopia — roșu și verde apar identic
Fix: Okabe-Ito vermilion (#D55E00) + green (#009E73). Test: Chrome DevTools → Deuteranopia

GV5: DATE FĂRĂ CONTEXT
Problemă: "5.200 RON" fără comparație = dată brută, nu informație
Fix: Delta față de luna trecută (±%), comparație față de target, trend pe sparkline

GV6: CHARTJUNK — pixeli fără funcție
Problemă: Griduri groase, umbre, fundaluri, 3D, gradiente decorative pe bare
Fix: Tufte data-ink ratio maxim — elimină tot ce nu reprezintă date

GV7: PREA MULTE CULORI PE ACELAȘI GRAFIC
Problemă: 7+ culori → ochiul nu mai urmează seriile
Fix: Max 5 culori per grafic; pentru mai multe serii → small multiples

GV8: GRADIENT PE BAR CHARTS
Problemă: Gradienta implică o dimensiune continuă care nu există
Fix: Culoare solidă pe bare; gradient acceptabil DOAR pe fill-ul area charts
```

#### GT — Technical (16 greșeli tehnice)

```
GT1: chart.destroy() OMIS [BLOCKER]
Problemă: La remount, "Canvas is already in use by Chart"
Fix: return () => { chartRef.current?.destroy() } în useEffect cleanup

GT2: maintainAspectRatio: false FĂRĂ CONTAINER HEIGHT
Problemă: Grafic cu 0px sau 100vh înălțime
Fix: Container cu height explicit SAU aspectRatio: 2 pe options

GT3: CANVAS HiDPI IGNORAT
Problemă: Text și linii blur pe Retina
Fix: setupCanvas() cu devicePixelRatio + ctx.scale(dpr, dpr)

GT4: 'use client' SAU ssr:false ABSENT PE RECHARTS [BLOCKER]
Problemă: "window is not defined" sau hydration mismatch
Fix: 'use client' + 'use client' pe componentă SAU dynamic(() => import(), { ssr: false })

GT5: RESPONSIVECONTAINER FĂRĂ HEIGHT PE CONTAINER
Problemă: Grafic cu înălțime 0px
Fix: <div style={{ height: 300 }}> sau height={300} direct pe ResponsiveContainer

GT6: cancelAnimationFrame OMIS ÎN CLEANUP
Problemă: Memory leak — loop continuă pe componentă unmounted
Fix: return () => { if (rafId) cancelAnimationFrame(rafId) } OBLIGATORIU

GT7: CLICK COORDS GREȘITE PE CANVAS HIDPI
Problemă: Click offset față de element real pe Retina
Fix: getCanvasPos() cu (canvas.width / rect.width) / dpr

GT8: ctx.save() FĂRĂ ctx.restore() PERECHE
Problemă: Transform-urile se acumulează → graficul se deplasează fiecare frame
Fix: Orice ctx.save() are ctx.restore() garantat (try/finally dacă e necesar)

GT9: beginPath() OMIS ÎNTRE SHAPE-URI
Problemă: Shape-urile anterioare se contopesc cu cele noi în același path
Fix: ctx.beginPath() OBLIGATORIU înainte de fiecare shape nou

GT10: DATE OBJECTS SERIALIZATE SERVER→CLIENT [BLOCKER]
Problemă: new Date() pierde metodele la serializare JSON → "date.getMonth is not a function"
Fix: Transmite string ISO, convertești cu new Date(str + 'T00:00:00') în Client Component

GT11: TIMEZONE BUG CU DATE PARSING
Problemă: new Date('2026-01-15') = UTC midnight → zi anterioară în UTC-x
Fix: new Date('2026-01-15T00:00:00') sau parseISO din date-fns

GT12: chart.update() PREA DES (live data)
Problemă: Update la fiecare event WebSocket → 60fps redraw inutil
Fix: Batch cu setInterval + chart.update('none') la 1-2 fps

GT13: REFERINȚE INSTABILE ÎN RECHARTS
Problemă: formatter={() => ...} nou la fiecare render → re-render complet Recharts
Fix: useCallback cu [] dependencies pentru funcții pure

GT14: TOUCH EVENTS FĂRĂ passive:false
Problemă: preventDefault() ignorat de browser → scroll în loc de interacțiune
Fix: addEventListener('touchstart', fn, { passive: false })

GT15: FORMATTERI LIPSĂ PE AXELE MONETARE
Problemă: Axa afișează "12345.67" în loc de "12.3k RON"
Fix: tickFormatter={(v) => fmtCompact(v, ' RON')} — din lib/formatters.ts

GT16: NICIUN ERROR BOUNDARY PE GRAFICE
Problemă: Un grafic cu date malformate crapă toată pagina
Fix: <ChartErrorBoundary name="..."> în jurul oricărui grafic cu date externe
```

---

### Secțiunea 15 — Performanță: Tiers + ECharts în Next.js

#### 15.1 Decision tree performanță

```
< 1.000 puncte, interactivitate:      Recharts (SVG, accesibil, CSS theming)
< 1.000 puncte, customizare:          Chart.js (react-chartjs-2)
1.000 – 10.000 puncte:               Chart.js cu decimation LTTB
10.000 – 100.000 puncte:             Chart.js cu parsing:false + normalized:true + animation:false
> 100.000 puncte:                     ECharts cu WebGL renderer
Date geografice masive:              deck.gl
```

#### 15.2 ECharts în Next.js — integrare completă

```bash
npm install echarts echarts-for-react
# Pentru WebGL (scatter/heatmap masive):
npm install echarts-gl
```

```tsx
// OBLIGATORIU: dynamic import — ECharts apelează window în render
import dynamic from 'next/dynamic'
const ReactECharts = dynamic(() => import('echarts-for-react'), {
  ssr: false,
  loading: () => <ChartSkeleton height={400} />
})

export function BigScatterChart({ data }: { data: { x: number; y: number }[] }) {
  const option = {
    series: [{
      type: 'scatterGL',       // WebGL renderer
      data: data.map(d => [d.x, d.y]),
      symbolSize: 2,
      itemStyle: { color: OKABE_ITO.skyBlue, opacity: 0.6 },
      progressive: 200_000,        // randează în batches de 200k
      progressiveThreshold: 10_000 // activează progressive rendering > 10k
    }],
    xAxis: { type: 'value' },
    yAxis: { type: 'value' },
    tooltip: { trigger: 'item', formatter: (p: any) => `(${p.value[0]}, ${p.value[1]})` }
  }

  return (
    <ReactECharts
      option={option}
      style={{ height: 400 }}
      lazyUpdate={true}   // batched updates
      notMerge={false}    // merge cu options anterioare
    />
  )
}
```

#### 15.3 React DevTools Profiling — diagnosticare re-renders

```
React DevTools Profiler → Record → interacționezi → Stop

Semne de problemă:
- Recharts re-renderizează la fiecare keystroke dintr-un form → GT13 (referințe instabile)
- rAF loop > 16ms/frame → OffscreenCanvas sau reduce draw complexity
- useMemo nu cache-uiește → dependencies instabile (obiect nou la fiecare render)

Fix rapid pentru re-renders:
export const RevenueChart = React.memo(({ data }: Props) => { ... })
// Re-renderizează NUMAI când referința `data` se schimbă
```

---

### Secțiunea 16 — Accesibilitate Reală

#### 16.1 Table fallback — soluția corectă

```tsx
// aria-label="..." pe canvas NU e suficient pentru screen readers
// Soluția: tabel cu datele complete (vizibil sau sr-only)

export function AccessibleRevenueChart({ data }: { data: MonthlyData[] }) {
  return (
    <div>
      {/* Graficul — decorativ pentru screen readers (tabelul conține informația) */}
      <div aria-hidden="true">
        <ChartErrorBoundary name="Revenue">
          <RevenueChart data={data} />
        </ChartErrorBoundary>
      </div>

      {/* Tabel accesibil — sr-only îl ascunde vizual dar rămâne în DOM */}
      <table className="sr-only">
        <caption>Venituri și cheltuieli lunare 2026</caption>
        <thead>
          <tr>
            <th scope="col">Lună</th>
            <th scope="col">Venituri (RON)</th>
            <th scope="col">Cheltuieli (RON)</th>
            <th scope="col">Net (RON)</th>
          </tr>
        </thead>
        <tbody>
          {data.map(row => (
            <tr key={row.month}>
              <th scope="row">{row.month}</th>
              <td>{row.income.toLocaleString('ro-RO')}</td>
              <td>{row.expenses.toLocaleString('ro-RO')}</td>
              <td>{(row.income - row.expenses).toLocaleString('ro-RO')}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
```

#### 16.2 Recharts SVG — accesibil nativ

```tsx
<AreaChart
  data={data}
  role="img"
  aria-labelledby="chart-title chart-desc"
>
  <title id="chart-title">Venituri lunare Ian–Iun 2026</title>
  <desc id="chart-desc">
    Grafic area cu trend crescător: Ian 5.200, Feb 4.800, Mar 5.600, Apr 6.100, Mai 5.800, Iun 6.400 RON
  </desc>
  <Area dataKey="income" />
  <XAxis dataKey="month" />
  <YAxis />
  <Tooltip />
</AreaChart>
```

#### 16.3 WCAG AA checklist

```
□ Contrast text pe grafic: ≥ 4.5:1 (verificat cu contrastRatio() din Sec. 1.3)
□ Contrast elemente grafice (bare, linii): ≥ 3:1 față de fundal
□ Nu comunici informație EXCLUSIV prin culoare (+ pattern fill sau etichetă)
□ Tooltip accesibil cu tastatură (Recharts are focus management built-in)
□ Tabel alternativ prezent (vizibil sau sr-only)
□ role="img" + aria-labelledby pe SVG charts
□ ChartErrorBoundary pe orice grafic cu date externe
□ Testare cu Deuteranopia în Chrome DevTools
□ Testare cu NVDA (Windows) sau VoiceOver (Mac/iOS)
```

---

### Secțiunea 17 — Decision Tree Complet + Comparison + Checklist + Quick Reference

#### 17.1 Decision tree complet

```
START: Ce tip de date?

→ CATEGORII (comparare)
  ≤ 12 categorii              → Bar Chart vertical
  > 12 categorii, etichete lungi → Bar Chart orizontal, sortate
  ≤ 5 categorii, compoziție   → Pie / Doughnut
  Categorie × perioadă        → Heatmap

→ TEMPORAL (trend)
  1 serie                     → Line Chart
  2-3 serii, comparare        → Multi-line Chart
  Stacking (compoziție în timp) → Stacked Area
  Anomalii față de medie      → Area + ReferenceLine

→ DISTRIBUȚIE STATISTICĂ
  1 variabilă, frecvență      → Histogram
  Outliers, quartile          → Box Plot
  2 variabile                 → Scatter Plot
  Densitate mare (> 5k)       → Alpha Scatter / Hexbin

→ FLUXURI
  Flux între categorii        → Sankey
  Ierarhie cu proporții       → Treemap

→ GEOGRAFIC
  Culori per regiune          → Choropleth (Recharts + SVG map)
  Puncte la scară             → deck.gl

→ METRICI SINGLE VALUE
  Progres față de target      → Bullet Chart (nu Gauge)
  Trend rapid, inline         → Sparkline (Area 40px, fără axe)
```

#### 17.2 Comparison table

| Criteriu | Chart.js 4 | Recharts 2 | Canvas pur | ECharts |
|---|---|---|---|---|
| Setup complexity | Mediu | Mic | Mare | Mediu |
| React integration | react-chartjs-2 | Nativ | Manual | echarts-for-react |
| Bundle size | ~80kB | ~170kB | 0kB | ~800kB (tree-shakable) |
| Max data points | ~50k cu decimation | ~5k | ~100k | Milioane (WebGL) |
| Customizare | Medie (plugins) | Mare (JSX) | Totală | Mare (option API) |
| Animații | Built-in | Built-in | Manual | Built-in |
| Accesibilitate | Mediocru | Bună (SVG) | Manual | Mediocru |
| SSR (Next.js) | ✗ dynamic ssr:false | ✗ dynamic ssr:false | ✗ | ✗ dynamic ssr:false |
| TypeScript | ✓ Excelent | ✓ Bun | Native | ✓ Bun |
| Export SVG | ✗ PNG only | ✓ Nativ | ✗ PNG only | ✗ |
| Best for | Standard + live data | Dashboarduri React | Custom vizualizări | Big data |

#### 17.3 Checklist pre-deploy

```
□ CULORI
  □ Paleta testată cu Deuteranopia (Chrome DevTools → Rendering)
  □ Contrast text ≥ 4.5:1 cu contrastRatio()
  □ Nu comunici date exclusiv prin culoare

□ PERFORMANCE
  □ Chart.js: chartRef.current?.destroy() în useEffect cleanup
  □ Canvas: cancelAnimationFrame + observer.disconnect() în cleanup
  □ Recharts: formatters și tickFormatters cu useCallback([])
  □ Date > 1k: decimation sau Canvas în loc de SVG

□ NEXT.JS APP ROUTER
  □ Recharts: 'use client' SAU dynamic ssr:false
  □ Niciun Date object server→client (string ISO)
  □ Data fetch în Server Component, chart în Client Component
  □ userId exclusiv din getUser(), nu din params sau body

□ ERROR HANDLING
  □ ChartErrorBoundary pe orice grafic cu date externe
  □ ChartShell cu loading/empty/error states
  □ Timezone-safe: new Date(str + 'T00:00:00') sau parseISO

□ ACCESIBILITATE
  □ Tabel alternativ (sr-only sau vizibil)
  □ role="img" + aria-labelledby pe SVG charts
  □ Keyboard navigation testată în Recharts

□ EXPORT (dacă necesar)
  □ PNG testat (html2canvas sau canvas.toDataURL)
  □ SVG export pentru Recharts
  □ PDF cu jsPDF testat pe Safari (diferit de Chrome)
```

#### 17.4 Quick Reference Card

```typescript
// ============================================================
// SETUP RAPID — copiezi în orice proiect
// ============================================================

// 1. Chart.js register (o singură dată)
import { Chart, CategoryScale, LinearScale, BarElement, LineElement,
  PointElement, ArcElement, Title, Tooltip, Legend, Filler } from 'chart.js'
Chart.register(CategoryScale, LinearScale, BarElement, LineElement,
  PointElement, ArcElement, Title, Tooltip, Legend, Filler)

// 2. Canvas HiDPI setup
const setupCanvas = (el, w, h) => {
  const dpr = devicePixelRatio ?? 1
  el.width = w * dpr; el.height = h * dpr
  el.style.width = `${w}px`; el.style.height = `${h}px`
  const ctx = el.getContext('2d'); ctx.scale(dpr, dpr); return ctx
}

// 3. Canvas coords (HiDPI-aware)
const getPos = (canvas, e) => {
  const r = canvas.getBoundingClientRect(), dpr = devicePixelRatio ?? 1
  return {
    x: (e.clientX - r.left) * (canvas.width / r.width)  / dpr,
    y: (e.clientY - r.top)  * (canvas.height / r.height) / dpr
  }
}

// 4. Axis formatters
const fmtK   = v => v >= 1e6 ? `${(v/1e6).toFixed(1)}M` : v >= 1e3 ? `${(v/1e3).toFixed(0)}k` : v
const fmtRON = v => new Intl.NumberFormat('ro-RO', { style:'currency', currency:'RON', maximumFractionDigits:0 }).format(v)
const fmtM   = iso => new Intl.DateTimeFormat('ro-RO', { month:'short' }).format(new Date(iso + 'T00:00:00'))
const fmtPct = v => new Intl.NumberFormat('ro-RO', { style:'percent', maximumFractionDigits:1 }).format(v)

// 5. Okabe-Ito (daltonism-safe)
const OI = { blue:'#0072B2', orange:'#E69F00', green:'#009E73',
             vermilion:'#D55E00', skyBlue:'#56B4E9', purple:'#CC79A7' }

// 6. Recharts checklist
// 'use client' OU dynamic ssr:false
// ResponsiveContainer → container cu height explicit
// Formatters → useCallback([])
// isAnimationActive={false} pentru live data sau SSR
// syncId="dashboard" pentru tooltip sincronizat multi-chart

// 7. Data transitions
// Chart.js: chart.data.datasets[0].data = newValues; chart.update()
// Canvas: spring physics (k=0.12, d=0.85) în rAF loop
// Recharts: actualizezi props → React diffing gestionează

// 8. Wrappers obligatorii
// <ChartErrorBoundary name="...">
//   <ChartShell isLoading={...} isEmpty={!data?.length} error={error}>
//     <ActualChart data={data!} />
//   </ChartShell>
// </ChartErrorBoundary>

// 9. Timezone-safe date parsing
// ✗ new Date('2026-01-15')         → UTC midnight, wrong day în UTC-x
// ✓ new Date('2026-01-15T00:00:00') → local time, corect
// ✓ parseISO('2026-01-15')          → date-fns, cel mai sigur

// 10. Test culori înainte de deploy
// Chrome DevTools → Rendering → Emulate vision deficiencies → Deuteranopia
```

---

*Ghid 7 — Data Visualization v1.0 Final*
*Stack: Chart.js 4 · react-chartjs-2 · Canvas 2D · Recharts 2 · D3 utilities · ECharts · Next.js 14+*
*Proiecte de referință: Vibe Budget · ERP Financiar · CashPulse · Daily Sales Flash · MenuMix Matrix · StudioFlow Intelligence*
