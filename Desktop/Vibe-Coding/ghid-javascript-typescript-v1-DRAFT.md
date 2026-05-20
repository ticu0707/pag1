# GHID PRACTIC: JavaScript & TypeScript pentru Vibe-Coding cu Claude
**Skill 2 — v1.0 · Ediție Inițială**
**Data:** Mai 2026 | **Nivel:** Beginner → Expert
**Timp realist:** 60 min citit + practică imediată pe proiectele tale

---

## TL;DR — 3 Lucruri Care Schimbă Totul

Dacă citești doar atât, reții esența:

1. **`await` lipsit = primești un Promise, nu date.** Fiecare apel Supabase, fetch sau Claude API fără `await` în față întoarce un obiect `Promise { <pending> }` în loc de datele reale. Este bug-ul #1 din sesiunile de vibe-coding.

2. **TypeScript types sunt documentație executabilă.** Citind semnătura unei funcții — ce primește, ce returnează — înțelegi ce face codul fără să-l execuți. Skill-ul nu e să scrii tipuri, e să le citești corect.

3. **`map`, `filter`, `find` sunt vocabularul de date al lui Claude.** Orice transformare, selecție sau căutare pe o listă — Claude o scrie cu aceste metode. Dacă nu le citești în 3 secunde, nu poți verifica dacă logica e corectă — indiferent câte ore ai petrecut cu codul.

---

## Cum Să Folosești Ghidul

**Prima dată:** Citește liniar Bloc 1 + Bloc 2 (~25 min). Returnarea din investiție e imediată.

**Când ceva nu merge:** Salt direct la Parte 11 (Checklist Pre-Apply) sau Parte 13 (Flowchart).

**Referință rapidă:** Parte 15 (Quick Reference Card) — deschide în orice sesiune.

**Dacă lucrezi pe agenți Node.js** (Agenti AI, Safe Change Agent): citește obligatoriu și Parte 6 (Module System).

**Dacă proiectul e React/Next.js** (Vibe Budget, ERP, Clinică, StudioFlow): prioritizează Parte 9 (useEffect).

---

## Learning Map

```
BLOC 1 — FUNDAMENTE MENTALE                            [TOATE proiectele]
  [0]  JS vs TS — ce bug concret previne TypeScript
  [1]  Cum Citești Cod Necunoscut — metoda în 3 pași
  [2]  TypeScript Types în practică — citind, nu scriind  ★

BLOC 2 — TEHNICI (în ordinea impactului)
  [3]  Async/Await + Error Handling — împreună          [TOATE]
  [4]  Array Methods — map/filter/reduce/find/some      [TOATE]
  [5]  Destructuring + Optional Chaining (?.)           [TOATE]
  [6]  Module System — ESM vs CommonJS                  [Node.js/Next.js]  ★

BLOC 3 — EXECUȚIE
  [7]  Pattern Complet: fetch server + mutations client  [React/Next]
  [8]  8 Greșeli Comune JS/TS (before/after)            [TOATE]
  [9]  useEffect + Closures — de ce dependencies contează [React/Next]

BLOC 4 — JUDECATĂ
  [10] Securitate JS/TS: XSS, eval(), injection         [TOATE]
  [11] Cum Validezi Codul Claude Pre-Apply              [TOATE]
  [12] Când să nu ai încredere în Claude cu JS/TS       [TOATE]

BLOC 5 — REFERINȚĂ
  [13] Flowchart: "Ce tip de problemă am cu codul ăsta?"
  [14] Transcript real: debugging async bug (sesiune slabă vs expertă)
  [15] Quick Reference Card v1.0
```

**Etichete de context:**
- `[TOATE]` — se aplică în orice proiect (HTML offline, Next.js, Node.js)
- `[React/Next]` — specific aplicații cu React sau Next.js
- `[Node.js]` — specific agenți CLI sau backend
- `[HTML]` — specific aplicații offline (CashPulse, Reorder Radar, FollowUp Board etc.)

---

## BLOC 1 — FUNDAMENTE MENTALE

### PARTE 0 — JS vs TypeScript: Ce Bug Concret Previne

**De ce există TypeScript — nu răspunsul generic, ci cel concret:**

JavaScript este un limbaj cu tipizare dinamică: tipurile variabilelor sunt determinate la runtime, în momentul execuției. Asta înseamnă că erorile de tip apar **când utilizatorul folosește aplicația**, nu când tu scrii codul.

TypeScript adaugă tipizare statică: tipurile sunt verificate **la compilare**, înainte să ruleze codul. Bug-ul e prins în editorul tău, nu în producție.

**Exemplul concret din proiectele tale:**

```typescript
// JavaScript — bug descoperit la runtime, de utilizator
function calculeazaTotal(suma, taxa) {
  return suma + taxa; // + face și concatenare de string-uri!
}
calculeazaTotal(undefined, 50); // → NaN — nimeni nu știe de ce suma e greșită
calculeazaTotal("1000", 190);   // → "1000190" — string concatenation, nu aritmetică
```

```typescript
// TypeScript — bug prins în editor, înainte de execuție
function calculeazaTotal(suma: number, taxa: number): number {
  return suma + taxa;
}
calculeazaTotal(undefined, 50); // ❌ Eroare TS: Argument of type 'undefined' is not assignable to 'number'
calculeazaTotal("1000", 190);   // ❌ Eroare TS: Argument of type 'string' is not assignable to 'number'
```

**Cel mai frecvent bug prins de TypeScript în proiectele reale:**

```typescript
// ERP financiar — fără TypeScript
const invoice = invoices.find(inv => inv.id === selectedId);
invoice.amount * 1.19; // crash dacă invoice e undefined (ID inexistent)

// Cu TypeScript
const invoice: Invoice | undefined = invoices.find(inv => inv.id === selectedId);
invoice.amount * 1.19; // ❌ Eroare TS: Object is possibly 'undefined'

if (!invoice) return; // TypeScript te OBLIGĂ să gestionezi cazul
invoice.amount * 1.19; // ✓ safe
```

**Regula practică:**
> TypeScript nu te face mai lent — îți mută erorile din producție în editor. La proiecte cu date reale (medicale, financiare, CRM), asta contează.

**Când JavaScript e suficient:**
Aplicațiile tale HTML offline (CashPulse, Reorder Radar, FollowUp Board) sunt scrise în JavaScript pur și funcționează perfect. TypeScript adaugă valoare când:
- Codul e partajat între fișiere sau colegi
- Datele vin dintr-un API extern (Supabase, Claude)
- Proiectul depășește ~500 linii

---

### PARTE 1 — Cum Citești Cod Necunoscut: Metoda în 3 Pași

Când primești cod de la Claude și nu știi de unde să începi, există o metodă de scanare care îți dă înțelegerea în 30 de secunde.

**Pasul 1 — Citești TIPURILE (semnătura funcției)**

Semnătura îți spune tot ce trebuie să știi despre o funcție fără să citești implementarea:

```typescript
async function fetchTransactions(
  userId: string,           // primește: un ID de utilizator
  filters: TransactionFilter // și un obiect de filtre
): Promise<Transaction[]>   // returnează: o promisiune cu array de tranzacții
```

În 5 secunde știi: e async, primește 2 parametri, returnează un array de obiecte Transaction.

**Pasul 2 — Citești CE FACE funcția (ultimele linii)**

Return statement-ul și efectele secundare (console, setState, supabase.insert) îți spun rezultatul:

