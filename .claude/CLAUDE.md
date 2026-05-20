# Reguli Tehnice Active — JS/TypeScript

Stack-uri active în acest mediu: Next.js 14+ App Router, Supabase v2, React 18+, Node.js ESM, TypeScript.
Aplicate la orice sesiune de cod, indiferent de proiect.

---

## Universal

- **`await` obligatoriu** la orice apel async: Supabase, `fetch`, Claude API, `fs`, `readFile` — lipsă `await` returnează `Promise {}`, nu date.
- **`data ?? []`** după orice query Supabase — `.data` poate fi `null`; nu presupune array.
- **`if (error) throw error`** înainte de a folosi `data` — Supabase returnează erori ca obiect, nu le aruncă automat.
- **Null check după `.find()`** — returnează `T | undefined`; acces pe proprietăți fără verificare prealabilă = crash garantat.
- **`??` nu `||`** pentru fallback numeric sau string — `||` tratează `0` și `''` ca falsy; `??` verifică strict `null`/`undefined`.
- **`async` e prefix pentru funcție, nu pentru apel**: `const fn = async () => {}` ✓ / `async supabase.from(...)` ❌ SyntaxError.
- **Spread în arrow ce returnează obiect literal**: `prev => ({ ...prev, x: 1 })` ✓ / `prev => { ...prev, x: 1 }` ❌ SyntaxError sau `undefined` silențios.

---

## React / Next.js App Router

- **`userId` exclusiv din `supabase.auth.getUser()`** — niciodată din `searchParams`, URL params, sau request body (bypass auth trivial).
- **`setLoading(true/false)`** în orice handler async cu acțiune utilizator — previne double-submit și UI inconsistent.
- **`.maybeSingle()`** pe SELECT care poate returna 0 rânduri — `.single()` aruncă eroare dacă nu găsește nimic (Supabase v2).
- **`.single()` după INSERT** (`.insert().select().single()`) e corect — INSERT returnează întotdeauna exact 1 rând.
- **`'use client'`** dacă fișierul folosește `useState`, `useEffect`, sau orice browser API (`localStorage`, `window`, `document`).
- **`useEffect` fără `async` direct** — învelești în funcție internă și o apelezi; `useEffect(async () => {...})` ignoră cleanup și pierde Error Boundary.
- **State update funcțional** când depinde de starea anterioară: `setState(prev => [...prev, item])` nu `setState([...state, item])`.
- **Cleanup în `useEffect`** cu operații async pe pagini cu navigare frecventă — flag `cancelled` sau `AbortController`.
- **`key={item.id}`** pe orice element din `.map()` în JSX — lipsă `key` = warning + comportament impredictibil la reorder.

---

## Node.js / ESM

- **`"type": "module"`** în `package.json` pentru syntax `import/export`; extensia `.js` obligatorie în import-uri, chiar dacă sursa e `.ts`.
- **`process.env.X`** are tipul `string | undefined` — validează existența la startup, nu presupune `string`.
- **Path traversal**: `path.resolve` + `startsWith(allowed + path.sep)` — fără `path.sep`, un director `/files_backup` trece validarea pentru `/files`.

---

## Securitate — Non-Negociabile

- `innerHTML = userInput` → înlocuit cu `textContent` sau `innerText`.
- `dangerouslySetInnerHTML` → evitat complet, indiferent de context.
- `eval()`, `new Function(userInput)`, `setTimeout(string, ms)` → interzis.
- Chei API în cod client → `process.env` server-side exclusiv; prefix `NEXT_PUBLIC_` doar pentru chei intenționat publice.
- RLS Supabase activat **și** `auth.getUser()` validat server-side — ambele, nu alternativ.

---

## TypeScript

- Interface pentru tabel Supabase: compară câmp cu câmp cu schema reală din dashboard — Claude nu vede schema DB.
- `Omit<T, 'id' | 'created_at'>` pentru tipul de input la INSERT (câmpuri generate de DB excluse).
- `unknown` în loc de `any` la date din surse externe — forțezi narrowing explicit.
- `Number(value)` conversie explicită pe câmpuri numerice din surse externe înainte de calcule financiare.

---

*Proiecte de referință: Vibe Budget · ERP Financiar · StudioFlow · Clinică Medicală · Safe Change Agent · Agenți AI · CashPulse*
*Actualizat: Mai 2026 — bazat pe ghid-javascript-typescript-v1.md*
