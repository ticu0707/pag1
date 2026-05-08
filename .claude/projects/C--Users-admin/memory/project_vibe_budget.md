---
name: Vibe Budget
description: Aplicatie de buget personal — deployed pe Vercel, feature-uri principale implementate
type: project
---

Proiect la C:\Users\admin\vibe-budget-starter.
GitHub: https://github.com/ticu0707/vibe-budget-starter (cont ticu0707)
**Live pe Vercel:** https://vibe-budget-starter-one.vercel.app

Stack: Next.js 16 + React 19 + TypeScript + Tailwind CSS 4 + Drizzle ORM + Supabase (ticu0707@gmail.com, ref: ovarlscdxahqskeehjtb) + Claude AI (Sonnet)

**Why:** Curs vibe-coding — aplicatie de gestiune financiara personala.

**Feature-uri implementate (toate pe main):**
- ✅ Auth (Register / Login cu JWT + Supabase)
- ✅ Dashboard cu grafice (pie + bar charts, Recharts)
- ✅ CRUD tranzactii cu categorizare inline
- ✅ Upload CSV/Excel cu auto-categorization (reguli romanesti built-in)
- ✅ Auto-categorize button
- ✅ Reports page cu pivot table lunar (venituri/cheltuieli/economii/rata ec.)
- ✅ AI Financial Coach (Claude API) — momentan blocat: credit Anthropic "too low" desi $5 platiti
- ✅ Deploy Vercel cu toate env vars

**Variabile de mediu Vercel (toate setate):**
- DATABASE_URL, NEXT_PUBLIC_SUPABASE_URL, NEXT_PUBLIC_SUPABASE_ANON_KEY, JWT_SECRET, ANTHROPIC_API_KEY

**Urmeaza / Probleme nerezolvate:**
- AI Coach de testat pe URL-ul live (posibil creditele Anthropic au propagat)
- Testare completa in productie (login, dashboard, upload, rapoarte)
- Functionalitati noi TBD

**How to apply:** Server local: cd vibe-budget-starter && npm run dev → localhost:3000. Deploy automat pe Vercel la fiecare push pe main.