```typescript
// Nu citi toată funcția — citești return-ul și efectele
return data ?? [];         // returnează date sau array gol
// sau
setTransactions(data);    // modifică state-ul React
// sau
throw new Error(message); // poate arunca eroare
```

**Pasul 3 — Citești FLOW-UL (condițiile și loops)**

Abia acum citești logica din interior, dacă ai nevoie:

```typescript
if (error) throw error;   // condiție de eroare — iese devreme
return data.filter(...)   // transformare pe date
```

**Exemplu complet — scanare în 30 secunde:**

```typescript
// Funcție din ghid-agent-ai-v4.md (Task Management Agent)
async function callClaudeWithRetry(
  messages: MessageParam[],   // 1. TIPURI: primește array de mesaje
  maxRetries = 3              //    cu retry configurabil
): Promise<Message> {         //    returnează un Message

  for (let i = 0; i < maxRetries; i++) {  // 3. FLOW: buclă retry
    try {
      const response = await anthropic.messages.create({  // apel API
        model: "claude-opus-4-7",
        messages
      });
      return response;                    // 2. CE FACE: returnează response
    } catch (err) {
      if (i === maxRetries - 1) throw err; // re-throw la ultimul retry
      await sleep(1000 * (i + 1));         // exponential backoff — sleep = ms => new Promise(r => setTimeout(r, ms))
    }
  }
}
```

Scanarea: async, primește mesaje, returnează Message, face retry cu backoff. Știi ce face fără să ai nevoie de comentarii.

---

### PARTE 2 — TypeScript Types în Practică [TOATE]

Nu trebuie să scrii tipuri complexe — trebuie să le **recunoști** când Claude le generează.

**Tipurile primitive:**

```typescript
let name: string = "Andrei";        // text
let amount: number = 1500.50;       // număr (întreg sau decimal)
let isActive: boolean = true;       // true sau false
let nothing: null = null;           // absența valorii (explicit)
let missing: undefined = undefined; // variabilă nedefinită
```

**Array — 2 sintaxe identice:**

```typescript
let prices: number[] = [100, 200, 300];
let prices: Array<number> = [100, 200, 300]; // identic
```

**Union types — o variabilă poate fi mai multe tipuri:**

```typescript
let id: string | number;      // poate fi "abc" sau 123
let name: string | null;      // poate fi string sau null — pattern comun Supabase
let status: string | undefined; // poate lipsi
```

**Interface — structura unui obiect:**

```typescript
// Fiecare proiect al tău are interfețe ca asta
interface Transaction {
  id: string;
  user_id: string;
  amount: number;
  description: string;
  category: string | null;   // nullable — vine din Supabase
  created_at: string;        // ISO date string
}

interface Lead {             // StudioFlow CRM
  id: string;
  name: string;
  company?: string;          // ? = optional (poate lipsi complet)
  status: 'new' | 'contacted' | 'qualified' | 'lost'; // literal union
  value: number | null;
}
```

**Type alias — alternativă la interface, util pentru unions:**

```typescript
type Status = 'active' | 'inactive' | 'pending'; // enum alternativ
type ID = string | number;
type Nullable<T> = T | null; // generic — vezi mai jos
```

**Void și unknown:**

```typescript
function logEvent(message: string): void { // nu returnează nimic
  console.log(message);
}

function parseResponse(data: unknown): string { // nu știi tipul — safer decât any
  if (typeof data === 'string') return data;
  return String(data);
}
```

**Generics — T ca placeholder pentru un tip:**

```typescript
// T va fi înlocuit cu tipul real la apel
function firstItem<T>(arr: T[]): T | undefined {
  return arr[0];
}

firstItem<Transaction>(transactions); // T = Transaction
firstItem<string>(["a", "b"]);        // T = string

// Le vei vedea în useState și Promise:
const [items, setItems] = useState<Transaction[]>([]); // T = Transaction[]
async function fetch(): Promise<Lead[]> { ... }        // T = Lead[]
```

**Partial\<T\>, Record\<K,V\>, Omit\<T,K\> — utility types pe care Claude le generează frecvent:**

```typescript
// Partial<T> — toate câmpurile devin opționale (la update operations)
async function updateLead(id: string, changes: Partial<Lead>): Promise<void> {
  await supabase.from('leads').update(changes).eq('id', id);
}
updateLead('123', { status: 'qualified' }); // ✓ nu trebuie să dai toate câmpurile din Lead

// Record<K, V> — obiect cu chei de tip K și valori de tip V
const totalByCategory: Record<string, number> = { 'Food': 450, 'Transport': 120 };
// Apare frecvent ca output din .reduce() — CashPulse, Vibe Budget

// Omit<T, K> — exclude câmpuri dintr-un tip (la create operations)
type NewTransaction = Omit<Transaction, 'id' | 'created_at'>; // toate câmpurile, minus id și created_at
// Claude generează asta când vrei să adaugi o înregistrare nouă fără câmpurile generate de DB
```

**Limita critică: TypeScript verifică la compilare, nu la runtime**

```typescript
// TypeScript "crede" că amount e number — dar nu verifică datele reale din Supabase
interface Transaction { amount: number; }

// Bug posibil: dacă DB returnează amount ca string din cauza unui migration vechi
const total = transactions.reduce((sum, t) => sum + t.amount, 0);
// "150" + "200" → "150200" (concatenare string), nu 350
// TypeScript nu prinde asta — validează structura, nu valorile reale la runtime

// Prevenție pentru câmpuri numerice în calcule financiare:
const amount = Number(transaction.amount); // conversie explicită dacă originea e nesigură
```

> Supabase și SDK-urile oficiale (Anthropic, Next.js) au tipuri TypeScript fiabile — nu e o problemă în practică pentru proiectele tale. Dacă lucrezi cu API-uri externe necontrolate sau date legacy, librăria `zod` oferă validare runtime completă.

**Cum recunoști dacă tipul Claude e corect:**

```typescript
// Claude a generat asta pentru Vibe Budget:
interface Transaction {
  id: string;
  amount: number;
  category_id: string;    // ← verifică: există 'category_id' în tabelul Supabase?
  created_at: string;
}

// Dacă tabelul Supabase are 'categoryId' (camelCase) în loc de 'category_id' →
// query-ul va returna undefined pentru acel câmp — TypeScript nu prinde asta
// pentru că nu compară cu schema DB, ci doar validează intern
```

> Regula: după ce Claude generează un interface pentru un tabel Supabase, compară câmp cu câmp cu schema reală din dashboard-ul Supabase.

---

## BLOC 2 — TEHNICI

### PARTE 3 — Async/Await + Error Handling [TOATE]

**Mecanismul real — fără metaforă, direct:**

JavaScript rulează pe un singur fir de execuție (single thread). Operațiile lente — apeluri de rețea, baze de date, fișiere — ar bloca tot dacă ar fi sincrone. Soluția: le faci "async" — le trimiți în fundal și JavaScript continuă cu altceva.

```javascript
// Ce ar însemna fetch SINCRON (ipotetic — nu există în browser):
const data = syncFetchFromSupabase(); // blochează totul până vine răspunsul
// → UI înghețat 200ms–2s, nicio animație, niciun click nu funcționează
// → pe conexiune mobilă slabă: experiență spartă

// Cum funcționează real — async:
const { data } = await supabase.from('transactions').select('*');
// ↑ JavaScript trimite cererea și e liber să facă altceva în timp ce așteaptă
console.log('done'); // rulează DUPĂ ce Supabase a răspuns
// → UI rămâne responsiv, animații continuă, alte componente se randează
```

