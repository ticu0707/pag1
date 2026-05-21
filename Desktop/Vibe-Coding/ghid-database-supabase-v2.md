# GHID PRACTIC: Database Design & Supabase/PostgreSQL pentru Vibe-Coding
**Skill 5 — v2.0 · Ediție Expert**
**Data:** Mai 2026 | **Nivel:** Beginner → Expert
**Timp realist:** 90 min citit + practică pe proiectele tale

---

## TL;DR — 3 Lucruri Care Schimbă Totul

Dacă citești doar atât, reții esența:

1. **O schemă proastă se plătește cu săptămâni de rework.** Spre deosebire de cod, o tabelă cu structura greșită nu se refactorizează în 5 minute — ai date reale acolo. Planifică schema ÎNAINTE să scrii primul `INSERT`.

2. **RLS dezactivat = orice user vede datele tuturor.** Row Level Security în Supabase nu e opțional pentru proiecte cu autentificare. Fără policy corectă, `SELECT * FROM invoices` returnează facturile tuturor utilizatorilor, nu doar ale celui logat.

3. **`await` + `if (error) throw error` la fiecare query.** Supabase nu aruncă excepții automat — returnează `{ data, error }`. Dacă ignori câmpul `error`, rulezi pe date corupte sau `null` fără să știi.

---

## Cum Să Folosești Ghidul

**Prima dată:** Citește liniar Bloc 1 + Bloc 2 (~30 min). Bloc 1 te salvează de refactoring dureros; Bloc 2 e toolkit-ul zilnic.

**Proiect nou:** Începe cu Parte 0 (normalizare) + Parte 2 (relații) + Parte 6 (RLS) — cele 3 decizii ireversibile.

**Ceva nu funcționează:** Salt direct la Parte 13 (greșeli comune) sau Parte 15 (checklist).

**Referință rapidă:** Parte 17 (Quick Reference Card) — deschide în orice sesiune.

**Dacă lucrezi pe proiecte financiare** (ERP, FinanceOS, Clinică): prioritizează Parte 10 (Funcții) și Parte 11 (Transactions + Isolation).

**Dacă ești în StudioFlow sau CRM:** citește obligatoriu Parte 2 (relații N:N) și Parte 9 (Views).

---

## Learning Map

```
BLOC 1 — SCHEMA DESIGN CORECT                     [ERP, FinanceOS, Clinică, StudioFlow]
  [0]  Normalizare + Denormalizare deliberată — când să rupi regulile
  [1]  Tipuri de Date PostgreSQL — ce alegi când (incl. citext, domain)
  [2]  Relații (1:1, 1:N, N:N) — cum le modelezi în Supabase  ★

BLOC 2 — SUPABASE: SCRIS ȘI CITIT DATE
  [3]  SELECT + JOINuri în Supabase — fără SQL brut + N+1 evitat  [TOATE]
  [4]  INSERT / UPDATE / DELETE — pattern-urile corecte           [TOATE]
  [5]  Filtre avansate + paginare + cursor pagination              [TOATE]  ★

BLOC 3 — SECURITATE ȘI PERFORMANȚĂ
  [6]  RLS (Row Level Security) — cum funcționează + FORCE RLS     ★★
  [7]  Policies RLS — SELECT/INSERT/UPDATE/DELETE + admin + public ★★
  [8]  Indexare — B-Tree, GIN, BRIN, compuși, INCLUDE, CONCURRENTLY

BLOC 4 — OPERAȚII COMPLEXE
  [9]  Views — date agregate + securitate corectă + CRON refresh
  [10] Funcții și Triggers — SECURITY DEFINER + volatility + FOR EACH STATEMENT
  [11] Transactions — FOR UPDATE, isolation levels, deadlock prevention
  [12] Migrations — soft delete + schimbări fără downtime + rollback

BLOC 5 — DEBUGGING ȘI TOOLKIT
  [13] 13 Greșeli Comune DB (before/after)
  [14] TypeScript pentru Supabase — typed client, types, Omit, generics
  [15] Checklist Pre-Deploy                                        ★
  [16] Supabase Realtime — subscriptions + RLS + error handling
  [17] Quick Reference Card
```

`★` = Citit obligatoriu înainte de primul proiect cu Supabase
`★★` = Cel mai mare risc de securitate — nu sări peste

---

## BLOC 1 — Schema Design Corect

---

### Parte 0 — Normalizare și Denormalizare Deliberată

**Regula de bază:** Fiecare informație se stochează o singură dată, în locul care îi aparține semantic. Dar regula are excepții intenționate — și un expert le cunoaște pe amândouă.

#### Cele 3 forme normale — explicate cu exemple reale

**1NF (Prima Formă Normală):** Niciun câmp nu conține mai multe valori.

```sql
-- ✗ GREȘIT: câmp cu valori multiple
CREATE TABLE orders (
  id uuid PRIMARY KEY,
  products text  -- "Cafea,Lapte,Zahăr" — imposibil de filtrat/numărat
);

-- ✓ CORECT: tabel separat pentru produse
CREATE TABLE order_items (
  id        uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  order_id  uuid REFERENCES orders(id) ON DELETE CASCADE,
  product   text NOT NULL,
  quantity  integer NOT NULL DEFAULT 1
);
```

**2NF (A Doua Formă Normală):** Câmpurile non-cheie depind de TOATĂ cheia primară, nu de o parte din ea.

```sql
-- ✗ GREȘIT: order_items conține date despre produs (depind doar de product_id, nu de order_id)
CREATE TABLE order_items (
  order_id    uuid,
  product_id  uuid,
  product_name  text,    -- duplicat în fiecare rând!
  product_price numeric, -- duplicat în fiecare rând!
  quantity    integer,
  PRIMARY KEY (order_id, product_id)
);

-- ✓ CORECT: datele produsului stau în tabelul products
CREATE TABLE products (
  id    uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  name  text NOT NULL,
  price numeric(10,2) NOT NULL
);

CREATE TABLE order_items (
  order_id    uuid REFERENCES orders(id) ON DELETE CASCADE,
  product_id  uuid REFERENCES products(id),
  quantity    integer NOT NULL DEFAULT 1,
  unit_price  numeric(10,2) NOT NULL,  -- prețul LA MOMENTUL comenzii, nu referință live
  PRIMARY KEY (order_id, product_id)
);
```

> **Notă importantă pentru date financiare:** `unit_price` se stochează ca valoare copiată, nu ca referință la `products.price`. Dacă prețul produsului se schimbă mâine, comenzile vechi trebuie să rămână cu prețul de atunci. Acesta este un exemplu de **denormalizare deliberată** (vezi mai jos).

**3NF (A Treia Formă Normală):** Câmpurile non-cheie depind direct de cheie, nu de alt câmp non-cheie.

```sql
-- ✗ GREȘIT: zip_code determină city și state — transitivitate
CREATE TABLE clients (
  id        uuid PRIMARY KEY,
  name      text,
  zip_code  text,
  city      text,  -- depinde de zip_code, nu de id
  state     text   -- depinde de zip_code, nu de id
);

-- ✓ CORECT: adresa în JSONB dacă nu filtrezi după ea
CREATE TABLE clients (
  id      uuid PRIMARY KEY,
  name    text NOT NULL,
  address jsonb  -- {zip, city, state, street} — simplu, dacă nu filtrezi după city
);
```

---

#### Denormalizare deliberată — când să rupi 3NF intenționat

Normalizarea totală e ideală pe hârtie, dar în practică există scenarii în care un câmp calculat sau duplicat e cea mai bună decizie. Criteriul: **dacă calculul e scump și datele sursă nu se schimbă frecvent, stochează rezultatul.**

**Exemplul 1 — Total factură calculat și stocat**

```sql
-- ✗ NORMALIZAT DAR LENT: calculezi SUM la fiecare afișare
SELECT i.id, SUM(ii.quantity * ii.unit_price) AS total
FROM invoices i
JOIN invoice_items ii ON ii.invoice_id = i.id
GROUP BY i.id;
-- Pe 100.000 facturi cu 10 items fiecare = 1.000.000 rânduri scanate pentru dashboard

-- ✓ DENORMALIZAT DELIBERAT: total_amount stocat pe factură
CREATE TABLE invoices (
  id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  total_amount  numeric(12,2) NOT NULL DEFAULT 0,  -- redundant, dar rapid
  ...
);
-- Actualizat prin trigger la fiecare INSERT/UPDATE/DELETE pe invoice_items
-- Dashboard-ul face SELECT simplu, fără JOIN
```

**Exemplul 2 — Câmp `items_count` pe o comandă**

```sql
-- Stochezi numărul de items pe comandă pentru listele paginare
ALTER TABLE orders ADD COLUMN items_count integer NOT NULL DEFAULT 0;
-- Actualizat prin trigger — evită COUNT() la fiecare listare
```

**Regula de decizie:**

| Criterii | Normalizat | Denormalizat |
|---|---|---|
| Datele sursă se schimbă des | ✓ | |
| Query-ul e rulat o dată la mii de ori | ✓ | |
| Dashboard, listare, paginare frecventă | | ✓ |
| Date financiare cu valoare la moment fix | | ✓ (snapshot) |
| Poate fi actualizat prin trigger | | ✓ |

---

#### Pattern: Soft Delete — ștergere logică, nu fizică

În aplicații financiare, CRM și orice proiect unde datele șterse trebuie să fie recuperabile sau auditabile, nu ștergi rânduri — le marchezi ca șterse.

```sql
-- Adaugi câmpul pe orice tabelă care necesită soft delete
ALTER TABLE invoices ADD COLUMN deleted_at timestamptz DEFAULT NULL;
-- NULL = activ | timestamp = șters la acel moment

-- View care expune doar rândurile active
CREATE VIEW active_invoices AS
SELECT * FROM invoices WHERE deleted_at IS NULL;

-- Index parțial — indexezi DOAR rândurile active (mai mic, mai rapid)
CREATE INDEX CONCURRENTLY idx_invoices_active
ON invoices(created_at DESC)
WHERE deleted_at IS NULL;

-- Supabase JS — filtrezi în query
const { data, error } = await supabase
  .from('invoices')
  .select('*')
  .is('deleted_at', null);  -- sau folosești view-ul active_invoices

-- "Ștergere" soft
const { error } = await supabase
  .from('invoices')
  .update({ deleted_at: new Date().toISOString() })
  .eq('id', invoiceId);

-- Restaurare
const { error } = await supabase
  .from('invoices')
  .update({ deleted_at: null })
  .eq('id', invoiceId);
```

> **Când să folosești soft delete:** proiecte cu audit trail (ERP, FinanceOS, Clinică), date cu valoare legală, orice loc unde userul poate cere recuperarea datelor. **Când să NU folosești:** tabele cu date efemere (sesiuni, log-uri, queue-uri) — cresc nelimitat și complică indexarea.

#### Trade-off critic: soft delete în RLS policy vs în query

Există două locuri unde poți pune filtrul `deleted_at IS NULL`. Alegerea are consecințe majore:

```sql
-- OPȚIUNEA A: filtrul în policy RLS
CREATE POLICY "select own" ON invoices FOR SELECT
  USING (auth.uid() = user_id AND deleted_at IS NULL);
-- Avantaj: simplu, userul NU poate vedea rânduri șterse niciodată
-- ⚠️ Dezavantaj: restore/audit IMPOSIBIL din Supabase JS client
-- → Un .update({ deleted_at: null }) pe un rând șters va returna 0 rows affected
--   (policy blochează chiar și UPDATE pe rânduri "invizibile")
-- → Restore necesită obligatoriu funcție RPC cu SECURITY DEFINER sau service_role

-- OPȚIUNEA B: filtrul în query (recomandat pentru ERP/CRM cu audit)
CREATE POLICY "select own" ON invoices FOR SELECT
  USING (auth.uid() = user_id);  -- policy fără filtru deleted_at

-- Filtrul vine din query, explicit:
const { data } = await supabase
  .from('invoices')
  .select('*')
  .is('deleted_at', null);  // normal — doar active

// Restore din client (posibil cu Opțiunea B, imposibil cu A):
const { error } = await supabase
  .from('invoices')
  .update({ deleted_at: null })
  .eq('id', invoiceId);
```

> **Recomandare:** Opțiunea B pentru proiecte cu audit/restore. Opțiunea A dacă vrei să garantezi prin arhitectură că userul nu vede niciodată date șterse — cu condiția să ai o rută de restore via RPC.

#### Autovacuum — îngrijire obligatorie pentru tabele cu soft delete

Tabelele cu soft delete acumulează **dead tuples** (rânduri "șterse" logic dar fizic prezente). PostgreSQL autovacuum le curăță automat, dar pe tabele mari cu delete frecvent, default-urile pot fi insuficiente:

```sql
-- Verifică dead tuples pe o tabelă
SELECT relname, n_dead_tup, n_live_tup,
       round(n_dead_tup::numeric / NULLIF(n_live_tup + n_dead_tup, 0) * 100, 1) AS dead_pct
FROM pg_stat_user_tables
WHERE relname = 'invoices';
-- dead_pct > 20% → vacuum agresiv recomandat

-- Rulează manual dacă autovacuum nu ține pasul (ex: batch delete masiv)
VACUUM ANALYZE invoices;

-- Configurare per-tabelă dacă ai soft deletes frecvente (mii/zi)
ALTER TABLE invoices SET (
  autovacuum_vacuum_scale_factor = 0.05,  -- vacuum la 5% dead tuples (default: 20%)
  autovacuum_analyze_scale_factor = 0.02
);
```

