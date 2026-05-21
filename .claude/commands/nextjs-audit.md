---
description: Audit Next.js App Router — verifică 19 reguli critice (securitate, boundary, Server Actions, TypeScript, pre-deploy). Raportează BLOCKER / ATENȚIE / OK fără a modifica codul. Bazat pe ghid-nextjs-full-stack-v2.md.
---

# /nextjs-audit — Audit Next.js App Router

**Scopul:** Analizează fișierele unui proiect Next.js App Router pentru greșeli critice și raportează BLOCKER / ATENȚIE / OK per regulă. Bazat pe ghid-nextjs-full-stack-v2.md.

---

## PASUL 1 — Identifică directorul

**Dacă $ARGUMENTS conține o cale** (ex: `/nextjs-audit Desktop/vibe-budget`):
Lucrează în: `C:\Users\admin\$ARGUMENTS`

**Dacă $ARGUMENTS este gol:**
Întreabă utilizatorul: `Pe care proiect Next.js rulăm auditul? (ex: Desktop/vibe-budget)`
Sau dacă există context clar din sesiune, folosește directorul curent.

---

## PASUL 2 — Găsește fișierele relevante

Rulează în paralel cu Glob:
- `**/*.tsx` în directorul proiectului (exclude node_modules, .next, dist, .git)
- `**/*.ts` în directorul proiectului (exclude node_modules, .next, dist, .git)
- `next.config.ts` sau `next.config.js` (rădăcina proiectului)
- `middleware.ts` sau `middleware.js` (rădăcina sau src/)
- `.env.local` (rădăcina proiectului)
- `package.json` (rădăcina proiectului)

Dacă nu găsești fișiere TSX/TS: raportează `EROARE: director gol sau proiect non-Next.js` și oprește.

Notează: [N] TSX + [M] TS + next.config: DA/NU + middleware: DA/NU + .env.local: DA/NU

---

## PASUL 3 — Rulează verificările pe 5 categorii

### CATEGORIA A — SECURITATE (cel mai critic)

*Ordinea A1→A6 reflectă impactul de securitate — fixează întotdeauna în această ordine.*

**A1 — getUser() vs getSession() pe server**
Grep pentru `getSession()` în fișierele `.ts` și `.tsx` din `app/`, `actions/`, `lib/`.
- Apel `getSession()` găsit → **BLOCKER** (JWT nevalidat cu serverul; atacatorul poate manipula cookie-ul și trece de orice `if (session)`. Fix: înlocuiește cu `await supabase.auth.getUser()` și verifică `data.user`)
- Absent → **OK**

**A2 — server-only în fișiere cu chei secrete**
Grep pentru `SERVICE_ROLE` sau `SUPABASE_SERVICE_ROLE_KEY` sau `createServiceRoleClient` în fișierele `.ts`/`.tsx`.
Pentru fiecare fișier găsit, verifică dacă conține `import 'server-only'` sau se află în `route.ts` (garantat server-side).
- Fișier cu SERVICE_ROLE fără `import 'server-only'` și care nu e `route.ts` → **BLOCKER** (cheie secretă poate ajunge în bundle JS client dacă cineva importă fișierul greșit. Fix: adaugă `import 'server-only'` ca prima linie)
- Toate au `server-only` sau sunt `route.ts` → **OK**
- Nicio folosire SERVICE_ROLE → **OK**

**A3 — NEXT_PUBLIC_ pe chei secrete**
Grep în `.env.local` (dacă există) și în fișierele `.ts`/`.tsx` pentru `NEXT_PUBLIC_.*SECRET`, `NEXT_PUBLIC_.*SERVICE_ROLE`, `NEXT_PUBLIC_.*PRIVATE`, `NEXT_PUBLIC_.*PASSWORD`.
- Pattern găsit → **BLOCKER** (cheie secretă expusă în bundle JS — vizibilă în DevTools de oricine. Fix: renumește fără `NEXT_PUBLIC_` și mută accesul server-side)
- Absent → **OK**

**A4 — dangerouslySetInnerHTML absent**
Grep pentru `dangerouslySetInnerHTML` în `.tsx`/`.ts`.
- Găsit → **BLOCKER** (risc XSS direct. Fix: înlocuiește cu `textContent` sau folosește `DOMPurify` dacă HTML e strict necesar)
- Absent → **OK**

