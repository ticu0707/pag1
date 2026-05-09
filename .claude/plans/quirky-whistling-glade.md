# Plan Implementare StudioFlow v6.0

## Context
StudioFlow este un CRM/BizDev offline-first pentru HERTZ Studio (arhitectură, București). PRD v6.0 este finalizat (2218 linii, 24 gap-uri față de v5.0 rezolvate). Implementarea se face **modul cu modul**, fiecare livrat, testat și comis înainte de a trece la următorul. Stack: Vanilla JS ES6+, IndexedDB, Chart.js bundled, CSS Custom Properties, PWA — zero server, zero npm runtime. Fișiere finale: `app.html` + `offer.html` + `manifest.json` + `sw.js`.

**Principiu arhitectural cheie:** `app.html` este un SPA single-file dar codul JavaScript este organizat în **secțiuni `<script>` separate și etichetate**, fiecare modul fiind independent și testabil în izolare prin DevTools. Fiecare secțiune = max ~300 linii.

---

## Fișiere de creat
```
Desktop/studioflow/
├── app.html        ← Sprint 1–4, construit incremental modul cu modul
├── offer.html      ← Sprint 3, separat pentru print/PDF
├── manifest.json   ← Sprint 1 (stub) → Sprint 4 (final)
├── sw.js           ← Sprint 1 (stub) → Sprint 4 (final)
└── README.txt      ← instrucțiuni first-run (creat la final)
```

---

## Structura internă app.html (secțiuni script)

```html
<!-- Ordinea de inițializare — CRITIC -->
<script id="sf-utils">     <!-- uuid(), formatDate(), daysDiff(), addDays() -->
<script id="sf-db">        <!-- class DB (wrapper 50 linii) + openDB() + MIGRATIONS -->
<script id="sf-state">     <!-- AppState + constante (DEFAULT_SOURCE_RATES etc.) -->
<script id="sf-router">    <!-- ROUTES map + navigate() + hashchange listener -->
<script id="sf-ui">        <!-- showToast(), showConfirmDialog(), showModal(), closeModal() -->
<script id="sf-f8">        <!-- initApp(), backup (auto+manual), SW register, icoane PWA -->
<script id="sf-f0">        <!-- Setup wizard 6 pași + CSV import + importRow() -->
<script id="sf-f2">        <!-- Lead CRUD + scoring live + Go/No-Go + Win Probability -->
<script id="sf-f3">        <!-- Pipeline Kanban render + filtre + stage age -->
<script id="sf-f3-dnd">    <!-- Drag-and-Drop HTML5 (adăugat în Sprint 2) -->
<script id="sf-f1">        <!-- Calculator ARH/INT + Price Intelligence -->
<script id="sf-f4">        <!-- Activity CRUD + Cadence generation + deduplicare -->
<script id="sf-f9">        <!-- Today View + Desktop notifications -->
<script id="sf-f5a">       <!-- Portfolio manager + upload/compress imagini -->
<script id="sf-f5">        <!-- Offer generator + offerCode + revision workflow -->
<script id="sf-f6">        <!-- Client 360 view + LTV + re-engagement -->
<script id="sf-f7">        <!-- Intelligence dashboard (Chart.js 6 panouri) -->
<script id="sf-f10">       <!-- Settings page (7 secțiuni) -->
<script id="sf-export">    <!-- Export JSON + Import JSON + Export CSV leads -->
<script id="sf-shortcuts"> <!-- Keyboard shortcuts global listener -->
<script id="sf-init">      <!-- document.addEventListener('DOMContentLoaded', initApp) -->
```

---

## Sprint 1 — MVP (4 module)

### M1 — HTML Shell + Design System CSS
**Fișier:** `app.html` (schelet)  
**Conținut:**
- HTML structure completă din PRD sec. 2.4 (sidebar nav, topbar, main pages, modal root, toast root)
- CSS Design System complet (PRD sec. 3.1–3.4): `:root` tokens, layout, butoane, badges, cards, inputs, toasts, sidebar, topbar
- Sidebar collapse (60px ↔ 240px) cu `localStorage.sf_sidebar_collapsed`
- Placeholder gol pentru toate `<script>` sections  
**Dimensiune estimată CSS:** ~250 linii | **HTML:** ~80 linii  
**Test:** Deschide în browser → vedere sidebar navy + topbar + pagini goale (hidden) — fără erori JS în console

