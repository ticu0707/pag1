# Plan: Daily Sales Flash — Implementare Modulară

## Context

Aplicație offline lead-magnet pentru oweri de business (restaurant, magazin fizic, eCommerce).
Distribuită ca 2 fișiere HTML descărcabile: `index.html` (landing) + `app.html` (aplicație).
Bazată pe PRD v4.0 — fără backend, fără API, fără cont. LocalStorage + Chart.js inline.

**Principiu de implementare:** fiecare modul este mic (~50-120 linii JS), independent, testabil izolat.
Implementare secvențială — fiecare modul verificat înainte de a trece la următorul.

---

## Fișiere finale

```
C:\Users\admin\Desktop\daily-sales-flash\
├── index.html    ← landing page (M17 — ultimul)
└── app.html      ← aplicația completă (M0–M16)
```

---

## Convenție date

- **Stocare internă** (LocalStorage keys + câmpul `date` din entry): `YYYY-MM-DD` — pentru sortare alfabetică corectă
- **Afișare în UI** (toate ecranele, tabelele, greeting, export vizual): `DD/MM/YYYY`
- **Utilitar de conversie** în `DSF.utils`:
  - `DSF.utils.toDisplay(isoStr)` → `"27/04/2026"`
  - `DSF.utils.toISO(ddmmyyyy)` → `"2026-04-27"`
  - `DSF.utils.todayISO()` → `"2026-04-27"` (data curentă în format ISO)
  - `DSF.utils.yesterdayISO()` → `"2026-04-26"`

---

## Structura internă app.html

```html
<head>  <!-- M0: CSS + variabile + Chart.js inline -->
<body>
  <!-- M0: HTML skeleton — toate ecranele, ascunse implicit -->
  <script>
    // DSF.utils — utilitar date + helpers
    // M1: DSF.storage  — engine LocalStorage
    // M2: DSF.config   — setări utilizator
    // M3: DSF.score    — calcul Day Score (funcții pure)
    // M4: DSF.nav      — navigare între ecrane
    // M5: DSF.onboard  — flow prima lansare
    // M6: DSF.form     — formular intrare zilnică
    // M7: DSF.dash     — ecranul Azi
    // M8: DSF.insights — micro-insights contextuale
    // M9: DSF.anim     — animații (flip, confetti, pulse)
    // M10: DSF.week    — ecranul Săptămână + Chart.js
    // M11: DSF.history — ecranul Istoric + Chart.js
    // M12: DSF.backup  — export/import JSON
    // M13: DSF.email   — captare email post-first-score
    // M14: DSF.share   — Web Share API + clipboard
    // M15: DSF.demo    — mod demo (?demo=true)
    // M16: DSF.settings — ecranul Settings
    // INIT: boot sequence
  </script>
</body>
```

---

## Module — specificație și ordine implementare

---

### M0 — Core Shell
**Ce face:** HTML skeleton complet + tot CSS-ul aplicației.
**Nu conține JS logic.**

HTML:
- `#screen-onboarding` — ascuns implicit
- `#screen-dash` — ecranul principal
- `#screen-week` — săptămână
- `#screen-history` — istoric
- `#screen-settings` — setări
- `#nav-bottom` — bară navigare fixă (4 butoane)
- `#modal-input` — formular intrare zilnică (overlay)
- `#modal-email` — captare email (overlay)
- `#demo-banner` — banner MOD DEMO (ascuns implicit)
- `#confetti-canvas` — canvas animație

CSS:
- Variabile: `--color-green`, `--color-yellow`, `--color-red`, `--color-gold`
- Dark theme implicit (background `#0f0f0f`, carduri `#1a1a1a`)
- Card components, bottom nav, modal overlay, score display (80px)
- Responsive single-column, max-width 480px centrat

**Estimare:** ~200 linii HTML, ~300 linii CSS
**Test:** deschide în browser — toate elementele prezente în DOM, niciun error în consolă.

---

### M1 — Storage Engine (`DSF.storage`)
**Ce face:** interfața unică cu LocalStorage. Niciun alt modul nu scrie direct în localStorage.

```js
DSF.storage = {
  save(dateStr, entry),      // salvează ziua (key: "dsf_day_YYYY-MM-DD")
  load(dateStr),             // returnează entry sau null
  loadRange(days),           // returnează array ultimele N zile cu date
  loadAll(),                 // returnează toate intrările sortate desc
  delete(dateStr),           // șterge o zi
  clear(),                   // șterge tot (cu confirmare externă)
  getExportData(),           // returnează obiect complet pentru export
  importData(jsonObj),       // validează și importă (returnează {ok, error})
  validateEntry(entry)       // validează structura unui entry
}
```

