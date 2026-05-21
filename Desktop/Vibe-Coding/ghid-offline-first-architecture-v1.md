# Ghid Offline-First Architecture pentru Vibe-Coding
**LocalStorage · SessionStorage · IndexedDB · Service Workers · PWA · File System Access API**
v1.1 | Stack: HTML/JS Vanilla · Next.js 14 App Router · Chrome/Edge · Windows 10

> **De ce contează:** Jumătate din portofoliul tău (CashPulse, FollowUp Board, PurchaseCompare,
> Reorder Radar, InvoiceChaser, Daily Sales Flash, MenuMix Matrix, StudioFlow) rulează complet
> offline. Bug-urile recurente — date pierdute la refresh, JSON corupt, 5MB exceeded silențios,
> tab care blochează upgrade-ul bazei de date — au o singură cauză: lipsa unui model mental clar
> despre *ce* stochezi *unde* și *cum*. Ghidul ăsta fixează asta definitiv.

---

## Walkthrough — De la HTML Static la PWA Funcțională în 15 Pași

Flow complet, end-to-end. Împărțit în 3 grupe progresive — citești grupa relevantă
pentru stadiul actual al proiectului.

### Grupa 1 — Persistență de bază (Pași 1–5): pentru orice HTML static

```javascript
// Pas 1 — Date în memorie (se pierd la refresh — punctul de start)
const items = [{ id: 1, name: 'Produs', qty: 5 }];

// Pas 2 — Persistă în localStorage (supraviețuiesc refresh)
localStorage.setItem('items', JSON.stringify(items));
const loaded = JSON.parse(localStorage.getItem('items') ?? '[]');

// Pas 3 — Schema versioning (previne bug-uri la update)
const STORAGE_VERSION = 1;
function initStorage(migrations = {}) {
  const saved = Number(localStorage.getItem('_schema_version') ?? 0);
  for (let v = saved + 1; v <= STORAGE_VERSION; v++) {
    if (migrations[v]) migrations[v]();
  }
  localStorage.setItem('_schema_version', String(STORAGE_VERSION));
}

// Pas 4 — Wrapper cu error handling (QuotaExceededError)
function save(key, value) {
  try {
    localStorage.setItem(key, JSON.stringify(value));
    return true;
  } catch (e) {
    if (e.name === 'QuotaExceededError') alert('Spațiu de stocare plin.');
    return false;
  }
}
function load(key, defaultValue = null) {
  try {
    const raw = localStorage.getItem(key);
    return raw !== null ? JSON.parse(raw) : defaultValue;
  } catch { return defaultValue; }
}

// Pas 5 — SessionStorage pentru stare temporară per tab
sessionStorage.setItem('step2_draft', JSON.stringify(formData));
```

### Grupa 2 — Date structurate + offline garantat (Pași 6–9)

```javascript
// Pas 6 — IndexedDB cu Dexie.js (când depășești 500 records)
// IMPORTANT: declari ÎNTOTDEAUNA toate stores în fiecare version()
import Dexie from 'dexie';  // Next.js/bundler
// HTML Vanilla cu CDN: Dexie e global — vezi Parte 6
const db = new Dexie('MyApp');
db.version(1).stores({ items: '++id, name, category, createdAt' });
await db.items.add({ name: 'Produs', category: 'A', createdAt: Date.now() });

// Pas 7 — StorageManager: ceri persistența datelor (nu fi evictat de browser)
async function initPersistentStorage() {
  if (!navigator.storage?.persist) return false;
  const granted = await navigator.storage.persist();
  console.log('Persistent storage:', granted ? 'garantat' : 'best-effort');
  return granted;
}
await initPersistentStorage();  // la startup, o singură dată

// Pas 8 — Service Worker: înregistrare coordonată (nu skipWaiting fără avertizare)
if ('serviceWorker' in navigator) {
  const reg = await navigator.serviceWorker.register('/sw.js');
  reg.addEventListener('updatefound', () => {
    reg.installing?.addEventListener('statechange', () => {
      if (reg.installing?.state === 'installed' && navigator.serviceWorker.controller) {
        showUpdateBanner();  // "Versiune nouă disponibilă — Actualizează"
      }
    });
  });
}

// Pas 9 — Indicator online/offline
window.addEventListener('online',  () => showBanner('Conexiune restabilită ✓', 'green'));
window.addEventListener('offline', () => showBanner('Offline — datele se salvează local', 'orange'));
// navigator.onLine e hint, nu garanție — vezi Parte 11 pentru verificare reală
```

### Grupa 3 — PWA completă (Pași 10–15)

```javascript
// Pas 10 — manifest.json în rădăcina proiectului (HTTPS sau localhost obligatoriu)
// { "name": "MyApp", "short_name": "App", "start_url": "/", "display": "standalone",
//   "theme_color": "#1a1a2e",
//   "icons": [
//     {"src":"icon-192.png","sizes":"192x192","type":"image/png","purpose":"any"},
//     {"src":"icon-512.png","sizes":"512x512","type":"image/png","purpose":"any"},
//     {"src":"icon-512-maskable.png","sizes":"512x512","type":"image/png","purpose":"maskable"}
//   ] }

// Pas 11 — Link manifest în HTML
// <link rel="manifest" href="/manifest.json">
// <meta name="theme-color" content="#1a1a2e">

// Pas 12 — sw.js — Cache First pentru assets statice
const CACHE_NAME = 'myapp-v1';
const PRECACHE = ['/', '/index.html', '/app.js', '/style.css', '/manifest.json'];
self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE_NAME).then(c => c.addAll(PRECACHE)));
  // NU apelezi skipWaiting() automat în producție — vezi Parte 7
});

// Pas 13 — Background Sync cu fallback obligatoriu (Chrome/Edge ~60% din browsere)
const reg = await navigator.serviceWorker.ready;
if ('sync' in reg) {
  await reg.sync.register('sync-pending');
} else {
  window.addEventListener('online', () => processQueue(), { once: true });
}

// Pas 14 — File System Access API — export CSV (HTTPS sau localhost obligatoriu)
async function exportCSV(data, filename = 'export.csv') {
  if (!('showSaveFilePicker' in window)) return exportFallback(data, filename, 'text/csv');
  try {
    const handle = await window.showSaveFilePicker({
      suggestedName: filename,
      types: [{ description: 'CSV', accept: { 'text/csv': ['.csv'] } }]
    });
    const writable = await handle.createWritable();
    await writable.write(convertToCSV(data));
    await writable.close();
  } catch (e) {
    if (e.name !== 'AbortError') throw e;
  }
}

// Pas 15 — Testare offline
// Application → Service Workers → ✓ "Update on reload" (dev)
// Network → Offline → refresh → verifici că app-ul funcționează
// Application → Clear site data → resetezi tot
```

---

## BLOC 1 — Storage Fundamentals

### Parte 0 — Mental Model: 4 Tipuri de Storage Comparate

| | localStorage | sessionStorage | IndexedDB | Cache API |
|---|---|---|---|---|
| **Capacitate** | ~5 MB | ~5 MB | Zeci de GB | Zeci de GB |
| **Durată** | Permanent | Tab session | Permanent* | Permanent* |
| **Tip date** | String only | String only | Orice (objects, Blob, ArrayBuffer) | Request/Response |
| **API** | Sincron (blocking) | Sincron (blocking) | Asincron | Asincron |
| **Acces** | Orice tab pe același origin | Doar tab-ul curent | Orice tab, Service Worker | Pagini + Service Worker |
| **Web Workers** | NU | NU | DA | DA |
| **Use case** | Setări, preferințe, small JSON | Form draft, wizard, temp state | Date structurate mari, offline DB | Assets statice, API responses |

*\*Browserele pot evicta IndexedDB și Cache API la low storage fără `navigator.storage.persist()` — vezi Parte 4.*

**Regula de bază:**
- Sub 500 records, date simple → **localStorage**
- Stare temporară per tab → **sessionStorage**
- Date structurate mari, query-uri, fișiere → **IndexedDB**
- Caching assets și HTTP responses → **Cache API** (via Service Worker)

---

### Parte 1 — LocalStorage: API Complet, Limite și Capcane

#### API de bază

```javascript
localStorage.setItem('user', JSON.stringify({ name: 'Ion', role: 'admin' }));
localStorage.setItem('theme', 'dark');

const user  = JSON.parse(localStorage.getItem('user'));
const theme = localStorage.getItem('theme');

localStorage.removeItem('user');
localStorage.clear();

for (let i = 0; i < localStorage.length; i++) {
  const key   = localStorage.key(i);
  const value = localStorage.getItem(key);
}
```

#### Capcanele Comune

**Capcana 1 — getItem returnează `null`, nu `undefined`**

```javascript
// GREȘIT — '||' tratează "0" și "" ca falsy
const count = localStorage.getItem('count') || 0;

// CORECT
const count = Number(localStorage.getItem('count') ?? '0');
```

**Capcana 2 — JSON.stringify pe tipuri speciale**