**Promise — "contractul" pentru o valoare viitoare:**

```javascript
// Un Promise este un obiect care va conține o valoare în viitor
const promise = fetch('https://api.example.com/data');
console.log(promise); // → Promise { <pending> }
// Nu e datele — e promisiunea că datele vor veni

// .then() — ce faci când promisiunea se rezolvă
promise.then(response => {
  console.log(response); // acum ai datele
});
```

**Async/await — același lucru, mai lizibil:**

```javascript
// .then() — dificil de citit cu multiple operații
fetch(url)
  .then(r => r.json())
  .then(data => processData(data))
  .catch(err => handleError(err));

// async/await — identic, mai clar
async function loadData() {
  const response = await fetch(url);
  const data = await response.json();
  const result = processData(data);
  return result;
}
```

**Bug-ul #1 — await lipsit:**

```typescript
// GREȘIT — transactions e un Promise object, nu array
const transactions = supabase
  .from('transactions')
  .select('*');

transactions.map(t => t.amount); // ❌ TypeError: transactions.map is not a function
// Promise nu are .map() — array-ul are

// CORECT
const { data: transactions } = await supabase
  .from('transactions')
  .select('*');

transactions.map(t => t.amount); // ✓ funcționează
```

**Error handling — integrat, nu opțional:**

Fiecare operație async poate eșua. Fără error handling, aplicația eșuează silențios sau crash-uiește fără mesaj util.

```typescript
// Pattern complet — folosit în toate proiectele tale
async function getLeads(userId: string): Promise<Lead[]> {
  try {
    const { data, error } = await supabase
      .from('leads')
      .select('*')
      .eq('user_id', userId);

    if (error) throw error;      // Supabase returnează error object, nu aruncă excepție
    return data ?? [];           // fallback la array gol dacă data e null
    
  } catch (err) {
    console.error('getLeads failed:', err);
    return [];                   // UI nu crash-uiește — afișează listă goală
  }
}
```

**3 tipuri de erori async pe care le vei întâlni:**

```typescript
// 1. Eroare de rețea (fetch/axios)
try {
  const res = await fetch('/api/data');
  if (!res.ok) throw new Error(`HTTP ${res.status}`); // verifică status code
  const data = await res.json();
} catch (err) { ... }

// 2. Eroare Supabase
const { data, error } = await supabase.from('table').select('*');
if (error) throw error; // sau: if (error) return { error }

// 3. Eroare Claude API (din ghid-agent-ai-v4.md)
try {
  const response = await anthropic.messages.create({ ... });
} catch (err) {
  if (err instanceof Anthropic.RateLimitError) {
    await sleep(retryDelay);         // retryDelay = 1000ms, 2000ms... — definit de apelant
    // retry
  }
  throw err;
}
```

**async în funcții, nu în variabile:**

```typescript
// async e un prefix pentru funcții — nu pentru apeluri de funcție
const data = async supabase.from('table').select(); // ❌ SyntaxError

// Funcția care conține await trebuie să fie async
const loadData = async () => {
  const data = await supabase.from('table').select();
  return data;
};
```

---

### PARTE 4 — Array Methods: map, filter, reduce, find, some [TOATE]

Acestea sunt cele mai frecvente construcții din codul Claude. Înțelege fiecare în 3 secunde.

**`map` — transformă fiecare element, returnează array de aceeași lungime:**

```typescript
// Regula: input array → output array, SAME length, elemente transformate
const amounts = transactions.map(t => t.amount);
// [{ id: '1', amount: 100 }, { id: '2', amount: 200 }]
// → [100, 200]

// Transformare mai complexă (FollowUp Board):
const taskCards = tasks.map(task => ({
  ...task,
  formattedDate: formatDate(task.due_date),
  isOverdue: new Date(task.due_date) < new Date()
}));
```

**`filter` — selectează elementele care trec condiția, returnează array mai mic (sau gol):**

```typescript
// Regula: input array → output array, MAI MIC sau EGAL ca lungime
const activeLeads = leads.filter(lead => lead.status === 'active');
const unpaidInvoices = invoices.filter(inv => inv.status !== 'paid');
const highValue = transactions.filter(t => t.amount > 1000);
```

**`find` — primul element care îndeplinește condiția, sau undefined:**

```typescript
// Regula: returnează UN element sau undefined — NU un array
const selectedCategory = categories.find(c => c.id === selectedId);
// → Category object sau undefined

// GREȘEALA FRECVENTĂ: confundat cu filter
const wrong = categories.filter(c => c.id === selectedId); // returnează array!
wrong.name; // ❌ undefined.name crash
```

**`reduce` — combină tot array-ul într-un singur output:**

```typescript
// Regula: array → orice (număr, obiect, string, alt array)
const total = transactions.reduce((sum, t) => sum + t.amount, 0);
// 0 = valoarea inițială a acumulatorului

// Total pe categorii (CashPulse):
// acc = "accumulator" — obiectul care se construiește progresiv, iterație cu iterație
// {} as Record<string, number> = valoarea inițială a lui acc (obiect gol)
//   'as' e necesar pentru că TypeScript nu poate infera tipul din {} gol
const byCategory = transactions.reduce((acc, t) => {
  acc[t.category] = (acc[t.category] ?? 0) + t.amount;
  //                 ↑ dacă categoria nu există încă în acc, tratează ca 0
  return acc; // returnezi acc modificat — devine input-ul pentru iterația următoare
}, {} as Record<string, number>);
// Progres: {} → {Food:100} → {Food:100, Transport:50} → {Food:450, Transport:120, Utilities:300}
// → rezultat final: { 'Food': 450, 'Transport': 120, 'Utilities': 300 }
```

**`some` și `every` — verifică condiții:**

```typescript
// some → cel puțin un element îndeplinește condiția (returnează boolean)
const hasUnpaid = invoices.some(inv => inv.status === 'unpaid');
const hasHighRisk = leads.some(lead => lead.score > 80);

// every → TOȚI îndeplinesc condiția
const allPaid = invoices.every(inv => inv.status === 'paid');
```

**Cum le recunoști rapid în cod Claude:**

```typescript
// Oriunde vezi .map() → Claude transformă fiecare element
// Oriunde vezi .filter() → Claude selectează un subset
// Oriunde vezi .find() → Claude caută UN element specific
// Oriunde vezi .reduce() → Claude calculează sau agregă
// Oriunde vezi .some()/.every() → Claude verifică o condiție pe toată lista
```

**Chaining — combinarea metodelor:**

```typescript
// Frecvent în proiectele tale:
const activeHighValueAmounts = leads
  .filter(l => l.status === 'active')     // selectează active
  .filter(l => (l.value ?? 0) > 1000)    // dintre ele, cele > 1000
  .map(l => l.value ?? 0);               // extrage valorile
```

---

### PARTE 5 — Destructuring + Optional Chaining [TOATE]

**Object destructuring — extrage proprietăți în variabile:**

```typescript
// Fără destructuring
const data = result.data;
const error = result.error;

// Cu destructuring — echivalent, mai concis
const { data, error } = result;

// Rename la destructurare (util când ai coliziuni de nume):
const { data: transactions, error: fetchError } = await supabase
  .from('transactions').select('*');
// 'transactions' conține result.data, 'fetchError' conține result.error

// Default value:
const { name = 'Anonim', role = 'user' } = userProfile ?? {};

// Nested destructuring:
const { user: { id, email } } = session;
// Atenție: crash dacă user e undefined — folosește optional chaining
```