---

#### Regula practică pentru vibe-coding

Înainte să creezi o tabelă, răspunde la 4 întrebări:
1. **Ce entitate reprezintă?** (un client, o factură, o programare — nu "date despre X")
2. **Ce face unic fiecare rând?** (ID-ul UUID + care câmpuri îl identifică semantic)
3. **Ce alte entități depind de asta?** (lista tabelelor care vor folosi un foreign key spre aceasta)
4. **Datele se pot șterge sau trebuie păstrate?** (soft delete vs hard delete)

---

### Parte 1 — Tipuri de Date PostgreSQL

Alegerea greșită de tip de date cauzează bug-uri greu de diagnosticat și pierderi de performanță.

#### Referință rapidă: ce tip alegi când

```sql
-- TEXT — pentru date de business
name          text          -- text fără limită — echivalent cu varchar în PG
description   text          -- text lung — blog posts, notițe
code          varchar(10)   -- dacă vrei să LIMITEZI lungimea (ex: cod poștal, ISO code)
                            -- varchar(n) și text cu CHECK sunt echivalente ca performanță

-- CITEXT — text case-insensitive (email, username)
-- Necesită: CREATE EXTENSION IF NOT EXISTS citext;
email         citext UNIQUE  -- 'Ion@Popescu.com' = 'ion@popescu.com' automat
                             -- Alternativă fără extensie: text + index UNIQUE pe lower(email)
                             -- CREATE UNIQUE INDEX idx_users_email ON users(lower(email));

-- NUMERIC — pentru bani și precizie
price         numeric(10,2) -- bani — NICIODATĂ float/real (erori de rotunjire!)
quantity      integer       -- numere întregi — int4
large_count   bigint        -- contoare mari (views, clicks) — int8

-- UUID — chei primare (nu serial/bigserial — UUID-urile nu sunt predictibile din exterior)
id  uuid PRIMARY KEY DEFAULT gen_random_uuid()
-- gen_random_uuid() e built-in din PostgreSQL 13+ — fără extensie suplimentară
-- NU folosi serial/bigserial pentru chei primare în proiecte noi — UUID e standard

-- Dată și timp
created_at    timestamptz DEFAULT now()  -- timestamptz = cu timezone (OBLIGATORIU)
event_date    date                       -- doar data, fără oră (birthday, deadline)
duration_min  integer                    -- durata în minute — simplu de lucrat în JS

-- Boolean
is_active     boolean DEFAULT true
is_paid       boolean DEFAULT false

-- JSON
metadata      jsonb  -- JSONB: binar, permite indexare GIN, operatori @> și ?
settings      jsonb  -- preferă jsonb în 99% din cazuri față de json
               -- json (fără 'b'): text exact, păstrează ordinea cheilor —
               -- util doar când ai nevoie de ordinea exactă sau spații originale

-- Enumerare
status  text CHECK (status IN ('draft','sent','paid','overdue'))
-- SAU enum tip separat — mai rigid, mai greu de migrat (adăugare valoare = ALTER TYPE):
-- CREATE TYPE invoice_status AS ENUM ('draft','sent','paid','overdue');
-- Recomandare: text + CHECK pentru flexibilitate; ENUM dacă vrei tip de date în schema

-- Array (rar, dar util)
tags  text[]  -- ['marketing','vip','recurent'] — indexabil cu GIN
```

#### Cele mai frecvente greșeli de tip

```sql
-- ✗ float pentru bani — erori de rotunjire garantate
price  float  -- 19.99 + 0.01 = 20.000000000002 în float

-- ✓ numeric pentru bani — precizie exactă
price  numeric(10,2)  -- 10 cifre total, 2 zecimale

-- ✗ timestamp fără timezone — ambiguitate la DST
created_at  timestamp  -- 03:00 la schimbarea orei? Imposibil de știut

-- ✓ timestamptz — stochează UTC, afișează corect în orice timezone
created_at  timestamptz DEFAULT now()

-- ✗ varchar(255) fără motiv — moștenire MySQL, fără beneficiu în PG dacă nu vrei limita
name  varchar(255)  -- același spațiu și performanță ca text în PG

-- ✓ text dacă nu ai nevoie de limită
name  text NOT NULL
-- ✓ varchar(n) dacă ai nevoie de limită explicită
country_code  varchar(2)  -- ISO: 'RO', 'US', 'DE'
```

#### Domain types — validare la nivel de tip

```sql
-- Poți crea tipuri reutilizabile cu CHECK constraints încorporate
-- Util când același tip apare în mai multe tabele
CREATE DOMAIN positive_numeric AS numeric CHECK (VALUE > 0);
CREATE DOMAIN email_address AS text CHECK (VALUE ~ '^[^@\s]+@[^@\s]+\.[^@\s]+$');

-- Folosire:
CREATE TABLE invoices (
  amount  positive_numeric NOT NULL,  -- CHECK (amount > 0) implicit
  ...
);
CREATE TABLE users (
  email  email_address UNIQUE NOT NULL  -- validare email la nivel DB
);
-- Schimbi domainul → schimbarea se propagă în toate tabelele care îl folosesc
```

---

### Parte 2 — Relații: 1:1, 1:N, N:N

#### 1:N — cel mai comun (un client are multe facturi)

```sql
CREATE TABLE clients (
  id    uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  name  text NOT NULL
);

CREATE TABLE invoices (
  id          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  client_id   uuid NOT NULL REFERENCES clients(id) ON DELETE RESTRICT,
  -- ON DELETE RESTRICT: nu poți șterge clientul dacă are facturi
  -- ON DELETE CASCADE: șterge facturile când ștergi clientul
  -- ON DELETE SET NULL: NULL pe client_id — folosit când relația e opțională
  amount      numeric(10,2) NOT NULL,
  created_at  timestamptz DEFAULT now()
);

-- Index obligatoriu pe foreign key (Supabase nu-l adaugă automat!)
CREATE INDEX CONCURRENTLY idx_invoices_client_id ON invoices(client_id);
```

#### 1:1 — date suplimentare pe un user (profil extins)

```sql
-- Tabelul auth.users e creat de Supabase — nu-l modifica direct
CREATE TABLE profiles (
  id          uuid PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  -- NU gen_random_uuid() — același UUID ca auth.users!
  full_name   text,
  avatar_url  text,
  company     text,
  updated_at  timestamptz DEFAULT now()
);
```

#### N:N — un proiect are mulți membri, un membru e în mai multe proiecte

```sql
CREATE TABLE project_members (
  project_id  uuid REFERENCES projects(id) ON DELETE CASCADE,
  user_id     uuid REFERENCES auth.users(id) ON DELETE CASCADE,
  role        text CHECK (role IN ('owner','editor','viewer')) DEFAULT 'viewer',
  joined_at   timestamptz DEFAULT now(),
  PRIMARY KEY (project_id, user_id)
);

CREATE INDEX CONCURRENTLY idx_project_members_user_id ON project_members(user_id);
```

#### SELECT N:N în Supabase JS — sintaxa corectă cu hint

```typescript
// Supabase JS necesită hint explicit pentru relații N:N cu redenumire
// Sintaxa: alias!foreign_key_column(câmpuri)
const { data, error } = await supabase
  .from('projects')
  .select(`
    id,
    name,
    project_members (
      role,
      profiles!project_members_user_id_fkey (
        id,
        full_name
      )
    )
  `);
// ✗ GREȘIT (nu funcționează): users: user_id (id, email)
// ✓ CORECT: profiles!project_members_user_id_fkey(id, full_name)
// Hint-ul este necesar când PostgREST nu poate deduce automat foreign key-ul
// (ambiguitate sau redenumire de tabelă)
```

#### Alegerea ON DELETE — tabel de decizie

| Scenariu | ON DELETE |
|---|---|
| Factură → Client (nu șterge clientul cu facturi) | `RESTRICT` |
| Order items → Order (dacă comanda e ștearsă, și items dispar) | `CASCADE` |
| Post → Author (postul rămâne dacă userul e șters) | `SET NULL` |
| Profile → auth.users | `CASCADE` |
| Project members → Project | `CASCADE` |
| Log entries → User (log-urile rămân) | `SET NULL` |

---

## BLOC 2 — Supabase: Scris și Citit Date

---

### Parte 3 — SELECT + JOINuri în Supabase

#### SELECT de bază

```typescript
// Citire simplă — toate rândurile
const { data, error } = await supabase
  .from('invoices')
  .select('*');
if (error) throw error;
const invoices = data ?? [];

// Câmpuri specifice — mai rapid, mai sigur (nu expui date sensibile)
const { data, error } = await supabase
  .from('invoices')
  .select('id, amount, status, created_at');
if (error) throw error;

// Un singur rând după ID
const { data, error } = await supabase
  .from('invoices')
  .select('*')
  .eq('id', invoiceId)
  .maybeSingle();  // .single() aruncă eroare dacă nu găsește nimic
if (error) throw error;
if (!data) { /* nu există */ }
```

#### SELECT cu relații (JOIN implicit) — și cum eviți N+1

> **Problema N+1** este cel mai comun bug de performanță în aplicații cu query builder. Apare când faci un query pentru lista de entități și apoi câte un query separat pentru fiecare entitate:
>
> ```typescript
> // ✗ N+1: 1 query pentru clienți + N queries pentru facturile fiecăruia
> const { data: clients } = await supabase.from('clients').select('*');
> for (const client of clients) {
>   const { data: invoices } = await supabase
>     .from('invoices').select('*').eq('client_id', client.id);
>   // 100 clienți = 101 queries!
> }
> ```
>
> **Soluția:** un singur SELECT cu embedding de relații:

```typescript
// ✓ UN singur query — Supabase face JOIN pe server
const { data, error } = await supabase
  .from('clients')
  .select(`
    id,
    name,
    invoices (
      id,
      amount,
      status,
      created_at
    )
  `);
if (error) throw error;
// data[0].invoices — array de facturi pentru primul client
// Total: 1 query, nu N+1

// Relație inversă: facturile cu datele clientului incluse
const { data, error } = await supabase
  .from('invoices')
  .select(`
    id,
    amount,
    status,
    created_at,
    clients (
      id,
      name,
      email
    )
  `);
if (error) throw error;
// data[0].clients.name — accesezi direct obiectul client
```

#### Agregări și numărare

```typescript
// Numără rânduri (fără să le aduci) — HEAD request, fără date
const { count, error } = await supabase
  .from('invoices')
  .select('*', { count: 'exact', head: true })
  .eq('client_id', clientId);
if (error) throw error;
// count = numărul de facturi

// ⚠️ count: 'exact' face full table scan — LENT pe tabele mari (>500k rânduri)
// Pentru UI "aproximativ N rezultate" pe tabele mari, folosești 'estimated':
const { count } = await supabase
  .from('invoices')
  .select('*', { count: 'estimated', head: true });
// 'estimated' = statistici PG (pg_class.reltuples) — instant dar inexact ±10%

// Verificare rapidă dacă un rând există
const { count } = await supabase
  .from('invoices')
  .select('*', { count: 'exact', head: true })
  .eq('id', invoiceId)
  .eq('user_id', userId);
const exists = (count ?? 0) > 0;

// Agregări PostgREST v12+ (Supabase din 2023+) — fără view sau RPC
const { data, error } = await supabase
  .from('invoices')
  .select('amount.sum(), amount.avg(), id.count()')
  .eq('client_id', clientId)
  .is('deleted_at', null);
if (error) throw error;
// data[0] = { sum: '15200.50', avg: '760.025', count: '20' } — valori ca string!
// Convertire: Number(data[0]?.sum ?? '0')

// Agregări cu alias — necesare când ai mai multe pe aceeași coloană
const { data } = await supabase
  .from('invoices')
  .select('amount.sum(), amount.max(), amount.min()');
// data[0] = { sum: '...', max: '...', min: '...' }

// Agregări complexe (group by, multiple condiții) → view sau funcție RPC
```

---

### Parte 4 — INSERT / UPDATE / DELETE

#### INSERT corect

```typescript
// INSERT un rând — returnează rândul creat
const { data, error } = await supabase
  .from('invoices')
  .insert({
    client_id: clientId,
    amount: 1500.00,
    status: 'draft'
    // id, created_at — generate automat de DB
  })
  .select()  // OBLIGATORIU dacă vrei datele înapoi
  .single(); // INSERT returnează exact 1 rând — .single() e corect
if (error) throw error;
const newInvoice = data; // are id, created_at populate de DB

// INSERT multiplu
const { data, error } = await supabase
  .from('order_items')
  .insert([
    { order_id: orderId, product_id: 'p1', quantity: 2, unit_price: 10 },
    { order_id: orderId, product_id: 'p2', quantity: 1, unit_price: 25 }
  ])
  .select();
if (error) throw error;

// UPSERT — INSERT sau UPDATE dacă există
// Default: conflict pe PRIMARY KEY
const { data, error } = await supabase
  .from('profiles')
  .upsert({ id: userId, full_name: 'Ion Popescu', updated_at: new Date().toISOString() })
  .select()
  .single();
if (error) throw error;

// UPSERT cu conflict pe altă coloană — folosești onConflict
// Util când cheia de unicitate e pe un câmp != id (ex: email, slug)
const { data, error } = await supabase
  .from('users')
  .upsert(
    { email: 'ion@example.com', name: 'Ion', updated_at: new Date().toISOString() },
    { onConflict: 'email' }  // ← specifici coloana de conflict (necesită UNIQUE constraint)
  )
  .select()
  .single();
if (error) throw error;
// Dacă există rând cu același email → UPDATE; altfel → INSERT
```

