# /dataviz-audit — Audit Data Visualization

**Scopul:** Analizează fișierele proiectului pentru probleme de data visualization și raportează BLOCKER / ATENȚIE / OK per regulă. Bazat pe ghid-data-visualization-v1.md. Nu modifică niciun fișier — doar raportează.

**Stack acoperit:** Chart.js 4 · Canvas 2D API · Recharts 2 · ECharts · Next.js App Router · HTML Vanilla.

---

## PASUL 1 — Identifică directorul

**Dacă argumentul conține o cale** (ex: `/dataviz-audit Desktop/vibe-budget`):
Lucrează în: `C:\Users\admin\Desktop/vibe-budget`

**Dacă argumentul este gol:**
Întreabă: `Pe care proiect rulăm auditul? (ex: Desktop/cashpulse)`
Sau, dacă există context clar din sesiune, folosește directorul curent.

---

## PASUL 2 — Determină tipul de proiect și detectează librăriile

Rulează în **paralel** cu Glob și Grep:

1. **Tip proiect:** Glob pentru `next.config.*` și `package.json` în directorul proiectului
   - Dacă găsești `next.config.*` sau `"next"` în package.json → **Next.js**
   - Dacă găsești doar `*.html` fără next.config → **HTML Vanilla**
   - Ambele pot coexista (ex: HTML prototype + Next.js app)

2. **Chart.js:** Grep pentru `new Chart(` sau `Chart.register(` sau `from 'chart.js'` în fișierele proiectului
   - Găsit → marchează **Chart.js detectat** + listează fișierele

3. **Canvas API:** Grep pentru `getContext('2d')` în fișierele proiectului
   - Găsit → marchează **Canvas detectat** + listează fișierele

4. **Recharts:** Grep pentru `from 'recharts'` sau `require('recharts')` în fișierele `.tsx/.ts/.jsx/.js`
   - Găsit → marchează **Recharts detectat** + listează fișierele

5. **ECharts:** Grep pentru `from 'echarts'` sau `echarts-for-react` în fișierele proiectului
   - Găsit → marchează **ECharts detectat** + listează fișierele

Dacă nu găsești nicio librărie și niciun canvas → raportează `EROARE: nu s-au detectat librării de vizualizare` și oprește.

Notează: `[Tip proiect] + [Librării detectate]`

---

## PASUL 3 — Verificări pe categorii

Rulează **numai categoriile pentru librăriile detectate**. Dacă o librărie nu e detectată, marchează categoria cu `— (nedectată)`.

---

### CATEGORIA A — Chart.js

*Rulează dacă Chart.js detectat.*

**A1 — cleanup destroy() [BLOCKER dacă absent]**

Grep pentru `new Chart(` în toate fișierele.
Pentru fiecare fișier cu `new Chart(`:
- HTML Vanilla JS: verifică dacă există `chart.destroy()` sau `chartRef.destroy()` sau `[variabila].destroy()` în același fișier (la cleanup sau la re-inițializare).
- React/Next.js: verifică dacă există `chartRef.current?.destroy()` sau `chartRef.current.destroy()` în `useEffect` cleanup (în `return () => { ... }`).
- Există destroy() → **OK**
- Lipsește destroy() → **BLOCKER** — la remount: `Canvas is already in use by Chart`

**A2 — update date corect (chart.update vs destroy+new) [ATENȚIE]**

Grep pentru fișiere care au atât `destroy()` cât și `new Chart(` în același `useEffect` sau funcție de update.
- Ambele în același bloc de update (nu în cleanup) → **ATENȚIE** — ștergi și recreezi la fiecare update (flickering, pierdere animație); folosește `chart.data.datasets[0].data = newData; chart.update()` în schimb
- `destroy()` apare NUMAI în cleanup (return) → **OK**

**A3 — maintainAspectRatio fără height [ATENȚIE]**

Grep pentru `maintainAspectRatio: false`.
Dacă găsit:
- Verifică dacă canvas-ul sau container-ul părinte are `height` sau `style={{ height: ... }}` explicit.
- Lipsă height pe container → **ATENȚIE** — grafic cu 0px sau 100vh înălțime

---

### CATEGORIA B — Canvas API

*Rulează dacă Canvas detectat.*

**B1 — HiDPI setup (devicePixelRatio) [ATENȚIE]**