**Array destructuring:**

```typescript
// Clasic — useState
const [count, setCount] = useState(0);
const [isOpen, setIsOpen] = useState(false);

// Poți ignora elemente:
const [, second, third] = [1, 2, 3]; // ignori primul
```

**Spread operator — copiază sau combină:**

```typescript
// Obiect spread — combini sau suprascrii proprietăți
const updatedLead = { ...existingLead, status: 'qualified' };
// creează obiect NOU — existingLead rămâne neschimbat

// Array spread — adaugă sau combini
const newTasks = [...tasks, { id: Date.now(), title: 'New task' }];
const allLeads = [...activeLeads, ...archivedLeads];

// Pattern comun React — actualizare state:
setUser(prev => ({ ...prev, name: 'Andrei' })); // schimbă doar name
setTasks(prev => prev.filter(t => t.id !== deletedId)); // elimină un task

// GOTCHA CRITIC — parantezele exterioare sunt OBLIGATORII la object literal:
setUser(prev => ({ ...prev, name: 'Andrei' })); // ✓ ({ }) — JavaScript știe că e obiect
setUser(prev => { ...prev, name: 'Andrei' });   // ❌ SyntaxError — { e interpretat ca bloc de cod
// Motorul JS nu poate interpreta ...prev ca statement valid în bloc → "Unexpected token '...'"
// Varianta fără spread (ex: { name: 'Andrei' }) e mai periculoasă — JS o vede ca labeled statement,
// nu generează eroare, returnează undefined silențios
```

**Optional chaining `?.` — safe property access:**

```typescript
// Problema: crash dacă orice e null/undefined pe drum
const city = user.address.city; // TypeError dacă user sau address e null

// Cu optional chaining: returnează undefined în loc de crash
const city = user?.address?.city;
// Dacă user e null → undefined
// Dacă address e null → undefined
// Dacă city există → city

// Funcționează și pe metode:
const length = data?.items?.length ?? 0;
const found = list?.find(item => item.id === id);

// Nullish coalescing ?? — fallback pentru null/undefined
const name = user?.name ?? 'Utilizator necunoscut';
// ?? returnează dreapta DOAR dacă stânga e null sau undefined
// (spre deosebire de ||, care returnează dreapta și pentru 0, '', false)
```

---

### PARTE 6 — Module System: ESM vs CommonJS [Node.js/Next.js]

Aceasta este cauza a ~30% din erorile de start pe proiectele de agenți Node.js.

**Cele două sisteme:**

```
CommonJS (CJS) — vechiul standard Node.js
├── require('./module')
├── module.exports = ...
└── Funcționează sincron, se evalua la runtime

ESM — ECMAScript Modules (standardul modern)
├── import ... from './module.js'
├── export default / export { named }
└── Funcționează asincron, se analizează static
```

**Eroarea frecventă și cauza:**

```
SyntaxError: Cannot use import statement in a module
```

Cauza: Node.js tratează fișierul ca CJS dar găsește sintaxă ESM (`import`).

**Fix-ul:**

```json
// package.json — adaugă "type": "module"
{
  "name": "task-agent",
  "type": "module",       // ← asta spune Node.js că toate .js sunt ESM
  "scripts": { ... }
}
```

**Named vs Default exports:**

```typescript
// Named exports — poți exporta mai multe lucruri
// src/tools.ts (din ghid-agent-ai-v4.md)
export const toolDefinitions = [...];
export function executeTool(name: string, input: unknown) { ... }
export const MAX_ITERATIONS = 15;

// Import named — trebuie să specifici exact ce vrei
import { toolDefinitions, executeTool, MAX_ITERATIONS } from './tools.js';
// NU poți: import tools from './tools.js' — nu există default export

// Default export — un singur lucru principal per fișier
export default function handler(req: Request, res: Response) { ... }

// Import default — orice nume vrei
import handler from './handler.js';
import myHandler from './handler.js'; // același lucru, alt nume
```

**Extensia `.js` în import-uri ESM — detaliu care strică tot:**

```typescript
// CJS — extensia opțională
const { runAgent } = require('./agent');     // ✓ merge

// ESM — extensia OBLIGATORIE, chiar dacă fișierul e .ts
import { runAgent } from './agent.js';       // ✓ corect
import { runAgent } from './agent';          // ❌ poate eșua în ESM strict
import { runAgent } from './agent.ts';       // ❌ greșit — e compilat la .js
```

**`process.env` — variabile de mediu în Node.js:**

```typescript
// .env file
ANTHROPIC_API_KEY=sk-ant-...
PORT=3000

// Citire în cod (după dotenv)
const apiKey = process.env.ANTHROPIC_API_KEY; // tipul e string | undefined — validateEnv() de mai jos verifică la startup

// Validare la startup (pattern din ghid-agent-ai-v4.md)
function validateEnv() {
  if (!process.env.ANTHROPIC_API_KEY) {
    throw new Error('ANTHROPIC_API_KEY lipsește din .env');
  }
}
```

---

## BLOC 3 — EXECUȚIE

### PARTE 7 — Pattern Complet: Fetch Server + Mutations Client [React/Next]

Acesta e "rețeta completă" pentru orice feature cu date Supabase: fetch la randare (Server Component) și operații interactive (Client Component + mutations). Aplicațiile reale le folosesc pe amândouă — ghidul acoperă fiecare.

**Contextul:** adaugi pagina de Tranzacții în Vibe Budget — mai întâi fetch-ul la randare, apoi delete și add interactiv.

---

**Pasul 1 — Definești tipul (corespunde cu tabelul Supabase):**

```typescript
// types/index.ts sau direct în fișier
interface Transaction {
  id: string;
  user_id: string;
  amount: number;
  description: string;
  category: string | null;   // nullable în Supabase
  type: 'income' | 'expense';
  created_at: string;        // ISO 8601 string
}

// Ce verifici: fiecare câmp există în tabelul Supabase?
// Tipurile corespund? (number vs string pentru amount?)
// Câmpurile nullable sunt marcate ca T | null?
```

**Pasul 2 — Funcția de fetch (server sau client):**

```typescript
// lib/transactions.ts
import { createClient } from '@/utils/supabase/server';

async function getTransactions(userId: string): Promise<Transaction[]> {
  const supabase = await createClient();

  const { data, error } = await supabase
    .from('transactions')
    .select('*')
    .eq('user_id', userId)
    .order('created_at', { ascending: false });

  if (error) {
    console.error('getTransactions:', error);
    return [];
  }

  return data ?? [];
}

// Ce verifici:
// ✓ await prezent înainte de supabase
// ✓ error verificat înainte de a folosi data
// ✓ data ?? [] — returnează array gol, nu null
```

**Pasul 3 — Componenta (Next.js App Router):**

```typescript
// app/transactions/page.tsx
import { getTransactions } from '@/lib/transactions';
import { auth } from '@/utils/auth';

export default async function TransactionsPage() {
  const { userId } = await auth();
  const transactions = await getTransactions(userId);

  if (transactions.length === 0) {
    return <p>Nu există tranzacții.</p>;
  }

  const total = transactions.reduce((sum, t) =>
    t.type === 'expense' ? sum - t.amount : sum + t.amount, 0
  );

  return (
    <div>
      <h1>Tranzacții</h1>
      <p>Sold: {total} RON</p>
      <ul>
        {transactions.map(t => (
          <li key={t.id}>           {/* key OBLIGATORIU pe liste */}
            {t.description}: {t.amount} RON
          </li>
        ))}
      </ul>
    </div>
  );
}

// Ce verifici:
// ✓ key={t.id} pe fiecare element din .map()
// ✓ empty state gestionat (length === 0)
// ✓ page.tsx e async (Server Component — poate await direct)
```