#### UPDATE corect

```typescript
// UPDATE cu WHERE — OBLIGATORIU să ai un filtru
const { data, error } = await supabase
  .from('invoices')
  .update({ status: 'paid' })
  .eq('id', invoiceId)  // FĂRĂ .eq() → updatezi TOATE rândurile!
  .select()
  .single();
if (error) throw error;

// UPDATE mai multe câmpuri
const { data, error } = await supabase
  .from('clients')
  .update({
    name: newName,
    email: newEmail,
    updated_at: new Date().toISOString()
  })
  .eq('id', clientId)
  .select()
  .single();
if (error) throw error;
```

#### DELETE corect

```typescript
// DELETE cu WHERE — OBLIGATORIU
const { error } = await supabase
  .from('invoices')
  .delete()
  .eq('id', invoiceId);  // FĂRĂ .eq() → ștergi TOATE rândurile!
if (error) throw error;

// DELETE și returnează ce ai șters (util pentru undo)
const { data, error } = await supabase
  .from('invoices')
  .delete()
  .eq('id', invoiceId)
  .select()
  .single();
if (error) throw error;
const deleted = data; // ai datele înainte de ștergere
```

#### `.throwOnError()` — pattern alternativ (Supabase JS v2.49+)

```typescript
// Pattern clasic — manual if (error) throw error la fiecare query
const { data, error } = await supabase.from('invoices').select('*');
if (error) throw error;

// Pattern modern — .throwOnError() aruncă automat dacă există eroare
// Elimină boilerplate-ul, dar nu mai ai acces la obiectul error pentru logare fină
const { data } = await supabase
  .from('invoices')
  .select('*')
  .throwOnError();
const invoices = data ?? [];  // data nu poate fi null dacă nu s-a aruncat excepție

// Util în funcții helper unde vrei să propagezi eroarea sus
async function getInvoices(userId: string) {
  const { data } = await supabase
    .from('invoices')
    .select('*')
    .eq('user_id', userId)
    .throwOnError();
  return data ?? [];
}
// Recomandare: folosești un singur pattern consistent în proiect (nu amesteca)
```

---

### Parte 5 — Filtre Avansate și Paginare

#### Filtre disponibile în Supabase JS

```typescript
// Egalitate și comparație
.eq('status', 'paid')           // status = 'paid'
.neq('status', 'draft')         // status != 'draft'
.gt('amount', 1000)             // amount > 1000
.gte('amount', 1000)            // amount >= 1000
.lt('amount', 1000)             // amount < 1000
.lte('amount', 1000)            // amount <= 1000

// Text și pattern matching
.ilike('name', '%popescu%')     // ILIKE — case insensitive LIKE
.like('name', 'Ion%')           // LIKE — case sensitive

// Full-text search — necesită index GIN cu tsvector
.textSearch('description', 'servicii web', { type: 'websearch' })
// Necesită index: CREATE INDEX CONCURRENTLY idx_invoices_fts
//   ON invoices USING gin(to_tsvector('romanian', description));
// type: 'websearch' → suportă operatori: "servicii web" OR consultanta

// Liste
.in('status', ['draft', 'sent'])        // IN (...)
.not('status', 'in', '("paid","void")')  // NOT IN

// NULL
.is('deleted_at', null)         // IS NULL — soft delete activ
.not('deleted_at', 'is', null)  // IS NOT NULL — rânduri șterse

// OR condiții — .or() combinator
.or('status.eq.draft,status.eq.sent')          // status = 'draft' OR status = 'sent'
.or('name.ilike.%ion%,email.ilike.%ion%')      // caută în două câmpuri
// Echivalent cu .in() pentru valori fixe — prefer .in() pentru claritate

// JSONB și arrays
.contains('metadata', { currency: 'RON' })     // JSONB conține perechea dată
.containedBy('tags', ['vip', 'premium', 'nou']) // tags e subset al array-ului dat
.overlaps('tags', ['vip', 'premium'])           // tags are cel puțin un element comun

// Range de date
.gte('created_at', '2026-01-01')
.lt('created_at', '2027-01-01')

// Sortare și paginare
.order('created_at', { ascending: false })        // ORDER BY DESC
.order('amount', { ascending: true, nullsFirst: false })  // NULLS LAST — implicit
.limit(20)                                        // LIMIT 20
.range(0, 19)                                     // OFFSET 0 LIMIT 20
```

#### Pattern paginare cu OFFSET — simplu, pentru tabele mici

```typescript
const PAGE_SIZE = 20;

async function fetchInvoices(page: number, status?: string) {
  let query = supabase
    .from('invoices')
    .select('*', { count: 'exact' })
    .is('deleted_at', null)
    .order('created_at', { ascending: false })
    .range(page * PAGE_SIZE, (page + 1) * PAGE_SIZE - 1);

  if (status) query = query.eq('status', status);

  const { data, error, count } = await query;
  if (error) throw error;
  return {
    items: data ?? [],
    total: count ?? 0,
    hasMore: (count ?? 0) > (page + 1) * PAGE_SIZE
  };
}
// ⚠️ OFFSET e lent pe tabele mari: .range(50000, 50019) scanează 50.020 rânduri
// Potrivit pentru: tabele < 50k rânduri sau când userul navigă pagini (nu scroll infinit)
```

#### Pattern paginare cu cursor — rapid, pentru tabele mari și scroll infinit

```typescript
// CURSOR paginare = "adu-mi înregistrările mai vechi decât ultimul item văzut"
// Cost constant indiferent de poziție — ideal pentru scroll infinit
const PAGE_SIZE = 20;

async function fetchNextPage(lastCreatedAt: string | null, userId: string) {
  let query = supabase
    .from('invoices')
    .select('id, amount, status, created_at')
    .eq('user_id', userId)
    .is('deleted_at', null)
    .order('created_at', { ascending: false })
    .limit(PAGE_SIZE);

  if (lastCreatedAt) {
    // Înregistrările MAI VECHI decât ultimul item afișat
    query = query.lt('created_at', lastCreatedAt);
  }

  const { data, error } = await query;
  if (error) throw error;
  return data ?? [];
}

// Utilizare în React:
const [items, setItems] = useState<Invoice[]>([]);
const lastItemRef = useRef<string | null>(null);

async function loadMore() {
  const newItems = await fetchNextPage(lastItemRef.current, userId);
  if (newItems.length > 0) {
    setItems(prev => [...prev, ...newItems]);
    lastItemRef.current = newItems[newItems.length - 1].created_at;
  }
}

// Prima pagină: loadMore() cu lastCreatedAt = null
// Pagini următoare: loadMore() cu lastCreatedAt = created_at al ultimului item

// NOTĂ: dacă ai timestamp-uri identice (import batch), adaugi tie-breaker pe id:
// .order('created_at', { ascending: false })
// .order('id', { ascending: false })
// query = query.or(`created_at.lt.${lastCreatedAt},and(created_at.eq.${lastCreatedAt},id.lt.${lastId})`);
```

---

## BLOC 3 — Securitate și Performanță

---

### Parte 6 — RLS: Cum Funcționează cu Adevărat

**Row Level Security (RLS)** este mecanismul prin care PostgreSQL filtrează automat rândurile bazat pe identitatea utilizatorului. Fără RLS activ, orice query client-side returnează TOATE datele din tabelă — indiferent de cine e logat.

#### Starea RLS — verificare și activare

```sql
-- Verifică dacă RLS e activ pe o tabelă
SELECT tablename, rowsecurity
FROM pg_tables
WHERE schemaname = 'public';

-- Activează RLS pe o tabelă
ALTER TABLE invoices ENABLE ROW LEVEL SECURITY;

-- IMPORTANT: RLS activ fără policies = nimeni nu poate citi/scrie (deny all by default)
-- Adaugă policies IMEDIAT după activare
```

#### `FORCE ROW LEVEL SECURITY` — când contează

În PostgreSQL, owner-ul tabelei bypass-ează implicit RLS — chiar dacă `ENABLE ROW LEVEL SECURITY` e activ. În Supabase, userul `postgres` este owner pe toate tabelele publice.

```sql
-- RLS activ dar bypass posibil pentru owner (postgres):
ALTER TABLE invoices ENABLE ROW LEVEL SECURITY;
-- postgres user: SELECT * FROM invoices → returnează TOATE rândurile (bypass!)

-- FORCE RLS — aplică policies și pentru owner:
ALTER TABLE invoices FORCE ROW LEVEL SECURITY;
-- postgres user: SELECT * FROM invoices → filtrat prin policies

-- Când e relevant în Supabase:
-- ✓ Conectezi direct cu credențiale postgres (script admin, pg client)
-- ✓ Folosești service_role? Service_role bypass-ează RLS indiferent de FORCE
--   (FORCE RLS nu afectează service_role — acesta operează cu SET session_replication_role)
-- ✓ API Supabase cu anon/authenticated? RLS e activ fără FORCE — FORCE e redundant dar inofensiv

-- Recomandare: adaugă FORCE RLS pe tabele cu date sensibile ca măsură de siguranță extra
ALTER TABLE invoices FORCE ROW LEVEL SECURITY;
ALTER TABLE profiles FORCE ROW LEVEL SECURITY;
ALTER TABLE accounts FORCE ROW LEVEL SECURITY;
```

#### Identitatea curentă — `auth.uid()` și `auth.role()`

```sql
-- auth.uid() — UUID-ul userului logat (din JWT Supabase)
-- Returnează NULL dacă userul nu e autentificat (role = 'anon')

-- auth.role() — rolul curent: 'anon' sau 'authenticated'
-- 'anon'          = utilizator nelogat (cheie anon publică)
-- 'authenticated' = utilizator logat (JWT valid)

-- Exemplu: policy SELECT care permite citire proprie
CREATE POLICY "users see own invoices"
ON invoices FOR SELECT
USING (auth.uid() = user_id);
-- USING = condiție aplicată la citire (SELECT)
-- WITH CHECK = condiție aplicată la scriere (INSERT/UPDATE)

-- Exemplu: policy pentru date PUBLICE (orice vizitator poate citi)
CREATE POLICY "public can read products"
ON products FOR SELECT
TO anon, authenticated  -- specificare explicită a rolurilor
USING (true);           -- fără filtru — toți văd tot
-- Dacă omiti TO clause → policy se aplică la TOATE rolurile (incl. postgres, service_role în unele contexte)
```

#### Service Role vs Anon Key — diferența critică

| Cheie | RLS aplicat? | Când o folosești |
|---|---|---|
| `anon` (client-side) | DA — RLS filtrează | Browser, aplicație client |
| `service_role` (server-side) | NU — bypass complet | Server Node.js, migrations, admin |

```typescript
// Client Supabase cu anon key — RLS ACTIV
import { createClient } from '@supabase/supabase-js';
const supabase = createClient(url, process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!);

// Client server cu service_role — RLS BYPASS — NICIODATĂ în browser!
const supabaseAdmin = createClient(url, process.env.SUPABASE_SERVICE_ROLE_KEY!);
// NEXT_PUBLIC_ = expus în browser → NU pune service_role cu prefix NEXT_PUBLIC_
```

#### `getUser()` vs `getSession()` — diferența de securitate critică

```typescript
// ✗ PERICULOS: getSession() citește din cache local (cookie/localStorage)
// JWT-ul NU e verificat cu serverul → poate fi manipulat sau expirat fără să știi
const { data: { session } } = await supabase.auth.getSession();
const userId = session?.user.id;  // NU folosi asta pentru logică de business!

// ✓ CORECT: getUser() face request HTTP la Supabase și validează JWT pe server
// Singurul mod garantat că userId-ul e real și sesiunea e activă
const { data: { user }, error } = await supabase.auth.getUser();
if (error || !user) throw new Error('Neautentificat');
const userId = user.id;  // sursă de adevăr

// Regulă practică:
// getSession() → ok pentru UI (avatar, email afișat, stare logat/nelogat)
// getUser()    → obligatoriu pentru orice operație cu date (INSERT, UPDATE, DELETE)
```

> **Context Next.js App Router:** În Server Components și Route Handlers, folosești `supabase.auth.getUser()` exclusiv — `getSession()` pe server citește cookie-ul brut fără revalidare JWT.

#### Connection Pooling — relevant pentru conexiuni directe la DB

**Important:** `@supabase/supabase-js` NU face conexiuni directe la PostgreSQL — comunică prin PostgREST HTTP API. Pooling-ul nu te privește dacă folosești doar clientul Supabase JS.

Pooling-ul contează când folosești `pg`, `drizzle`, `prisma` sau `knex` direct:

