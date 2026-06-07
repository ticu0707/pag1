---
name: project_team_builder_kb
description: Baza de cunoaștere pentru meta-skill /team-builder — v4.0 COMPLET cu toate lacunele rezolvate
metadata: 
  node_type: memory
  type: project
  originSessionId: cd2cfd53-aa2a-41de-aad6-9b4f5d9354e3
---

Baza de cunoaștere pentru meta-skill `/team-builder` și `/skill-creator`.

**Why:** Documentul servește ca fundament pentru generarea meta-skill-ului de creare echipe de agenți AI — conține toate regulile, pattern-urile, template-urile și spec-urile necesare.

**Fișier curent:** `C:\Users\admin\Desktop\Agenti AI\baza-cunostinte-team-builder-v4.md`

**How to apply:** La reluarea lucrului pe /team-builder, citește v4 direct. Versiunile anterioare (v1, v2, v3) există pe același path cu numărul corespunzător — v4 le supersedează pe toate.

**v4.0 — 3253 linii, 122KB, 24 secțiuni + Executive Summary cu 9 concluzii**

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