**A5 — eval / innerHTML direct absent**
Grep pentru `eval(` sau `innerHTML\s*=` sau `new Function(` în `.ts`/`.tsx`.
- Găsit → **BLOCKER** (code injection / XSS garantat dacă inputul vine de la utilizator)
- Absent → **OK**

**A6 — userId exclusiv din getUser(), nu din params/body**
Grep pentru pattern `params.*[Uu]ser[Ii]d` sau `searchParams.*[Uu]ser[Ii]d` sau `body.*[Uu]ser[Ii]d` sau `req\.body.*[Uu]ser[Ii]d` ca sursă de identificare în fișiere server-side.
- Pattern găsit ca sursă de identificare (nu doar citire date) → **BLOCKER** (bypass auth trivial — oricine poate trimite alt userId. Fix: `const { data: { user } } = await supabase.auth.getUser()` și folosește `user.id`)
- Absent → **OK**

---

### CATEGORIA B — APP ROUTER BOUNDARY

**B1 — error.tsx are 'use client'**
Glob pentru fișiere numite `error.tsx` în oricare subdirector al proiectului.
Pentru fiecare, verifică dacă prima linie sau primele 3 linii conțin `'use client'`.
- `error.tsx` fără `'use client'` → **BLOCKER** (Next.js cere explicit ca error.tsx să fie Client Component — altfel aruncă eroare la build sau nu funcționează error boundary. Fix: adaugă `'use client'` ca prima linie)
- Toate au `'use client'` → **OK**

**B2 — global-error.tsx are html și body**
Verifică dacă există `global-error.tsx` în rădăcina folderului `app/`.
Dacă există, citește-l și verifică prezența tag-urilor `<html>` și `<body>` în JSX returnat.
- Există fără `<html>` și `<body>` → **BLOCKER** (global-error.tsx înlocuiește complet root layout.tsx când e activat — trebuie să furnizeze structura HTML completă. Fix: învelește conținutul în `<html><body>...</body></html>`)
- Are `<html><body>` sau nu există → **OK**

**B3 — useRouter din 'next/navigation', nu 'next/router'**
Grep pentru `from 'next/router'` în `.ts`/`.tsx`.
- Găsit → **BLOCKER** (App Router folosește `next/navigation` — `next/router` e Pages Router; `useRouter` din `next/router` returnează un obiect incompatibil și `router.push()` poate să nu funcționeze sau să dea erori greu de depanat. Fix: înlocuiește cu `import { useRouter } from 'next/navigation'`)
- Absent → **OK**

**B4 — 'use client' pe page.tsx justificat**
Glob pentru fișiere `page.tsx`. Grep pentru `'use client'` la începutul lor.
Pentru fiecare `page.tsx` cu `'use client'`, verifică dacă există și `useState`, `useEffect`, `onClick`, `onChange`, `useRef` sau alt hook/event handler în același fișier.
- `'use client'` pe `page.tsx` fără niciunul din markerii de mai sus → **ATENȚIE** (toate beneficiile RSC pierdute: no SSR data fetching, no server-side Supabase, bundle mai mare. Probabil `'use client'` pus preventiv. Fix: mută interactivitatea într-un Client Component copil și păstrează `page.tsx` ca Server Component)
- `'use client'` justificat sau absent → **OK**

---

### CATEGORIA C — SERVER ACTIONS

*Categoria se aplică dacă există un director `actions/` sau funcții cu `'use server'`.*
*Dacă nu există Server Actions în proiect: marchează toate cu `— (Server Actions negăsite)`*

**C1 — 'use server' prezent în fișierele de actions**
Glob pentru fișiere în `actions/`, `app/actions/`, `src/actions/`.
Grep pentru `'use server'` în fiecare fișier găsit.
- Fișier în `actions/` fără `'use server'` → **BLOCKER** (funcțiile nu sunt Server Actions — rulează pe client, accesul direct la DB/Supabase e imposibil, cheile API sunt expuse. Fix: adaugă `'use server'` ca prima linie a fișierului)
- Toate au `'use server'` sau nu există `actions/` → **OK**

**C2 — redirect() în afara try/catch**
Grep pentru `redirect(` în fișierele cu `'use server'`.
Dacă există, verifică dacă apelul e învelit într-un bloc `try {`.
- `redirect(` găsit în interiorul unui bloc `try { ... }` → **ATENȚIE** (redirect() aruncă o eroare specială Next.js care e prinsă de catch — redirect-ul nu se execută niciodată, utilizatorul rămâne pe pagină fără feedback. Fix: mută `redirect()` după blocul try/catch, în afara lui)
- Absent sau în afara try/catch → **OK**