```typescript
// Conexiune directă (port 5432) — pentru procese long-running (server dedicat, Docker)
DATABASE_URL=postgresql://user:pass@db.xxx.supabase.co:5432/postgres

// Transaction Pooler (port 6543) — OBLIGATORIU pentru serverless (Vercel, Netlify, Lambda)
// Serverless = funcții care pornesc/se opresc la fiecare request → fiecare deschide conexiune nouă
// Fără pooler: 1000 requests simultan = 1000 conexiuni DB → PostgreSQL refuză
DATABASE_URL=postgresql://user:pass@db.xxx.supabase.co:6543/postgres?pgbouncer=true

// În Prisma (serverless) — pgbouncer=true + connection_limit=1
DATABASE_URL=postgresql://...@...:6543/postgres?pgbouncer=true&connection_limit=1
```

> **Regula simplă:** Folosești `@supabase/supabase-js`? Nu ai nicio configurare de făcut. Folosești Prisma/drizzle/pg direct pe Vercel? Folosești portul 6543 cu `pgbouncer=true`.

---

### Parte 7 — Policies RLS: SELECT / INSERT / UPDATE / DELETE

#### Pattern standard — user vede și modifică doar datele lui

```sql
ALTER TABLE invoices ENABLE ROW LEVEL SECURITY;

-- SELECT: citire proprie
CREATE POLICY "select own invoices"
ON invoices FOR SELECT
USING (auth.uid() = user_id);

-- INSERT: poate crea doar cu user_id = al lui
CREATE POLICY "insert own invoices"
ON invoices FOR INSERT
WITH CHECK (auth.uid() = user_id);
-- WITH CHECK = validează valoarea ÎNAINTE de scriere
-- USING nu se aplică la INSERT — nu există rând "existent" de filtrat

-- UPDATE: poate modifica doar ale lui, și nu poate schimba user_id-ul
CREATE POLICY "update own invoices"
ON invoices FOR UPDATE
USING (auth.uid() = user_id)      -- ce rânduri poate selecta pentru update
WITH CHECK (auth.uid() = user_id); -- cum trebuie să arate rândul DUPĂ update

-- DELETE: poate șterge doar ale lui
CREATE POLICY "delete own invoices"
ON invoices FOR DELETE
USING (auth.uid() = user_id);
```

#### Pattern team/organizație — membri văd datele organizației

```sql
CREATE POLICY "org members see invoices"
ON invoices FOR SELECT
USING (
  EXISTS (
    SELECT 1 FROM organization_members om
    WHERE om.organization_id = invoices.organization_id
    AND om.user_id = auth.uid()
  )
);
-- EXISTS e mai eficient decât IN (...) pentru subquery-uri mari
```

#### Pattern admin — JWT claims (recomandat) vs subquery

```sql
-- ✗ PROBLEMATIC: subquery la profiles în policy poate cauza recursivitate
CREATE POLICY "admins see all"
ON invoices FOR SELECT
USING (
  (SELECT is_admin FROM profiles WHERE id = auth.uid())  -- subquery în policy!
  OR auth.uid() = user_id
);

-- ✓ CORECT: folosești JWT app_metadata — fără subquery, fără recursivitate
-- Setezi în Supabase Dashboard → Authentication → Users → Edit user → app_metadata:
-- { "role": "admin" }

CREATE POLICY "admins see all"
ON invoices FOR SELECT
USING (
  (auth.jwt() -> 'app_metadata' ->> 'role') = 'admin'
  OR auth.uid() = user_id
);

-- Alternativ: funcție security definer cu search_path fix
CREATE OR REPLACE FUNCTION is_admin()
RETURNS boolean AS $$
  SELECT (auth.jwt() -> 'app_metadata' ->> 'role') = 'admin';
$$ LANGUAGE sql STABLE SECURITY DEFINER SET search_path = public, auth;

CREATE POLICY "admins see all"
ON invoices FOR SELECT
USING (is_admin() OR auth.uid() = user_id);
```

#### Pattern date publice — access fără autentificare

```sql
ALTER TABLE products ENABLE ROW LEVEL SECURITY;

CREATE POLICY "public read products"
ON products FOR SELECT
TO anon, authenticated
USING (is_published = true);

CREATE POLICY "authenticated write products"
ON products FOR INSERT
TO authenticated
WITH CHECK (auth.uid() = created_by);
```

#### RLS pe Views — ce moștenesc și ce nu

Views cu `SECURITY INVOKER` (default în Supabase) **moștenesc RLS de pe tabelele sursă** — userul curent trebuie să aibă acces la FIECARE tabelă din JOIN pentru ca view-ul să returneze date.

> **EROARE FRECVENTĂ:** `ALTER VIEW ... ENABLE ROW LEVEL SECURITY` NU există în PostgreSQL — views nu suportă RLS direct. Securitatea views vine din RLS pe tabelele de bază sau din restricții de acces (GRANT/REVOKE).

```sql
-- ✓ View SECURITY INVOKER (default): moștenește RLS de pe toate tabelele sursă
CREATE VIEW invoice_details AS
SELECT i.id, i.amount, i.user_id, c.name AS client_name
FROM invoices i
JOIN clients c ON c.id = i.client_id;
-- user_id TREBUIE inclus în SELECT pentru ca RLS din invoices să funcționeze

-- ✓ View cu SECURITY DEFINER — bypass RLS pe tabelele sursă
CREATE VIEW monthly_summary WITH (security_definer = true) AS
SELECT DATE_TRUNC('month', created_at) AS month, SUM(amount) AS total
FROM invoices WHERE status = 'paid'
GROUP BY 1;
-- Controlezi accesul prin GRANT/REVOKE:
GRANT SELECT ON monthly_summary TO authenticated;
REVOKE SELECT ON monthly_summary FROM anon;
```

#### Greșeala clasică: RLS pe profiles

```sql
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;

CREATE POLICY "users see own profile"
ON profiles FOR SELECT
USING (auth.uid() = id);

CREATE POLICY "users update own profile"
ON profiles FOR UPDATE
USING (auth.uid() = id)
WITH CHECK (auth.uid() = id);

-- INSERT la signup — făcut prin trigger (nu prin policy INSERT pe profiles)
```

---

### Parte 8 — Indexare

Un index incorect = query-uri lente pe tabele mari. Un index lipsă pe foreign key = JOIN de 10× mai lent.

#### `CONCURRENTLY` — obligatoriu în producție cu date existente

```sql
-- ✗ PERICULOS PE PRODUCȚIE: blochează toate scrierile pe tabelă până indexul e gata
CREATE INDEX idx_invoices_client_id ON invoices(client_id);

-- ✓ NONBLOCKING: PostgreSQL construiește indexul fără să blocheze scrierile
CREATE INDEX CONCURRENTLY idx_invoices_client_id ON invoices(client_id);

-- Excepție: la CREATE TABLE din zero (fără date existente) — CONCURRENTLY nu e necesar
-- și nu e permis în interiorul unui bloc de tranzacție BEGIN/COMMIT
```

#### Indexuri obligatorii — adaugă la crearea schemei

```sql
-- 1. Orice foreign key care apare în JOIN sau WHERE
CREATE INDEX CONCURRENTLY idx_invoices_client_id ON invoices(client_id);
CREATE INDEX CONCURRENTLY idx_invoices_user_id ON invoices(user_id);
CREATE INDEX CONCURRENTLY idx_order_items_order_id ON order_items(order_id);

-- 2. Câmpuri frecvent filtrate
CREATE INDEX CONCURRENTLY idx_invoices_status ON invoices(status);
CREATE INDEX CONCURRENTLY idx_invoices_created_at ON invoices(created_at DESC);

-- 3. Câmpuri de text cu căutare ILIKE
CREATE INDEX CONCURRENTLY idx_clients_name_trgm ON clients USING gin(name gin_trgm_ops);
-- Necesită: CREATE EXTENSION IF NOT EXISTS pg_trgm;
```

#### Tipuri de index — când le folosești

```sql
-- B-Tree (default) — egalitate, comparație, ORDER BY
CREATE INDEX CONCURRENTLY idx_invoices_amount ON invoices(amount);

-- GIN — arrays, JSONB, full-text search
CREATE INDEX CONCURRENTLY idx_clients_tags ON clients USING gin(tags);
CREATE INDEX CONCURRENTLY idx_products_meta ON products USING gin(metadata);
-- Full-text search cu GIN:
CREATE INDEX CONCURRENTLY idx_invoices_fts
ON invoices USING gin(to_tsvector('romanian', description));

-- BRIN (Block Range Index) — pentru tabele time-series foarte mari (logs, events)
-- Mult mai mic decât B-Tree (câteva KB vs sute de MB); funcționează bine când
-- datele sunt fizic ordonate pe disk în ordine cronologică (INSERT secvențial)
CREATE INDEX CONCURRENTLY idx_events_created_at_brin
ON events USING brin(created_at) WITH (pages_per_range = 128);
-- Când să folosești: tabele > 1M rânduri cu inserare secvențială pe timp
-- Când să NU folosești: UPDATE frecvent pe created_at (distruge ordonarea fizică)

-- Index parțial — indexezi doar rândurile relevante (mai mic, mai rapid)
CREATE INDEX CONCURRENTLY idx_invoices_active_created
ON invoices(created_at DESC)
WHERE deleted_at IS NULL;  -- parțial: exclude rândurile șterse

CREATE INDEX CONCURRENTLY idx_invoices_unpaid_date
ON invoices(created_at)
WHERE status IN ('draft', 'sent') AND deleted_at IS NULL;
```

#### Indici compuși — cel mai neglijat tip, cel mai mare impact

```sql
-- REGULA: ordinea coloanelor contează
-- 1. Câmpuri de egalitate (=) mai întâi
-- 2. Câmpuri de range (>, <, BETWEEN) al doilea
-- 3. Câmpuri de sortare (ORDER BY) ultimele

-- Multi-tenant — acoperă 90% din query-urile de listare per user
CREATE INDEX CONCURRENTLY idx_invoices_user_status_date
ON invoices(user_id, status, created_at DESC);
-- Acoperă eficient:
-- WHERE user_id = X                              → prefix stâng
-- WHERE user_id = X AND status = Y              → primele 2 coloane
-- WHERE user_id = X ORDER BY created_at DESC    → prefix + sort
-- NU acoperă: WHERE status = Y fără user_id     → regula prefixului stâng

-- Index compus parțial — multi-tenant + soft delete
CREATE INDEX CONCURRENTLY idx_invoices_user_active
ON invoices(user_id, created_at DESC)
WHERE deleted_at IS NULL;
```

#### Covering indexes cu `INCLUDE` — index-only scan

```sql
-- Problema: indexul are user_id dar query-ul selectează și status, amount
-- PostgreSQL face "heap fetch" — citire suplimentară din tabelă pentru câmpurile lipsă
EXPLAIN ANALYZE
SELECT user_id, status, amount FROM invoices WHERE user_id = 'uuid';
-- → "Index Scan using idx_invoices_user_id" + "Heap Fetches: 10000" ← suplimentar lent

-- Soluție: INCLUDE adaugă câmpuri în index fără să fie chei de căutare
-- Index-only scan: PostgreSQL citește totul din index, fără a atinge tabela
CREATE INDEX CONCURRENTLY idx_invoices_user_covering
ON invoices(user_id) INCLUDE (status, amount, created_at);
-- Acum: "Index Only Scan" — zero heap fetches!
-- INCLUDE e diferit de index compus:
-- (user_id, status) → poți filtra WHERE status = X
-- (user_id) INCLUDE (status) → poți citi status dar NU filtra WHERE status = X
-- Alege INCLUDE pentru câmpuri SELECT frecvente, index compus pentru câmpuri WHERE

-- Verificare că funcționează
EXPLAIN ANALYZE
SELECT user_id, status, amount FROM invoices WHERE user_id = 'uuid';
-- Caută: "Index Only Scan" și "Heap Fetches: 0" ✓
```

#### Monitorizare index bloat și utilizare

```sql
-- Indexuri care nu sunt folosite — candidați la DROP
SELECT schemaname, tablename, indexname, idx_scan, idx_tup_read
FROM pg_stat_user_indexes
WHERE idx_scan = 0 AND schemaname = 'public'
ORDER BY pg_relation_size(indexrelid) DESC;
-- idx_scan = 0 → indexul nu a fost folosit niciodată de la ultima resetare statistici
-- Verifică înainte să ștergi: poate fi index nou sau tabelă rar accesată

-- Index bloat — indexuri care s-au umflat (UPDATE/DELETE frecvent)
SELECT indexname,
       pg_size_pretty(pg_relation_size(indexrelid)) AS index_size
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
ORDER BY pg_relation_size(indexrelid) DESC;
-- Index > 3× mărimea așteptată → REINDEX CONCURRENTLY

-- Reconstruiește index fără downtime (PG 12+)
REINDEX INDEX CONCURRENTLY idx_invoices_client_id;

-- Verificare că indexul e folosit
EXPLAIN ANALYZE
SELECT * FROM invoices WHERE user_id = 'uuid' AND status = 'sent'
ORDER BY created_at DESC;
-- "Index Scan using idx_invoices_user_status_date" ✓
-- "Seq Scan" ✗ → index lipsește sau nu acoperă query-ul
```

---

