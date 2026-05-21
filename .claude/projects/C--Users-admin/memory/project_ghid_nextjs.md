---
name: project_ghid_nextjs
description: "Ghid Next.js Full-Stack Development (17 secțiuni, 5 Bloc-uri): RSC, Server vs Client, Server Actions, useTransition, Router Cache, Intercepting Routes, CSP, 18 greșeli comune"
metadata: 
  node_type: memory
  type: project
  originSessionId: a3fd517a-f93d-4269-830f-cf60e6caed19
---

Ghid Skill 6 — Next.js Full-Stack Development v2.0 COMPLET, salvat la Desktop/Vibe-Coding/ghid-nextjs-full-stack-v1.md

**Why:** Framework-ul principal pentru toate cele 5 proiecte full-stack (ERP, Clinică, Vibe Budget, StudioFlow, Descrieri Produse). Gap-urile critice: App Router avansat, server vs client, middleware, caching, performanță.

**How to apply:** Referință la orice sesiune Next.js + Supabase — în special server-only (Parte 7), React.cache() vs unstable_cache vs `use cache` (Parte 9), useOptimistic + useTransition (Parte 3), Context Providers (Parte 1), redirect() outside try/catch (Parte 3), greșeli comune (Parte 12), checklist pre-deploy (Parte 15), CSP + security headers (Parte 16).

## Structură

17 secțiuni (0–16) în 5 Blocuri:
- Bloc 1: Arhitectură (RSC, Server vs Client, Providers pattern, file conventions, generateStaticParams, global-error.tsx, Route Groups)
- Bloc 2: Data & Mutations (Server Actions, useFormStatus, useActionState, useOptimistic, useTransition, bind(), Zod)
- Bloc 3: Supabase SSR (createServerClient, Middleware + rate limiting Upstash, getUser vs getSession, admin client)
- Bloc 4: Performanță (Caching 4 nivele, Router Cache staleTimes, React.cache, unstable_cache, `use cache` Next.js 15, revalidatePath vs router.refresh, Streaming, Suspense, Intercepting Routes, Parallel Routes, next/dynamic, next/image, next/font)
- Bloc 5: Producție (CSP + security headers complet, 18 greșeli comune, TypeScript Next.js 15 params, z.infer, satisfies, checklist, Quick Reference Card)

## Concepte Cheie

- `import 'server-only'` — build error dacă codul server ajunge în client bundle
- `React.cache()` — per-request deduplication (request memoization)
- `unstable_cache()` — persistent cross-request (Data Cache), cu revalidate + tags
- `use cache` + `cacheTag()` + `cacheLife()` — Next.js 15 API stabil (înlocuiește unstable_cache)
- `redirect()` — aruncă NEXT_REDIRECT, trebuie **în afara** try/catch
- `getUser()` vs `getSession()` — getUser() validează cu server Auth (sigur); getSession() local-only (bypassabil)
- `useOptimistic` — UI instant fără await server
- `useTransition` + `startTransition` — apel Server Action din event handler (non-form)
- `router.refresh()` vs `revalidatePath()` — refresh e client-side RSC re-fetch, NU invalidează Data Cache; revalidatePath e server-side
- Router Cache — `staleTimes: { dynamic: 0, static: 300 }` în next.config.ts
- `bind(null, id)` — trimite argumente extra la Server Actions
- Context Providers — izolat în Client Component separat, nu în root layout
- `nuqs` — URL search params type-safe (filtre, paginare)
- `use()` hook React 19 — citire Promise în Client Component (Suspense automat)
- Intercepting Routes `(.)` — pattern modal cu URL propriu
- `generateStaticParams` + `dynamicParams` — SSG cu rute dinamice
- Date objects — pierd metodele la serializare server→client; transmite string ISO

## Appendix: Template CRUD Complet

Include cod complet gata de copiat cu useTransition + useOptimistic:
- lib/supabase/server.ts + client.ts + admin.ts
- lib/data/invoices.ts cu getCachedInvoices (unstable_cache)
- lib/actions/invoices.ts cu createInvoice/deleteInvoice (Server Actions, Zod, revalidateTag)
- app/(dashboard)/invoices/page.tsx cu Suspense streaming
- components/InvoiceList.tsx cu useOptimistic + useTransition
- middleware.ts cu cookie refresh + auth protection + rate limiting

[[project_erp_financiar]] [[project_clinica_medicala]] [[project_vibe_budget]] [[project_studioflow]] [[project_descriere_produse_app]] [[reference-skill-nextjs-audit]]
