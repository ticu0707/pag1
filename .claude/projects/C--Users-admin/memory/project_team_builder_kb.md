---
name: project_team_builder_kb
description: Meta-skill /team-builder — v6.0 COMPLET (12 gap-uri rezolvate: TypeScript API, Secrets, Structured Output, Pattern E, Chaos Testing, CI/CD, effort, PLANNER, MCP, bypassPermissions, When-to-Redesign, Shadow Testing)
metadata: 
  node_type: memory
  type: project
  originSessionId: cd2cfd53-aa2a-41de-aad6-9b4f5d9354e3
---

Meta-skill `/team-builder` — skill complet pentru crearea de echipe de agenți AI care funcționează în producție.

**Why:** Skill-ul acoperă complet problematica creării echipelor de agenți AI în producție — de la calificare și design la hardening, evals, secrets management, versionare și diagnosticare.

**Fișier skill:** `C:\Users\admin\.claude\skills\team-builder\` (8 fișiere: SKILL.md + 7 references)

**How to apply:** La reluarea lucrului pe /team-builder, citește direct fișierele din skills folder. Baza de cunoaștere v4 de pe Desktop este supercedată — skill-ul live este autoritatea.

**v6.0 — toate cele 12 gap-uri din analiza finală rezolvate:**

**Dimensiuni fișiere v6.0:** SKILL.md 331L · skill-output.md 523L · production-hardening.md 442L · patterns.md 291L · evals.md 239L · tool-matrix.md 219L · agent-roles.md 217L · cost-reference.md 170L

**Gap-uri rezolvate în v6.0:**
1. B1 — Structured Output Contract: production-hardening.md + SKILL.md checklist
2. B2 — TypeScript Managed Agents API: skill-output.md (exemplu complet cu streaming + NDJSON)
3. M1 — MCP server tools guidance: tool-matrix.md (Claude Code + Managed API + Pattern C)
4. M2 — `task_budget` în workflow: cost-reference.md (tabel team size → budget) + SKILL.md Step 6
5. M3 — Agent versioning cu shadow testing: skill-output.md Day-2 (proces 5 pași)
6. M4 — Secrets management: production-hardening.md (secțiune dedicată, MCP creds, startup validation)
7. M5 — Pattern E (team-of-teams): patterns.md (CLI + Managed API router, agent count planning)
8. M6 — "When to redesign" diagnostic: patterns.md + skill-output.md (tabel cu 8 semnale → acțiuni)
9. m1 — `effort` în toate template-urile: agent-roles.md (low/medium/high/xhigh per rol)
10. m2 — `initialPrompt` în template RESEARCHER: agent-roles.md (cu ghidaj caching >1024 tokens)
11. m3 — Pattern C YAML orchestrator: patterns.md (exemplu complet fanout-coordinator)
12. m4 — Color conventions: agent-roles.md + tool-matrix.md (tabel semantic blue/green/orange/red/purple)

**Bonus adăugat:**
- Rol 5 PLANNER/ANALYZER: agent-roles.md (purple, plan permissionMode, produce plan nu cod)
- bypassPermissions risk documentation: tool-matrix.md
- disallowedTools vs tools guidance: tool-matrix.md
- Chaos testing matrix + script Python: evals.md
- CI/CD integration GitHub Actions: evals.md

**Structura documentului:**
- S0: Când NU construiești o echipă (criterii + cost overhead)
- S1: Câmpul `description` — routing primer
- S2: Contractul în 4 Părți + Brief Inheritance Attack
- S3: 4 Roluri canonice (Orchestrator/Researcher/Worker/Validator) cu YAML complet
- S4: Matricea Tool Restriction
- S5: YAML Frontmatter spec + thinking clarificat + YAML edge cases + naming conventions
- S6: 4 Pattern-uri orchestrare + State Machine + Concurrency Hazards
- S7: 4 Pattern-uri timing + mecanica exactă `background: true`
- S8: Decision Tree cu routing CLI vs Managed Agents API
- S9: Fault Tolerance (maxTurns, circuit breaker, idempotent, checkpoint, graceful degradation, rate limiting, rollback, **format erori runtime**)
- S10: Cost Reality (prețuri, range-uri, prompt caching, Batch API)
- S11: Observability (logging, trace ID, clasificare erori, debug workflow, cost alerting)
- S12: Securitate — Prompt Injection (4 tiere mitigare, Brief Inheritance Attack)
- S13: Non-Determinism (5 surse + 5 strategii)
- S14: Managed Agents API vs. Claude Code (tabel comparativ)
- S15: 3 exemple complete de echipe cu cod real
- S16: 18 Anti-patterns (v3 avea 15; adăugate: #16 background wait, #17 migrare model, #18 skill fără exemplu)
- S17: Production Checklist — 35 itemi binari (v3 avea 26; adăugate: naming, background wait, Haiku limit, Day-2)
- S18: Outputul Meta-Skill + **exemplu complet research-team.md convenience skill**
- S19: Workflow `/team-builder` spec executabilă — 9 pași + **Step 2.5 routing CLI/API**
- S20: Anatomia SKILL.md + clarificare invocare agenți din skills
- **S20.5 NOU:** Skill Discovery — unde trăiesc, când se încarcă, cum se descoperă, flux complet
- S21: Taxonomia Skill-urilor — 5 tipuri cu template-uri complete
- S22: Context Window Budget Management (formulă + 4 strategii)
- S23: Testing Multi-Agent (5 tipuri de teste cu cod Python)
- **S24 NOU:** Day-2 Operations (migrare model, brief evolution, A/B testing, regression cadence, arhivare)

**14 lacune rezolvate față de v3:**
1. Concluzia 9 în Executive Summary (Day-2 plan obligatoriu)
2. Avertisment Haiku context limit în S3 Researcher (>150K tokeni = output trunchiat silențios)
3. S5: `thinking` clarificat (Python API only, nu YAML); YAML edge cases (6 greșeli); naming conventions
4. S7: mecanica exactă `background: true` + instrucțiunea obligatorie de așteptare
5. S8: routing CLI vs Managed Agents API în decision tree
6. S9.8 nou: format erori runtime (5 tipuri: maxTurns, context overflow, 429, schema invalid, scope creep)
7. S16: 3 anti-pattern-uri noi (#16–#18) → total 18
8. S17: 7 itemi noi în checklist (naming, background wait, Haiku limit, convenience skill, Day-2)
9. S18: exemplu complet `.claude/skills/research-team.md` (fișierul în sine, nu descrierea)
10. S19 Step 2.5 nou: routing Claude Code vs Managed Agents API
11. S20: clarificare mecanică invocare agenți din skills (Claude face apelul, nu skill-ul direct)
12. S20.5 nou: Skill Discovery & Scopes
13. S24 nou: Day-2 Operations (5 subsecțiuni)
14. Eliminat bug structural: duplicata goală "SECȚIUNEA 16 (REVĂZUTĂ)" de la finalul v3
