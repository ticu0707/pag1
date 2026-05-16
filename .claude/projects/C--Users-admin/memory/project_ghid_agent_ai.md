---
name: project_ghid_agent_ai
description: "Ghid complet creare agent AI de la zero (beginner) — v4.0 FINALIZAT, salvat pe Desktop/Agenti AI/"
metadata: 
  node_type: memory
  type: project
  originSessionId: a763b17b-df42-4f24-aed3-13c28ef203d0
---

Ghid complet pentru crearea primului agent AI de la zero, nivel beginner-intermediate.

**Why:** Scop educațional — utilizatorul urmează un curs de vibe-coding și vrea să creeze primul agent AI cu ghidare pas-cu-pas, nu doar teorie.

**Fișier ghid:** `C:\Users\admin\Desktop\Agenti AI\ghid-agent-ai-v4.md`

**Alegeri tehnice:**
- Limbaj: TypeScript (ESM, Node.js 20+)
- SDK: Anthropic SDK direct (`@anthropic-ai/sdk`)
- Exemplu concret: Task Management Agent (CRUD pe tasks.json)
- Format: ghid conversațional complet cu cod gata de copiat

**Structura ghidului v4.0:**
- Learning Map — harta timpului (45 min total)
- Parte 0: Setup — API key, .env, npm install, package.json, tsconfig.json
- Concepte Esențiale — tokeni, conversație, agent vs chatbot, bucla agentică
- src/taskStore.ts — stratul de date (readTasks, writeTasks, generateId, clearTasks)
- CHECKPOINT 1 — verificare compilare și structură fișiere
- src/tools.ts — toolDefinitions (4 tools), funcții (add/list/complete/delete), toolExecutors router
- src/agent.ts — CachedSystemBlock, callClaudeWithRetry (exponential backoff + jitter), safeTrimHistory, runAgent (bucla agentică)
- src/index.ts — validateEnv, SessionStats, calculateCost, printStats, CLI interactiv
- CHECKPOINT 2 — rulare npm start, test rapid
- src/test.ts — 6 teste state-based (verifică tasks.json, nu textul lui Claude)
- Extindere — template 3 pași pentru adăugare tool nou (exemplu: search_tasks)
- Troubleshooting — Top 5 erori + soluții
- Next Steps — Săptămâna 1-3 + dincolo (MCP, multi-agent, Computer Use)

**Concepte cheie acoperite:**
- Agentic loop (stop_reason: end_turn vs tool_use)
- Prompt Caching cu `cache_control: { type: "ephemeral" }` (~90% reducere costuri)
- MAX_ITERATIONS = 15 (prevenire bucle infinite)
- safeTrimHistory — tăiere sigură, fără a rupe perechi tool_use/tool_result
- Exponential backoff cu jitter pentru retry la RateLimitError
- Token tracking + cost estimation per sesiune
- State-based testing (readTasks() nu textul Claude)
- ENOENT check pentru diferențiere "fișier lipsă" vs "JSON corupt"
- crypto.randomUUID() pentru ID-uri unice garantate
- .env + dotenv — cheia API niciodată în cod

**Status:** COMPLET — v4.0 finalizat și salvat. Ghidul a trecut prin 4 iterații de optimizare (v1.0→v4.0) bazate pe feedback expert simulat + real.

**Ghid Tools suplimentar:** `C:\Users\admin\Desktop\Agenti AI\ghid-tools-agent-ai-v3.md`
- Ghid dedicat creării de Tools pentru agenți AI, nivel beginner → production-ready
- Conține: model mental complet + tool_choice (1.6), 5 componente anatomie, 3 exemple practice, buclă agentică production-ready, prompt caching cu prefix caching explanation, comparație framework-uri (+ LangGraph), securitate (path.sep + ALLOWED_EXTENSIONS + anti-injection), template reutilizabil, 9 greșeli comune, checklist extins, entry point (main)
- 18 rafinări față de v2: 6 bug fixes + 12 îmbunătățiri expert
- v2 la `ghid-tools-agent-ai-v2.md` (depășită); v1 la `ghid-skills-agent-ai.md` (depășită)

**How to apply:** La reluarea lucrului pe acest ghid, deschide direct `C:\Users\admin\Desktop\Agenti AI\ghid-agent-ai-v4.md`. Utilizatorul poate porni implementarea creând folderul `task-agent/` și urmând Partea 0.