```javascript
// GREȘIT — stochează "[object Object]"
localStorage.setItem('data', myObject);

// GREȘIT — Date devine string ISO, Map/Set devin {}
localStorage.setItem('date', JSON.stringify(new Date()));

// CORECT
localStorage.setItem('date', new Date().toISOString());
const date = new Date(localStorage.getItem('date'));
```

**Capcana 3 — QuotaExceededError silențios**

```javascript
function save(key, value) {
  try {
    localStorage.setItem(key, JSON.stringify(value));
    return { ok: true };
  } catch (error) {
    if (error.name === 'QuotaExceededError') return { ok: false, reason: 'quota_exceeded' };
    throw error;
  }
}
```

**Capcana 4 — API sincron blocking pe date mari**

localStorage blochează main thread-ul la stringify/parse.
Pe array-uri cu 5000+ items → UI freeze de 50–100ms.

```javascript
// Salvezi incremental, nu tot array-ul dintr-o dată
function saveItem(id, item) {
  const items = load('items', {});
  items[id] = item;
  save('items', items);
}
```

#### Pattern Recomandat: Modulul storage.js

```javascript
const STORAGE_VERSION = 1;

// PREFIX — prefixezi toate cheile cu numele app-ului
// Dacă ai mai multe app-uri pe același origin (localhost dev, Netlify multi-app),
// cheile fără prefix se ciocnesc silențios. Conventia: 'APPNAME.key'
const PREFIX = 'cashpulse.';

const storage = {
  init(migrations = {}) {
    const saved = Number(localStorage.getItem(PREFIX + '_schema_version') ?? 0);
    if (saved < STORAGE_VERSION) {
      for (let v = saved + 1; v <= STORAGE_VERSION; v++) {
        if (migrations[v]) migrations[v]();
      }
      localStorage.setItem(PREFIX + '_schema_version', String(STORAGE_VERSION));
    }
  },

  get(key, defaultValue = null) {
    try {
      const raw = localStorage.getItem(PREFIX + key);
      return raw !== null ? JSON.parse(raw) : defaultValue;
    } catch { return defaultValue; }
  },

  set(key, value) {
    try {
      localStorage.setItem(PREFIX + key, JSON.stringify(value));
      return true;
    } catch (e) {
      if (e.name === 'QuotaExceededError') console.error('Storage plin:', key);
      return false;
    }
  },

  remove(key) { localStorage.removeItem(PREFIX + key); },

  sizeKB() {
    // Calcul aproximativ (UTF-16, 2 bytes/char) — include atât chei cât și valori
    let total = 0;
    for (let i = 0; i < localStorage.length; i++) {
      const k = localStorage.key(i) ?? '';
      total += k.length + (localStorage.getItem(k) ?? '').length;
    }
    return (total * 2 / 1024).toFixed(1);
  }
};

storage.init({
  1: () => {
    const old = storage.get('todos');
    if (old) { storage.set('tasks', old); storage.remove('todos'); }
  }
});
```

#### Sincronizare între Tab-uri — `storage` event vs `BroadcastChannel`

**`storage` event** — varianta clasică:

```javascript
// Se declanșează în ALTE tab-uri pe același origin, NU în cel care a scris
// Nu funcționează în Service Workers sau Web Workers
window.addEventListener('storage', (event) => {
  if (event.key === PREFIX + 'tasks') renderTasks(JSON.parse(event.newValue ?? '[]'));
  if (event.key === null) resetApp();  // localStorage.clear() apelat
});
```

**`BroadcastChannel`** — varianta modernă (recomandat):

```javascript
// Funcționează: tab→tab, iframe→tab, SW→pagini (toate contextele în același origin)
// Nu necesită o schimbare în storage — poți trimite orice mesaj
// Suport: Chrome 54+, Firefox 38+, Safari 15.4+ (2021)
const channel = new BroadcastChannel('studioflow-sync');

// Emițător (orice context)
channel.postMessage({ type: 'CLIENT_UPDATED', clientId: 42 });

// Receptor (orice alt context)
channel.addEventListener('message', (event) => {
  if (event.data.type === 'CLIENT_UPDATED') refreshClient(event.data.clientId);
});

// Cleanup când pagina se închide
window.addEventListener('beforeunload', () => channel.close());
```

`BroadcastChannel` e preferabil atunci când:
- Nu ai nevoie de persistență (vrei doar să notifici alte tab-uri)
- Vrei să notifici de la Service Worker la pagini
- Ai `storage` event care nu se declanșează (Web Workers)

---

### Parte 2 — SessionStorage: Scope Tab și Use Cases

**Diferențe față de localStorage:**
- Izolat per tab — același URL în tab nou → sessionStorage gol
- Se șterge la închiderea tab-ului (nu la navigare în același tab)
- Duplicate tab (Ctrl+T) → copiază sessionStorage la momentul duplicării
- API identic cu localStorage

```javascript
// 1 — Wizard multi-step
sessionStorage.setItem('wizard_step', '2');
sessionStorage.setItem('wizard_data', JSON.stringify({ name: 'Ion' }));

// 2 — Stare filtre (se resetează la sesiune nouă — intentionat)
sessionStorage.setItem('active_filter', 'category_A');

// 3 — PurchaseCompare: date comparație temporare per sesiune
sessionStorage.setItem('products_for_compare', JSON.stringify(selected));

// 4 — Draft form cu expirare
function saveDraft(formData) {
  sessionStorage.setItem('form_draft', JSON.stringify({
    data: formData, savedAt: Date.now()
  }));
}
function loadDraft() {
  const draft = sessionStorage.getItem('form_draft');
  if (!draft) return null;
  const { data, savedAt } = JSON.parse(draft);
  if (Date.now() - savedAt > 30 * 60 * 1000) {
    sessionStorage.removeItem('form_draft');
    return null;
  }
  return data;
}
```

---

### Parte 3 — Decision Matrix: Când Folosești Ce

```
ÎNTREBARE 1: Datele trebuie să persiste după închiderea browserului?
  NU  → sessionStorage
  DA  → continuă →

ÎNTREBARE 2: Câte records ai sau estimezi că vei avea?
  < 500 records, < 1MB, fără query-uri complexe  → localStorage
  > 500 records SAU > 1MB SAU Blob/fișiere        → IndexedDB
  HTTP responses, assets statice (CSS/JS/img)      → Cache API (via SW)

ÎNTREBARE 3: Aplicația are animații sau rendering frecvent?
  DA și > 200 records  → IndexedDB (async, nu blochează main thread)
  NU sau date mici     → localStorage rămâne ok
```

**Mapping pe proiectele tale:**

| Proiect | Storage actual | Potrivit? | Notă |
|---|---|---|---|
| CashPulse | localStorage | ✓ | La 2000+ tranzacții → IndexedDB |
| FollowUp Board | localStorage | ✓ | La 1000+ contacte → IndexedDB |
| PurchaseCompare | sessionStorage | ✓ | Date temporare per sesiune — corect |
| Reorder Radar | localStorage | ✓ | Inventar mic — ok |
| MenuMix Matrix | sessionStorage | ✓ | Date upload per sesiune — corect |
| StudioFlow (planificat) | IndexedDB | ✓ | CRM cu sute de clienți/proiecte |

---

## BLOC 2 — IndexedDB

### Parte 4 — Concepte: Database, Object Store, Transaction, Index, onblocked

**Mental model:**

```
Database "StudioFlow"
  └── Object Store "clients"
  │     ├── keyPath: "id"        (cheie primară auto-increment)
  │     ├── index: "email"       (căutare rapidă după email)
  │     └── records: [{ id, name, email, phone }, ...]
  │
  └── Object Store "projects"
        ├── keyPath: "id"
        ├── index: "clientId"
        └── records: [{ id, clientId, title, status }, ...]
```

**Version: regula critică**

```javascript
// Incrementezi la orice schimbare de schemă — NICIODATĂ nu micșorezi
const DB_VERSION = 1;  // v2 la store nou, v3 la index nou
```

**onblocked — capcanele multi-tab (critic pentru StudioFlow)**

Scenariul real: userul are StudioFlow în Tab A (DB v1). Deployezi v2.
Tab B încearcă upgrade → blocat pe termen nedefinit de Tab A.
App-ul pare înghețat fără nicio eroare vizibilă.

```javascript
function openDB(name, version) {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open(name, version);

    request.onupgradeneeded = (event) => {
      const db = event.target.result;
      if (!db.objectStoreNames.contains('clients')) {
        const store = db.createObjectStore('clients', {
          keyPath: 'id', autoIncrement: true
        });
        store.createIndex('email', 'email', { unique: true });
        store.createIndex('status', 'status', { unique: false });
      }
    };

    request.onblocked = () => {
      alert(
        'Aplicația are o versiune nouă dar un alt tab o ține blocată.\n' +
        'Închide celelalte tab-uri cu această aplicație și reîncarcă pagina.'
      );
    };

    request.onsuccess = () => {
      const db = request.result;
      setupVersionChangeHandler(db);  // OBLIGATORIU — atașezi handler-ul
      resolve(db);
    };
    request.onerror  = () => reject(request.error);
  });
}

// Pe conexiunea existentă — ascultă versionchange și eliberează lock-ul
function setupVersionChangeHandler(db) {
  db.onversionchange = () => {
    db.close();
    alert('Aplicația a fost actualizată. Pagina se reîncarcă...');
    window.location.reload();
  };
}
```

