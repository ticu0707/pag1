---
name: project-ghid-claude-api-ai
description: "Ghid Claude API & AI Integration v4.0 — status complet, salvat Desktop/Vibe-Coding"
metadata: 
  node_type: memory
  type: project
  originSessionId: a3fd517a-f93d-4269-830f-cf60e6caed19
---

Ghid Claude API & AI Integration v4.0 COMPLET, salvat la Desktop/Vibe-Coding/ghid-claude-api-ai-integration-v4.md.

**Why:** ghid universal pentru integrări Claude AI în proiectele vibe-coding (Vibe Budget AI Coach, Clinică IVR, ERP Financiar, Safe Change Agent). Construit pe 3 sesiuni de rafinare expert cu analiză ultra-critică.

**How to apply:** la orice proiect cu Claude API, trimite la secțiunea relevantă din ghid înainte de implementare.

## Conținut v4.0 — 32 secțiuni, 5 blocuri, 50 greșeli critice

**BLOC 1 (S0-S5):** SDK Setup + singleton Vercel, Model selection matrix (Haiku/Sonnet/Opus/Thinking), Structured output (tool_use + schema quality + generateObject + prefill), stop_reason handling, Streaming (text + tool_use cu input_json_delta), Context management + smart truncation sandwich

**BLOC 2 (S6-S12):** Prompt caching + hit rate tracking, Cost tracking multi-dimensional (user + feature + org), Model versioning canary, Rate limiting Upstash, Circuit breaker Redis fixed half-open, Error taxonomy complet + retry exponential backoff cu full jitter, Semantic cache (skip Claude 30-40% din calls)

**BLOC 3 (S13-S19):** Tool use agent loop cu parallel tools, Context compaction în agent runs lungi, RAG pgvector + hybrid search, Files API + long document chunking Map-Reduce, Extended Thinking budget, Batches API + partial failure + webhook, Prompt design patterns (XML structure + few-shot placement + tool descriptions + output format)

**BLOC 4 (S20-S24):** Testing AI (mocks + MockResponses builders + snapshot), Evals 4 niveluri (unit + model-graded + regression + adversarial), A/B testing prompts cu alocare deterministă, Observabilitate AgentTracer + LangFuse + alerting anomalii, IVR Twilio Pattern 1 (Haiku direct) + Pattern 2 (async Redis)

**BLOC 5 (S25-S31):** Prompt injection defense arhitecturală (XML + tool_use + Zod + audit), GDPR general (PII redaction + minimizare), GDPR medical-grade (Art.9 + DPA Anthropic + data residency + anonymizare transcripturi), MCP server, Graceful degradation 4 niveluri (full→cached→simple→disabled), 50 greșeli critice, Pre-deploy checklist complet

## Adăugiri față de v3.0

- S11 (NOU): Error taxonomy complet (400/401/403/404/422/429/500/529 + APIConnectionError + APITimeoutError) + retry cu full jitter
- S12 (NOU): Semantic cache cu cosine similarity — skip Claude complet pentru queries similare
- S19 (NOU): Prompt design patterns — XML system prompt, tool schema descriptions, few-shot placement, output format control
- S22 (NOU): A/B testing prompts în producție cu alocare deterministă + metrics tracking
- S29 (NOU): Graceful degradation 4 niveluri cu static fallbacks per feature
- S0 îmbunătățit: singleton pattern explicat, maxRetries: 0
- S2 îmbunătățit: tool schema descriptions quality (impact 15-20% pe acuratețe)
- S5 îmbunătățit: smart truncation "sandwich" pentru chat sessions lungi
- S7 îmbunătățit: multi-tenant cost attribution (per-org pentru billing)
- S16 îmbunătățit: Map-Reduce chunking pentru documente > context window