Grep pentru `getContext('2d')` și verifică dacă în **același fișier** există `devicePixelRatio` sau `window.devicePixelRatio`.
- Există → **OK**
- Lipsește → **ATENȚIE** — text și linii blur pe ecrane Retina (Mac, iOS, Android HiDPI)
- Fix: `const dpr = window.devicePixelRatio ?? 1; canvas.width = w * dpr; ctx.scale(dpr, dpr)`

**B2 — beginPath() înainte de fiecare shape [BLOCKER dacă absent]**

Grep pentru `ctx.rect(` sau `ctx.arc(` în fișierele cu Canvas.
Dacă găsit, verifică dacă există `ctx.beginPath()` în **același fișier**.
- Numără apariții: `ctx.beginPath()` vs (`ctx.rect(` + `ctx.arc(`)
- `ctx.beginPath()` apare de 0 ori, dar `rect`/`arc` apar → **BLOCKER** — shape-urile se contopesc, umplute cu culoarea ultimei operații
- `ctx.beginPath()` apare cel puțin o dată → **OK** (nu putem verifica pozițiile exact, informăm)
- Notă: reamintești regula — `ctx.beginPath()` OBLIGATORIU înaintea fiecărui shape nou

**B3 — cancelAnimationFrame în cleanup [BLOCKER dacă absent]**

Grep pentru `requestAnimationFrame` în fișierele cu Canvas.
Dacă găsit, verifică dacă `cancelAnimationFrame` există în **același fișier**.
- HTML Vanilla: verifică dacă există handler de cleanup (event `beforeunload`, funcție `destroy`, etc.) care apelează `cancelAnimationFrame`.
- React/Next.js: verifică dacă `cancelAnimationFrame` apare în `useEffect` cleanup (return).
- Există → **OK**
- Lipsește → **BLOCKER** — memory leak: loop rAF continuă pe componentă unmounted sau pagină închisă

**B4 — ctx.save() cu ctx.restore() pereche [ATENȚIE]**

Grep pentru `ctx.save()` și `ctx.restore()` în fișierele cu Canvas.
Numără apariții:
- `save()` == `restore()` → **OK**
- `save()` > `restore()` → **ATENȚIE** — transform-urile se acumulează frame după frame; graficul se deplasează progresiv
- `save()` == 0 → **OK** (nu e folosit)

---

### CATEGORIA C — Recharts

*Rulează dacă Recharts detectat. Se aplică NUMAI pentru Next.js App Router.*

**C1 — 'use client' sau dynamic ssr:false [BLOCKER dacă absent]**

Pentru fiecare fișier care importă din `recharts`:
- Verifică dacă fișierul are `'use client'` pe primul rând SAU
- Verifică dacă este importat în altă parte via `dynamic(() => import('...'), { ssr: false })`.
- Una dintre cele două → **OK**
- Niciuna → **BLOCKER** — `window is not defined` la build sau hydration mismatch la runtime

**C2 — ResponsiveContainer cu height explicit [BLOCKER dacă absent]**

Grep pentru `<ResponsiveContainer` în fișierele cu Recharts.
Pentru fiecare apariție, citește contextul (±10 linii):
- `<ResponsiveContainer height={N}` (valoare numerică sau procent) → **OK**
- Container părinte cu `style={{ height: ... }}` sau clasă Tailwind cu `h-[...]` sau `h-48` etc. → **OK**
- `<ResponsiveContainer width="100%">` fără niciun height → **BLOCKER** — grafic cu 0px înălțime
- Notă: `height="100%"` funcționează NUMAI dacă părintele are height explicit

**C3 — Formatters stabili cu useCallback [ATENȚIE]**

Grep pentru `formatter=` sau `tickFormatter=` în fișierele cu Recharts.
Pentru fiecare apariție:
- Pattern: `formatter={(v) =>` sau `tickFormatter={(v) =>` inline (arrow fără useCallback) → **ATENȚIE** — Recharts re-renderizează complet la orice keystroke din formularele de pe pagină
- Pattern: `formatter={fmtFn}` unde `fmtFn = useCallback(...)` sau funcție definită în afara componentei → **OK**
- Pattern: `content={<CustomTooltip />}` inline → **ATENȚIE** (aceeași problemă)

**C4 — isAnimationActive pe live data [ATENȚIE informativ]**