**StorageManager — Persistența datelor (obligatoriu pentru StudioFlow)**

Browserele pot **evicta** (șterge automat) IndexedDB la low storage, fără avertisment.

```javascript
async function initPersistentStorage() {
  // navigator.storage nu există în browsere foarte vechi sau în unele WebViews
  if (!navigator.storage?.persist) {
    console.warn('StorageManager nedisponibil — date în modul best-effort');
    return { persistent: false, usedMB: 0, quotaMB: 0 };
  }

  const isPersisted = await navigator.storage.persisted();
  if (!isPersisted) {
    const granted = await navigator.storage.persist();
    // Chrome: afișează prompt dacă PWA e instalată sau site bookmarked
    // Firefox: returnează true automat dacă userul nu a blocat
    // Safari/iOS: returnează false — persist() nu e implementat pe iOS
    //   → pe iOS, datele pot fi evictate; backup manual e singura soluție reală
    if (!granted) {
      console.warn('Persistent storage neacordat (iOS Safari sau permisiune refuzată)');
    }
  }

  const { usage, quota } = await navigator.storage.estimate();
  const usedMB  = Number((usage  / 1024 / 1024).toFixed(1));
  const quotaMB = Number((quota  / 1024 / 1024).toFixed(0));
  console.log(`Storage: ${usedMB}MB din ~${quotaMB}MB disponibil`);

  return { persistent: isPersisted, usedMB, quotaMB };
}
```

---

### Parte 5 — CRUD Nativ cu IndexedDB

API nativ e verbose. Util să înțelegi conceptele; în practică folosești Dexie.js.

```javascript
async function addItem(db, item) {
  return new Promise((resolve, reject) => {
    const tx = db.transaction('items', 'readwrite');
    const req = tx.objectStore('items').add({ ...item, createdAt: Date.now() });
    req.onsuccess = () => resolve(req.result);
    req.onerror  = () => reject(req.error);
  });
}

async function getItem(db, id) {
  return new Promise((resolve, reject) => {
    const tx  = db.transaction('items', 'readonly');
    const req = tx.objectStore('items').get(id);
    req.onsuccess = () => resolve(req.result ?? null);
    req.onerror  = () => reject(req.error);
  });
}

async function getAllItems(db) {
  return new Promise((resolve, reject) => {
    const tx  = db.transaction('items', 'readonly');
    const req = tx.objectStore('items').getAll();
    req.onsuccess = () => resolve(req.result);
    req.onerror  = () => reject(req.error);
  });
}

async function updateItem(db, item) {
  return new Promise((resolve, reject) => {
    const tx  = db.transaction('items', 'readwrite');
    const req = tx.objectStore('items').put(item);
    req.onsuccess = () => resolve(req.result);
    req.onerror  = () => reject(req.error);
  });
}

async function deleteItem(db, id) {
  return new Promise((resolve, reject) => {
    const tx  = db.transaction('items', 'readwrite');
    const req = tx.objectStore('items').delete(id);
    req.onsuccess = () => resolve();
    req.onerror  = () => reject(req.error);
  });
}

async function getByCategory(db, category) {
  return new Promise((resolve, reject) => {
    const tx    = db.transaction('items', 'readonly');
    const index = tx.objectStore('items').index('category');
    const req   = index.getAll(category);
    req.onsuccess = () => resolve(req.result);
    req.onerror  = () => reject(req.error);
  });
}
```

**Capcana tranzacțiilor expirate:**

```javascript
// GREȘIT — tranzacția expiră la primul await extern
const tx = db.transaction('clients', 'readwrite');
await someOtherAsyncOperation();  // ← expiră aici
tx.objectStore('clients').add(data);  // EROARE: transaction has finished

// CORECT — toate operațiile consecutive, fără await intermediar
const tx = db.transaction('clients', 'readwrite');
const store = tx.objectStore('clients');
store.add(client1);
store.add(client2);
await new Promise((resolve, reject) => {
  tx.oncomplete = resolve;
  tx.onerror    = () => reject(tx.error);
});
```

---

### Parte 6 — Dexie.js: Wrapper Recomandat

**Versiune și instalare:**

```html
<!-- HTML Vanilla — Dexie e global după <script> tag, fără import -->
<script src="https://unpkg.com/dexie@3/dist/dexie.js"></script>
<!-- SAU versiune exactă pentru reproducibilitate -->
<script src="https://unpkg.com/dexie@3.2.7/dist/dexie.js"></script>
```

```javascript
// HTML Vanilla cu CDN — Dexie e variabilă globală, nu ai nevoie de import
const db = new Dexie('MyApp');
```

```bash
# Next.js / bundler — instalezi ca pachet
npm install dexie

# Dexie 4.x (2024+) e compatibil cu codul din ghid pentru CRUD de bază
# Diferența principală față de v3: liveQuery îmbunătățit + TypeScript mai strict
# Dacă primești erori de tip la upgrade v3→v4, verifici signature-urile din changelog
```

```javascript
// Next.js / bundler — import explicit
import Dexie from 'dexie';
```

**Setup și schemă:**

```javascript
// db.js — definit o singură dată, importat oriunde ai nevoie
const db = new Dexie('StudioFlow');

db.version(1).stores({
  clients:  '++id, name, email, &phone, status',
  projects: '++id, clientId, title, status, createdAt',
  tasks:    '++id, projectId, status, dueDate'
});

// ─────────────────────────────────────────────────────────────────
// ⚠ REGULĂ CRITICĂ: declari TOATE stores la fiecare db.version()
//   Stores omise din versiunea nouă sunt ȘTERSE automat de Dexie.
//   Aceasta e cauza #1 de pierdere accidentală de date cu Dexie.js.
// ─────────────────────────────────────────────────────────────────
db.version(2).stores({
  clients:  '++id, name, email, &phone, status, city', // adăugat: city
  projects: '++id, clientId, title, status, createdAt', // NESCHIMBAT — obligatoriu
  tasks:    '++id, projectId, status, dueDate'          // NESCHIMBAT — obligatoriu
}).upgrade(tx => {
  return tx.table('clients').toCollection().modify(client => {
    client.city = client.city ?? '';
  });
});

// versionchange — deblochează upgrade-ul din alt tab
// ⚠ Pe iOS Safari, versionchange nu se declanșează fiabil.
//   Pe iOS, strategia multi-tab e best-effort — nu te poți baza pe reload automat.
db.on('versionchange', () => {
  db.close();
  alert('Versiune nouă disponibilă. Pagina se reîncarcă...');
  window.location.reload();
});

export default db;
```

**`[Next.js App Router]` — IndexedDB nu există pe server:**

```javascript
// IMPORTANT: IndexedDB e browser-only.
// Dacă importezi db.js într-un Server Component → crash la build sau runtime.

// Soluție 1 — marchezi orice fișier care importă db.js
'use client'

// Soluție 2 — guard explicit (pentru hooks sau utils shared)
if (typeof window === 'undefined') return;

// Soluție 3 — import dinamic (lazy, doar în browser)
const { default: db } = await import('./db.js');
```

**CRUD cu Dexie:**

```javascript
import db from './db.js';

// ADD
const newId = await db.clients.add({
  name: 'Ion Popescu', email: 'ion@example.com',
  phone: '0722000000', status: 'active', city: 'București'
});

// GET
const client = await db.clients.get(1);          // undefined dacă nu există
const all    = await db.clients.toArray();

// UPDATE
await db.clients.put({ id: 1, name: 'Ion', status: 'inactive', city: 'Cluj' }); // upsert complet
await db.clients.update(1, { status: 'inactive' });                               // parțial

// DELETE
await db.clients.delete(1);

// QUERY
const active = await db.clients.where('status').equals('active').toArray();
const multi  = await db.clients.where('status').anyOf(['active', 'prospect']).toArray();
const recent = await db.projects
  .where('createdAt').above(Date.now() - 30 * 24 * 60 * 60 * 1000).toArray();
const custom = await db.projects
  .filter(p => p.clientId === 5 && p.status !== 'archived').toArray();

// JOIN manual
async function getProjectsWithClients() {
  const projects   = await db.projects.toArray();
  const clientIds  = [...new Set(projects.map(p => p.clientId))];
  const clients    = await db.clients.where('id').anyOf(clientIds).toArray();
  const clientMap  = Object.fromEntries(clients.map(c => [c.id, c]));
  return projects.map(p => ({ ...p, client: clientMap[p.clientId] ?? null }));
}

// TRANZACȚIE atomică
await db.transaction('rw', db.projects, db.tasks, async () => {
  const projectId = await db.projects.add({ title: 'Proiect nou', clientId: 1 });
  await db.tasks.bulkAdd([
    { projectId, title: 'Task 1', status: 'todo' },
    { projectId, title: 'Task 2', status: 'todo' }
  ]);
  // Oricare operație eșuează → totul rollback automat
});

// COUNT
const total  = await db.clients.count();
const active = await db.clients.where('status').equals('active').count();

// BULK — BulkError pentru duplicate keys (nu e Error generic)
try {
  await db.clients.bulkAdd(arrayOfClients);
} catch (error) {
  if (error.name === 'BulkError') {
    // error.failures = array de erori per record eșuat
    // Restul records au fost adăugate cu succes — BulkError nu rollback-ează
    console.error(`${error.failures.length} records au eșuat:`, error.failures);
  } else {
    throw error;
  }
}

await db.clients.bulkPut(arrayToUpsert);
await db.clients.bulkDelete(arrayOfIds);
await db.clients.clear();
```