**Pasul 4 — Pattern Client-Side: Mutations / CRUD Interactiv**

Fetch-ul de mai sus (Server Component) e pentru afișare. Operațiile interactive — delete, add, update — se fac în Client Components cu event handlers async. Aceasta e a doua jumătate a pattern-ului complet.

```typescript
// app/transactions/TransactionList.tsx — Client Component
'use client';
import { useState } from 'react';
import { createClient } from '@/utils/supabase/client';

interface Props {
  initialTransactions: Transaction[]; // primite de la Server Component ca prop
}

export default function TransactionList({ initialTransactions }: Props) {
  const [transactions, setTransactions] = useState(initialTransactions);
  const [loading, setLoading] = useState(false);
  const supabase = createClient();

  // DELETE — pattern complet cu loading state
  const handleDelete = async (id: string) => {
    setLoading(true);
    const { error } = await supabase
      .from('transactions')
      .delete()
      .eq('id', id);

    if (!error) {
      setTransactions(prev => prev.filter(t => t.id !== id)); // state update — fără refetch
    }
    setLoading(false);
  };

  // ADD — pattern complet, preia date din DB după insert (returnează row-ul creat)
  const handleAdd = async (formData: NewTransaction) => { // NewTransaction = Omit<Transaction, 'id' | 'created_at'>
    setLoading(true);
    const { data, error } = await supabase
      .from('transactions')
      .insert(formData)
      .select()
      .single(); // ✓ .single() OK după INSERT — returnează mereu exact 1 row (spre deosebire de SELECT — Parte 12)

    if (!error && data) {
      setTransactions(prev => [data, ...prev]); // adaugă la începutul listei
    }
    setLoading(false);
  };

  return (
    <ul>
      {transactions.map(t => (
        <li key={t.id}>
          {t.description}: {t.amount} RON
          <button
            onClick={() => handleDelete(t.id)}
            disabled={loading}
          >
            Șterge
          </button>
        </li>
      ))}
    </ul>
  );
}

// Ce verifici față de Server Component:
// ✓ 'use client' la prima linie (folosești useState)
// ✓ createClient() din '@/utils/supabase/client' (nu server)
// ✓ await pe fiecare operație Supabase din handler
// ✓ setTransactions(prev => ...) — state update funcțional, nu mutare directă
// ✓ loading state — dezactivezi butonul în timpul operației
```

**Cum le împarți în practică:**

```
Server Component (page.tsx)          Client Component (TransactionList.tsx)
─────────────────────────────────    ──────────────────────────────────────
fetch inițial la randare          →  primește data ca prop (initialTransactions)
nu are useState / useEffect          gestionează interacțiunile (add, delete, edit)
mai rapid, SEO-friendly              re-randare locală fără refetch complet
```

---

**Semnele că ceva lipsește — ambele pattern-uri:**

```
Server Component (Pașii 1–3):
❌ Lipsește await → transactions e Promise, .map() crash
❌ Lipsește if (error) → erori silențioase în producție
❌ data fără ?? [] → Supabase returnează null, .map() crash
❌ Lipsește key={t.id} → Warning React + comportament ciudat la reorder
❌ Interface greșit față de schema DB → câmpuri undefined la afișare

Client Component (Pasul 4):
❌ Lipsește 'use client' → useState/useEffect crash server-side
❌ Lipsește await în handler → state update cu Promise, nu cu date reale
❌ Mutare directă state (tasks.push) → React nu detectează schimbarea
❌ Lipsește loading state → utilizatorul poate apăsa de două ori
```

---

### PARTE 8 — 8 Greșeli Comune JS/TS

**Greșeala 1: Await lipsit**
```typescript
❌ const { data } = supabase.from('tasks').select('*');
   data.map(t => t.title); // TypeError: Cannot read property of undefined

✅ const { data } = await supabase.from('tasks').select('*');
   data?.map(t => t.title);

De ce: fără await, data e un PromiseLike object, nu array.
```

**Greșeala 2: Mutare directă a state-ului React**
```typescript
❌ tasks.push(newTask);
   setTasks(tasks);    // React nu detectează — tasks e același obiect în memorie

✅ setTasks([...tasks, newTask]);      // array NOU → React detectează schimbarea
✅ setTasks(prev => [...prev, newTask]); // pattern funcțional — mai sigur
```

**Greșeala 3: `any` în loc de tipul corect**
```typescript
❌ async function processData(data: any) {
     return data.amount * 1.19; // TypeScript nu verifică nimic
   }

✅ async function processData(data: Transaction) {
     return data.amount * 1.19; // dacă 'amount' lipsește din interface → eroare TS
   }

De ce: `any` dezactivează TypeScript pe acea variabilă — pierzi tocmai protecția.
```

**Greșeala 4: `find` confundat cu `filter`**
```typescript
❌ const category = categories.filter(c => c.id === id);
   category.name; // undefined — filter returnează array, nu element

✅ const category = categories.find(c => c.id === id);
   category?.name; // safe cu optional chaining

Regula: find → UN element | undefined. filter → array (poate fi gol).
```

**Greșeala 5: Missing null check după `find`**
```typescript
❌ const invoice = invoices.find(inv => inv.id === id);
   return invoice.amount; // crash dacă ID nu există

✅ const invoice = invoices.find(inv => inv.id === id);
   if (!invoice) return 0; // sau throw, sau return null
   return invoice.amount;
```

**Greșeala 6: `map` cu funcție cu corp, fără `return`**
```typescript
❌ items.map(item => {
     item.name.toUpperCase(); // lipsește return → fiecare element devine undefined
   });

✅ items.map(item => {
     return item.name.toUpperCase();
   });
✅ items.map(item => item.name.toUpperCase()); // arrow fără corp → return implicit
```

**Greșeala 7: `async` în `useEffect` direct**
```typescript
❌ useEffect(async () => {
     const data = await fetchData();
     setData(data);
     // Probleme reale, nu doar un warning:
     // (1) Dacă componenta se demontează în timpul await → setData() pe component mort
     // (2) Dacă fetchData() aruncă eroare → React nu o poate captura în Error Boundary
     // (3) useEffect returnează Promise în loc de cleanup function → React ignoră cleanup
   }, []);

✅ useEffect(() => {
     const load = async () => {
       const data = await fetchData();
       setData(data);
     };
     load(); // apelezi funcția, nu o returnezi
   }, []);
```

**Greșeala 8: `||` în loc de `??` pentru fallback**
```typescript
❌ const count = data.count || 0;
   // Dacă data.count e 0 (zero legitim) → || îl tratează ca falsy → returnează fallback-ul

❌ const name = user.name || 'Anonim';
   // Dacă user.name e '' (string gol valid, ex: utilizator fără nume setat) → returnează 'Anonim' — date corupte

✅ const count = data.count ?? 0;
✅ const name = user.name ?? 'Anonim';
   // ?? returnează fallback DOAR pentru null/undefined — 0 și '' sunt valori legitime și sunt păstrate
```

---

### PARTE 9 — useEffect + Closures: De ce Dependencies Contează [React/Next]