## BLOC 4 — Operații Complexe

---

### Parte 9 — Views: Date Agregate Fără Logică în JS

O view e o query SQL salvată ca tabelă virtuală. Supabase o expune ca orice tabelă.

#### View simplă — facturile cu datele clientului

```sql
-- SECURITY INVOKER (default): RLS din invoices se aplică automat
CREATE VIEW invoice_details AS
SELECT
  i.id,
  i.amount,
  i.status,
  i.created_at,
  i.user_id,       -- NECESAR: RLS din invoices îl folosește pentru filtrare
  c.name AS client_name,
  c.email AS client_email
FROM invoices i
JOIN clients c ON c.id = i.client_id
WHERE i.deleted_at IS NULL;

-- Acces identic cu o tabelă
const { data, error } = await supabase
  .from('invoice_details')
  .select('*')
  .eq('status', 'overdue');
```

#### View materializată — pentru rapoarte complexe

```sql
-- Cache al query-ului — nu recalculează la fiecare SELECT
CREATE MATERIALIZED VIEW monthly_revenue AS
SELECT
  DATE_TRUNC('month', created_at) AS month,
  SUM(amount) AS total,
  COUNT(*) AS invoice_count
FROM invoices
WHERE status = 'paid' AND deleted_at IS NULL
GROUP BY 1
ORDER BY 1 DESC;

-- Index pe view materializată (e o tabelă reală, nu virtuală)
CREATE UNIQUE INDEX ON monthly_revenue(month);

-- Reîmprospătare manuală
REFRESH MATERIALIZED VIEW CONCURRENTLY monthly_revenue;
-- CONCURRENTLY = nu blochează citirile (necesită UNIQUE index)

-- Reîmprospătare automată cu Supabase Cron (pg_cron extension)
-- Activat din Dashboard: Database → Extensions → pg_cron
SELECT cron.schedule(
  'refresh-monthly-revenue',  -- job name
  '0 * * * *',                -- la fiecare oră (cron syntax)
  'REFRESH MATERIALIZED VIEW CONCURRENTLY monthly_revenue'
);
-- Verificare jobs active:
SELECT jobname, schedule, command FROM cron.job;
```

#### View cu agregate pentru dashboard

```sql
CREATE VIEW client_summary AS
SELECT
  c.id,
  c.name,
  c.user_id,  -- pentru RLS (SECURITY INVOKER moștenește policy din clients)
  COUNT(i.id) AS total_invoices,
  -- FILTER (WHERE ...) — sintaxa modernă PG 9.4+, mai clară decât CASE WHEN
  SUM(i.amount) FILTER (WHERE i.status = 'paid')                 AS paid_total,
  SUM(i.amount) FILTER (WHERE i.status IN ('draft','sent'))      AS pending_total,
  COUNT(i.id)   FILTER (WHERE i.status = 'overdue')              AS overdue_count,
  MAX(i.created_at) AS last_invoice_date
FROM clients c
LEFT JOIN invoices i ON i.client_id = c.id AND i.deleted_at IS NULL
GROUP BY c.id, c.name, c.user_id;
```

---

### Parte 10 — Funcții și Triggers: Volatility + SECURITY DEFINER + FOR EACH STATEMENT

**Regula critică:** Orice funcție cu `SECURITY DEFINER` trebuie să aibă `SET search_path = public, auth` explicit.

#### Volatilitate funcții — impact pe query optimizer

PostgreSQL clasifică funcțiile în 3 categorii. Alegerea greșită = query-uri 10× mai lente sau rezultate incorecte:

```sql
-- VOLATILE (default): funcția poate modifica DB sau returna valori diferite
-- PostgreSQL o apelează la FIECARE rând în query — nu cache-uiește niciodată
-- Folosești: orice funcție care scrie în DB sau citește stare de sesiune (auth.uid(), now())
CREATE OR REPLACE FUNCTION create_invoice(...) RETURNS invoices AS $$ ... $$ VOLATILE;

-- STABLE: returnează același rezultat pentru aceeași intrare în cadrul ACELEIAȘI tranzacții
-- PostgreSQL poate optimiza să o apeleze o singură dată per tranzacție
-- Folosești: funcții de lookup care citesc din DB dar nu modifică
-- NU folosi dacă funcția apelează now(), random(), auth.uid() — acestea sunt volatile!
CREATE OR REPLACE FUNCTION get_client_name(p_id uuid)
RETURNS text AS $$
  SELECT name FROM clients WHERE id = p_id;
$$ LANGUAGE sql STABLE SET search_path = public;
-- Dacă o pui în WHERE: PostgreSQL evaluează o dată per query, nu per rând

-- IMMUTABLE: returnează ÎNTOTDEAUNA același rezultat pentru aceeași intrare
-- PostgreSQL poate cache-ui rezultatul și chiar stoca în index expressions
-- Folosești: calcule pure fără niciun acces la DB sau stare externă
CREATE OR REPLACE FUNCTION calculate_tax_amount(amount numeric)
RETURNS numeric AS $$
  SELECT amount * 0.19;
$$ LANGUAGE sql IMMUTABLE;

-- IMMUTABLE în index expression — calculul e stocat în index
CREATE INDEX CONCURRENTLY idx_invoices_tax
ON invoices((amount * 0.19));  -- sau cu funcție: (calculate_tax_amount(amount))
-- Potrivit pentru câmpuri calculate frecvent în WHERE sau ORDER BY

-- STRICT (RETURNS NULL ON NULL INPUT) — funcția returnează NULL dacă ORICE argument e NULL
-- Evită execuția funcției pentru rânduri cu NULL în câmpuri relevante → performanță
CREATE OR REPLACE FUNCTION full_address(street text, city text, country text)
RETURNS text AS $$
  SELECT street || ', ' || city || ', ' || country;
$$ LANGUAGE sql IMMUTABLE STRICT;
-- full_address(NULL, 'Cluj', 'RO') → NULL (fără execuție SQL)
-- Potrivit pentru funcții de formatare și calcul care nu au sens cu NULL
```

#### Funcție RPC — cu search_path fix

```sql
CREATE OR REPLACE FUNCTION create_invoice(
  p_client_id uuid,
  p_amount    numeric,
  p_items     jsonb
) RETURNS invoices AS $$
DECLARE
  new_invoice invoices;
BEGIN
  INSERT INTO invoices (client_id, amount, status, user_id)
  VALUES (p_client_id, p_amount, 'draft', auth.uid())
  RETURNING * INTO new_invoice;

  INSERT INTO invoice_items (invoice_id, description, quantity, unit_price)
  SELECT
    new_invoice.id,
    item->>'description',
    (item->>'quantity')::integer,
    (item->>'unit_price')::numeric
  FROM jsonb_array_elements(p_items) AS item;

  RETURN new_invoice;
END;
$$ LANGUAGE plpgsql
   SECURITY DEFINER
   SET search_path = public, auth;  -- OBLIGATORIU: previne SQL injection prin schema
```

```typescript
const { data, error } = await supabase.rpc('create_invoice', {
  p_client_id: clientId,
  p_amount: 1500,
  p_items: [{ description: 'Servicii web', quantity: 1, unit_price: 1500 }]
});
if (error) throw error;
```

#### Funcție care returnează tabelă — RETURNS TABLE

```sql
-- RETURNS TABLE — mai flexibil decât RETURNS SETOF typename
-- Util când returnezi câmpuri din mai multe tabele sau câmpuri calculate
CREATE OR REPLACE FUNCTION get_client_invoices(p_user_id uuid)
RETURNS TABLE (
  invoice_id    uuid,
  client_name   text,
  amount        numeric,
  status        text,
  created_at    timestamptz
) AS $$
  SELECT i.id, c.name, i.amount, i.status, i.created_at
  FROM invoices i
  JOIN clients c ON c.id = i.client_id
  WHERE i.user_id = p_user_id AND i.deleted_at IS NULL
  ORDER BY i.created_at DESC;
$$ LANGUAGE sql STABLE SET search_path = public;

-- Apel Supabase JS:
const { data, error } = await supabase.rpc('get_client_invoices', { p_user_id: userId });
// data = array de obiecte cu structura din RETURNS TABLE
```

#### Trigger `updated_at` — funcție cu search_path

```sql
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql
   SET search_path = public;

CREATE TRIGGER set_updated_at
BEFORE UPDATE ON clients
FOR EACH ROW EXECUTE FUNCTION update_updated_at();
```

#### Trigger la signup — cel mai des scris cu SECURITY DEFINER

```sql
CREATE OR REPLACE FUNCTION handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO public.profiles (id, full_name)
  VALUES (
    NEW.id,
    NEW.raw_user_meta_data->>'full_name'  -- NULL dacă nu există — corect semantic
    -- NU COALESCE cu '' (string gol) — NULL și '' sunt diferite în SQL
  );
  RETURN NEW;
END;
$$ LANGUAGE plpgsql
   SECURITY DEFINER
   SET search_path = public, auth;  -- OBLIGATORIU

CREATE TRIGGER on_auth_user_created
AFTER INSERT ON auth.users
FOR EACH ROW EXECUTE FUNCTION handle_new_user();
```

#### Trigger pentru total_amount denormalizat — FOR EACH ROW vs FOR EACH STATEMENT

```sql
-- VARIANTA SIMPLĂ: FOR EACH ROW — ok pentru operații single-row
-- ⚠️ La bulk INSERT (.insert([100 items])) → 100 UPDATE-uri separate pe același rând!
CREATE OR REPLACE FUNCTION sync_invoice_total()
RETURNS TRIGGER AS $$
DECLARE
  v_invoice_id uuid;
BEGIN
  v_invoice_id := COALESCE(NEW.invoice_id, OLD.invoice_id);
  UPDATE invoices
  SET total_amount = (
    SELECT COALESCE(SUM(quantity * unit_price), 0)
    FROM invoice_items
    WHERE invoice_id = v_invoice_id
  )
  WHERE id = v_invoice_id;
  RETURN NULL;  -- AFTER trigger: return value ignorat — NULL e corect, nu NEW
END;
$$ LANGUAGE plpgsql SET search_path = public;

CREATE TRIGGER sync_total_row
AFTER INSERT OR UPDATE OR DELETE ON invoice_items
FOR EACH ROW EXECUTE FUNCTION sync_invoice_total();

-- VARIANTA PRODUCȚIE: FOR EACH STATEMENT (PG 10+) — UN singur UPDATE la bulk
-- .insert([100 items]) → 1 recalcul, nu 100
CREATE OR REPLACE FUNCTION sync_invoice_total_bulk()
RETURNS TRIGGER AS $$
BEGIN
  UPDATE invoices
  SET total_amount = (
    SELECT COALESCE(SUM(quantity * unit_price), 0)
    FROM invoice_items
    WHERE invoice_id = invoices.id
  )
  WHERE id IN (
    SELECT invoice_id FROM new_items WHERE invoice_id IS NOT NULL
    UNION
    SELECT invoice_id FROM old_items WHERE invoice_id IS NOT NULL
  );
  RETURN NULL;
END;
$$ LANGUAGE plpgsql SET search_path = public;

DROP TRIGGER IF EXISTS sync_total_row ON invoice_items;
CREATE TRIGGER sync_total_stmt
AFTER INSERT OR UPDATE OR DELETE ON invoice_items
REFERENCING NEW TABLE AS new_items OLD TABLE AS old_items
FOR EACH STATEMENT EXECUTE FUNCTION sync_invoice_total_bulk();
-- Alege O SINGURĂ variantă — nu le combina pe aceeași tabelă
```

---

### Parte 11 — Transactions: FOR UPDATE, Isolation Levels, Deadlock Prevention

**Regula fundamentală:** Orice operație care citește o valoare și o actualizează bazat pe valoarea citită (sold, stoc, contor) trebuie să gestioneze concurența.

#### Race condition — problema fără `FOR UPDATE`

```
Sesiunea A                    Sesiunea B
-----------                   -----------
SELECT balance = 100          SELECT balance = 100
  (verificare: 100 >= 80 ✓)    (verificare: 100 >= 90 ✓)
UPDATE balance = 100 - 80     UPDATE balance = 100 - 90
  → balance devine 20           → balance devine 10
                              -- Ambele au trecut! Soldul real: -70 ❌
```

#### Transfer fonduri — cu `FOR UPDATE` și prevenire deadlock

```sql
-- ⚠️ DEADLOCK CLASSIC: două funcții iau lock-uri în ordine inversă
-- Funcția A: blochează accounts_from, apoi accounts_to
-- Funcția B: blochează accounts_to, apoi accounts_from
-- → A și B se blochează reciproc indefinit

-- ✓ SOLUȚIE: ordinea deterministă (ORDER BY id) — imposibil deadlock circular
CREATE OR REPLACE FUNCTION transfer_funds(
  p_from_account  uuid,
  p_to_account    uuid,
  p_amount        numeric
) RETURNS void AS $$
DECLARE
  v_balance numeric;
BEGIN
  -- Blochezi AMBELE conturi simultan, în ordine deterministă
  -- Dacă A și B intră cu aceleași conturi în ordine diferită, ambele
  -- vor bloca în aceeași ordine → unul așteaptă, nu deadlock
  PERFORM id FROM accounts
  WHERE id IN (p_from_account, p_to_account)
  ORDER BY id ASC  -- ordine deterministă (UUID alphabetic)
  FOR UPDATE;

  SELECT balance INTO v_balance
  FROM accounts WHERE id = p_from_account;

  IF v_balance < p_amount THEN
    RAISE EXCEPTION 'Sold insuficient: disponibil %, solicitat %', v_balance, p_amount;
  END IF;

  UPDATE accounts SET balance = balance - p_amount WHERE id = p_from_account;
  UPDATE accounts SET balance = balance + p_amount WHERE id = p_to_account;

  INSERT INTO transactions (from_account, to_account, amount)
  VALUES (p_from_account, p_to_account, p_amount);
END;
$$ LANGUAGE plpgsql SET search_path = public;
```

