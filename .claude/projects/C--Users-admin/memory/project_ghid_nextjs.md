---
name: project_ghid_nextjs
description: "Ghid Next.js Full-Stack Development (17 secțiuni, 5 Bloc-uri): RSC, Server vs Client, Server Actions, Middleware, Supabase SSR, Caching, Streaming, next/dynamic, 15 greșeli comune"
metadata: 
  node_type: memory
  type: project
  originSessionId: a3fd517a-f93d-4269-830f-cf60e6caed19
---

Ghid Skill 6 — Next.js Full-Stack Development v1.1 COMPLET, salvat la Desktop/Vibe-Coding/ghid-nextjs-full-stack-v1.md

**Why:** Framework-ul principal pentru toate cele 5 proiecte full-stack (ERP, Clinică, Vibe Budget, StudioFlow, Descrieri Produse). Gap-urile critice: App Router avansat, server vs client, middleware, caching, performanță.

**How to apply:** Referință la orice sesiune Next.js + Supabase — în special server-only (Parte 7), React.cache() vs unstable_cache (Parte 9), useOptimistic (Parte 3), bind() pattern (Parte 3), Context Providers (Parte 1), redirect() outside try/catch (Parte 3), greșeli comune (Parte 12), checklist pre-deploy (Parte 15).

## Structură

17 secțiuni (0–16) în 5 Blocuri:
- Bloc 1: Arhitectură (RSC, Server vs Client, Providers pattern, file conventions, Route Groups)
- Bloc 2: Data & Mutations (Server Actions, useFormStatus, useActionState, useOptimistic, bind())
- Bloc 3: Supabase SSR (createServerClient, Middleware, getUser vs getSession, admin client)
- Bloc 4: Performanță (Caching 4 nivele, React.cache, unstable_cache, revalidatePath, Streaming, Suspense, Parallel Routes, next/dynamic, next/image, next/font)
- Bloc 5: Producție (Security headers, 15 greșeli comune, TypeScript patterns, checklist, Quick Reference Card)

## Concepte Cheie

- `import 'server-only'` — build error dacă codul server ajunge în client bundle
- `React.cache()` — per-request deduplication (request memoization)
- `unstable_cache()` — persistent cross-request (Data Cache), cu revalidate + tags
- `redirect()` — aruncă NEXT_REDIRECT, trebuie **în afara** try/catch
- `getUser()` vs `getSession()` — getUser() validează cu server Auth (sigur); getSession() local-only (bypassabil)
- `useOptimistic` — UI instant fără await server
- `bind(null, id)` — trimite argumente extra la Server Actions
- Context Providers — izolat în Client Component separat, nu în root layout
- `Promise.all` + verificare separată fiecare `.error` (nu fail-fast)
- `next/dynamic` cu `ssr: false` — pentru componente browser-only (charts, maps)
- Date objects — pierd metodele la serializare server→client; transmite string ISO

## Appendix: Template CRUD Complet

Include cod complet gata de copiat:
- lib/supabase/server.ts + client.ts + admin.ts
- lib/data/invoices.ts cu getCachedInvoices (unstable_cache)
- lib/actions/invoices.ts cu createInvoice/deleteInvoice (Server Actions, Zod, revalidateTag)
- app/(dashboard)/invoices/page.tsx cu Suspense streaming
- components/InvoiceList.tsx cu useOptimistic
- middleware.ts cu cookie refresh + auth protection

[[project_erp_financiar]] [[project_clinica_medicala]] [[project_vibe_budget]] [[project_studioflow]] [[project_descriere_produse_app]]
