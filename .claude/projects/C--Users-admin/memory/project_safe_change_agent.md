---
name: Safe Change Agent
description: PRD clarificat pentru agent CLI de refactoring TypeScript sigur — urmează implementarea
type: project
originSessionId: 4afaf7f1-0a31-4bfe-8652-ddfccc09f6e6
---
Agent CLI pentru refactoring TypeScript local sigur, construit în etape P0 → V1 → V2.

**Why:** Dezvoltatorul solo face refactoring manual, îl strică uneori, dă rollback manual — proces stresant. Agentul elimină frica de commit după refactoring.

**How to apply:** Implementarea începe cu Demo-ul end-to-end (walking skeleton), nu cu infrastructura. Demo 1 = patch pur safe. Demo 2 = refuz corect cu efecte secundare.

## Status
PRD clarificat prin 5 întrebări. Implementare neîncepută.

## Utilizator țintă
Dezvoltator solo / freelancer, TypeScript, rulează local din terminal.

## Arhitectură
- CLI tool: `safe-change init/analyze/plan/apply/verify/report/rollback`
- Artefacte în `.safe-change/` (config, plans, patches, rollback, reports)
- 8 skill-uri P0, apoi V1, V2

## Skill-uri P0 (ordinea de build: demo-first)
1. Demo 1 end-to-end (patch pur safe) — PRIMUL
2. Demo 2 end-to-end (refuz corect) — AL DOILEA
3. Sandbox & Permissions
4. Baseline Health Gate
5. Git Patch Lifecycle
6. AST Range Detection
7. Effect Detector
8. Risk Engine + Hard Blockers

## 5 tipuri patch permise V1
1. remove unused imports
2. rename local variable
3. extract pure function
4. remove duplicated pure helper
5. split long pure function

## Metrici P0
- False Safe Rate = 0
- Hard Blocker Recall = 100%
- Rollback Success Rate = 100%
- Verification Accuracy ≥ 95%
- Patch Acceptance Rate ≥ 80% pe cazurile safe

## Referință
Specificație completă: `C:\Users\admin\Desktop\skill agent refactoring.txt`