**Ce e un closure — în 30 secunde:**

```javascript
function createAdder(x) {       // x e "captat" în closure
  return function(y) {
    return x + y;               // accesează x din scope exterior
  };
}

const add5 = createAdder(5);
add5(3); // 8 — funcția "ține minte" că x = 5
add5(10); // 15
// x nu e accesibil din afară, dar funcția returned îl "vede"
```

**De ce contează în React:**

Fiecare funcție din interiorul unui component React este un closure — "capturează" valorile din scope-ul componentului la momentul creării.

```typescript
// Problema: stale closure în useEffect
function TransactionList({ userId }) {
  const [transactions, setTransactions] = useState([]);

  useEffect(() => {
    // Această funcție e creată ODATĂ (la mount)
    // Capturează userId de la MOMENTUL CREĂRII
    fetchTransactions(userId).then(setTransactions);
  }, []); // [] = rulează o singură dată — userId capturat e cel inițial

  // Dacă userId se schimbă (user switch) → useEffect nu rulează din nou
  // → afișezi tranzacțiile user-ului anterior
}

// Fix: adaugă userId în dependencies
useEffect(() => {
  fetchTransactions(userId).then(setTransactions);
}, [userId]); // rulează din nou la fiecare schimbare de userId
```

**Regula simplă:**

> Dacă folosești o variabilă din afara `useEffect` în interiorul lui, acea variabilă trebuie să fie în dependencies array.

**Variabile care sunt stabile (nu trebuie în dependencies):**

```typescript
// NU trebuie în dependencies:
const [data, setData] = useState(null);
// setData e stabilă — React garantează că nu se schimbă între render-uri

const ref = useRef(null);
// ref.current se poate schimba, dar ref în sine e stabilă

const CONSTANT = 'value'; // constante definite în afara componentului
```

**Variabile care TREBUIE în dependencies:**

```typescript
// TREBUIE în dependencies:
const [userId, setUserId] = useState('');
// userId e state — se poate schimba

const fetchData = () => { ... }; // funcție definită în component — recreată la fiecare render
// Dacă e în dep[]: effect rulează → fetchData() face setState → re-render → fetchData nouă → effect din nou → loop
// (Nu e loop dacă efectul nu face setState — dar useCallback rămâne buna practică)

// Fix pentru funcții în dependencies: useCallback
const fetchData = useCallback(() => {
  return supabase.from('data').select('*').eq('user', userId);
}, [userId]); // fetchData e recreată DOAR când userId se schimbă
```

**Loop infinit — cel mai frecvent bug useEffect:**

```typescript
// Pattern care creează loop:
const [data, setData] = useState([]);

useEffect(() => {
  fetchData().then(result => setData(result)); // schimbă data
}, [data]); // data e în dependencies → re-rulează când data se schimbă → loop

// Fix: elimini data din dependencies (nu e nevoie de ea în effect)
useEffect(() => {
  fetchData().then(result => setData(result));
}, []); // sau [userId] dacă fetch depinde de user
```

**Cleanup function — previne race conditions la navigare rapidă:**

```typescript
// Problema: user navighează rapid între pagini
// fetchTransactions() pornește, dar componenta se demontează înainte să termine
// → setTransactions() se apelează pe o componentă demontată
// → Warning în console: "Can't perform a React state update on an unmounted component"
// → Potențial: afișezi date pentru user-ul anterior

// Fix cu flag de cleanup:
useEffect(() => {
  let cancelled = false;

  fetchTransactions(userId)
    .then(data => { if (!cancelled) setTransactions(data); })
    .catch(err => { if (!cancelled) console.error('fetchTransactions failed:', err); });
  // ↑ .catch() obligatoriu — fără el, erorile dispar silențios

  return () => {
    cancelled = true; // se apelează automat la demontarea componentei
  };
}, [userId]);

// Alternativă cu AbortController (pentru fetch nativ — mai explicit):
useEffect(() => {
  const controller = new AbortController();

  fetch('/api/transactions', { signal: controller.signal })
    .then(r => r.json())
    .then(data => setTransactions(data))
    .catch(err => {
      if (err.name === 'AbortError') return; // ignoră anularea deliberată, nu e eroare
      console.error(err);
    });

  return () => controller.abort(); // anulează request-ul la demontare
}, [userId]);
```

> Regula: orice `useEffect` care pornește o operație async ar trebui să returneze un cleanup. Nu e mereu critic — devine important în pagini cu navigare frecventă sau liste cu filtrare rapidă.

---

## BLOC 4 — JUDECATĂ

### PARTE 10 — Securitate JS/TS [TOATE]

**XSS — Cross-Site Scripting:**

```javascript
// VULNERABIL — inserezi HTML controlat de utilizator direct în DOM
element.innerHTML = userInput;     // dacă userInput e '<script>stealCookies()</script>'
document.write(userInput);         // → execută cod malițios

// SAFE — text pur, niciodată interpretat ca HTML
element.textContent = userInput;   // ✓
element.innerText = userInput;     // ✓

// În React — JSX e safe implicit:
<p>{userInput}</p>          // ✓ React escape-uiește automat
<div dangerouslySetInnerHTML={{ __html: userInput }} /> // ❌ XSS
// "dangerouslySetInnerHTML" e avertisment în denumire — evită complet
```

**eval() și Function() — NICIODATĂ:**

```javascript
❌ eval(userInput);              // execută orice cod ca JavaScript
❌ new Function(userInput)();    // identic cu eval
❌ setTimeout(userInput, 1000);  // setTimeout cu string e eval deghizat

// Dacă Claude generează eval() → cere alternativă
// Cazul legitim aproape că nu există în proiectele tale
```

**Chei API în cod client:**

```typescript
// Ce apare în browser (bundle client-side) e vizibil pentru oricine
❌ const apiKey = 'sk-ant-api03-xyz'; // vizibil în Sources tab browser

// Corect — numai pe server, niciodată în bundle client
✅ // Next.js API Route sau Server Component
   const apiKey = process.env.ANTHROPIC_API_KEY; // server only — nu ajunge în browser

// Exception — cheile publice (anon keys Supabase)
✅ const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL; // NEXT_PUBLIC_ = poate fi în browser
```

**Path traversal în Node.js (relevant pentru Safe Change Agent):**

```typescript
// VULNERABIL — utilizatorul controlează calea fișierului
const content = fs.readFileSync(`./files/${userInput}`);
// userInput = '../../.env' → citești fișierul cu secretele

// SAFE — validezi că path-ul e în directorul permis
import path from 'path';
const safePath = path.resolve('./files', userInput);
const allowed = path.resolve('./files');

if (!safePath.startsWith(allowed + path.sep)) { // path.sep = '/' sau '\' — fără el, '/files_backup' trece verificarea
  throw new Error('Path traversal detectat');
}
```

**userId din sesiunea auth, nu din request [React/Next]:**

Cel mai frecvent bug de securitate în aplicațiile Supabase cu date per-user. Claude generează uneori cod care ia userId din URL params sau request body — oricine poate manipula acele valori.

```typescript
// VULNERABIL — userId vine din URL sau body (poate fi manipulat de oricine)
const userId = searchParams.get('user_id');   // URL: /transactions?user_id=altUserId
// sau
const { userId } = await req.json();          // din request body

const { data } = await supabase
  .from('transactions')
  .select('*')
  .eq('user_id', userId); // oricine pune orice ID → vede datele altui utilizator

// SAFE — userId vine întotdeauna din sesiunea autentificată, verificată de server
import { createClient } from '@/utils/supabase/server';

const supabase = await createClient();
const { data: { user } } = await supabase.auth.getUser(); // sesiune verificată server-side

if (!user) return redirect('/login');

const { data } = await supabase
  .from('transactions')
  .select('*')
  .eq('user_id', user.id); // ID din sesiune — imposibil de manipulat din exterior
```

