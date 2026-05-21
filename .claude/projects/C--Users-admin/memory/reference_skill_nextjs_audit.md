---
name: reference-skill-nextjs-audit
description: "Skill /nextjs-audit — audit static Next.js App Router pe 19 reguli critice (securitate, boundary, Server Actions, TypeScript, pre-deploy); locație, utilizare, reguli acoperite"
metadata: 
  node_type: memory
  type: reference
  originSessionId: a3fd517a-f93d-4269-830f-cf60e6caed19
---

Skill `/nextjs-audit` — audit static de cod pentru proiecte Next.js App Router.

**Locație fișier:** `C:\Users\admin\.claude\commands\nextjs-audit.md`

**Invocare:** `/nextjs-audit Desktop/vibe-budget` (cu cale) sau `/nextjs-audit` (întreabă)

**Ce face:** Citește fișierele proiectului (TSX + TS + next.config + middleware + .env.local) și raportează BLOCKER / ATENȚIE / OK pentru 19 reguli pe 5 categorii. Nu modifică cod — doar raportează.

**Cele 19 reguli:**

- **A. Securitate** (6 reguli — cel mai critic)
  - A1: `getUser()` vs `getSession()` pe server — JWT nevalidat = bypass auth
  - A2: `import 'server-only'` în fișiere cu SERVICE_ROLE key
  - A3: `NEXT_PUBLIC_` pe chei secrete (SECRET, SERVICE_ROLE, PRIVATE)
  - A4: `dangerouslySetInnerHTML` absent
  - A5: `eval()` / `innerHTML =` / `new Function()` absente
  - A6: `userId` exclusiv din `getUser()`, nu din `params`/`body`/`searchParams`

- **B. App Router Boundary** (4 reguli)
  - B1: `error.tsx` are `'use client'` (obligatoriu pentru Error Boundary)
  - B2: `global-error.tsx` are `<html><body>` (înlocuiește root layout)
  - B3: `useRouter` importat din `next/navigation` (nu `next/router` — Pages Router)
  - B4: `'use client'` pe `page.tsx` justificat (nu pus preventiv)

- **C. Server Actions** (3 reguli — dacă există `actions/`)
  - C1: `'use server'` prezent în fiecare fișier din `actions/`
  - C2: `redirect()` în afara blocului `try/catch`
  - C3: Server Actions nu sunt apelate din `useEffect`

- **D. TypeScript & Next.js 15** (3 reguli)
  - D1: `params` și `searchParams` accesate cu `await` (Next.js 15: sunt Promises)
  - D2: `unknown` în loc de `any` (max 3 apariții tolerate)
  - D3: `console.log` absent din codul de producție

- **E. Pre-Deploy** (3 reguli)
  - E1: Security headers în `next.config` (X-Frame-Options, X-Content-Type-Options, CSP)
  - E2: Variabile de mediu validate la startup
  - E3: Error tracking configurat (Sentry/similar — informativ)

**Verdict:** BLOCKER ✗ (cel puțin un blocker) / ATENȚIE ⚠ (zero blockere, atenții) / CLEAN ✓

**Ordinea fix-urilor la BLOCKER:** A1 (getSession) > A2 (server-only) > A3 (NEXT_PUBLIC_) > A4-A5 (XSS) > A6 (userId) > B1 (error.tsx) > B3 (next/router) > C1 (use server)

**Proiecte țintă:** Vibe Budget · Clinică Medicală · ERP Financiar · App Descriere Produse · Vibe Caffè · orice proiect Next.js App Router

**How to apply:** Înainte de orice deploy pe proiect Next.js, sau când apar bug-uri de auth/securitate/routing — rulează `/nextjs-audit [proiect]` pentru diagnostic rapid.

**Legat de:** [[reference-skill-offline-audit]], [[project-ghid-nextjs]]