Grep pentru `refetchInterval` sau `setInterval` în fișierele cu componente Recharts.
Dacă găsit, verifică dacă `isAnimationActive={false}` apare pe componentele de chart (BarChart, AreaChart, etc.).
- `isAnimationActive={false}` prezent → **OK**
- Absent pe componente cu live data → **ATENȚIE** — animația re-pornește la fiecare update, creând efect vizual deranjant

---

### CATEGORIA D — Date & Timezone

*Rulează universal pe toate fișierele JS/TS detectate.*

**D1 — Timezone-safe date parsing [ATENȚIE]**

Grep cu pattern regex pentru `new Date\(['"](\d{4}-\d{2}-\d{2})['"]\)` — date ISO fără ora locală.
- Găsit → **ATENȚIE** + listezi exact fișier:linie
- Exemplu greșit: `new Date('2026-01-15')` → UTC midnight → zi anterioară în UTC-5..UTC-11
- Fix: `new Date('2026-01-15T00:00:00')` (local time) sau `parseISO('2026-01-15')` (date-fns)
- Nu găsit → **OK**

**D2 — Date objects server→client (Next.js) [BLOCKER]**

*Aplică NUMAI dacă proiect Next.js.*

Grep pentru fișiere `.tsx` Server Components (fără `'use client'`) care transmit date din Supabase și verifică dacă în JSX-ul returnat trec props cu `.created_at` sau `.date` sau `.updated_at` fără `.toISOString()` sau `.toString()` sau string slicing.

Pattern de risc: `<ClientComponent date={item.created_at}` unde `created_at` e obiect Date (nu string).

Grep specific: caută `created_at={` sau `date={item.` sau `updatedAt={` în Server Components.
- Pattern găsit fără `.toISOString()` sau fără tip `string` explicit → **BLOCKER** — `date.getMonth is not a function` în Client Component
- Nu găsit sau transmis ca string → **OK**

---

### CATEGORIA E — Robustness & Corectitudine Vizuală

*Rulează universal.*

**E1 — beginAtZero pe bar charts [ATENȚIE]**

**Chart.js:** Grep pentru `type: 'bar'` sau `<Bar` (în context Chart.js, nu Recharts).
Verifică dacă în options există `beginAtZero: true` pe axa Y.
- Absent → **ATENȚIE** — Y pornește de la min(data), nu de la 0; bare scurte par proporțional mai mari (lie factor)

**Recharts:** Grep pentru `<BarChart` sau `<Bar` (în fișiere cu Recharts).
Verifică dacă `<YAxis domain={[0,` sau `domain={[0, 'auto']}` apare pe YAxis.
- Absent → **ATENȚIE** — aceeași problemă vizuală

**E2 — ChartErrorBoundary pe charts cu date externe [ATENȚIE]**

*Aplică NUMAI dacă Next.js cu Recharts sau react-chartjs-2.*

Grep pentru `ChartErrorBoundary` în întregul proiect.
- Există cel puțin o apariție → **OK** (prezent în proiect, nu verificăm fiecare grafic)
- 0 apariții → **ATENȚIE** — un grafic cu date malformate din Supabase/API crapă toată pagina; adaugă `<ChartErrorBoundary>` în jurul oricărui chart cu date externe

---

### CATEGORIA F — ECharts

*Rulează NUMAI dacă ECharts detectat, în context Next.js.*

**F1 — dynamic ssr:false pe ECharts [BLOCKER dacă absent]**

Grep pentru `from 'echarts-for-react'` sau `import ReactECharts`.
Verifică dacă e importat via `dynamic(() => import('echarts-for-react'), { ssr: false })`.
- `dynamic ssr:false` → **OK**
- Import static → **BLOCKER** — `window is not defined` la build

**F2 — progressive rendering pe datasets mari [ATENȚIE informativ]**

Grep pentru `scatterGL` sau `type: 'scatter'` în opțiunile ECharts.
Verifică dacă `progressive` și `progressiveThreshold` sunt definite.
- Definite → **OK**
- Absente → **ATENȚIE** — datasets > 10k puncte blochează main thread la render inițial

---

## PASUL 4 — Raportează în formatul exact de mai jos