**Structura entry:**
```js
{
  date: "2026-04-27",        // YYYY-MM-DD (intern) — afișat ca "27/04/2026" în UI
  sales: 3200,               // number >= 0
  orders: 45,                // number >= 0 (integer)
  refunds: 0,                // number >= 0
  cashVariance: 15,          // number (poate fi negativ)
  score: 97,                 // number 0-110
  savedAt: "2026-04-27T22:15:00"
}
```

**Edge cases de testat:**
- `load()` pe dată inexistentă → `null` (nu throw)
- `loadRange(7)` cu 0 zile de date → array gol `[]`
- `importData()` cu JSON corupt → `{ok: false, error: "..."}`
- `importData()` cu entry unde `refunds > sales` → `{ok: false, error: "..."}`
- `save()` suprascrie ziua existentă fără eroare

**Estimare:** ~100 linii JS

---

### M2 — Config Module (`DSF.config`)
**Ce face:** citire/scriere setări utilizator din localStorage.

```js
DSF.config = {
  get(),           // returnează obiect config complet cu defaults
  set(key, value), // setează o cheie
  setAll(obj),     // setează mai multe chei (la onboarding)
  reset(),         // resetează la defaults
  DEFAULTS: {
    name: "",
    target: 0,
    currency: "RON",
    alertThreshold: 80,
    emailCaptured: false,
    currencyLocked: false,
    lastExport: null,
    onboardingDone: false
  }
}
```

**Edge cases de testat:**
- `get()` înainte de orice setare → returnează DEFAULTS (nu null/undefined)
- `set("target", -100)` → ignorat sau corectat la 0
- `set("currency", "XYZ")` → ignorat (doar RON/EUR/USD/GBP acceptate)

**Estimare:** ~60 linii JS

---

### M3 — Score Engine (`DSF.score`)
**Ce face:** calcul Day Score — funcții pure, fără efecte secundare, fără DOM.

```js
DSF.score = {
  calcTarget(actual, target),   // → 0-120
  calcCash(cashVariance, sales), // → 0-100
  calcRefund(refunds, sales),    // → 0-100
  calc(entry, target),          // → {score, targetScore, cashScore, refundScore}
  getLabel(score),              // → "Zi de record" | "Zi excepțională" | etc.
  getColor(score),              // → "gold" | "green" | "yellow" | "red"
  isPersonalBest(score, history) // → boolean
}
```

**Formule exacte:**

```
calcTarget(actual, target):
  dacă target <= 0 → null (componentă ignorată)
  dacă actual >= target → min(100 + (actual-target)/target*100, 120)
  altfel → actual/target * 100

calcCash(cashVariance, sales):
  dacă cashVariance == null || sales <= 0 → 100
  pct = |cashVariance| / sales * 100
  pct == 0   → 100
  pct <= 0.5 → 90
  pct <= 1   → 70
  pct <= 2   → 50
  altfel     → 20

calcRefund(refunds, sales):
  dacă refunds == 0 || sales <= 0 → 100
  rate = refunds / sales * 100
  rate <= 1  → 95
  rate <= 3  → 80
  rate <= 5  → 60
  rate <= 10 → 40
  altfel     → 20

calc(entry, target):
  ts = calcTarget(entry.sales, target)
  cs = calcCash(entry.cashVariance, entry.sales)
  rs = calcRefund(entry.refunds, entry.sales)
  dacă ts == null → score = min(round(cs*0.5 + rs*0.5), 110)
  altfel          → score = min(round(ts*0.6 + cs*0.2 + rs*0.2), 110)
```

**Praguri label/culoare:**
```
100-110 → "Zi de record"       → gold
90-99   → "Zi excepțională"    → green-intense
75-89   → "Zi bună"            → green
50-74   → "Zi acceptabilă"     → yellow
0-49    → "Zi dificilă"        → red
```

**Edge cases obligatorii (toate testate manual înainte de M4):**