#### Optimistic Locking — alternativă la FOR UPDATE pentru contention redus

```sql
-- Schema: câmp version
ALTER TABLE invoices ADD COLUMN version integer NOT NULL DEFAULT 1;
```

```typescript
async function updateInvoiceOptimistic(id: string, patch: Partial<Invoice>, knownVersion: number) {
  const { data, error } = await supabase
    .from('invoices')
    .update({ ...patch, version: knownVersion + 1 })
    .eq('id', id)
    .eq('version', knownVersion)  // condiție de conflict
    .select()
    .maybeSingle();

  if (error) throw error;
  if (!data) throw new Error('Conflict: datele au fost modificate de altcineva. Reîncarcă și reîncearcă.');
  return data;
}
```

| Blocare pesimistă (FOR UPDATE) | Blocare optimistă (version) |
|---|---|
| Blochează rândul la citire | Nu blochează niciodată |
| Potrivit: sold/stoc financiar, atomicitate critică | Potrivit: formulare de editare, modificări rare |
| Performanță slabă la mulți useri pe același rând | Performanță bună, conflict e rar |
| Rezolvare: automat (celălalt user așteaptă) | Rezolvare: UI arată eroare de conflict |

#### Isolation levels — pentru operații financiare critice

```sql
-- DEFAULT: READ COMMITTED
-- Vede datele commise de alte tranzacții în timp real
-- Problemă: non-repeatable reads (citești aceeași valoare de două ori, rezultate diferite)
BEGIN;
  SELECT balance FROM accounts WHERE id = $1;  -- citești 100
  -- altă tranzacție commitează UPDATE → balance = 50
  SELECT balance FROM accounts WHERE id = $1;  -- citești 50 ← inconsistență!
COMMIT;

-- REPEATABLE READ — snapshot la începutul tranzacției
-- Rezolvă non-repeatable reads; recomandat pentru rapoarte financiare consistente
BEGIN TRANSACTION ISOLATION LEVEL REPEATABLE READ;
  SELECT balance FROM accounts WHERE id = $1;  -- 100
  -- altă tranzacție modifică → ignorat în această tranzacție
  SELECT balance FROM accounts WHERE id = $1;  -- tot 100 ← consistent
COMMIT;

-- SERIALIZABLE — cel mai strict; detectează anomalii de serializabilitate
-- Costul: mai multe serialization failure errors → necesită retry logic în aplicație
-- Recomandat: rapoarte financiare end-of-day, reconcilieri, operații critice de inventar
BEGIN TRANSACTION ISOLATION LEVEL SERIALIZABLE;
  -- dacă altă tranzacție scrie date care ar afecta rezultatul acesteia
  -- → error: ERROR: could not serialize access due to concurrent update
  -- → aplicația prinde eroarea și reîncearcă
COMMIT;
```

```sql
-- Isolation level în funcție SQL — setezi la nivel de funcție
-- Supabase JS nu expune BEGIN direct → tot ce are nevoie de isolation > READ COMMITTED
-- trebuie în funcție RPC:
CREATE OR REPLACE FUNCTION financial_snapshot(p_user_id uuid)
RETURNS TABLE(account_id uuid, balance numeric, snapshot_time timestamptz) AS $$
  SELECT id, balance, now()
  FROM accounts
  WHERE user_id = p_user_id;
$$ LANGUAGE sql STABLE
   SET default_transaction_isolation TO 'repeatable read'  -- ← isolation la nivel funcție
   SET search_path = public;
-- Supabase va rula această funcție în REPEATABLE READ automat
```

#### SAVEPOINT — rollback parțial în tranzacții complexe

```sql
-- Util când ai o secvență de operații și vrei să dai rollback doar la o parte
CREATE OR REPLACE FUNCTION process_batch(p_items jsonb) RETURNS jsonb AS $$
DECLARE
  item jsonb;
  results jsonb = '[]'::jsonb;
  error_msg text;
BEGIN
  FOREACH item IN ARRAY ARRAY(SELECT * FROM jsonb_array_elements(p_items))
  LOOP
    SAVEPOINT item_savepoint;  -- marker de rollback parțial
    BEGIN
      INSERT INTO processed_items (data) VALUES (item);
      results := results || jsonb_build_array(jsonb_build_object('status', 'ok', 'data', item));
    EXCEPTION WHEN OTHERS THEN
      ROLLBACK TO SAVEPOINT item_savepoint;  -- rollback DOAR la item curent, nu la tot
      GET STACKED DIAGNOSTICS error_msg = MESSAGE_TEXT;
      results := results || jsonb_build_array(jsonb_build_object('status', 'error', 'msg', error_msg));
    END;
  END LOOP;
  RETURN results;
END;
$$ LANGUAGE plpgsql SET search_path = public;
-- Un item eșuat nu anulează itemele procesate anterior
```

#### `FOR UPDATE SKIP LOCKED` — pentru job queues

```sql
CREATE OR REPLACE FUNCTION claim_next_job()
RETURNS jobs AS $$
DECLARE
  v_job jobs;
BEGIN
  SELECT * INTO v_job
  FROM jobs
  WHERE status = 'pending'
  ORDER BY created_at ASC
  LIMIT 1
  FOR UPDATE SKIP LOCKED;  -- sare peste rândurile deja luate de alte procese

  IF v_job.id IS NOT NULL THEN
    UPDATE jobs SET status = 'processing', started_at = now()
    WHERE id = v_job.id;
  END IF;

  RETURN v_job;
END;
$$ LANGUAGE plpgsql SET search_path = public;
```

#### Tranzacție din client JS — limitare importantă

```typescript
// Supabase JS nu expune BEGIN/COMMIT direct
// ✓ CORECT pentru orice operație cu mai mulți pași: funcție SQL via RPC
const { error } = await supabase.rpc('create_invoice', { p_client_id, p_amount, p_items });
if (error) throw error; // dacă eșuează, DB-ul e consistent
```

---

### Parte 12 — Migrations: Schimbări de Schemă Fără Downtime

#### Reguli de migrare sigure

```sql
-- ✓ Adăugare câmp nullable — instant, sigur
ALTER TABLE invoices ADD COLUMN notes text;

-- ✓ Adăugare câmp cu DEFAULT — instant din PG 11+
ALTER TABLE invoices ADD COLUMN currency text DEFAULT 'RON';

-- ✗ PERICULOS: câmp NOT NULL fără default pe tabelă cu date — eșuează imediat
ALTER TABLE invoices ADD COLUMN notes text NOT NULL;

-- ✓ Pattern sigur pentru câmp NOT NULL (3 pași):
ALTER TABLE invoices ADD COLUMN notes text DEFAULT '';      -- Pasul 1
UPDATE invoices SET notes = 'Migrated' WHERE notes IS NULL; -- Pasul 2
ALTER TABLE invoices ALTER COLUMN notes SET NOT NULL;        -- Pasul 3

-- ✓ Schimbare tip coloană — necesită USING dacă tipurile sunt incompatibile
ALTER TABLE invoices ALTER COLUMN amount TYPE numeric(14,2);         -- compatible direct
ALTER TABLE invoices ALTER COLUMN old_status TYPE integer USING
  CASE old_status WHEN 'draft' THEN 0 WHEN 'paid' THEN 1 ELSE 2 END; -- USING pt conversie

-- ✓ Ștergere coloană — ireversibil, fă backup
ALTER TABLE invoices DROP COLUMN IF EXISTS deprecated_field;
```

#### Adăugarea soft delete pe o tabelă existentă

```sql
ALTER TABLE invoices ADD COLUMN deleted_at timestamptz DEFAULT NULL;
CREATE INDEX CONCURRENTLY idx_invoices_active
ON invoices(created_at DESC) WHERE deleted_at IS NULL;
CREATE VIEW active_invoices AS SELECT * FROM invoices WHERE deleted_at IS NULL;
```

#### Migrations cu Supabase CLI — atenție la comenzi distructive

```bash
# Generare fișier de migrare cu timestamp
supabase migration new add_soft_delete_to_invoices
# Editezi: supabase/migrations/20260521120000_add_soft_delete_to_invoices.sql

# Aplici local — NEDISTRUCTIV, rulează DOAR migrarea nouă
supabase db push --local

# ⛔ PERICULOS: supabase db reset — ȘTERGE COMPLET DB-ul și îl recreează de la zero
# NICIODATĂ pe producție! Folosit DOAR local în development
supabase db reset  # echivalent cu DROP DATABASE → recreare → toate migările de la început

# Aplici în producție — rulează DOAR migările noi, nepuse
supabase db push   # sigur pe producție

# Status migrări — ce s-a aplicat vs ce urmează
supabase migration list
```

#### Strategie de rollback — down migrations

```sql
-- Supabase CLI nu generează down migrations automat
-- Pattern recomandat: creezi manual fișier de rollback

-- Migrare: 20260521_add_notes_to_invoices.sql (UP)
ALTER TABLE invoices ADD COLUMN notes text;

-- Rollback: 20260521_add_notes_to_invoices.rollback.sql (DOWN — manual)
ALTER TABLE invoices DROP COLUMN IF EXISTS notes;

-- Strategia mai sigură: deploy în 2 pași
-- Pasul 1: adaugi coloana (nullable) → deploy
-- Pasul 2: după validare, adaugi NOT NULL → deploy
-- Rollback Pasul 1 e trivial; rollback Pasul 2 nu implică pierdere de date
```

---

## BLOC 5 — Debugging și Toolkit

---

### Parte 13 — 13 Greșeli Comune DB

#### Greșeala 1: RLS dezactivat — date expuse

```typescript
// ✗ Tabelă fără RLS — orice user logat vede TOATE facturile
const { data } = await supabase.from('invoices').select('*');
// ✓ ALTER TABLE invoices ENABLE ROW LEVEL SECURITY + policy
```

#### Greșeala 2: UPDATE/DELETE fără WHERE — suprascrie tot

```typescript
// ✗ Lipsă filtru — updatează TOATE rândurile din tabelă
await supabase.from('invoices').update({ status: 'paid' });
// ✓ Întotdeauna cu .eq() sau alt filtru
await supabase.from('invoices').update({ status: 'paid' }).eq('id', invoiceId);
```

#### Greșeala 3: `.single()` pe SELECT care poate returna 0

```typescript
// ✗ .single() aruncă eroare dacă nu găsește nimic (error.code = 'PGRST116')
const { data, error } = await supabase
  .from('profiles').select('*').eq('id', userId).single();

// ✓ .maybeSingle() returnează null dacă nu găsește
const { data, error } = await supabase
  .from('profiles').select('*').eq('id', userId).maybeSingle();
if (!data) { /* user fără profil — cazul normal la signup */ }
```

#### Greșeala 4: userId din URL/params în loc de auth

```typescript
// ✗ VULNERABILITATE CRITICĂ: oricine poate schimba userId în URL
const userId = params.get('userId');
// ✓ userId exclusiv din sesiunea autentificată
const { data: { user } } = await supabase.auth.getUser();
if (!user) throw new Error('Neautentificat');
```

#### Greșeala 5: float pentru bani

```sql
price  float      -- ✗ 19.99 + 0.01 = 20.000000000002
price  numeric(12,2)  -- ✓ precizie exactă
```

#### Greșeala 6: Index lipsă pe foreign key

```sql
-- ✗ Foreign key fără index → Seq Scan la fiecare JOIN
-- ✓ CREATE INDEX CONCURRENTLY idx_invoices_client_id ON invoices(client_id);
```

#### Greșeala 7: `timestamp` fără timezone

```sql
created_at  timestamp      -- ✗ ambiguitate la DST
created_at  timestamptz    -- ✓ stochează UTC, conversie automată
```

#### Greșeala 8: Ignorat câmpul `error` din Supabase

```typescript
// ✗ Ignoră error — rulezi cu data = null fără să știi
const { data } = await supabase.from('invoices').select('*');
const invoices = data.map(i => i); // TypeError: Cannot read properties of null

// ✓ Verifici error înainte de a folosi data
const { data, error } = await supabase.from('invoices').select('*');
if (error) throw error;
const invoices = (data ?? []).map(i => i);
```

#### Greșeala 9: N+1 queries — performanță distrusă

```typescript
// ✗ N+1: 1 query + 1 per client = 101 queries
const { data: clients } = await supabase.from('clients').select('*');
for (const client of clients) {
  await supabase.from('invoices').select('*').eq('client_id', client.id);
}

// ✓ UN singur query cu embedding
const { data: clients } = await supabase
  .from('clients')
  .select('id, name, invoices(id, amount, status)');
```