---

### M2 — sf-utils + sf-db + sf-state + sf-router + sf-ui
**Fișier:** `app.html` (primele 5 secțiuni script)

**sf-utils** (~30 linii):
```javascript
function uuid()           // crypto.randomUUID() cu fallback Math.random
function formatDate(iso)  // "08 mai 2026"
function daysDiff(a, b)   // zile între 2 date
function addDays(date, n) // returnează Date
```

**sf-db** (~70 linii):
- `class DB` — 7 metode Promise-wrapped (PRD sec. 4.3)
- `const CURRENT_VERSION = 1`
- `const MIGRATIONS` — creează toate 8 store-uri + indexuri (PRD sec. 4.14)
- `async function openDB()` — cu onupgradeneeded, onsuccess, onerror, onblocked

**sf-state** (~30 linii):
- `const AppState = { db, backupFolderHandle, currentLeadId, draggedLeadId, searchQuery }`
- `const DEFAULT_SOURCE_RATES` + `const DEFAULT_TYPOLOGY_RATES` (PRD sec. F2)
- `const APP_VERSION = '1.0.0'`

**sf-router** (~25 linii):
- `const ROUTES = { '#today': renderToday, '#pipeline': renderPipeline, ... }`
- `function navigate(route)`
- `window.addEventListener('hashchange', ...)` — activare pagini + nav items

**sf-ui** (~80 linii):
- `function showToast(type, message, durationMs=4000)` — success/warning/error/info, auto-dismiss
- `function showConfirmDialog({ title, message, confirmText, dangerKeyword })` — Promise (PRD sec. 7.3)
- `function showModal(htmlContent, options)` — inject în `#sf-modal-root`
- `function closeModal()`

**Test:** `AppState.db = await openDB()` în DevTools console → succes fără erori. `showToast('success', 'Test')` → toast apare 4s.

---

### M3 — sf-f8 (Foundation: initApp + Backup + PWA)
**Fișier:** `app.html` (secțiunea sf-f8) + `manifest.json` (stub) + `sw.js` (complet)

**sf-f8** (~120 linii):
- `async function initApp()` — openDB → check studio → setup wizard SAU navigate(hash||'#today')
- `function renderSidebarLogo(blob)`, `function renderSidebarStudioName(name)`
- `async function autoBackup()` — File System Access API (PRD sec. F8)
- `function manualExportBackup(data)` — download JSON (fallback)
- `async function selectBackupFolder()` — showDirectoryPicker
- `function updateBackupStatusUI(status, msg)` — indicator sidebar footer
- `function scheduleBackupCheck()` — setInterval la 30 min
- `function registerServiceWorker()` — register + updatefound toast
- `function showFatalError(err)` — PRD sec. 7.1
- `async function exportAllData(db)` — toate store-urile (PRD sec. 6.1)

**manifest.json** (stub):
```json
{ "name": "StudioFlow — HERTZ Studio", "short_name": "StudioFlow",
  "start_url": "./app.html", "display": "standalone",
  "background_color": "#F7F7F5", "theme_color": "#1C3557" }
```

**sw.js** (complet din PRD sec. F8): cache-first + update notification

**sf-init** (~5 linii): `document.addEventListener('DOMContentLoaded', initApp)`

**Test:** Deschide browser → `initApp()` rulează → openDB succes → (fără studio în DB) → pagina setup se afișează. `Ctrl+B` → toast "backup folder necesar".

---

### M4 — sf-f0 (Setup Wizard + CSV Import)
**Fișier:** `app.html` (secțiunea sf-f0), ~280 linii