| Input | Rezultat așteptat |
|---|---|
| sales=0, orders=0, refunds=0 | score=0 (caz special: zi fără activitate) |
| sales=3000, target=3000, refunds=0, cashVariance=0 | score=100 |
| sales=3200, target=3000, refunds=0, cashVariance=0 | score=104 |
| sales=1800, target=3000, refunds=300, cashVariance=-200 | score=44 |
| sales=2700, target=3000, refunds=50, cashVariance=30 | score=87 |
| refunds=3000, sales=3000 | score valid (refund rate 100% → RS=20) |
| target=0 (nedefinit) | calcul doar din CS+RS |
| cashVariance=null | CS=100 (ignorat) |

**Estimare:** ~90 linii JS

---

### M4 — Navigation (`DSF.nav`)
**Ce face:** afișează/ascunde ecrane, setează starea activă în bottom nav.

```js
DSF.nav = {
  go(screenId),      // ascunde toate, afișează screenId, setează nav activ
  current(),         // returnează screenId-ul curent
  SCREENS: ["dash","week","history","settings"]
}
```

**Estimare:** ~30 linii JS
**Test:** click pe fiecare buton din nav → ecranul corespunzător apare, celelalte dispar.

---

### M5 — Onboarding (`DSF.onboard`)
**Ce face:** detectează prima lansare, afișează form onboarding, salvează config.

Flow:
1. La boot: dacă `config.onboardingDone == false` → afișează `#screen-onboarding`
2. Form: Prenume + Target zilnic + Monedă (select)
3. Validare: target > 0, prenume nevid
4. La submit: `config.setAll(...)`, `config.set("onboardingDone", true)`, `nav.go("dash")`

**Edge cases:**
- Submit cu target = 0 → eroare inline "Introdu un target valid"
- Submit cu prenume gol → eroare inline

**Estimare:** ~60 linii JS

---

### M6 — Input Form (`DSF.form`)
**Ce face:** formular intrare zilnică, validare, salvare, mod editare.

```js
DSF.form = {
  open(dateStr),     // deschide modal, precompletează dacă există date pentru dateStr
  close(),
  validate(data),    // returnează {ok, errors: []}
  save(data),        // salvează via DSF.storage.save()
  calcLive()         // recalculează scorul provizoriu la fiecare keystroke
}
```

**Câmpuri:**
- Vânzări totale (text, acceptă virgulă și punct ca separator zecimal)
- Număr bonuri (number, integer)
- Refund-uri (text, acceptă zecimale)
- Cash variance (text, acceptă negativ + zecimale)
- Selector: Astăzi / Ieri (simplu, fără calendar complet)

**Validări inline (în timp real):**
- Refund-uri > Vânzări → "Refund-urile nu pot depăși vânzările. Verifică suma."
- Câmpuri negative unde nu e permis → eroare
- Număr bonuri = 0 cu vânzări > 0 → permis, AOV afișat ca "—"

**Mod editare:** dacă există date pentru data selectată → form deschis cu datele existente, buton "Actualizează" în loc de "Salvează"

**Scor provizoriu live:**
- Se calculează după fiecare keystroke pe orice câmp
- Afișat deasupra formularului cu label italic "Scor provizoriu"
- Dacă câmpuri parțiale → calcul cu valorile disponibile, restul = 0

**Edge cases:**
- Câmp gol la submit → tratat ca 0 (nu eroare, cu excepția vânzărilor)
- "1.250,50" → parseFloat normalizat corect
- "-50" în cash variance → acceptat
- Submit rapid dublu → al doilea ignorat (flag `isSubmitting`)

**Estimare:** ~110 linii JS

---

### M7 — Dashboard Screen (`DSF.dash`)
**Ce face:** randează ecranul Azi cu toate componentele.

```js
DSF.dash = {
  render(),          // randează complet ecranul
  renderScore(entry), // actualizează cardul Day Score
  renderCards(entry), // actualizează cele 4 carduri metrice
  renderStreak(),    // calculează și afișează streak
  renderSparkline(), // mini grafic 7 zile (SVG simplu, nu Chart.js)
  renderRecord()     // badge record personal
}
```

**Componente:**
- Greeting: "Bună [dimineața/ziua/seara], [Prenume]! — [Zi], [DD/MM/YYYY]"
- Status bar: "Date lipsă pentru azi ●" (roșu) sau "Date introduse ✓ — Editează" (verde)
- Day Score: număr 80px, colorat, cu label
- 4 carduri: Target vs Actual (%), AOV net, Refund Rate, Cash Variance
- Streak: vizibil doar dacă ≥ 2 zile consecutive la target
- Sparkline 7 zile: 7 cercuri colorate — SVG simplu, zero dependențe
- Micro-insight: text generat de `DSF.insights`
- Buton "Copiază rezumatul zilei"
- Buton "Adaugă ziua de azi" / "Editează ziua de azi"