**Citiri paralele — `Promise.all` (esențial pentru performanță)**

```javascript
// LENT — 3 citiri secvențiale (sumă de timpi)
const clients  = await db.clients.toArray();
const projects = await db.projects.toArray();
const tasks    = await db.tasks.toArray();

// RAPID — 3 citiri în paralel (max din timpi, nu sumă)
const [clients, projects, tasks] = await Promise.all([
  db.clients.toArray(),
  db.projects.toArray(),
  db.tasks.toArray()
]);

// Cu filtre combinate
const [activeClients, openProjects] = await Promise.all([
  db.clients.where('status').equals('active').toArray(),
  db.projects.where('status').equals('open').toArray()
]);
```

**Paginare și iterare mare volum (>1000 records)**

```javascript
// PROBLEMĂ: toArray() pe 10k records → toate în memorie → OOM posibil
const all = await db.clients.toArray();  // nu face asta pe volume mari

// CORECT — paginare cu limit/offset
const PAGE_SIZE = 50;
async function getPage(page = 0) {
  return db.clients
    .orderBy('name')
    .offset(page * PAGE_SIZE)
    .limit(PAGE_SIZE)
    .toArray();
}

// Iterare cu each() — procesezi record cu record, fără a încărca totul în memorie
await db.clients.each(client => {
  processClient(client);  // e chemat sincron per record
});

// Iterare cu filtru — eficient pentru export CSV pe date mari
await db.clients
  .where('status').equals('active')
  .each(client => csvRows.push(toRow(client)));
```

**liveQuery — UI reactiv la schimbări IndexedDB**

```javascript
// liveQuery re-rulează automat query-ul când datele se schimbă
// Returneaza un Observable (subscribe/unsubscribe pattern)
// Dexie 3.x+: disponibil în pachetul dexie

// HTML Vanilla cu CDN:
const { liveQuery } = Dexie;

// Next.js / bundler:
import { liveQuery } from 'dexie';

// Exemplu: lista de clienți care se actualizează live la orice modificare
const subscription = liveQuery(
  () => db.clients.where('status').equals('active').toArray()
).subscribe({
  next: clients => renderClientList(clients),
  error: err => console.error('LiveQuery error:', err)
});

// Cleanup la unmount (React) sau la părăsirea paginii
// React: return () => subscription.unsubscribe();
window.addEventListener('beforeunload', () => subscription.unsubscribe());

// liveQuery cu React hook:
// npm install dexie-react-hooks
import { useLiveQuery } from 'dexie-react-hooks';
function ClientList() {
  const clients = useLiveQuery(
    () => db.clients.where('status').equals('active').toArray()
  );
  if (!clients) return <div>Loading...</div>;
  return clients.map(c => <div key={c.id}>{c.name}</div>);
}
```

---

## BLOC 3 — Service Workers & Cache API

### Parte 7 — Service Worker Lifecycle

**Ce este un Service Worker:**
Un fișier JavaScript care rulează într-un thread separat (fără acces la DOM),
interceptează toate request-urile rețelei din origin.
**Funcționează DOAR pe HTTPS sau localhost** — pe `http://` sau `file://` nu se înregistrează.

**Lifecycle:**

```
Register → Download → Install → [Waiting] → Activate → Idle → Fetch events
                                    ↑
                    (altă conexiune activă — onblocked între tabs)
```

**Service Worker scope — unde pui sw.js contează:**

```
sw.js plasat la /sw.js          → controlează tot origin-ul (/, /app/, /landing/, etc.)
sw.js plasat la /app/sw.js      → controlează DOAR /app/* (landing.html la / nu e protejat)
sw.js plasat la /sub/path/sw.js → controlează DOAR /sub/path/*

Exemplu FollowUp Board:
  index.html   la /
  landing.html la /
  sw.js        la / (rădăcină) → ambele pagini primesc SW

Regulă: pentru HTML static cu multiple pagini la nivel root → sw.js la rădăcină.
```

**sw.js complet cu versioning și coordonare corectă:**

```javascript
const CACHE_VERSION = 'v1';
const CACHE_NAME    = `myapp-${CACHE_VERSION}`;

// [HTML static] — listezi manual; [Next.js] — generezi cu workbox-build / next-pwa
const PRECACHE_ASSETS = [
  '/', '/index.html', '/landing.html',
  '/app.js', '/style.css', '/manifest.json',
  '/icon-192.png', '/icon-512.png'
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(c => c.addAll(PRECACHE_ASSETS))
    // NU apelezi self.skipWaiting() automat — vezi avertismentul de mai jos
  );
});

self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys()
      .then(names => Promise.all(
        names
          .filter(n => n.startsWith('myapp-') && n !== CACHE_NAME)
          .map(n => caches.delete(n))
      ))
      // clients.claim() face SW-ul să preia IMEDIAT paginile deja deschise fără SW.
      // Acele pagini nu au trecut prin Install/Activate → pot primi din cache
      // resurse pe care le-au încărcat deja din rețea → potențial mismatch.
      // Safe dacă SW-ul servește același conținut ca rețeaua în acel moment.
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', event => {
  if (event.request.method !== 'GET') return;
  if (!event.request.url.startsWith(self.location.origin)) return;
  event.respondWith(handleFetch(event.request));
});

async function handleFetch(request) {
  const cached = await caches.match(request);
  if (cached) return cached;
  try {
    const response = await fetch(request);
    if (response.ok) {
      const cache = await caches.open(CACHE_NAME);
      // clone() ÎNAINTE de return și cache.put() — response e stream read-once.
      // Dacă faci response.json() sau response.text() înainte de clone() → clone gol.
      cache.put(request, response.clone());
    }
    return response;
  } catch {
    return caches.match('/index.html') ??
      new Response('Offline', { status: 503 });
  }
}

// Primești mesajul de la pagină pentru update coordonat
self.addEventListener('message', event => {
  if (event.data?.type === 'SKIP_WAITING') self.skipWaiting();
});
```

**⚠ `skipWaiting()` automat în install — anti-pattern în producție**

```javascript
// PROBLEMA cu skipWaiting() automat:
// Tab A rulează cu SW v1 activ.
// SW v2 se instalează și apelează skipWaiting() fără confirmare.
// SW v2 preia controlul imediat.
// Tab A e acum controlat de SW v2 deși a fost încărcat cu assets din SW v1.
// Rezultat: Tab A poate servi un mix de resurse v1+v2 → crash sau comportament impredictibil.

// CORECT — coordonezi prin postMessage (în main.js al paginii)
async function setupSWUpdate() {
  if (!('serviceWorker' in navigator)) return;
  const registration = await navigator.serviceWorker.register('/sw.js');

  registration.addEventListener('updatefound', () => {
    const newWorker = registration.installing;
    newWorker?.addEventListener('statechange', () => {
      if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
        showUpdateBanner();  // "Versiune nouă — Actualizează acum"
      }
    });
  });

  // Reload după ce SW nou a preluat controlul
  navigator.serviceWorker.addEventListener('controllerchange', () => {
    window.location.reload();
  });
}

// Buton "Actualizează acum" din banner apelează:
function applyUpdate() {
  navigator.serviceWorker.getRegistration().then(reg => {
    reg?.waiting?.postMessage({ type: 'SKIP_WAITING' });
  });
}

// ✓ skipWaiting() automat e ACCEPTABIL pentru:
// - HTML static simplu, fără state complex între tab-uri
// - Dev/staging (nu producție cu utilizatori activi)
```

---

### Parte 8 — Cache API și 5 Strategii de Caching

#### Strategia 1 — Cache First `[HTML static + Next.js]`
**Când:** Assets statice (JS, CSS, imagini, fonturi). Viteză maximă, offline garantat.

```javascript
async function cacheFirst(request) {
  const cached = await caches.match(request);
  if (cached) return cached;
  const response = await fetch(request);
  if (response.ok) {
    const cache = await caches.open(CACHE_NAME);
    cache.put(request, response.clone()); // clone() înainte de return
  }
  return response;
}
```

#### Strategia 2 — Network First `[HTML static + Next.js]`
**Când:** API calls, date care se schimbă des.