- `function runSetupWizard()` — render 6 pași full-screen (PRD sec. F0)
- `function renderSetupStep(n)` — switch case 1–6, render HTML per pas
- `async function saveSetupData(formData)` — salvează Studio + default RateCard + default Settings în IndexedDB
- `function compressImage(file, maxKB, maxDim)` — Canvas API, iterativ quality
- `function previewLogo(blob, el)` — DataURL preview
- Pas 5: `async function importCSV(file)` — parse CSV, auto-detect separator (; sau ,), UTF-8 BOM handling
- `function mapSource(raw)` → SOURCE_LOOKUP (PRD sec. F0)
- `async function importRow(row, imported, warnings)` — crea client + lead + offer per rând
- `function showImportReport({ imported, errors, warnings })` — modal cu tabel
- `function parseCSV(text)` — split pe linii, header-uri, returnează array of objects

**Test:** Deschide app proaspăt (fără date) → wizard pornit → completezi Pas 1–4 → Skip import → "Intră în StudioFlow" → navigate '#today'. Alternativ: import CSV real HERTZ → raport import afișat.

---

### M5 — sf-f2 (Lead Capture + Scoring + Go/No-Go)
**Fișier:** `app.html` (secțiunea sf-f2), ~280 linii

- `async function renderLeads()` — pagina Leads cu tabel + filtre + căutare
- `function openNewLeadModal()` — modal formular creare lead (PRD sec. F2)
- `async function saveLead(formData)` — validare + put în IndexedDB + refresh
- `function computeScoreTotal(score)` — sum(14 criterii), max=140
- `function getScoreCategory(total)` — 'hot'/'warm'/'cold'
- `function renderScoringPanel(score, container)` — slider-uri 0–10 per criteriu + total live
- `async function computeGoNoGo(lead, db)` — PRD sec. F2 (cu estimatedEndDate fix)
- `function computeWinProbability(lead, settings, historicalLeads, priceIntelData)` — PRD sec. F2
- `function getWinRateBySource(sourceType, historicalLeads)` — cu DEFAULT fallback
- `function getWinRateByTypology(typology, historicalLeads)` — cu DEFAULT fallback
- `async function deleteLead(id)` — showConfirmDialog → delete lead + offers + activities
- `async function markLeadWon(leadId)` — dialog estimatedEndDate → update status
- `async function markLeadLost(leadId)` — dropdown motiv → update status → triggerDebrief

**Test:** Creare lead nou → panou scoring actualizat live → total + categorie (HOT/WARM/COLD) corecte. Go/No-Go "GO" pentru scor >70, "NOGO" pentru scor <70. Win Probability afișat cu sample size.

---

### M6 — sf-f3 (Pipeline Kanban — fără drag-drop)
**Fișier:** `app.html` (secțiunea sf-f3), ~250 linii

- `async function renderPipeline()` — pagina Pipeline cu header stats + tab Discovery/Design + board
- `function renderKanbanBoard(leads, funnelType, filters)` — 6 coloane per funnel
- `function renderKanbanCard(lead, client)` — card HTML (PRD sec. F3)
- `function getStageAgeClass(lead, avgDaysInStage)` — PRD sec. F3
- `async function calcAvgDaysPerStage(db, funnelType)` — din leads historical
- `function renderKanbanFilters(container)` — score, perioadă, sursă, sort
- `async function moveLead(leadId, newStage)` — update pipelineStage + stageEnteredAt
- `async function handleTerminalStageDrop(leadId, toStage)` — modal Won/Lost/Retras flow
- Buton "Mută ▸" pe card → dropdown stagii (fallback pentru non-DnD)

**Test:** Pipeline afișează leads pe coloane corecte. Mută lead cu buton → stagiu se actualizează. Drop pe "Contractat" → dialog valoare contract + estimatedEndDate. Stage age indicator corect (verde/gri/chihlimbar).

---

## Sprint 2 — v1.5

### M7 — sf-f1 (Calculator ARH/INT + Price Intelligence)
~280 linii: formula H_phase, H_total, Price; UI 2 taburi; ore live per fază; condiții speciale; gamma; 3 prețuri (minim/standard/premium); Price Intelligence overlay; getPricePosition().

### M8 — sf-f4 (Activity Cadence)
~220 linii: Activity CRUD; timeline per lead; generateCadenceActivities() cu deduplicare cadenceStep; CADENCE_TEMPLATES; quick-log modal (shortcut L).