**C3 — Server Action nu e apelat în useEffect**
Grep pentru fișiere cu `'use client'` care importă din `@/actions/` sau `../actions/`.
În fiecare astfel de fișier, verifică dacă importurile respective apar și în interiorul unui `useEffect`.
- Server Action apelat în `useEffect` → **ATENȚIE** (anti-pattern: Server Actions sunt pentru mutații declanșate de utilizator, nu pentru data fetching automat. În `useEffect` pot crea request-uri infinite, race conditions sau se execută la fiecare render. Fix: mută în event handler sau folosește `use()` hook + `Suspense` pentru fetching automat)
- Absent → **OK**

---

### CATEGORIA D — TYPESCRIPT & NEXT.JS 15

**D1 — params/searchParams cu await (Next.js 15)**
Grep pentru pattern `params: { [a-zA-Z]+: string }` sau `searchParams: { [a-zA-Z]+: string }` în fișierele `page.tsx` și `layout.tsx` (fără `Promise<` înainte).
Mai simplu: grep pentru `params\.` sau `searchParams\.` fără `await params` sau `await searchParams` în proximity.
- Pattern de acces sincron găsit în Next.js 15 → **ATENȚIE** (Next.js 15: `params` și `searchParams` sunt Promises — accesul direct returnează Promise obiect, nu valoarea; provoacă bug silențios. Fix: `const { id } = await params` în funcția async)
- Absent sau folosit cu `await` → **OK**

**D2 — unknown în loc de any**
Grep pentru `: any` sau `as any` în `.ts`/`.tsx` (exclude fișierele `.d.ts` și folderele `node_modules`).
- Mai mult de 3 apariții → **ATENȚIE** (any dezactivează type checking complet pe acea variabilă; erorile de tip nu mai sunt prinse la build. Fix: înlocuiește cu `unknown` și adaugă narrowing explicit: `if (typeof x === 'string')`)
- 0–3 apariții → **OK** (toleranță mică pentru cazuri rare justificate)

**D3 — console.log absent din codul de producție**
Grep pentru `console.log(` în `.ts`/`.tsx` (exclude fișiere cu `.test.`, `.spec.`, `/e2e/`, `/__tests__/`).
- Găsit → **ATENȚIE** (date sensibile și noise în browser console în producție; poate expune structuri interne. Fix: înlocuiește cu `console.error` pentru erori sau cu un logger dedicat; adaugă ESLint rule `no-console`)
- Absent → **OK**

---

### CATEGORIA E — PRE-DEPLOY

**E1 — Security headers în next.config**
Citește `next.config.ts` sau `next.config.js`.
Verifică prezența funcției `headers()` cu cel puțin `X-Frame-Options`, `X-Content-Type-Options`, și un header de tip `Content-Security-Policy`.
- Funcția `headers()` lipsește complet → **ATENȚIE** (aplicația vulnerabilă la clickjacking, MIME sniffing, XSS via iframe. Fix: adaugă blocul `headers()` din Parte 16 a ghidului Next.js)
- Există `headers()` dar lipsesc mai puțin de 3 headere de securitate → **ATENȚIE** (protecție parțială — listează headerele lipsă)
- Toate 3+ prezente → **OK**

**E2 — Variabile de mediu validate la startup**
Grep pentru `process.env.` în fișierele cheie: `middleware.ts`, orice fișier din `lib/`, `app/layout.tsx`.
Grep pentru funcție sau fișier `validateEnv` sau `env.ts` sau `env.mjs` în rădăcina proiectului.
- Cel puțin 5 `process.env.` accesate fără nicio validare centralizată (fără `validateEnv` sau similar) → **ATENȚIE** (variabilă `.env` lipsă = crash silențios sau `undefined` în producție; greu de depanat. Fix: creează `lib/env.ts` care validează existența la startup)
- Există validare sau mai puțin de 5 accesări directe → **OK**

**E3 — Error tracking configurat**
Citește `package.json` și verifică prezența în `dependencies` sau `devDependencies` a: `@sentry/nextjs`, `@sentry/react`, `@datadog/browser-rum`, `logrocket`, `bugsnag`.
- Niciuna din librăriile de mai sus → **INFO: neimplementat** (opțional dar recomandat pentru producție — erorile din prod nu sunt vizibile fără error tracking)
- Cel puțin una prezentă → **INFO: implementat**

---