> Row Level Security (RLS) în Supabase e o a doua linie de apărare utilă, dar nu înlocuiește validarea userId din sesiune. Activează RLS și validează userId din auth — ambele.
>
> Relevant pentru: Vibe Budget, ERP Financiar, StudioFlow, Clinică Medicală.

---

### PARTE 11 — Cum Validezi Codul Claude Pre-Apply [TOATE]

**5 puncte de verificat înainte să aplici orice cod generat:**

```
□ PUNCT 1 — AWAIT CHECK                              [1 min]
  Caută: supabase., fetch(, anthropic., readFile(
  Verifici: are await înainte fiecare apel?
  Simptom dacă lipsește: data e undefined sau Promise {}

□ PUNCT 2 — TYPES CHECK                              [2 min]
  Caută: interface, type, câmpurile din interface
  Verifici: corespunde cu schema Supabase / tipul real din API?
  Simptom dacă greșit: câmpuri undefined la afișare, TS errors

□ PUNCT 3 — ERROR HANDLING CHECK                     [1 min]
  Caută: try/catch, if (error), .catch(
  Verifici: există pentru fiecare operație async?
  Simptom dacă lipsește: erori silențioase, UI îngheață

□ PUNCT 4 — NULL SAFETY CHECK                        [1 min]
  Caută: .find(, ?.
  Verifici: fiecare .find() are verificare pentru undefined?
  Simptom dacă lipsește: "Cannot read property of undefined"

□ PUNCT 5 — DEPENDENCIES CHECK (React)               [1 min]
  Caută: useEffect(
  Verifici: variabilele din body sunt și în dependencies array?
  Simptom dacă lipsește: date stale, comportament inconsistent
```

**Formula de aplicat: Critic → Builder din ghidul de prompting:**

```
[Primești cod de la Claude]

Acum joacă rolul unui senior TypeScript developer care face code review.
Verifică specific:
1. Lipsesc await-uri?
2. Types corespund cu schema reală Supabase?
3. Error handling prezent?
4. Null checks după .find()?
5. useEffect dependencies complete?
```

**Cum debuguiești cu `console.log` când ceva nu merge:**

`console.log` e instrumentul #1 pentru a înțelege ce se întâmplă în cod async. Știind *unde* să-l pui face diferența dintre 2 minute și 20 de minute de debugging.

```typescript
// Plasezi console.log ÎNAINTE și DUPĂ fiecare await — localizezi exact unde se rupe
async function getLeads(userId: string): Promise<Lead[]> {
  console.log('[getLeads] start — userId:', userId); // verifici că funcția se apelează
  
  const { data, error } = await supabase
    .from('leads').select('*').eq('user_id', userId);
  
  console.log('[getLeads] result — data:', data, 'error:', error); // ce a returnat Supabase
  
  if (error) throw error;
  return data ?? [];
}

// Pattern de diagnostic pentru un handler async:
const handleDelete = async (id: string) => {
  console.log('[handleDelete] id:', id);          // s-a apelat? cu ce id?
  setLoading(true);
  const { error } = await supabase.from('transactions').delete().eq('id', id);
  console.log('[handleDelete] after delete — error:', error); // a mers?
  if (!error) setTransactions(prev => prev.filter(t => t.id !== id));
  setLoading(false);
};

// Dacă consolă afișează Promise {} în loc de date:
console.log(transactions); // → Promise { <pending> } = lipsă await
```

> Prefixul `[funcție]` în log-uri te ajută să urmărești fluxul când ai mai multe apeluri simultan. Șterge log-urile de diagnostic după ce rezolvi problema — nu le lăsa în producție.

---

### PARTE 12 — Când Să Nu Ai Încredere în Claude cu JS/TS [TOATE]

**1. Versiuni specifice de librării**

Claude are un knowledge cutoff. Supabase v2, Next.js 15, React 19 — API-urile s-au schimbat față de ce a văzut Claude în training.

```typescript
// Claude poate genera pattern Supabase v1:
const { data } = supabase.from('table').select('*').single()
// în Supabase v2: .single() pe SELECT aruncă eroare dacă 0 rânduri găsite → .maybeSingle()
// Notă: .single() după INSERT (.insert().select().single()) e corect — returnează mereu 1 row

// Auth API schimbat în Supabase v2:
const user = supabase.auth.user();         // ❌ Supabase v1 — deprecated
const { data: { user } } = await supabase.auth.getUser(); // ✓ Supabase v2

// Pattern Next.js 13 Pages Router în App Router:
export async function getServerSideProps() { ... }
// ❌ Nu există în App Router — e din Pages Router
```

→ Regula: pentru orice librărie cu major update în ultimele 12 luni — verifică documentația oficială înainte să aplici.

**2. Browser APIs în Server Components (Next.js)**

```typescript
// Claude poate scrie asta în App Router (Server Component):
'use client' // ← dacă lipsește această linie → crash

import { useState } from 'react';  // useState = client-only
const saved = localStorage.getItem('data'); // localStorage = browser-only

// Semnul de pericol: window, document, localStorage, sessionStorage,
// navigator, addEventListener, useState, useEffect
// fără 'use client' la începutul fișierului
```

**3. TypeScript generic inventat pentru o librărie:**

```typescript
// Claude poate genera:
const response = await anthropic.messages.create<MyCustomType>({ ... });
// ❌ Anthropic SDK nu acceptă generic la .create()
// Dacă apare "Type 'X' does not exist" → Claude a inventat API-ul

// Verifici: caută în documentația librăriei exact acea metodă
```

**4. Edge Runtime restrictions (Vercel) — mai rar**

Relevant dacă deploy-ezi funcții Edge (`export const runtime = 'edge'`). Proiectele tale actuale nu o folosesc — ține minte pentru viitor. Unele module Node.js nu funcționează în Edge Runtime:

```typescript
// Claude poate genera cod care folosește:
import crypto from 'node:crypto'; // ❌ nu e disponibil în Edge Runtime
import fs from 'node:fs';         // ❌ același
import { Buffer } from 'buffer';  // ❌ parțial limitat

// Simptom: build pass, dar deploy pe Vercel → "Module not found: Can't resolve..."
```

→ Regula: dacă deploy-ul Vercel cade cu erori de module inexistente, verifică dacă folosești Node.js APIs în rute Edge.

**5. Halucinația de încredere — cea periculoasă:**

La fel ca în ghidul de Prompt Engineering: Claude poate confirma cu mare siguranță un comportament specific al unei librării care e greșit pentru versiunea ta.

> Adaugă în prompturi critice: `"Dacă nu ești sigur de comportamentul exact în [librărie vX], spune explicit în loc să ghicești."`

---

## BLOC 5 — REFERINȚĂ

### PARTE 13 — Flowchart: "Ce Tip de Problemă Am?"