**Logică streak:**
```
streak = 0
parcurge zilele cu date, DESC
cât timp (score >= threshold) AND (ziua anterioară există în storage):
  streak++
oprire la prima zi lipsă sau sub threshold
```

**Edge cases:**
- Nicio intrare salvată → ecran cu status "Date lipsă", fără sparkline, greeting activ
- O singură intrare → sparkline cu 1 punct, fără streak
- Ziua de azi fără date, ieri cu date → status "Date lipsă"

**Estimare:** ~130 linii JS

---

### M8 — Insights Engine (`DSF.insights`)
**Ce face:** generează textul micro-insight contextual.

```js
DSF.insights = {
  generate(history, config)  // → string mesaj
}
```

**Logică (în ordinea priorității):**

```
dacă history.length == 0 → "Prima zi înregistrată..."
dacă history.length < 7 → "Zi X din 7. Tendința..."
dacă history.length < 14 → "Media săptămânii: X RON/zi"
dacă history.length < 28 → "Față de săptămâna trecută: +/-X%"
dacă history.length >= 28:
  → verifică pattern ziua săptămânii (min 4 ocurențe aceeași zi)
  → dacă există pattern: "Vinerea sunt în medie cele mai bune zile..."
  → dacă 3+ zile consecutive sub threshold: "3 zile consecutive sub target..."
  → altfel: "Media lunii: X RON/zi"

dacă prima zi din lună nouă + luna trecută ≥ 20 intrări:
  → card special sumar lună anterioară (prioritate maximă)
```

**Estimare:** ~70 linii JS

---

### M9 — Animations (`DSF.anim`)
**Ce face:** animații vizuale la salvare și la score excepțional.

```js
DSF.anim = {
  revealScore(scoreData, isPersonalBest), // secvență completă post-save
  confetti(),        // confetti 1.5s pe canvas (doar când isPersonalBest)
  pulse(element),    // pulse scurt pe un element DOM
  breathe(message)   // mesaj "respiră" pe zi dificilă (score < 50)
}
```

**Secvența revealScore:**
1. Modal input se închide
2. Delay 100ms
3. Card 1 (Target) flip → 300ms
4. Delay 150ms → Card 2 (AOV) flip → 300ms
5. Delay 150ms → Card 3 (Refund) flip → 300ms
6. Delay 200ms → Day Score apare cu scale-in 400ms
7. Dacă isPersonalBest → confetti 1.5s

**Confetti trigger:** DOAR dacă `score >= 100 AND isPersonalBest(score, history)`
(Nu se declanșează la fiecare zi bună — rezervat pentru record personal)

**Mesaj "respiră":** dacă score < 50 → toast discret timp de 4 secunde:
*"Ziua de mâine e o nouă oportunitate. Target-ul tău: [X] RON."*

**Estimare:** ~80 linii JS

---

### M10 — Week Screen (`DSF.week`)
**Ce face:** grafic bare Chart.js pe 7 zile + tabel + sumar.

```js
DSF.week = {
  render()   // randează tot ecranul săptămână
}
```

**Componente:**
- Chart.js bar: vânzări pe ultimele 7 zile, linie orizontală = target
- Bare colorate după score (verde/galben/roșu)
- Tabel compact: Zi | Vânzări | Score | Culoare
- Card sumar: total săptămână, medie zilnică, zile la target din N

**Edge cases:**
- 0 zile de date → mesaj "Nu există date pentru această săptămână"
- 1-2 zile de date → grafic cu bare doar pentru zilele existente, restul gol
- Target = 0 → linie target ascunsă

**Estimare:** ~80 linii JS

---

### M11 — History Screen (`DSF.history`)
**Ce face:** grafic linie Chart.js pe 30 zile + tabel cu filtru.

```js
DSF.history = {
  render(days),      // days: 7 | 30 | 90
  setFilter(days)    // schimbă filtrul și re-randează
}
```

**Componente:**
- Chart.js line: Day Score pe ultimele N zile
- Tabel: Data | Vânzări | AOV | Score | Culoare (sortat DESC)
- Butoane filtru: 7 zile / 30 zile / 90 zile

