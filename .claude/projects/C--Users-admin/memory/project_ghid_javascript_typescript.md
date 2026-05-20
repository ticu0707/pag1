---
name: project_ghid_javascript_typescript
description: "Ghid JS/TS pentru Vibe-Coding cu Claude — v1.0 FINALIZAT, salvat pe Desktop/Vibe-Coding/"
metadata:
  node_type: memory
  type: project
  originSessionId: current
---

Ghid practic JavaScript & TypeScript pentru vibe-coding cu Claude, nivel beginner → expert.

**Why:** Skill 2 identificat din analiza proiectelor utilizatorului — înțelegerea JS/TS generat de Claude pentru a putea valida și debuga codul înainte de aplicare.

**Fișier final:** `C:\Users\admin\Desktop\Vibe-Coding\ghid-javascript-typescript-v1.md`
**Draft păstrat:** `C:\Users\admin\Desktop\Vibe-Coding\ghid-javascript-typescript-v1-DRAFT.md`

**Structura ghidului v1.0 (16 secțiuni, Parte 0–15, 5 Blocs):**
- TL;DR — 3 lucruri care schimbă totul (await, types, array methods)
- BLOC 1: JS vs TS (bug concret) + Citești Cod Necunoscut (3 pași) + TypeScript Types (citind, nu scriind)
- BLOC 2: Async/Await + Error Handling + Array Methods + Destructuring + Module System (ESM/CJS)
- BLOC 3: Pattern Complet fetch server + mutations client (CRUD complet) + 8 Greșeli Comune + useEffect + Closures
- BLOC 4: Securitate (XSS/eval/path traversal/userId auth) + Checklist Pre-Apply + console.log debugging + Când nu ai încredere în Claude
- BLOC 5: Flowchart diagnostic + Transcript real debugging async + Quick Reference Card v1.0

**Teme distinctive față de alte ghiduri:**
- Checklist pre-apply în 5 puncte (await, types, error, null, deps)
- Pattern complet Server Component + Client Component mutations (CRUD real)
- Supabase userId din `auth.getUser()` (safe) vs URL params (bypass auth)
- Cleanup function cu flag pattern + AbortController
- `console.log` strategic placement pentru async debugging
- Spread operator parens GOTCHA — `({ ...prev })` obligatoriu
- `.single()` pe SELECT vs INSERT — comportament diferit Supabase v2
- Path traversal fix cu `path.sep` — bypass prevention

**Rafinări aplicate (3 runde de review expert):**
- Round 1: client mutations pattern, utility types, runtime limit TypeScript, cleanup function, userId security, Module System tag
- Round 2: structural fix Parte 7, .catch() în cleanup, spread GOTCHA, console.log debugging section, TL;DR, readFileSync → Supabase example, reduce acc explicat, Greșeala 7 reframed, Edge Runtime contextualizat
- Round 3: calculeazaTVA factual fix (+ operator vs *), spread SyntaxError vs silent, handleAdd loading state, path.sep security, async mental model, || vs ?? cu string gol, loop infinit clarificat, .single() INSERT vs SELECT, sleep/retryDelay comentate, process.env tip

**Status:** COMPLET — v1.0 finalizat și salvat.

**How to apply:** La reluarea lucrului pe JS/TS sau coaching al utilizatorului, ghidul e la `C:\Users\admin\Desktop\Vibe-Coding\ghid-javascript-typescript-v1.md`. Bazat pe proiectele: Vibe Budget, StudioFlow, ERP Financiar, Clinică Medicală, Agenți AI, CashPulse, FollowUp Board.