```
Ceva nu funcționează cum trebuie
            ↓
E o eroare în consolă (roșu)?
  DA → copiaz-o literal → Template Bug Fix din ghidul de prompting
  NU → continuă
            ↓
Datele sunt undefined, null sau {} / [] gol neașteptat?
  DA → verifică: lipsă await (Parte 3) sau null check lipsă (Greșeala 5)
  NU → continuă
            ↓
data e "Promise {}" sau "[object Promise]"?
  DA → lipsă await în față la apelul async → Parte 3
  NU → continuă
            ↓
Codul pare corect dar UI nu se actualizează?
  DA React → verifică: setState cu mutare directă (Greșeala 2)
            sau useEffect dependencies (Parte 9)
  NU → continuă
            ↓
Codul funcționa și s-a stricat după adăugarea unui feature?
  DA → verifică dacă noul cod a introdus: useEffect loop (Parte 9)
       sau a mutat state direct (Greșeala 2)
  NU → continuă
            ↓
E o eroare TypeScript la compilare?
  "does not exist on type" → Claude a inventat tip → Parte 12
  "is not assignable to"   → tipuri incompatibile → Parte 2
  "Object is possibly undefined" → null check lipsă → Parte 2
            ↓
E o eroare de import (Cannot use import / not found)?
  DA Node.js → verifică Module System (Parte 6)
            ↓
Nu se reproduce consistent (apare uneori)?
  DA → probabil race condition sau stale closure → Parte 9
  NU → citește funcția cu metoda 3 pași (Parte 1) și cere ajutor lui Claude
       cu Template Bug Fix complet (eroare + cod + "3 cauze posibile")
```

---

### PARTE 14 — Transcript Real: Debugging Async Bug

**Task identic:** Pagina de tranzacții din Vibe Budget nu afișează datele.

---

**SESIUNEA SLABĂ — 25 minute, problema nerezolvată:**

```
Tu → Claude:
"de ce nu se afișează tranzacțiile?"

Claude:
[Propune: verifică dacă componenta e importată corect, verifică
Network tab în browser, adaugă console.log să vezi ce se returnează,
verifică dacă Supabase e configurat, verifică middleware de auth...]

Tu → Claude:
"am adăugat console.log și data pare goală"

Claude:
[Propune: verifică dacă userId e corect, verifică query-ul Supabase,
poate e problemă de RLS policy, verifică dacă există date în tabel...]

Tu → Claude:
"există date în tabel, verificat"

Claude:
[Propune: poate e problemă cu modul de fetch, încearcă să folosești
useEffect pentru fetch pe client, poate e Server Component și nu
funcționează bine...]

→ 5 iterații, problema tot nerezolvată
```

---

**SESIUNEA EXPERTĂ — 4 minute, rezolvată:**

```
Tu → Claude:
"Vibe Budget, app/transactions/page.tsx.
Tranzacțiile nu se afișează — consolă fără erori.
Cod relevant:

const transactions = getTransactions(userId);
return (
  <ul>
    {transactions.map(t => <li key={t.id}>{t.description}</li>)}
  </ul>
);

getTransactions e definit async. Gândește-te la 3 cauze posibile."

Claude:
"1. getTransactions e async dar lipsește await → transactions e un
   Promise object → .map() nu există pe Promise → UI afișează nimic

2. userId e undefined la momentul apelului (dacă vine din auth async)

3. getTransactions returnează null în loc de [] pe eroare → .map() crash

Cel mai probabil: cauza 1. Fix:

const transactions = await getTransactions(userId);

Și page.tsx trebuie marcat async dacă nu e deja:
export default async function TransactionsPage() { ... }"

Tu: "fix corect, funcționează"
```

**Ce a făcut diferența:**
1. Cod relevant inclus — Claude a văzut exact linia problematică
2. Specificat că funcția e async — a dat contextul critic
3. Cerut "3 cauze posibile" — Chain of Thought din ghidul de prompting

---

### PARTE 15 — Quick Reference Card

```
╔══════════════════════════════════════════════════════════════╗
║   JS & TYPESCRIPT PENTRU VIBE-CODING — Quick Reference v1.0 ║
╠══════════════════════════════════════════════════════════════╣
║  CHECKLIST PRE-APPLY [5 min înainte să aplici cod Claude]    ║
║  □ await prezent la fiecare apel Supabase/fetch/API?         ║
║  □ Interface = schema tabel Supabase reală?                  ║
║  □ try/catch sau if (error) pe operații async?               ║
║  □ null check după fiecare .find()?                          ║
║  □ useEffect dependencies complete? cleanup returnat?        ║
║  □ onClick/handler async: await prezent + loading state?     ║
╠══════════════════════════════════════════════════════════════╣
║  ARRAY METHODS — DIFERENȚA ESENȚIALĂ                         ║
║  .map()    → transformă  (array → array, SAME length)        ║
║  .filter() → selectează  (array → array, MAI MIC)            ║
║  .find()   → caută unul  (element | undefined)               ║
║  .reduce() → combină     (array → orice)                     ║
║  .some()   → cel puțin 1 (boolean)                           ║
║  .every()  → toți        (boolean)                           ║
╠══════════════════════════════════════════════════════════════╣
║  ASYNC PATTERN COMPLET                                       ║
║  async function getData(): Promise<T[]> {                    ║
║    try {                                                     ║
║      const { data, error } = await supabase                  ║
║        .from('table').select('*');                           ║
║      if (error) throw error;                                 ║
║      return data ?? [];                                      ║
║    } catch (err) {                                           ║
║      console.error(err); return [];                          ║
║    }                                                         ║
║  }                                                           ║
╠══════════════════════════════════════════════════════════════╣
║  TYPESCRIPT TYPES ESENȚIALE                                  ║
║  string · number · boolean           — primitive             ║
║  T[] sau Array<T>                    — array                 ║
║  T | null sau T | undefined          — optional              ║
║  Promise<T>                          — async return          ║
║  Partial<T>                          — câmpuri opționale     ║
║  Record<K, V>                        — map cu tip fix        ║
║  Omit<T, K>                          — exclude câmpuri       ║
║  void                                — fără return           ║
║  unknown                             — tipul sigur necunoscut║
║  any                                 — EVITĂ               ║
╠══════════════════════════════════════════════════════════════╣
║  ERORI FRECVENTE → CAUZA                                     ║
║  .map is not a function  → lipsă await (data e Promise)      ║
║  Cannot read property    → obiect null/undefined             ║
║  data = Promise {}       → lipsă await                       ║
║  Render infinit          → useEffect dependency lipsă        ║
║  does not exist on type  → Claude a inventat tipul           ║
║  Cannot use import       → ESM/CJS mismatch (Parte 6)        ║
╠══════════════════════════════════════════════════════════════╣
║  SECURITATE — NICIODATĂ                                      ║
║  × innerHTML = userInput          (XSS)                      ║
║  × eval(userInput)                (code injection)           ║
║  × chei API în cod client         (expunere publică)         ║
║  × dangerouslySetInnerHTML        (XSS React)                ║
║  × userId din params/body         (bypass auth Supabase)     ║
╠══════════════════════════════════════════════════════════════╣
║  MODULE SYSTEM [Node.js/Next.js]                             ║
║  package.json: "type": "module"   → activezi ESM             ║
║  import { x } from './file.js'   → extensia .js OBLIGATORIE ║
║  Cannot use import statement      → lipsă "type":"module"    ║
╚══════════════════════════════════════════════════════════════╝
```

---

*v1.0 · Mai 2026 · Skill 2 din seria Vibe-Coding cu Claude*
*Bazat pe proiectele: Vibe Budget, StudioFlow, ERP Financiar, Clinică Medicală, Agenți AI, CashPulse, FollowUp Board*
