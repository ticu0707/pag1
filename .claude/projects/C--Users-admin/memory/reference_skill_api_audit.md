---
name: reference-skill-api-audit
description: "Skill /api-audit: audit static 21 reguli API Integration & Webhooks, 5 categorii cu detecție automată, BLOCKER/ATENȚIE/OK"
metadata: 
  node_type: memory
  type: reference
  originSessionId: a3fd517a-f93d-4269-830f-cf60e6caed19
---

Skill `/api-audit` salvat la `.claude/commands/api-audit.md`.

Rulează ca `/api-audit Desktop/proiect` sau fără argumente (întreabă directorul).

## 5 Categorii + 21 Reguli

**A — Securitate API Keys (5 reguli, ÎNTOTDEAUNA):**
- A1: Chei API hardcodate în cod (sk_live_, whsec_, sk-ant-, sk-proj-)
- A2: NEXT_PUBLIC_ pe variabile secrete
- A3: Env vars validate cu Zod la startup
- A4: `unknown` nu `any` pe răspunsuri API
- A5: Zod schema pe răspuns API extern

**B — Resilience fetch() (4 reguli, dacă `fetch(` detectat):**
- B1: AbortController/signal pe fetch extern
- B2: Retry exclusiv pe 5xx + 429 (nu 4xx)
- B3: Idempotency-Key pe POST retryable
- B4: Fără state in-memory în serverless (RateLimiter/CircuitBreaker local)

**C — Webhooks (6 reguli, dacă webhook handlers detectate):**
- C1: rawBody citit ÎNAINTE de HMAC
- C2: timingSafeEqual la comparare semnătură
- C3: Timestamp validation (max 5 min, replay prevention)
- C4: waitUntil() nu void fire-and-forget (Vercel)
- C5: Promise.allSettled în fan-out (nu Promise.all)
- C6: Idempotency DB (INSERT + 23505 catch, fără SELECT round-trip)

**D — Streaming SSE (3 reguli, dacă ReadableStream/SSE detectat):**
- D1: reader.releaseLock() în finally
- D2: Buffer acumulativ (nu split '\n' simplu)
- D3: EventSource fără custom headers (auth impossibil cu EventSource nativ)

**E — Logging & GDPR (3 reguli, dacă console.log server-side detectat):**
- E1: PII redactat din log-uri (telefoane/emailuri/CNP)
- E2: Webhook body complet absent din log-uri
- E3: Correlation ID propagat în operații async

## Notă SDK providers
Dacă `twilio.validateRequest(` sau `stripe.webhooks.constructEvent(` detectat → C1 și C2 automat OK.

## Verificări manuale (în output)
Rate limit headers proactive, circuit breaker TTL, BNR multiplier, ETag/conditional GET, dead letter queue, OpenAPI types generate, MSW în teste.

**Proiecte țintă:** Clinică Medicală (Twilio IVR), ERP Financiar (BNR + Stripe), Vibe Budget (Claude API), orice Next.js cu integrări externe.
