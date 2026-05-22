---
name: reference-skill-auth-audit
description: "Skill /auth-audit — audit static autentificare & autorizare pe 22 reguli (Supabase Auth/RLS/Storage/Middleware/Session/Server Actions/HTML Vanilla); Next.js + HTML Vanilla; BLOCKER/ATENȚIE/OK"
metadata:
  node_type: memory
  type: reference
  originSessionId: current
---

Skill `/auth-audit` — audit static de cod pentru proiecte cu autentificare și autorizare.

**Locație fișier:** `C:\Users\admin\.claude\commands\auth-audit.md`

**Invocare:** `/auth-audit Desktop/vibe-budget` (cu cale) sau `/auth-audit` (întreabă)

**Ce face:** Detectează automat tipul de proiect (Next.js / HTML Vanilla / Mix), găsește fișierele relevante (TS/TSX, HTML/JS, SQL migrations, middleware, next.config), și raportează BLOCKER / ATENȚIE / OK pentru 22 reguli pe 6 categorii. Nu modifică cod — doar raportează. Listează la final 6 verificări manuale nedetectabile static.

**Detectare automată:**
- Next.js: `next.config.ts` sau `next.config.js` prezent
- HTML Vanilla: doar fișiere `.html` / `.js`, fără `next.config.*`
- Supabase: `@supabase/ssr` sau `@supabase/supabase-js` în `package.json`

**Cele 22 reguli:**

- **A. Supabase Auth Setup** (5 reguli)
  - A1: `getSession()` server-side în loc de `getUser()` — **BLOCKER**
  - A2: `exchangeCodeForSession` absent în callback OAuth — **BLOCKER**
  - A3: Open redirect prevention absent (`safeNext` validation) — **BLOCKER**
  - A4: Cookie `httpOnly: true` + `sameSite: 'lax'` (nu 'strict') — **ATENȚIE**
  - A5: Env vars validate cu Zod la startup — **ATENȚIE**

- **B. RLS & Storage** (5 reguli)
  - B1: UPDATE policies fără `WITH CHECK` — **ATENȚIE**
  - B2: Politici fără `TO authenticated` — **ATENȚIE**
  - B3: `user_roles` / `audit_log` fără `WITH CHECK (false)` pe mutații — **BLOCKER**
  - B4: `getPublicUrl()` pe bucket privat — **BLOCKER**
  - B5: `SECURITY DEFINER` cu SQL dinamic (`||` / `EXECUTE format`) — **BLOCKER**

- **C. Middleware & Security Headers** (4 reguli — Next.js)
  - C1: Matcher pozitiv (nu negativ) în middleware — **BLOCKER**
  - C2: Security headers absent din `next.config` — **ATENȚIE**
  - C3: Webhook fără `timingSafeEqual` — **BLOCKER**
  - C4: Route Handlers POST fără Origin validation — **ATENȚIE**

- **D. Session & Password Security** (3 reguli)
  - D1: Password change fără `signOut(scope: 'others')` — **BLOCKER**
  - D2: `signOut()` fără scope explicit — **ATENȚIE**
  - D3: Magic link URL logat în server logs — **ATENȚIE**

- **E. Server Actions & Rate Limiting** (3 reguli — Next.js)
  - E1: Server Action cu mutații DB fără `getUser()` — **BLOCKER**
  - E2: Rate limiting absent (Upstash sau similar) — **ATENȚIE**
  - E3: Lanț auth→RBAC→Zod incomplet în Server Actions — **ATENȚIE**

- **F. HTML Vanilla Security** (2 reguli — HTML Vanilla)
  - F1: `innerHTML` cu date dinamice (nu literale) — **BLOCKER**
  - F2: SRI absent pe scripturi CDN — **ATENȚIE**

**Ordinea fix-urilor la BLOCKER:** A1 (getSession) > A2 (exchangeCode) > A3 (open redirect) > B3 (privilege escalation) > B5 (SECURITY DEFINER) > B4 (getPublicUrl) > C1 (matcher) > C3 (webhook HMAC) > D1 (password+sessions) > E1 (Server Action auth) > F1 (innerHTML)

**Verificări manuale listate în raport (nedetectabile static):**
- RLS ENABLE pe toate tabelele → Dashboard
- `.env.local` în `.gitignore` → `git log -S 'SERVICE_ROLE'`
- TypeScript types generate din schema → `supabase gen types typescript`
- MFA recovery codes hashuite în DB
- Backup-uri criptate activate → Dashboard
- Incident response plan documentat

**Proiecte țintă:** Clinică Medicală · ERP Financiar · Vibe Budget · Vibe Website (orice proiect Supabase) · orice proiect cu auth

**How to apply:** Înainte de orice deploy pe proiect cu autentificare, sau la audit al unui proiect existent. Rulează înaintea sau după `/nextjs-audit` — skill-urile sunt complementare (auth-audit merge adânc pe securitate auth, nextjs-audit acoperă arhitectura App Router).

**Legat de:** [[reference-skill-nextjs-audit]], [[project_ghid_auth_authorization]], [[project_clinica_medicala]], [[project_erp_financiar]], [[project_vibe_budget]]