```javascript
async function networkFirst(request) {
  try {
    const response = await fetch(request);
    if (response.ok) {
      const cache = await caches.open(CACHE_NAME);
      cache.put(request, response.clone());
    }
    return response;
  } catch {
    return caches.match(request) ??
      new Response(JSON.stringify({ error: 'Offline' }), {
        headers: { 'Content-Type': 'application/json' }
      });
  }
}
```

#### Strategia 3 — Stale While Revalidate `[HTML static + Next.js]`
**Când:** Date semi-statice (profil user, configurații).

```javascript
async function staleWhileRevalidate(request) {
  const cache  = await caches.open(CACHE_NAME);
  const cached = await cache.match(request);

  // .catch() OBLIGATORIU: request-ul eșuează offline, cached rămâne fallback
  const fetchPromise = fetch(request)
    .then(response => {
      if (response.ok) cache.put(request, response.clone());
      return response;
    })
    .catch(() => cached);

  return cached ?? fetchPromise;
}
```

#### Strategia 4 — Cache Only
**Când:** Assets precachate imutabile în versiunea curentă.

```javascript
async function cacheOnly(request) {
  return caches.match(request);
}
```

#### Strategia 5 — Network Only
**Când:** Plăți, analytics. Eșuează offline — intentionat.

```javascript
async function networkOnly(request) {
  return fetch(request);
}
```

#### Cache Coherence — HTML și assets trebuie din același snapshot

```
⚠ PROBLEMĂ CLASICĂ DE PRODUCȚIE:
   HTML servit prin Stale-While-Revalidate
   JS/CSS servit prin Cache First cu cache name 'myapp-v1'

   Deploy v2: Cache name → 'myapp-v2' (noul JS/CSS e acolo)
   Userul are HTML v1 în SWR cache → servit imediat
   HTML v1 cere app.js → Cache First găsește app.js în 'myapp-v1' (v1!)
   Sau: HTML v2 e servit dar JS din 'myapp-v1' e v1 → mismatch

SOLUȚIE: Precachezi toate assets la install + versionezi CACHE_NAME la fiecare deploy.
         Activate șterge cache-ul vechi → toate resursele din snapshot-ul nou.
         Strategia de routing devine Cache First pentru tot (assets din precache garantat fresh).
```

#### Routing pe strategii + notă CORS

```javascript
self.addEventListener('fetch', event => {
  // Cross-origin: răspunsurile opaque (no-cors) sunt cacheable dar fără status/headers
  // și pot umple cache-ul cu erori 0. Evită caching cross-origin fără CORS explicit.
  if (!event.request.url.startsWith(self.location.origin)) {
    event.respondWith(fetch(event.request));
    return;
  }

  const url = new URL(event.request.url);

  if (url.pathname.startsWith('/api/payments')) {
    event.respondWith(networkOnly(event.request));
    return;
  }
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(networkFirst(event.request));
    return;
  }
  if (/\.(js|css|png|jpg|svg|woff2)$/.test(url.pathname)) {
    event.respondWith(cacheFirst(event.request));
    return;
  }
  event.respondWith(staleWhileRevalidate(event.request));
});
```

---

### Parte 9 — Workbox: Service Workers fără Boilerplate

**⚠ `workbox-sw.js` via CDN — două limitări importante:**
1. CDN down → SW nu se înregistrează
2. `importScripts` + `workbox-sw.js` e modul **legacy** în Workbox 7 — nu suportă tree-shaking, include toți plugin-ii indiferent dacă îi folosești. Workbox 7 recomandă `workbox-build` + `generateSW` pentru producție.

**`[HTML static]` — Workbox local cu generateSW (recomandat):**

```bash
npm install workbox-build --save-dev
```

```javascript
// build-sw.js — rulezi cu: node build-sw.js
const { generateSW } = require('workbox-build');

generateSW({
  swDest: 'public/sw.js',
  globDirectory: 'public/',
  globPatterns: ['**/*.{html,js,css,png,jpg,svg,woff2}'],
  runtimeCaching: [
    {
      urlPattern: /\/api\//,
      handler: 'NetworkFirst',
      options: { cacheName: 'api-cache' }
    }
  ]
});
// Generează sw.js cu precache list automată și hash-uri pentru cache busting
```

**`[HTML static]` — Workbox via importScripts (rapid, ok pentru proiecte simple):**

```javascript
// sw.js — funcțional pentru proiecte mici; pentru producție serioasă → generateSW
importScripts('https://storage.googleapis.com/workbox-cdn/releases/7.0.0/workbox-sw.js');

const { registerRoute }   = workbox.routing;
const { CacheFirst, NetworkFirst } = workbox.strategies;
const { ExpirationPlugin } = workbox.expiration;

// maxEntries obligatoriu alături de maxAgeSeconds — fără el, fiecare deploy
// adaugă versiuni noi în cache până ajungi la sute de MB
registerRoute(
  ({ request }) => request.destination === 'script' || request.destination === 'style',
  new CacheFirst({
    cacheName: 'static-resources',
    plugins: [new ExpirationPlugin({ maxEntries: 10, maxAgeSeconds: 30 * 24 * 60 * 60 })]
  })
);

registerRoute(
  ({ request }) => request.destination === 'image',
  new CacheFirst({
    cacheName: 'images',
    plugins: [new ExpirationPlugin({ maxEntries: 50, maxAgeSeconds: 60 * 24 * 60 * 60 })]
  })
);

registerRoute(
  ({ url }) => url.pathname.startsWith('/api/'),
  new NetworkFirst({ cacheName: 'api-cache' })
);
```

**`[Next.js]` — @ducanh2912/next-pwa (fork activ al next-pwa):**

```bash
# next-pwa original e abandonat din 2022 — nu îl folosi
# @ducanh2912/next-pwa e fork-ul activ, API identic, compatibil Next.js 14+
npm install @ducanh2912/next-pwa

# Alternativă modernă pentru Workbox 7 + App Router complet:
# npm install serwist
```

```javascript
// next.config.js cu @ducanh2912/next-pwa
const withPWA = require('@ducanh2912/next-pwa').default({
  dest: 'public',
  disable: process.env.NODE_ENV === 'development',
  register: true,
  skipWaiting: false,  // false = coordonezi update cu pagina (recomandat)
});

module.exports = withPWA({ /* nextjs config */ });
```

---

## BLOC 4 — PWA

### Parte 10 — manifest.json, Installability și Custom Install Button

**manifest.json complet cu icoane corecte:**

```json
{
  "name": "StudioFlow — CRM Creativ",
  "short_name": "StudioFlow",
  "description": "CRM offline pentru freelanceri și agenții creative",
  "start_url": "/",
  "scope": "/",
  "display": "standalone",
  "orientation": "any",
  "background_color": "#1a1a2e",
  "theme_color": "#6c63ff",
  "lang": "ro",
  "icons": [
    {
      "src": "/icon-192.png",
      "sizes": "192x192",
      "type": "image/png",
      "purpose": "any"
    },
    {
      "src": "/icon-512.png",
      "sizes": "512x512",
      "type": "image/png",
      "purpose": "any"
    },
    {
      "src": "/icon-512-maskable.png",
      "sizes": "512x512",
      "type": "image/png",
      "purpose": "maskable"
    }
  ]
}
```

**De ce două icon-uri separate pentru `any` și `maskable`:**

Pe Android, iconițele `maskable` sunt tăiate circular sau pătrat, aplicând un mask care
îndepărtează ~40% din margini. Dacă folosești `purpose: "any maskable"` pe un singur icon
care nu e designuit cu "safe zone" (conținut în centrul 60% al imaginii), logo-ul apare
decupat pe Android.

Soluție: două fișiere separate.
- `icon-512.png` — icon normal, fără safe zone (`purpose: "any"`)
- `icon-512-maskable.png` — același icon dar cu padding de 20% pe toate laturile,
  astfel încât conținutul vizual să fie în zona centrală sigură (`purpose: "maskable"`)

Dacă ai un singur icon și nu poți crea varianta maskable, folosești doar `"purpose": "any"` —
Android va folosi icon-ul pătrat nemascat, mai bine decât un logo decupat.

**Link în HTML:**

```html
<head>
  <link rel="manifest" href="/manifest.json">
  <meta name="theme-color" content="#6c63ff">
  <meta name="apple-mobile-web-app-capable" content="yes">
  <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
  <meta name="apple-mobile-web-app-title" content="StudioFlow">
  <link rel="apple-touch-icon" href="/icon-192.png">
</head>
```

**Criterii installability Chrome:**
- ✓ HTTPS sau localhost (obligatoriu — `http://` și `file://` nu merg)
- ✓ manifest.json cu `name`, `icons` (192px + 512px), `start_url`, `display: standalone`
- ✓ Service Worker cu handler pentru `fetch`
- ✓ Pagina nu e deja instalată

**Verificare:** `DevTools → Application → Manifest` — erorile exacte.
`DevTools → Lighthouse → Progressive Web App` → audit complet.

**Buton "Instalează App" custom — `beforeinstallprompt`:**

