---
name: Vibe Budget
description: Aplicatie de buget personal — deployed pe Vercel, finalizata si gata de portofoliu
type: project
originSessionId: 59781e7e-333a-41d4-a79f-819d5b53fa73
---
Proiect la C:\Users\admin\vibe-budget-starter.
GitHub: https://github.com/ticu0707/vibe-budget-starter (cont ticu0707)
**Live pe Vercel:** https://vibe-budget-starter-one.vercel.app

Stack: Next.js 16 + React 19 + TypeScript + Tailwind CSS 4 + Drizzle ORM + Supabase (ticu0707@gmail.com, ref: ovarlscdxahqskeehjtb) + Claude AI (Haiku)

**Why:** Curs vibe-coding — aplicatie de gestiune financiara personala. Gata de portofoliu/prezentat.

**Feature-uri implementate (toate pe main, toate pushate):**
- ✅ Auth (Register / Login cu JWT + Supabase)
- ✅ Dashboard cu grafice (pie + bar charts, Recharts)
- ✅ CRUD tranzactii cu categorizare inline
- ✅ Upload CSV/Excel cu auto-categorization (reguli romanesti built-in)
- ✅ Auto-categorize button
- ✅ Reports page cu pivot table lunar (venituri/cheltuieli/economii/rata ec.)
- ✅ AI Financial Coach + AI Chat (Claude Haiku API)
- ✅ Trial system (7 zile, bypass in dev cu NODE_ENV)
- ✅ Unlock cod single-use per cont (`vibe-acces-2026` in env UNLOCK_PASSWORD)
- ✅ proxy.ts (Next.js 16 convention, inlocuieste middleware.ts)
- ✅ Date filters cu label "De la / Pana la" in pagina Tranzactii
- ✅ Upload UX: banner warning cand nu exista banci adaugate
- ✅ Deploy Vercel cu toate env vars

**Variabile de mediu Vercel (toate setate):**
- DATABASE_URL, NEXT_PUBLIC_SUPABASE_URL, NEXT_PUBLIC_SUPABASE_ANON_KEY, JWT_SECRET, ANTHROPIC_API_KEY, UNLOCK_PASSWORD

**Comportament intentionat (nu bug):**
- User deja logat care da click pe "Incearca gratuit 7 zile" → redirectat la /dashboard (proxy.ts)
- Unlock cod returneaza 409 daca user.user_metadata.unlocked === true deja

**How to apply:** Server local: cd vibe-budget-starter && npm run dev → localhost:3000. Deploy automat pe Vercel la fiecare push pe main.