## PASUL 4 — Raportează în formatul exact de mai jos

```
=== NEXTJS-AUDIT: [director / proiect] ===
Fișiere analizate: [N] TSX + [M] TS + [next.config: DA/NU] + [middleware: DA/NU] + [.env.local: DA/NU]

── A. SECURITATE ────────────────────────────────
  [✓/✗]   A1 getUser() vs getSession()           [status + fișier:linie dacă BLOCKER]
  [✓/✗]   A2 server-only pe SERVICE_ROLE          [status + fișier:linie dacă BLOCKER]
  [✓/✗]   A3 NEXT_PUBLIC_ pe chei secrete         [status + cheie expusă dacă BLOCKER]
  [✓/✗]   A4 dangerouslySetInnerHTML absent        [status + fișier:linie dacă BLOCKER]
  [✓/✗]   A5 eval / innerHTML direct absent       [status + fișier:linie dacă BLOCKER]
  [✓/✗]   A6 userId exclusiv din getUser()        [status + fișier:linie dacă BLOCKER]

── B. APP ROUTER BOUNDARY ───────────────────────
  [✓/✗]   B1 error.tsx are 'use client'           [status + fișier dacă BLOCKER]
  [✓/✗]   B2 global-error.tsx are html+body       [status dacă BLOCKER]
  [✓/✗]   B3 useRouter din next/navigation        [status + fișier:linie dacă BLOCKER]
  [✓/!]   B4 'use client' pe page.tsx justificat  [status + fișiere cu problemă dacă ATENȚIE]

── C. SERVER ACTIONS ────────────────────────────
  [✓/✗]   C1 'use server' în actions/             [status + fișier dacă BLOCKER]
  [✓/!]   C2 redirect() în afara try/catch        [status + fișier:linie dacă ATENȚIE]
  [✓/!]   C3 Server Action nu e în useEffect      [status + fișier dacă ATENȚIE]
  (sau: — Server Actions negăsite în proiect)

── D. TYPESCRIPT & NEXT.JS 15 ───────────────────
  [✓/!]   D1 params cu await (Next.js 15)         [status + fișiere afectate dacă ATENȚIE]
  [✓/!]   D2 unknown în loc de any                [status + număr apariții dacă ATENȚIE]
  [✓/!]   D3 console.log absent din prod          [status + număr apariții dacă ATENȚIE]

── E. PRE-DEPLOY ────────────────────────────────
  [✓/!]   E1 Security headers în next.config      [status + headere lipsă dacă ATENȚIE]
  [✓/!]   E2 Env vars validate la startup         [status]
  [i]     E3 Error tracking (Sentry/similar)      [Implementat / Neimplementat (opțional)]

══════════════════════════════════════════════════
BLOCKER-e: [N]  |  ATENȚIE: [M]  |  OK: [K]

VERDICT: [BLOCKER ✗ / ATENȚIE ⚠ / CLEAN ✓]

Fix-uri necesare (BLOCKER-e în ordinea impactului):
  1. [A1/A2/B1/...] descriere exactă + codul de adăugat/modificat
  2. ...
```

---

## Reguli de verdict

| Condiție | Verdict |
|---|---|
| Cel puțin un BLOCKER | **BLOCKER ✗** — listezi fix-ul complet pentru fiecare |
| Zero BLOCKER-e, cel puțin un ATENȚIE | **ATENȚIE ⚠** — informezi, utilizatorul decide |
| Toate OK sau INFO | **CLEAN ✓** |

---

## Note de execuție

- **Nu modifica niciun fișier** — doar raportezi; utilizatorul decide ce și când fixează
- **Specifică întotdeauna fișier + linie** pentru BLOCKER și ATENȚIE — nu raporta vag
- **Ordinea fix-urilor la BLOCKER**: A1 (getSession) > A2 (server-only) > A3 (NEXT_PUBLIC_) > A4-A5 (XSS) > A6 (userId) > B1 (error.tsx) > B3 (next/router) > C1 (use server) — securitate primul
- **Proiecte fără Supabase**: A1, A2 marchează cu `— (Supabase negăsit în proiect)` și explică în paranteză
- **Proiecte Pages Router** (fără folder `app/`): raportează `ATENȚIE: proiect folosește Pages Router — regulile B, C și D1 nu se aplică; consideră migrarea la App Router`
- **Proiecte fără Server Actions** (fără folder `actions/`): categoria C marchează cu `— (Server Actions negăsite)` — nu e eroare