```javascript
// Chrome/Edge afișează promptul de instalare o singură dată și nu-l mai arată.
// Dacă userul a dat dismiss, nu mai apare niciodată fără un buton custom.
// Captezi promptul și îl declanșezi tu la click.

let deferredInstallPrompt = null;

// Evenimentul se declanșează ÎNAINTE de a afișa promptul nativ
window.addEventListener('beforeinstallprompt', (event) => {
  event.preventDefault();               // oprești promptul automat
  deferredInstallPrompt = event;        // îl salvezi pentru mai târziu
  document.getElementById('btn-install')?.removeAttribute('hidden');
});

async function installApp() {
  if (!deferredInstallPrompt) return;
  deferredInstallPrompt.prompt();
  const { outcome } = await deferredInstallPrompt.userChoice;
  // outcome: 'accepted' | 'dismissed'
  console.log('Install outcome:', outcome);
  deferredInstallPrompt = null;
  document.getElementById('btn-install')?.setAttribute('hidden', '');
}

// Ascunzi butonul după instalare reușită
window.addEventListener('appinstalled', () => {
  deferredInstallPrompt = null;
  document.getElementById('btn-install')?.setAttribute('hidden', '');
});
```

**⚠ iOS Safari — `beforeinstallprompt` nu există**

Pe iOS, promptul automat de instalare nu există. Ghidezi userul manual:

```javascript
// Detectezi iOS
function isIOS() {
  return /iphone|ipad|ipod/.test(navigator.userAgent.toLowerCase());
}

// La prima vizită pe iOS, arăți un tooltip
if (isIOS() && !localStorage.getItem('ios_install_shown')) {
  showIOSInstallHint();  // "Apasă Share → Add to Home Screen"
  localStorage.setItem('ios_install_shown', '1');
}
```

**⚠ iOS Safari — Limitări PWA consolidate**

Dacă construiești un PWA care trebuie să funcționeze pe iPhone/iPad, cunoaște aceste limitări:

| Funcționalitate | iOS Safari |
|---|---|
| Service Workers | ✓ (din iOS 11.3, 2018) |
| Background Sync | ✗ Nu e implementat |
| Push Notifications | ✓ Parțial (din iOS 16.4, 2023) — DOAR când PWA e instalat |
| File System Access API | ✗ Nu e implementat |
| `beforeinstallprompt` | ✗ Nu există — utilizatorul instalează manual |
| `navigator.storage.persist()` | Returnează `false` — date pot fi evictate |
| `db.on('versionchange')` | Nesigur — nu te baza pe reload automat |
| SW activat în background | ✗ SW-ul e terminat după ~30s inactivitate |
| Cache limit | ~50MB per origin (variabil) |

**Strategie iOS:**
- Backup manual (JSON export) e obligatoriu pentru datele critice
- Nu te baza pe Background Sync — folosești `online` event fallback
- Testezi explicit pe Safari cu DevTools → Safari → "Responsive Design Mode"

---

### Parte 11 — Offline UX Patterns

#### Pattern 1 — Indicator online/offline

```javascript
function createOfflineBanner() {
  const banner = document.createElement('div');
  banner.id = 'offline-banner';
  banner.style.cssText = `
    display: none; position: fixed; top: 0; left: 0; right: 0;
    background: #ff6b35; color: white; text-align: center;
    padding: 8px; z-index: 9999; font-size: 14px;
  `;
  document.body.prepend(banner);

  function update() {
    if (navigator.onLine) {
      banner.style.display = 'none';
    } else {
      banner.textContent = 'Offline — datele se salvează local';
      banner.style.display = 'block';
    }
  }

  window.addEventListener('online',  update);
  window.addEventListener('offline', update);
  update();
}
```

#### Pattern 2 — Verificare conexiune reală (navigator.onLine e nesigur)

`navigator.onLine` returnează `true` dacă device-ul e conectat la o rețea, **nu garantează
că există internet real**. Pe WiFi captiv (hotel, aeroport), returnează `true` deși niciun
request nu ajunge la destinație.

```javascript
// AbortSignal.timeout() a fost introdus în Chrome 103+ / Safari 16+ / Firefox 100+.
// Pe browsere mai vechi sau în unele WebViews → TypeError silențios.
// Soluție universală: AbortController + setTimeout manual.

async function isReallyOnline() {
  if (!navigator.onLine) return false;  // offline cert — nu mai verifici

  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 3000);

  try {
    await fetch('/ping', {
      method: 'HEAD',
      cache: 'no-store',
      signal: controller.signal
    });
    return true;
  } catch {
    // fetch eșuat sau timeout → fără internet real
    return false;
  } finally {
    clearTimeout(timer);
  }
}

// Creează /ping pe server (Express/Next.js) sau folosești /favicon.ico
// GET /ping → 200 OK cu body gol (zero latency, zero bandwidth)
```

#### Pattern 3 — Optimistic Updates

```javascript
async function deleteItem(id) {
  removeFromDOM(id);  // 1. Update UI instant

  try {
    await db.items.delete(id);           // 2. Persist local
    await api.delete(`/items/${id}`);    // 3. Sync server
  } catch (error) {
    const item = await restoreFromBackup(id);
    addToDOM(item);  // 4. Rollback la eroare
    showError('Nu s-a putut șterge. Încearcă din nou.');
  }
}
```

#### Pattern 4 — Sync Queue cu verificare reală a conexiunii

```javascript
const QUEUE_KEY = 'sync_queue';

function enqueue(operation) {
  const queue = JSON.parse(localStorage.getItem(QUEUE_KEY) ?? '[]');
  queue.push({
    // crypto.randomUUID() cere secure context (HTTPS sau localhost)
    // Pe http:// sau file:// → fallback cu timestamp + random
    id:        (typeof crypto !== 'undefined' && crypto.randomUUID)
                 ? crypto.randomUUID()
                 : `${Date.now().toString(36)}-${Math.random().toString(36).slice(2)}`,
    operation,
    timestamp: Date.now(),
    retries:   0
  });
  localStorage.setItem(QUEUE_KEY, JSON.stringify(queue));
}

async function processQueue() {
  const online = await isReallyOnline();  // verificare reală, nu navigator.onLine
  if (!online) return;

  const queue = JSON.parse(localStorage.getItem(QUEUE_KEY) ?? '[]');
  if (queue.length === 0) return;

  const remaining = [];
  for (const item of queue) {
    try {
      // executeOperation: implementezi în funcție de tipul operației (add/update/delete)
      // ex: if (item.operation.type === 'add') await api.post('/items', item.operation.data)
      await executeOperation(item.operation);
    } catch {
      if (item.retries < 3) remaining.push({ ...item, retries: item.retries + 1 });
    }
  }
  localStorage.setItem(QUEUE_KEY, JSON.stringify(remaining));
}

// setTimeout 1s — aștepți stabilizarea conexiunii după 'online' event
window.addEventListener('online', () => setTimeout(processQueue, 1000));
```

#### Pattern 5 — "Ultima sincronizare" timestamp

```javascript
function updateLastSync() {
  localStorage.setItem('last_sync', new Date().toISOString());
  renderLastSync();
}

function renderLastSync() {
  const saved = localStorage.getItem('last_sync');
  if (!saved) return;
  const diff = Math.round((Date.now() - new Date(saved)) / 60000);
  document.getElementById('last-sync').textContent =
    diff < 1  ? 'Sincronizat acum' :
    diff < 60 ? `Sincronizat acum ${diff} min` :
    `Sincronizat la ${new Date(saved).toLocaleTimeString('ro-RO')}`;
}
```

#### Pattern 6 — Salvare automată înainte de închidere tab

```javascript
// Scenariul: userul are un form nesalvat și închide accidental tab-ul.
// beforeunload — se declanșează când tab-ul se închide sau navighezi în altă parte
// visibilitychange — mai fiabil pe mobile (browser minimizat, schimbi app)

let currentFormData = {};

function trackFormChanges() {
  document.querySelectorAll('input, textarea, select').forEach(el => {
    el.addEventListener('input', () => {
      currentFormData[el.name] = el.value;
    });
  });
}

function saveBeforeExit() {
  if (Object.keys(currentFormData).length > 0) {
    sessionStorage.setItem('exit_draft', JSON.stringify({
      data: currentFormData,
      savedAt: Date.now(),
      url: window.location.pathname
    }));
  }
}

// Pe desktop — se declanșează la navigare/închidere
window.addEventListener('beforeunload', saveBeforeExit);

// Pe mobile — mai fiabil (browser-ul nu garantează beforeunload pe mobile)
document.addEventListener('visibilitychange', () => {
  if (document.visibilityState === 'hidden') saveBeforeExit();
});

// La deschidere — verifici dacă există draft nesalvat
window.addEventListener('DOMContentLoaded', () => {
  const draft = sessionStorage.getItem('exit_draft');
  if (!draft) return;
  const { data, savedAt, url } = JSON.parse(draft);
  if (url === window.location.pathname && Date.now() - savedAt < 60 * 60 * 1000) {
    const restore = confirm('Ai un draft nesalvat. Vrei să-l restaurezi?');
    if (restore) restoreFormData(data);
  }
  sessionStorage.removeItem('exit_draft');
});
```