**Edge cases:**
- 0 intrări → mesaj "Nu există date înregistrate"
- Filtru 90 zile cu doar 5 intrări → afișează doar cele 5 (nu eroare)

**Estimare:** ~80 linii JS

---

### M12 — Backup System (`DSF.backup`)
**Ce face:** export JSON, import JSON cu validare, indicator export în header.

```js
DSF.backup = {
  export(),              // descarcă JSON cu toate datele + config
  import(file),          // citește fișier, validează, importă
  getExportAge(),        // → număr zile de la ultimul export (sau null)
  updateExportIndicator() // actualizează badge-ul din header
}
```

**Export format:**
```json
{
  "app": "Daily Sales Flash",
  "version": "1.0",
  "exportedAt": "2026-04-27T22:00:00",
  "config": {...},
  "entries": [...]
}
```

**Validare import:**
- Verifică câmpul `"app": "Daily Sales Flash"` (protecție fișier greșit)
- Verifică că `entries` e array
- Validează fiecare entry via `DSF.storage.validateEntry()`
- Dacă orice entry e invalidă → import refuzat cu mesaj specific

**Indicator header:**
- "Export: azi" (verde) | "acum X zile" | "niciodată" (roșu)
- Badge galben dacă > 7 zile, roșu dacă > 14 zile

**Estimare:** ~80 linii JS

---

### M13 — Email Capture (`DSF.email`)
**Ce face:** modal captare email afișat după primul Day Score salvat.

```js
DSF.email = {
  maybeShow(),    // verifică dacă trebuie afișat (o singură dată)
  show(),         // afișează modal
  submit(email),  // trimite la Formspree, salvează config.emailCaptured
  dismiss()       // "Nu acum" — setează flag, nu mai apare
}
```

**Trigger:** apelat din `DSF.anim.revealScore()` după prima intrare
**Condiție afișare:** `!config.emailCaptured && storage.loadAll().length === 1`

**Formspree:**
- POST la `https://formspree.io/f/[FORM_ID]` (placeholder în cod)
- Timeout 5s — dacă fail → `config.set("emailCaptured", true)` oricum
- Niciun mesaj de eroare vizibil dacă offline — aplicația continuă normal

**Estimare:** ~50 linii JS

---

### M14 — Sharing (`DSF.share`)
**Ce face:** distribuire aplicație + copiere rezumat zi.

```js
DSF.share = {
  shareApp(),         // Web Share API cu fallback clipboard
  copyDaySummary(entry) // copiază text formatat în clipboard
}
```

**Rezumat copiat (fără date sensibile ca suma exactă dacă owner nu vrea):**
```
Daily Sales Flash ⚡
Azi: [Vânzări] [Monedă] | Score [X]/100
Target: [✓ depășit / ✗ sub target cu X%]
[link landing page]
```

**Web Share API fallback:** dacă `navigator.share` indisponibil → copiază link în clipboard + toast "Link copiat!"

**Estimare:** ~40 linii JS

---

### M15 — Demo Mode (`DSF.demo`)
**Ce face:** detectează `?demo=true`, încarcă date demo în memorie, afișează banner.

```js
DSF.demo = {
  isActive(),       // → boolean
  loadData(),       // returnează array de 14 intrări demo realiste
  init()            // dacă isActive: patch DSF.storage să citească din demo data
}
```

**Implementare:**
- Detectează `new URLSearchParams(location.search).get("demo")`
- Dacă activ: `DSF.storage.load/loadRange/loadAll` citesc din `DSF.demo.data` (in-memory)
- `DSF.storage.save/delete/clear` → no-op în demo mode (niciodată în localStorage real)
- Banner permanent: "MOD DEMO — datele nu se salvează | Încearcă cu datele tale →"

**Date demo:** 14 zile cu scoruri variate (2 zile roșii, 4 galbene, 6 verzi, 2 gold) + mix de refund-uri și cash variance realist.

**Estimare:** ~60 linii JS

---

### M16 — Settings Screen (`DSF.settings`)
**Ce face:** UI pentru modificarea setărilor.

```js
DSF.settings = {
  render(),          // randează ecranul cu valorile curente
  save(formData)     // validează și salvează config
}
```

**Câmpuri editabile:**
- Prenume
- Target zilnic
- Prag alertă (slider sau input numeric)
- Monedă (select) — cu avertisment dacă există date: "Istoricul tău e în [RON]. Schimbarea afectează afișarea."
- Export JSON (buton)
- Import JSON (buton file input)
- Resetare completă (buton roșu, confirmare dublă)