#### Greșeala 10: Race condition fără `FOR UPDATE`

```typescript
// ✗ Două sesiuni citesc soldul simultan → sold negativ
// ✓ Funcție SQL cu FOR UPDATE + ordine deterministă a lock-urilor
const { error } = await supabase.rpc('transfer_funds', { p_from, p_to, p_amount });
```

#### Greșeala 11: RLS aplicat direct pe view — SQL invalid

```sql
-- ✗ EROARE: ALTER VIEW ... ENABLE ROW LEVEL SECURITY nu există în PostgreSQL
ALTER VIEW invoice_details ENABLE ROW LEVEL SECURITY;  -- ERROR: not a table

-- ✓ CORECT: RLS vine din tabelele de bază (SECURITY INVOKER) — fără configurare extra
```

#### Greșeala 12: `getSession()` ca sursă de adevăr pentru userId

```typescript
// ✗ getSession() citește cache local, fără validare server
const { data: { session } } = await supabase.auth.getSession();
// ✓ getUser() validează JWT pe server la fiecare apel
const { data: { user }, error } = await supabase.auth.getUser();
if (error || !user) redirect('/login');
```

#### Greșeala 13: `count: 'exact'` în loop-uri sau pe tabele mari

```typescript
// ✗ count: 'exact' face COUNT(*) complet — LENT pe tabele > 500k rânduri
// Înmulțit cu N componente care se montează simultan = zeci de COUNT() simultane
for (const category of categories) {
  const { count } = await supabase
    .from('products')
    .select('*', { count: 'exact', head: true })
    .eq('category_id', category.id);
}

// ✓ VARIANTA 1: count: 'estimated' pentru afișare UI aproximativă
const { count } = await supabase
  .from('products')
  .select('*', { count: 'estimated', head: true });
// Citește pg_class.reltuples — instant, ±10% precizie

// ✓ VARIANTA 2: query unic cu aggregare pentru toate categoriile
const { data } = await supabase
  .from('products')
  .select('category_id, id.count()');
// Un singur query pentru toate categoriile — nu N queries

// ✓ VARIANTA 3: câmp denormalizat items_count pe categorii (cel mai rapid)
// Actualizat prin trigger — zero overhead la citire
```

---

### Parte 14 — TypeScript pentru Supabase

#### Typed Supabase client — type safety complet

```typescript
// Cel mai important pas: typezi clientul la nivel de createClient
// Toate query-urile vor fi type-safe automat

import { createClient } from '@supabase/supabase-js';
import { Database } from '@/types/supabase';  // tipurile generate

// ✓ Client tipizat — autocompletion + type checking pentru orice query
const supabase = createClient<Database>(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
);

// Acum supabase.from('invoices') știe exact ce câmpuri există:
const { data } = await supabase.from('invoices').select('id, amount, status');
// data: Array<{ id: string; amount: number; status: string }> — automat!
// data.map(i => i.amoutn)  → TypeScript error: Property 'amoutn' does not exist

// Client server (Route Handler, Server Component)
import { createServerClient } from '@supabase/ssr';
const supabase = createServerClient<Database>(url, key, { cookies });
```

#### Generare tipuri din schema DB (recomandat)

```bash
# Generare automată — sincronizat cu schema reală
npx supabase gen types typescript --project-id your-project-id > types/supabase.ts

# Folosire
import { Database } from '@/types/supabase';
type Invoice = Database['public']['Tables']['invoices']['Row'];
type InvoiceInsert = Database['public']['Tables']['invoices']['Insert'];
type InvoiceUpdate = Database['public']['Tables']['invoices']['Update'];
```

#### Definire manuală — când nu ai CLI configurat

```typescript
// types/db.ts

interface Invoice {
  id: string;                              // uuid
  user_id: string;
  client_id: string;
  amount: number;                          // numeric(10,2) → number în TS
  status: 'draft' | 'sent' | 'paid' | 'overdue' | 'void';
  notes: string | null;
  deleted_at: string | null;
  created_at: string;                      // timestamptz → string ISO
  updated_at: string;
  version: number;                         // optimistic locking
}

// Insert = ce trimiți la INSERT (fără câmpuri generate de DB)
type InvoiceInsert = Omit<Invoice, 'id' | 'created_at' | 'updated_at' | 'deleted_at' | 'version'>;

// Update = toate câmpurile opționale
type InvoiceUpdate = Partial<Omit<Invoice, 'id' | 'created_at' | 'user_id'>>;

// Cu relație inclusă
interface InvoiceWithClient extends Invoice {
  clients: { id: string; name: string; email: string };
}
```

#### Tipuri helper utile

```typescript
type InvoiceStatus = 'draft' | 'sent' | 'paid' | 'overdue' | 'void';

interface PaginatedResult<T> {
  items: T[];
  total: number;
  hasMore: boolean;
}

// satisfies — verificare tip fără widening (TS 4.9+)
// Util când construiești obiecte cu tip fix dar vrei să păstrezi tipul literal
const DEFAULT_INVOICE = {
  status: 'draft',
  amount: 0,
  notes: null
} satisfies Partial<Invoice>;
// DEFAULT_INVOICE.status are tipul 'draft', nu string

// Funcție tipizată complet
async function getInvoices(
  userId: string,
  status?: InvoiceStatus,
  includeSoftDeleted = false
): Promise<Invoice[]> {
  let query = supabase
    .from('invoices')
    .select('*')
    .eq('user_id', userId);

  if (!includeSoftDeleted) query = query.is('deleted_at', null);
  if (status) query = query.eq('status', status);

  const { data, error } = await query;
  if (error) throw error;
  return data ?? [];
}
```

---

### Parte 15 — Checklist Pre-Deploy

Verifică ÎNAINTE de primul deploy pe producție:

#### Schema DB

- [ ] Toate tabelele au `id uuid PRIMARY KEY DEFAULT gen_random_uuid()`
- [ ] Câmpurile de timp sunt `timestamptz`, nu `timestamp`
- [ ] Câmpurile monetare sunt `numeric(X,Y)`, nu `float`
- [ ] Foreign keys au `ON DELETE` explicit (CASCADE/RESTRICT/SET NULL)
- [ ] Index adăugat pentru FIECARE foreign key (`CONCURRENTLY` dacă tabela are date)
- [ ] Index adăugat pe câmpurile filtrate frecvent în WHERE
- [ ] Index compus adăugat pentru pattern multi-tenant: `(user_id, status, created_at DESC)`
- [ ] INCLUDE adăugat pe indici pentru câmpurile frecvent în SELECT (index-only scan)
- [ ] Tabele cu audit/CRM/financiar au câmp `deleted_at` pentru soft delete
- [ ] Ales explicit: soft delete în policy RLS vs în query (cu implicații pentru restore)
- [ ] Funcțiile cu SECURITY DEFINER au `SET search_path = public, auth`
- [ ] Funcțiile de lookup sunt marcate STABLE; funcțiile de calcul pur sunt IMMUTABLE

#### RLS și Securitate

- [ ] `ALTER TABLE X ENABLE ROW LEVEL SECURITY` pe toate tabelele publice
- [ ] `ALTER TABLE X FORCE ROW LEVEL SECURITY` pe tabele cu date sensibile
- [ ] Policy SELECT există pentru fiecare tabelă cu RLS activ
- [ ] Policy INSERT/UPDATE/DELETE există unde e nevoie
- [ ] `service_role` key NU e prefix-ată cu `NEXT_PUBLIC_`
- [ ] `userId` vine din `supabase.auth.getUser()`, nu din URL/params
- [ ] `getUser()` folosit (nu `getSession()`) pentru orice operație cu DB
- [ ] Policy admin folosește JWT claims (`auth.jwt() -> 'app_metadata'`), nu subquery la profiles
- [ ] Views NU au `ALTER VIEW ... ENABLE ROW LEVEL SECURITY` (invalid SQL)

#### Queries

- [ ] Fiecare `await supabase...` are `if (error) throw error` după (sau `.throwOnError()`)
- [ ] Toate INSERT au `.select().single()` dacă folosești `data`
- [ ] Toate UPDATE și DELETE au filtru explicit (`.eq(...)`)
- [ ] `.maybeSingle()` folosit în loc de `.single()` pe SELECT opțional
- [ ] `data ?? []` după fiecare query care returnează array
- [ ] Niciun loop cu query în interior (N+1 eliminat cu select embedding)
- [ ] `count: 'exact'` nu e folosit în loop-uri sau pe tabele > 500k rânduri
- [ ] UPSERT cu `onConflict` explicit dacă conflictul e pe câmp non-PK

#### Transactions și Funcții

- [ ] Operații cu mai mulți pași (insert + update) sunt în funcție SQL via RPC
- [ ] Funcțiile care citesc și modifică solduri/stocuri au `FOR UPDATE` + ordine deterministă
- [ ] Trigger-uri pe tabele cu bulk insert folosesc `FOR EACH STATEMENT`
- [ ] Funcții AFTER trigger returnează `NULL`, nu `NEW`
- [ ] Funcții financiare care necesită snapshot consistent folosesc `REPEATABLE READ`

#### Realtime (dacă folosești subscripții)

- [ ] `ALTER TABLE t REPLICA IDENTITY FULL` pe tabelele cu subscripții
- [ ] `supabase.removeChannel(channel)` apelat la unmount component
- [ ] `.subscribe((status, err) => {})` callback cu error handling
- [ ] Filtrul Realtime nu conține JOIN sau relații — doar câmpuri din tabelă directă

#### TypeScript

- [ ] `createClient<Database>` folosit pentru type safety complet
- [ ] Interfețe definite pentru fiecare tabelă principală
- [ ] `Omit<T, 'id' | 'created_at'>` folosit pentru tipul Insert
- [ ] Niciun `any` explicit — `unknown` pentru date externe

---

### Parte 16 — Supabase Realtime: Subscriptions + RLS

Supabase Realtime permite primirea automată a modificărilor din DB prin WebSocket.

#### Cum funcționează Realtime cu RLS

Realtime **respectă RLS** — userul primește doar modificările pe care policy-urile îi permit să le vadă.

```typescript
// Subscripție la modificările unei tabele
const channel = supabase
  .channel('invoices-changes')
  .on(
    'postgres_changes',
    {
      event: '*',              // 'INSERT' | 'UPDATE' | 'DELETE' | '*'
      schema: 'public',
      table: 'invoices',
      filter: `user_id=eq.${userId}`
    },
    (payload) => {
      console.log('Eveniment:', payload.eventType);
      console.log('Rând nou:', payload.new);
      console.log('Rând vechi:', payload.old);
    }
  )
  .subscribe((status, err) => {
    // ✓ Error handling în callback subscribe — nu ignora!
    if (status === 'CHANNEL_ERROR') {
      console.error('Realtime error:', err);
      // Reconectare automată sau fallback la polling
    }
    if (status === 'TIMED_OUT') {
      console.warn('Realtime timeout — reconectare automată în curs');
    }
    // Status: 'SUBSCRIBED' | 'CHANNEL_ERROR' | 'TIMED_OUT' | 'CLOSED'
  });

// Dezabonare (obligatoriu la unmount)
supabase.removeChannel(channel);
```

```typescript
// Pattern React — subscripție cu cleanup și error handling
useEffect(() => {
  const channel = supabase
    .channel(`invoices-${userId}`)
    .on('postgres_changes', {
      event: 'INSERT',
      schema: 'public',
      table: 'invoices',
      filter: `user_id=eq.${userId}`
    }, (payload) => {
      setInvoices(prev => [payload.new as Invoice, ...prev]);
    })
    .on('postgres_changes', {
      event: 'UPDATE',
      schema: 'public',
      table: 'invoices',
      filter: `user_id=eq.${userId}`
    }, (payload) => {
      setInvoices(prev =>
        prev.map(i => i.id === payload.new.id ? payload.new as Invoice : i)
      );
    })
    .on('postgres_changes', {
      event: 'DELETE',
      schema: 'public',
      table: 'invoices'
    }, (payload) => {
      setInvoices(prev => prev.filter(i => i.id !== payload.old.id));
    })
    .subscribe((status, err) => {
      if (status === 'CHANNEL_ERROR') {
        console.error('Subscripție eșuată:', err);
        setRealtimeError(true);  // afișezi fallback UI sau polling
      }
    });

  return () => { supabase.removeChannel(channel); };
}, [userId]);
```

#### Activare Realtime pe tabele

```sql
ALTER TABLE invoices REPLICA IDENTITY FULL;
-- REPLICA IDENTITY FULL = trimite rândul complet la DELETE
-- Default: la DELETE primești doar { id: 'uuid' }, nu celelalte câmpuri
```

#### Presence și Broadcast — alternative fără DB