---

### Parte 12 — Background Sync API

Permite retry automat al operațiilor eșuate la revenirea conexiunii.

**Suport browsere (mai 2026):** Chrome, Edge — ~60% din utilizatori.
Firefox și Safari **NU** suportă Background Sync.
**Fallback cu `online` event este soluția principală pentru 40% din utilizatori.**

**⚠ Retry-urile nu sunt infinite:**
Chrome încearcă timp de ~3 zile sau ~10 retry-uri, după care abandonează silențios.
Dacă userul e offline mai mult de 3 zile → operațiile pending se pierd.
Soluție: persistezi operațiile pending în IndexedDB (nu doar în memorie SW) — le poți
relua manual la deschiderea app-ului, indiferent de retry limit.

```javascript
// pagina — înregistrezi sync + fallback obligatoriu
async function saveWithBackgroundSync(data) {
  // Persistezi MEREU în IndexedDB înainte de orice sync
  await db.pendingUploads.add({ data, timestamp: Date.now() });

  try {
    const reg = await navigator.serviceWorker.ready;
    if ('sync' in reg) {
      await reg.sync.register('upload-pending');
      // Chrome/Edge: SW procesează când conexiunea e disponibilă (max ~3 zile)
    } else {
      // Firefox, Safari, browsere fără Background Sync
      if (await isReallyOnline()) {
        await uploadData(data);
      } else {
        window.addEventListener('online', () => processQueue(), { once: true });
      }
    }
  } catch {
    window.addEventListener('online', () => processQueue(), { once: true });
  }
}

// La deschiderea app-ului — procesezi pending indiferent de Browser Sync
window.addEventListener('DOMContentLoaded', async () => {
  const pending = await db.pendingUploads.count();
  if (pending > 0 && await isReallyOnline()) await processQueue();
});

// sw.js — procesezi sync
self.addEventListener('sync', event => {
  if (event.tag === 'upload-pending') {
    event.waitUntil(uploadPendingFromDB());
  }
});

async function uploadPendingFromDB() {
  const pending = await db.pendingUploads.toArray();
  for (const item of pending) {
    try {
      await fetch('/api/upload', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(item.data)
      });
      await db.pendingUploads.delete(item.id);
    } catch {
      throw new Error('Upload failed — SW retry automat (max ~3 zile)');
    }
  }
}
```

---

## BLOC 5 — Advanced & Tooling

### Parte 13 — File System Access API

**Cerințe:**
- HTTPS sau localhost obligatoriu — pe `http://` și `file://` API-ul nu există
- **User gesture** (click, keydown) obligatoriu — nu poți apela automat sau în `load`

**Export fișier (Save dialog):**

```javascript
async function exportToJSON(data, filename = 'backup.json') {
  if (!('showSaveFilePicker' in window)) {
    return exportFallback(JSON.stringify(data, null, 2), filename, 'application/json');
  }
  try {
    const handle = await window.showSaveFilePicker({
      suggestedName: filename,
      types: [{ description: 'JSON', accept: { 'application/json': ['.json'] } }]
    });
    const writable = await handle.createWritable();
    await writable.write(JSON.stringify(data, null, 2));
    await writable.close();
    return { ok: true };
  } catch (error) {
    if (error.name === 'AbortError') return { ok: false, reason: 'cancelled' };
    throw error;
  }
}

async function exportToCSV(headers, rows, filename = 'export.csv') {
  const escape = cell =>
    typeof cell === 'string' && (cell.includes(',') || cell.includes('"'))
      ? `"${cell.replace(/"/g, '""')}"` : cell;

  const csvContent = [
    headers.join(','),
    ...rows.map(row => row.map(escape).join(','))
  ].join('\n');

  if (!('showSaveFilePicker' in window)) {
    return exportFallback(csvContent, filename, 'text/csv');
  }
  const handle = await window.showSaveFilePicker({
    suggestedName: filename,
    types: [{ description: 'CSV', accept: { 'text/csv': ['.csv'] } }]
  });
  const writable = await handle.createWritable();
  await writable.write(csvContent);
  await writable.close();
}

// Fallback pentru Firefox, Safari, http://, file:// — mereu prezent
// Nu adaugi/scoti din DOM — dispatchEvent funcționează fără inserție în DOM
function exportFallback(content, filename, mimeType) {
  const blob = new Blob(
    [typeof content === 'string' ? content : JSON.stringify(content, null, 2)],
    { type: mimeType }
  );
  const url = URL.createObjectURL(blob);
  const a   = Object.assign(document.createElement('a'), { href: url, download: filename });
  a.dispatchEvent(new MouseEvent('click'));  // declanșezi descărcarea fără DOM insertion
  URL.revokeObjectURL(url);
}
```

**Import fișier (Open dialog):**

```javascript
async function importFromJSON() {
  if (!('showOpenFilePicker' in window)) return importFallback('application/json');
  try {
    const [handle] = await window.showOpenFilePicker({
      types: [{ description: 'JSON', accept: { 'application/json': ['.json'] } }],
      multiple: false
    });
    const file = await handle.getFile();
    return JSON.parse(await file.text());
  } catch (error) {
    if (error.name === 'AbortError') return null;
    throw error;
  }
}

function importFallback(accept) {
  return new Promise((resolve, reject) => {
    const input = Object.assign(document.createElement('input'), { type: 'file', accept });
    input.addEventListener('change', async () => {
      const file = input.files?.[0];
      if (!file) return resolve(null);
      try { resolve(JSON.parse(await file.text())); }
      catch (e) { reject(e); }
    });
    input.click();
  });
}
```

**Suport browsere:**

| Browser | showSaveFilePicker | showOpenFilePicker |
|---|---|---|
| Chrome 86+ / Edge 86+ | ✓ | ✓ |
| Firefox | ✗ | ✗ |
| Safari | ✗ | ✗ |
| `http://` sau `file://` | ✗ | ✗ |

---

### Parte 14 — Securitate: Ce NU Stochezi Offline

#### NU stoca niciodată:

```javascript
// ✗ — chei API (oricine deschide DevTools le vede)
localStorage.setItem('openai_key', 'sk-...');

// ✗ — parole plain text
localStorage.setItem('password', userPassword);

// ✗ — JWT token în localStorage (XSS îl poate citi)
// Token-urile → httpOnly cookie (inaccesibil din JS)
localStorage.setItem('auth_token', jwtToken);

// ✗ — date financiare sensibile
localStorage.setItem('card_number', '4111 1111 1111 1111');
```

#### DA, poți stoca:

```javascript
// ✓ Preferințe UI
localStorage.setItem('theme', 'dark');
localStorage.setItem('language', 'ro');

// ✓ Date business non-sensitive
localStorage.setItem('transactions', JSON.stringify(transactions));

// ✓ User ID (nu token)
localStorage.setItem('user_id', userId);
```

#### XSS și localStorage:

Un script injectat poate citi tot localStorage instant. Protecție cu CSP:

```html
<!-- Content Security Policy — se aplică la <script> tags inline și atribute on*  -->
<!-- style-src controlează <style> tags inline și atribute style="" din HTML        -->
<!-- Nu afectează .style.cssText sau .style.color = ... din JavaScript              -->
<!-- → stilurile aplicate din JS sunt controlate de script-src, nu style-src        -->
<meta http-equiv="Content-Security-Policy"
  content="default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'">
<!-- 'unsafe-inline' pentru style-src e necesar dacă ai <style> tags inline în HTML -->
<!-- Dacă toate stilurile sunt în fișiere .css externe → poți elimina 'unsafe-inline' -->
```

```
# Netlify _headers (mai robust decât meta tag, aplicat server-side)
/*
  Content-Security-Policy: default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'
  X-Content-Type-Options: nosniff
  X-Frame-Options: DENY
```

**Niciodată `innerHTML` cu date din storage:**

```javascript
const data = localStorage.getItem('username');
element.innerHTML  = data;   // ✗ XSS dacă data conține <script> sau <img onerror=...>
element.textContent = data;  // ✓ safe întotdeauna
```

---

### Parte 15 — Debug & Testing Offline

**Chrome DevTools — Application Tab:**

```
Application → Local Storage → [origin]    — vezi/editezi/ștergi chei individual
Application → Session Storage             — tab-scoped
Application → IndexedDB                  — navighezi object stores, records, indexuri
Application → Cache Storage              — ce a cacheat Service Worker-ul
Application → Service Workers
  ✓ "Update on reload"   — forțează reload SW la fiecare refresh (dev)
  ✓ "Bypass for network" — dezactivezi SW temporar
  ✓ "Offline"            — simulezi offline din perspectiva SW
Network → No throttling → Offline          — simulezi offline la nivel TCP
Application → Clear site data             — resetezi tot: storage + SW + cache
```

**Verificare manuală în consolă:**