**Estimare:** ~70 linii JS

---

### M17 — Landing Page (`index.html`)
**Ce face:** pagină de prezentare separată.

**Componente:**
- Hero: headline + sub-headline + CTA descărcare + CTA demo
- 3 carduri beneficii cu iconițe SVG inline
- Mock dashboard animat (CSS animation, nu JS)
- Footer: "Gratuit pentru orice tip de business. Funcționează fără internet."
- Link `app.html` pentru download + `app.html?demo=true` pentru demo

**Nu are logică JS** — CSS pur pentru animații decorative.

**Estimare:** ~250 linii HTML+CSS, ~10 linii JS

---

## Secvența de boot (INIT)

```js
(function init() {
  if (DSF.demo.isActive()) DSF.demo.init();
  if (!DSF.config.get().onboardingDone) {
    DSF.onboard.show();
    return;
  }
  DSF.nav.go("dash");
  DSF.dash.render();
  DSF.backup.updateExportIndicator();
})();
```

---

## Ordine implementare și verificare

| # | Modul | Verificare înainte de a continua |
|---|---|---|
| 1 | M0 Core Shell | HTML complet în DOM, CSS ok, zero erori consolă |
| 2 | M1 Storage Engine | Test manual toate funcțiile în consolă browser |
| 3 | M2 Config Module | `DSF.config.get()` returnează defaults, `set()` persistă |
| 4 | M3 Score Engine | Toate scenariile din tabelul edge cases verificate în consolă |
| 5 | M4 Navigation | Click pe fiecare tab → ecranul corect vizibil |
| 6 | M5 Onboarding | Flow complet: prenume + target → nav to dash |
| 7 | M6 Input Form | Intrare completă, validare refund>sales, mod editare |
| 8 | M7 Dashboard | Toate componentele randează cu date reale |
| 9 | M8 Insights | Mesajele corecte la 1/7/14/28+ zile de date |
| 10 | M9 Animations | Secvența flip + confetti la personal best |
| 11 | M10 Week | Grafic + tabel cu 0, 1, 7 zile de date |
| 12 | M11 History | Grafic + tabel + filtru 7/30/90 |
| 13 | M12 Backup | Export descarcă JSON valid, import restaurează |
| 14 | M13 Email | Modal apare doar după prima intrare, Formspree ok |
| 15 | M14 Sharing | Share API pe mobile, clipboard fallback pe desktop |
| 16 | M15 Demo | `?demo=true` → localStorage virgin, banner vizibil |
| 17 | M16 Settings | Toate câmpurile salvează, avertisment monedă |
| 18 | M17 Landing | CTA-uri funcționale, mock animat, design ok |

---

## Cazuri extreme — test final înainte de deploy

- [ ] Lansare pe device fără nicio dată → onboarding corect
- [ ] Intrare cu vânzări=0 → score=0, mesaj "Zi fără activitate"
- [ ] Intrare retroactivă "Ieri" → data corectă în storage
- [ ] Editare intrare existentă → suprascrie, nu duplică
- [ ] Refund > Vânzări → blocat cu mesaj inline
- [ ] Import JSON corupt → refuzat cu mesaj, datele existente intacte
- [ ] Import JSON din altă aplicație → refuzat (verificare câmp "app")
- [ ] Schimbare monedă cu date existente → avertisment afișat
- [ ] Resetare completă → toate datele șterse, onboarding reapare
- [ ] Demo mode → zero scrieri în localStorage, banner permanent
- [ ] Offline complet (avion mode) → aplicația funcționează 100%
- [ ] Chart.js cu 1 singur punct de date → nu crăpare
- [ ] LocalStorage blocat (Safari private mode) → mesaj de eroare prietenos
- [ ] Streak cu zile lipsă la mijloc → streak resetat corect
- [ ] Confetti → apare DOAR la personal best, nu la orice zi bună

---

## Note implementare

- **Chart.js:** versiunea minificată copiată inline în `<script>` la finalul `app.html`
- **Formspree Form ID:** placeholder `YOUR_FORM_ID` — înlocuit de creator înainte de publicare
- **Landing page link:** placeholder `YOUR_LANDING_URL` în `DSF.share.shareApp()`
- **Creator name/link:** placeholder `[Nume Creator]` în footer app.html
- **Monede acceptate:** `["RON", "EUR", "USD", "GBP"]` — hardcodat în M2