```typescript
// PRESENCE — tracking utilizatori online (fără DB)
// Util pentru: "3 utilizatori văd acest document", cursori colaborativi
const presenceChannel = supabase.channel('room-online-users');
presenceChannel
  .on('presence', { event: 'sync' }, () => {
    const state = presenceChannel.presenceState();
    const onlineUsers = Object.values(state).flat();
    setOnlineCount(onlineUsers.length);
  })
  .subscribe(async (status) => {
    if (status === 'SUBSCRIBED') {
      await presenceChannel.track({ user_id: userId, online_at: new Date().toISOString() });
    }
  });

// BROADCAST — pub/sub fără persistență în DB
// Util pentru: notificări în timp real, actualizări UI collaborative
const broadcastChannel = supabase.channel('cursor-positions');
broadcastChannel
  .on('broadcast', { event: 'cursor' }, ({ payload }) => {
    updateCursorPosition(payload.user_id, payload.x, payload.y);
  })
  .subscribe();

// Trimite eveniment broadcast (fără scriere în DB)
broadcastChannel.send({ type: 'broadcast', event: 'cursor', payload: { user_id, x, y } });
```

#### Limitări importante

```typescript
// 1. Realtime nu funcționează pe views — abonezi tabele, nu views
// 2. Filtrul Realtime nu suportă JOIN sau relații
filter: `status=in.(draft,sent)`   // ✓
filter: `client.name=eq.Ion`       // ✗

// 3. Payload.old incomplet fără REPLICA IDENTITY FULL
```

#### Când să folosești Realtime vs polling

| Scenariu | Realtime | Polling |
|---|---|---|
| Dashboard live, notificări instant | ✓ ideal | inutil |
| Date care se schimbă rar (< 1/min) | overkill | ✓ simplu |
| Mobile / conexiuni instabile | atenție la reconnect | ✓ mai robust |
| Date cu RLS complex (relații) | atenție la payload | ✓ mai sigur |

---

### Parte 17 — Quick Reference Card

```
┌──────────────────────────────────────────────────────────────────────┐
│                     QUICK REFERENCE — SUPABASE                       │
├──────────────────────────────────────────────────────────────────────┤
│  SELECT              │  .from('t').select('*')                       │
│  SELECT cu JOIN      │  .select('*, clients(name, email)')           │
│  SELECT N:N          │  .select('*, rel!fk_name(id, col)')           │
│  SELECT un rând      │  .eq('id', id).maybeSingle()                  │
│  COUNT exact         │  .select('*', { count: 'exact', head: true }) │
│  COUNT estimat       │  .select('*', { count: 'estimated', head: t })│
│  EXISTS check        │  count: 'exact', head: true → count > 0       │
│  Soft delete filter  │  .is('deleted_at', null)                      │
├──────────────────────────────────────────────────────────────────────┤
│  INSERT              │  .insert({...}).select().single()             │
│  UPSERT pe PK        │  .upsert({...}).select().single()             │
│  UPSERT pe col       │  .upsert({...}, { onConflict: 'email' })      │
│  UPDATE              │  .update({...}).eq('id', id).select().single()│
│  DELETE (hard)       │  .delete().eq('id', id)                       │
│  DELETE (soft)       │  .update({ deleted_at: new Date().toISO() })  │
├──────────────────────────────────────────────────────────────────────┤
│  FILTRE              │  .eq .neq .gt .gte .lt .lte                   │
│                      │  .ilike .in .is .not                          │
│                      │  .or('col.eq.x,col.eq.y') — OR condiții      │
│                      │  .contains({ key: val }) — JSONB subset       │
│                      │  .overlaps('tags', ['a','b']) — array overlap │
│                      │  .textSearch('col', 'query', {websearch})     │
│  SORTARE             │  .order('col', { ascending: false })          │
│  PAGINARE OFFSET     │  .range(start, end) .limit(n)                 │
│  PAGINARE CURSOR     │  .lt('created_at', last).limit(n)             │
├──────────────────────────────────────────────────────────────────────┤
│  AGREGARE v12+       │  .select('amount.sum(), id.count()')          │
│  RPC                 │  .rpc('fn_name', { param: value })            │
│  ERROR               │  .throwOnError() — auto throw                 │
├──────────────────────────────────────────────────────────────────────┤
│  AUTH USER           │  const { data: { user } } = await            │
│                      │    supabase.auth.getUser()  ← sursă adevăr   │
│                      │  getSession() — doar pentru UI, NU pentru DB  │
│  AUTH ROLE           │  auth.uid() — UUID logat                      │
│                      │  auth.role() — 'anon' sau 'authenticated'     │
│                      │  auth.jwt() -> 'app_metadata' — claims        │
├──────────────────────────────────────────────────────────────────────┤
│  REALTIME            │  .channel('x').on('postgres_changes', {...},  │
│                      │    cb).subscribe((status, err) => {...})      │
│                      │  supabase.removeChannel(channel) — cleanup    │
│  PRESENCE            │  .channel('x').on('presence', ...).subscribe()│
│                      │  channel.track({ user_id, ... })              │
│  REPLICA IDENTITY    │  ALTER TABLE t REPLICA IDENTITY FULL          │
├──────────────────────────────────────────────────────────────────────┤
│  TIPURI SQL          │  text, numeric(10,2), integer, bigint         │
│                      │  uuid, boolean, timestamptz, jsonb, citext    │
│  INDEX               │  B-Tree (default), GIN (array/JSONB/FTS)     │
│                      │  BRIN (time-series mari), INCLUDE (covering)  │
│                      │  Compus: (user_id, status, created_at DESC)   │
│  TRANSACTION         │  FOR UPDATE + ordine deterministă (antiDL)   │
│                      │  REPEATABLE READ pentru rapoarte financiare   │
│  SECURITY DEFINER    │  SET search_path = public, auth — OBLIGATORIU │
│  VOLATILITY          │  STABLE (lookup), IMMUTABLE (calcul pur)      │
├──────────────────────────────────────────────────────────────────────┤
│  REGULI CRITICE      │  ✓ if (error) throw error — MEREU            │
│                      │  ✓ data ?? [] — după orice query array        │
│                      │  ✓ RLS ENABLE + FORCE + policy                │
│                      │  ✓ numeric, nu float — pentru bani            │
│                      │  ✓ maybeSingle() nu single() la SELECT        │
│                      │  ✓ getUser(), nu getSession() — pentru DB op  │
│                      │  ✓ userId din auth.getUser(), nu din URL       │
│                      │  ✓ FOR UPDATE + ordine deterministă           │
│                      │  ✓ CONCURRENTLY la CREATE INDEX în producție  │
│                      │  ✓ Index compus (user_id, status, created_at) │
│                      │  ✓ supabase db reset NICIODATĂ pe producție   │
│                      │  ✓ FOR EACH STATEMENT la trigger bulk         │
└──────────────────────────────────────────────────────────────────────┘
```

---

## Appendix — Schema Template Starter

Schema completă pentru orice proiect Supabase cu autentificare — copiezi, adaptezi, gata.

```sql
-- 1. Extensii
CREATE EXTENSION IF NOT EXISTS pg_trgm;  -- pentru ILIKE rapid pe text
CREATE EXTENSION IF NOT EXISTS citext;   -- pentru email case-insensitive (opțional)

-- 2. Profil utilizator (legat de auth.users, relație 1:1)
CREATE TABLE profiles (
  id          uuid PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  full_name   text,         -- NULL dacă userul nu a completat — semantic corect
  avatar_url  text,
  created_at  timestamptz DEFAULT now(),
  updated_at  timestamptz DEFAULT now()
);
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE profiles FORCE ROW LEVEL SECURITY;
CREATE POLICY "select own" ON profiles FOR SELECT USING (auth.uid() = id);
CREATE POLICY "update own" ON profiles FOR UPDATE
  USING (auth.uid() = id) WITH CHECK (auth.uid() = id);

-- Trigger updated_at automat
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN NEW.updated_at = now(); RETURN NEW; END;
$$ LANGUAGE plpgsql SET search_path = public;

CREATE TRIGGER set_updated_at BEFORE UPDATE ON profiles
FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- Trigger creare profil la signup (SECURITY DEFINER + search_path)
CREATE OR REPLACE FUNCTION handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO public.profiles (id, full_name)
  VALUES (
    NEW.id,
    NEW.raw_user_meta_data->>'full_name'  -- NULL dacă nu există — corect semantic
  );
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER SET search_path = public, auth;

CREATE TRIGGER on_auth_user_created
AFTER INSERT ON auth.users FOR EACH ROW EXECUTE FUNCTION handle_new_user();

-- 3. Tabelă principală — exemplu cu invoices (soft delete inclus)
CREATE TABLE invoices (
  id           uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id      uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  client_name  text NOT NULL,
  amount       numeric(12,2) NOT NULL CHECK (amount <> 0),
  -- CHECK (amount <> 0): permite negative (credit notes, stornări) dar nu zero
  status       text NOT NULL DEFAULT 'draft'
               CHECK (status IN ('draft','sent','paid','overdue','void')),
  notes        text,
  deleted_at   timestamptz DEFAULT NULL,  -- soft delete
  version      integer NOT NULL DEFAULT 1, -- optimistic locking
  created_at   timestamptz DEFAULT now(),
  updated_at   timestamptz DEFAULT now()
);

-- Indexuri (schema din zero — fără CONCURRENTLY)
CREATE INDEX idx_invoices_user_id          ON invoices(user_id);
CREATE INDEX idx_invoices_status           ON invoices(status);
CREATE INDEX idx_invoices_active           ON invoices(created_at DESC) WHERE deleted_at IS NULL;
CREATE INDEX idx_invoices_user_status_date ON invoices(user_id, status, created_at DESC);
-- Index compus acoperă 90% din query-urile de listare multi-tenant

ALTER TABLE invoices ENABLE ROW LEVEL SECURITY;
ALTER TABLE invoices FORCE ROW LEVEL SECURITY;
CREATE POLICY "select own" ON invoices FOR SELECT
  USING (auth.uid() = user_id);  -- Opțiunea B: fără deleted_at în policy (permite restore)
CREATE POLICY "insert own" ON invoices FOR INSERT
  WITH CHECK (auth.uid() = user_id);
CREATE POLICY "update own" ON invoices FOR UPDATE
  USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);
CREATE POLICY "delete own" ON invoices FOR DELETE
  USING (auth.uid() = user_id);

CREATE TRIGGER set_updated_at BEFORE UPDATE ON invoices
FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- 4. View active (fără rânduri soft-deleted)
CREATE VIEW active_invoices AS
SELECT * FROM invoices WHERE deleted_at IS NULL;
```

---

*Proiecte de referință: ERP Financiar · FinanceOS · Clinică Medicală · StudioFlow · Vibe Budget*

*Actualizat: Mai 2026 — v2.0 cu rafinări expert:*
- *FIX REGRESIE: `COALESCE(full_name, '')` → NULL în Appendix (semantic corect)*
- *ADĂUGAT: `FORCE ROW LEVEL SECURITY` — owner bypass RLS implicit (Parte 6)*
- *ADĂUGAT: `citext` extension pentru email case-insensitive (Parte 1)*
- *ADĂUGAT: Domain types pentru validare la nivel de tip (Parte 1)*
- *ADĂUGAT: UPSERT cu `onConflict` explicit (Parte 4)*
- *ADĂUGAT: `.throwOnError()` pattern modern Supabase JS v2.49+ (Parte 4)*
- *ADĂUGAT: `.or()` combinator, `.contains()/.overlaps()`, `.textSearch()` (Parte 5)*
- *ADĂUGAT: Cursor-based pagination — rapid pentru tabele mari (Parte 5)*
- *ADĂUGAT: `count: 'estimated'` vs `count: 'exact'` (Parte 3 + Greșeala 13)*
- *ADĂUGAT: BRIN index pentru time-series (Parte 8)*
- *ADĂUGAT: Covering indexes cu INCLUDE — index-only scan (Parte 8)*
- *ADĂUGAT: Index bloat monitoring + REINDEX CONCURRENTLY (Parte 8)*
- *ADĂUGAT: Supabase Cron pentru materialized view refresh (Parte 9)*
- *ADĂUGAT: Function volatility STABLE/IMMUTABLE/VOLATILE (Parte 10)*
- *ADĂUGAT: `STRICT` keyword pentru funcții NULL-safe (Parte 10)*
- *ADĂUGAT: `RETURNS TABLE(...)` pattern (Parte 10)*
- *ADĂUGAT: Transaction isolation levels — REPEATABLE READ/SERIALIZABLE (Parte 11)*
- *ADĂUGAT: Deadlock prevention — ordine deterministă a lock-urilor (Parte 11)*
- *ADĂUGAT: SAVEPOINT pentru rollback parțial (Parte 11)*
- *ADĂUGAT: `supabase db reset` warning — PERICULOS în producție (Parte 12)*
- *ADĂUGAT: Down migrations + strategie rollback (Parte 12)*
- *ADĂUGAT: Column type change cu USING clause (Parte 12)*
- *ADĂUGAT: Greșeala 13 — `count: 'exact'` performanță (Parte 13)*
- *ADĂUGAT: `createClient<Database>` typed client (Parte 14)*
- *ADĂUGAT: `satisfies` operator TypeScript 4.9+ (Parte 14)*
- *ADĂUGAT: Error handling în `.subscribe()` callback (Parte 16)*
- *ADĂUGAT: Presence API + Broadcast API (Parte 16)*
- *ACTUALIZAT: Quick Reference Card cu toate adăugirile*
- *ACTUALIZAT: Checklist Pre-Deploy cu 8 itemi noi*
- *ACTUALIZAT: Appendix Schema Template cu FORCE RLS, index compus, version column*