### M9 — sf-f9 (Today View + Notificări)
~180 linii: renderToday() cu 4 secțiuni (întârziate/azi/fără activitate/contractate); checkAndNotify() cu notifiedSet în sessionStorage; PWA App Badge.

### M10 — sf-f3-dnd (Drag-and-Drop pe Kanban existent)
~80 linii: adăugat pe cardurile și coloanele existente din sf-f3; dragstart/dragover/dragleave/drop handlers; AppState.draggedLeadId.

---

## Sprint 3 — v2.0

### M11 — sf-f5a (Portfolio Manager)
~250 linii: grid CSS cu thumbnailBlob; processImage() cu iterative compression; thumbnailBlob 300×200px; drag reordering sortOrder; alertă storage >50MB.

### M12 — sf-f5 + offer.html (Offer Generator + Renderer)
**sf-f5** ~280 linii: wizard 5 pași; generateOfferCode() cu counter monoton; portfolio selection modal; createRevision(); openOfferPreview(); marcaj trimisă + startCadence().  
**offer.html** ~200 linii: loadOffer() cu URL param + sessionStorage fallback; renderOffer() 9 secțiuni; CSS @media print complet.

### M13 — sf-f6 (Client 360)
~180 linii: renderClients() tabel; renderClientDetail() cu 4 KPI cards + timeline deals; alertă re-engagement; rating relație 1–5.

---

## Sprint 4 — v3.0 (Final)

### M14 — sf-f7 (Intelligence Dashboard)
~280 linii: Chart.js 6 panouri (PRD sec. F7); Learning Loop debrief dialog; nudge la n=20/n=50; Export CSV per panou.

### M15 — sf-f10 (Settings complet)
~280 linii: 7 secțiuni (Studio, Scoring, Cadence, Backup, Rate Card, Price Intel, Sistem); slider dual HOT/WARM; sliders pondere Win Probability cu normalizare la 100%.

### M16 — sf-export (Export/Import complet)
~150 linii: exportAllData() + blobToBase64() + base64ToBlob(); importFromBackup() cu validare + confirmare "RESTAUREAZĂ"; exportLeadsCSV() cu BOM UTF-8.

### M17 — sf-shortcuts (Keyboard Shortcuts)
~60 linii: global keydown listener; keyMap N/L/Escape/1–9/?; Ctrl+S/B; dezactivat pe input/textarea.

### M17-PWA — manifest.json final + icoane
Adăugare icoane 192px + 512px generate din logo via Canvas API. manifest.json complet cu toate câmpurile.

---

## Reguli de implementare (non-negociabile)

1. **Un modul pe rând** — implementăm M1 → test → commit → M2 → test → commit etc.
2. **Max ~300 linii per secțiune script** — dacă depășește, se rupe în sub-secțiuni
3. **Fiecare modul testabil fără cel următor** — M3 funcționează fără M4, M5 fără M6 etc.
4. **Test în browser după fiecare modul** — DevTools console deschis, zero erori JS
5. **Commit după fiecare modul funcțional** — nu comitem cod broken
6. **Niciodată decrementat `lastOfferCodeSeq`** — counter monoton
7. **`backupFolderHandle` NICIODATĂ în IndexedDB** — doar AppState
8. **INT special conditions** — marcate vizibil în UI "⚠ Estimat — verificați față de Calculator Excel"

---

## Verificare end-to-end (după Sprint 1 MVP)

1. Deschide `app.html` → Setup Wizard apare (pagina goală)
2. Completează 6 pași → "Intră în StudioFlow" → Today View gol
3. Creare lead nou (shortcut N) → scoring live → Go/No-Go + Win%
4. Lead apare în Pipeline Kanban pe coloana corectă
5. Mută lead cu buton → stagiu actualizat, stageEnteredAt setat
6. Drop pe "Contractat" → dialog → lead.status = 'won'
7. Ctrl+B → selectează folder → backup JSON creat în folder
8. Reload pagina → app repornit cu datele existente (nu setup wizard)
9. DevTools > Application > IndexedDB > studioflow → toate 8 store-urile vizibile

## Locație fișiere
- Folder de lucru: `C:\Users\admin\Desktop\studioflow\`
- PRD de referință: `C:\Users\admin\Desktop\StudioFlow PRD v6.0.md`