```
=== DATAVIZ-AUDIT: [director / proiect] ===
Tip proiect: [HTML Vanilla / Next.js / Ambele]
Librării detectate: [Chart.js ✓ / Canvas ✓ / Recharts ✓ / ECharts ✓]

── A. CHART.JS ──────────────────────────────
  [✓/✗/!] A1 destroy() în cleanup          [status + fișier:linie dacă BLOCKER]
  [✓/!]   A2 chart.update() vs destroy+new  [status + detaliu dacă ATENȚIE]
  [✓/!]   A3 maintainAspectRatio + height   [status]
  (sau: — Chart.js nedetectat)

── B. CANVAS API ────────────────────────────
  [✓/!]   B1 devicePixelRatio (HiDPI)       [status + fișier dacă ATENȚIE]
  [✓/✗]   B2 beginPath() înainte de shape   [status + fișier:linie dacă BLOCKER]
  [✓/✗]   B3 cancelAnimationFrame cleanup   [status + fișier:linie dacă BLOCKER]
  [✓/!]   B4 ctx.save() + ctx.restore()     [status + count dacă dezechilibrat]
  (sau: — Canvas nedetectat)

── C. RECHARTS ──────────────────────────────
  [✓/✗]   C1 'use client' sau ssr:false     [status + fișier:linie dacă BLOCKER]
  [✓/✗]   C2 ResponsiveContainer + height   [status + fișier:linie dacă BLOCKER]
  [✓/!]   C3 Formatters cu useCallback      [status + fișier:linie dacă ATENȚIE]
  [i]     C4 isAnimationActive live data    [OK / ATENȚIE informativ]
  (sau: — Recharts nedetectat)

── D. DATE & TIMEZONE ───────────────────────
  [✓/!]   D1 new Date() timezone-safe       [status + fișier:linie dacă ATENȚIE]
  [✓/✗]   D2 Date objects server→client     [status + fișier:linie dacă BLOCKER]
  (sau D2: — (aplică doar Next.js))

── E. ROBUSTNESS ────────────────────────────
  [✓/!]   E1 beginAtZero pe bar charts      [status + fișier dacă ATENȚIE]
  [✓/!]   E2 ChartErrorBoundary prezent     [status]
  (sau E2: — (aplică doar Next.js cu date externe))

── F. ECHARTS ───────────────────────────────
  [✓/✗]   F1 dynamic ssr:false              [status + fișier dacă BLOCKER]
  [i]     F2 progressive rendering          [OK / ATENȚIE informativ]
  (sau: — ECharts nedetectat)

══════════════════════════════════════════════
BLOCKER-e: [N]  |  ATENȚIE: [M]  |  OK: [K]

VERDICT: [BLOCKER ✗ / ATENȚIE ⚠ / CLEAN ✓]

Fix-uri necesare (BLOCKER-e în ordinea impactului):
  1. [A1/B3/C1/C2] descriere exactă + fișier:linie + snippet de cod de adăugat
  2. ...
```

---

## Reguli de verdict

| Condiție | Verdict |
|---|---|
| Cel puțin un BLOCKER | **BLOCKER ✗** — listezi fix-ul complet cu snippet |
| Zero BLOCKER-e, cel puțin un ATENȚIE | **ATENȚIE ⚠** — informezi, utilizatorul decide |
| Toate OK sau INFO | **CLEAN ✓** |

---

## Ordinea fix-urilor la BLOCKER (impact descrescător)

`B3` (rAF leak) > `A1` (Chart.js destroy) > `C1` (Recharts SSR) > `C2` (ResponsiveContainer height) > `B2` (beginPath) > `D2` (Date server→client) > `F1` (ECharts SSR)

---

## Note de execuție

- **Nu modifica niciun fișier** — doar raportezi
- **Specifică fișier + linie** pentru BLOCKER și ATENȚIE — niciodată vag
- **Categorii nedetectate**: marchează cu `—` și explică în paranteză
- **HTML Vanilla vs Next.js**: C1/C2/C4/D2/E2/F1-F2 se aplică doar Next.js; A1-A3/B1-B4/D1/E1 se aplică ambelor
- **Proiecte HTML cu Chart.js CDN**: `new Chart(` e global — regulile A se aplică identic
- **Proiecte mixte** (ex: HTML prototype + Next.js app în același repo): auditezi ambele tipuri
- **Categoria C4 și F2** sunt informative (nu contribuie la BLOCKER/ATENȚIE count) — le raportezi cu `[i]`