```javascript
// localStorage ca tabel
console.table(
  Object.fromEntries(
    Array.from({ length: localStorage.length }, (_, i) => {
      const key = localStorage.key(i);
      return [key, localStorage.getItem(key)];
    })
  )
);

// Dimensiune utilizată (include chei + valori, aproximativ UTF-16)
let total = 0;
for (let i = 0; i < localStorage.length; i++) {
  const k = localStorage.key(i) ?? '';
  total += k.length + (localStorage.getItem(k) ?? '').length;
}
console.log(`localStorage: ~${(total * 2 / 1024).toFixed(1)} KB / 5120 KB`);

// StorageManager — spațiu real
const { usage, quota } = await navigator.storage.estimate();
console.log(`Total: ${(usage/1024/1024).toFixed(1)}MB / ${(quota/1024/1024).toFixed(0)}MB`);

// Service Workers active
const regs = await navigator.serviceWorker.getRegistrations();
console.log('SW:', regs.map(r => ({ scope: r.scope, state: r.active?.state })));

// Cache Storage
for (const name of await caches.keys()) {
  const cache = await caches.open(name);
  console.log(name, (await cache.keys()).map(r => r.url));
}

// IndexedDB cu Dexie
import db from './db.js';
console.log('Clients:', await db.clients.count());
console.log('Sample:', await db.clients.limit(3).toArray());
```

**Flow de test offline complet:**

```
1. DevTools → Application → SW → ✓ "Update on reload"
2. DevTools → Network → Offline
3. Refresh → app-ul trebuie să încarce din SW cache
4. Faci o operație (add/edit/delete) — se salvează local
5. DevTools → Network → Online
6. Verifici sync-ul (dacă ai server sync)
7. DevTools → Application → Clear site data
8. Refresh → SW reinstalat, assets reprecachate
```

---

### Parte 16 — Quick Reference Card

```
╔══════════════════════════════════════════════════════════════════╗
║          OFFLINE-FIRST QUICK REFERENCE v1.1                      ║
╠══════════════════════════════════════════════════════════════════╣
║ ALEGERE STORAGE                                                  ║
║  < 500 records, < 1MB, fără query-uri  →  localStorage          ║
║  Stare temporară per tab               →  sessionStorage         ║
║  500+ records, query-uri, Blob         →  IndexedDB (Dexie.js)   ║
║  HTTP responses, assets                →  Cache API (via SW)     ║
╠══════════════════════════════════════════════════════════════════╣
║ LOCALSTORAGE — REGULI CRITICE                                    ║
║  getItem()  returnează null, nu undefined                        ║
║  MEREU  JSON.stringify/parse pentru obiecte                      ║
║  MEREU  try/catch → QuotaExceededError la setItem                ║
║  Prefixezi cheile: 'APPNAME.key' (anti-coliziune multi-app)      ║
║  storage event → ALTE tab-uri, nu cel care a scris               ║
║  BroadcastChannel → mai puternic: funcț. și în SW/Workers        ║
╠══════════════════════════════════════════════════════════════════╣
║ INDEXEDDB cu DEXIE                                               ║
║  ⚠ Declari TOATE stores la fiecare db.version()                 ║
║     Stores omise sunt ȘTERSE automat                             ║
║  await db.items.add(obj)                                         ║
║  await db.items.put(obj)            // upsert complet            ║
║  await db.items.update(id, patch)   // parțial                   ║
║  await db.items.delete(id)                                       ║
║  await db.items.where('f').equals(v).toArray()                   ║
║  .limit(50).offset(page*50)         // paginare mari volume      ║
║  .each(fn)                          // iterare fără OOM          ║
║  Promise.all([...])                 // reads paralele = 3× rapid ║
║  liveQuery(() => query)             // UI reactiv (Dexie 3+)     ║
║  bulkAdd → try/catch Dexie.BulkError (nu rollback tot)           ║
║  setupVersionChangeHandler() → apelat în onsuccess               ║
║  db.on('versionchange') → db.close() + reload (multi-tab)        ║
║  ⚠ versionchange nu fiabil pe iOS Safari                        ║
║  Startup: navigator.storage.persist() (anti-eviction)            ║
║  ⚠ persist() returnează false pe iOS Safari — backup manual     ║
╠══════════════════════════════════════════════════════════════════╣
║ SERVICE WORKER — LIFECYCLE                                       ║
║  Register → Install (precache) → Activate (cleanup) → Fetch     ║
║  sw.js la /root → controlează tot origin; la /sub/ → doar /sub  ║
║  ⚠ skipWaiting() automat = anti-pattern în producție            ║
║     Coordonezi cu pagina: postMessage → showUpdateBanner()       ║
║  response.clone() ÎNAINTE de cache.put() și return               ║
║  ⚠ HTML+assets din același CACHE_NAME = update atomic           ║
║     Strategii diferite pe HTML vs assets → mismatch la deploy    ║
║  Funcționează DOAR pe HTTPS sau localhost                        ║
╠══════════════════════════════════════════════════════════════════╣
║ WORKBOX / NEXT-PWA                                               ║
║  ExpirationPlugin: maxEntries + maxAgeSeconds (amândouă)         ║
║  workbox-sw.js CDN = modul legacy; workbox-build = recomandat    ║
║  next-pwa original = abandonat; folosești @ducanh2912/next-pwa   ║
╠══════════════════════════════════════════════════════════════════╣
║ STRATEGII CACHING                                                ║
║  Cache First         → assets statice (JS, CSS, imagini)        ║
║  Network First       → API calls cu date dinamice               ║
║  Stale While Reval.  → semi-statice + .catch(() => cached)      ║
║  Network Only        → plăți, analytics, efecte ireveribile      ║
╠══════════════════════════════════════════════════════════════════╣
║ PWA — INSTALLABILITY CHECKLIST                                   ║
║  ✓ HTTPS sau localhost                                           ║
║  ✓ manifest.json: name, icons (192+512), start_url, standalone   ║
║  ✓ Icoane separate: purpose "any" + purpose "maskable"           ║
║  ✓ Service Worker cu fetch handler                               ║
║  ✓ <link rel="manifest"> + <meta name="theme-color">             ║
║  beforeinstallprompt → captezi promptul pentru buton custom      ║
║  iOS: fără beforeinstallprompt → ghidezi user: Share → Add       ║
╠══════════════════════════════════════════════════════════════════╣
║ iOS SAFARI — LIMITĂRI PWA                                        ║
║  ✗ Background Sync, File System Access API, beforeinstallprompt  ║
║  ✓ Push Notifications (iOS 16.4+, doar când PWA e instalat)      ║
║  persist() → false (date pot fi evictate)                        ║
║  SW terminat după ~30s inactivitate în background                ║
║  Strategie: backup manual + online event fallback                 ║
╠══════════════════════════════════════════════════════════════════╣
║ NAVIGATOR.ONLINE — ATENȚIE                                       ║
║  navigator.onLine = hint, nu garanție                            ║
║  true pe WiFi captiv fără internet real                          ║
║  Verificare reală: AbortController + fetch('/ping', 3s timeout)  ║
╠══════════════════════════════════════════════════════════════════╣
║ BACKGROUND SYNC                                                  ║
║  Chrome/Edge ONLY (~60%); Firefox + Safari NU suportă           ║
║  Retry max ~3 zile sau ~10 încercări — nu infinit                ║
║  Persistezi pending în IndexedDB (nu doar în memoria SW)         ║
║  Mereu fallback: window.addEventListener('online', ...)          ║
╠══════════════════════════════════════════════════════════════════╣
║ FILE SYSTEM ACCESS API                                           ║
║  HTTPS sau localhost obligatoriu                                  ║
║  Necesită user gesture — nu apelezi automat                      ║
║  exportFallback cu dispatchEvent (fără appendChild/removeChild)  ║
║  Mereu fallback Blob → Firefox, Safari, http://, file://         ║
╠══════════════════════════════════════════════════════════════════╣
║ SECURITATE                                                       ║
║  ✗ NU: chei API, parole, JWT tokens, date card                   ║
║  ✓ DA: preferințe, date business non-sensitive, user ID          ║
║  element.textContent = data (nu innerHTML cu date din storage)   ║
║  CSP style-src → <style> tags + atribute style=""               ║
║         NU afectează .style.cssText din JavaScript               ║
╠══════════════════════════════════════════════════════════════════╣
║ DEBUG                                                            ║
║  DevTools → Application → Storage / SW / Cache                   ║
║  "Update on reload" în SW settings pentru dev                    ║
║  Network → Offline pentru test offline                           ║
║  "Clear site data" pentru reset complet                          ║
║  navigator.storage.estimate() → spațiu utilizat/disponibil       ║
╚══════════════════════════════════════════════════════════════════╝
```

---

*Stack acoperit: HTML/JS Vanilla · Next.js 14 App Router · Chrome/Edge · Netlify · Vercel · Windows 10 · Claude Code*
*Proiecte de referință: CashPulse · FollowUp Board · PurchaseCompare · Reorder Radar · InvoiceChaser · Daily Sales Flash · MenuMix Matrix · StudioFlow*
*v1.1 | Mai 2026*
