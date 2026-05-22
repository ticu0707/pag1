---
name: project-ghid-api-webhooks
description: "Ghid API Integration & Webhooks v3.0 — status complet, salvat Desktop/Vibe-Coding"
metadata: 
  node_type: memory
  type: project
  originSessionId: a3fd517a-f93d-4269-830f-cf60e6caed19
---

Ghid API Integration & Webhooks v3.0 COMPLET, salvat la Desktop/Vibe-Coding/ghid-api-webhooks-v3.md.

**Why:** ghid universal pentru integrări API în proiectele vibe-coding (Twilio IVR clinică, BNR cursuri valutare, Stripe, orice API terț). Construit pe 3 sesiuni de rafinare expert.

**How to apply:** la orice proiect cu API extern sau webhooks, trimite la secțiunea relevantă din ghid înainte de implementare.

## Conținut v3.0 — 26 secțiuni, 5 blocuri, 50 greșeli critice

**BLOC 1 (S1-S4):** HTTP fundamentals, REST + idempotency keys, Zod validation (discriminated union), HTTP Caching Headers & ETag/If-None-Match conditional requests

**BLOC 2 (S5-S8):** Auth (API Key/Basic/OAuth2/mTLS), HMAC + rawBody WHY + replay prevention, token cache Redis + single-flight, env Zod la startup

**BLOC 3 (S9-S14):** fetch() AbortController, retry backoff (no 4xx, rate limit headers proactive), circuit breaker Redis (TTL aliniat), caching BNR cu Intl DST fix, serverless gotchas (waitUntil), **Streaming APIs SSE + ReadableStream (NOU)**

**BLOC 4 (S15-S20):** Webhook fundamentals + idempotency fix (INSERT+23505, fără SELECT), Next.js handlers, semnătură per provider (Twilio SDK/GitHub/Stripe), dead letter + payload limits, **Webhook Fan-out cu Promise.allSettled (NOU)**, testare locală + **MSW (NOU)**

**BLOC 5 (S21-S26):** Twilio IVR complet, BNR 3-level fallback + ETag + Intl DST, rate limiting distribuit, logging + **correlation IDs + GDPR redaction (NOU)**, **OpenAPI type generation (NOU)**, 50 greșeli + checklist

## Fix-uri față de v2.0

- DST Romania: `Intl.DateTimeFormat Europe/Bucharest` în loc de `month >= 2 && <= 9`
- Circuit breaker: failuresKey TTL aliniat cu `config.resetMs` (nu hardcodat 300s)
- Webhook idempotency: `INSERT + 23505 catch` (eliminat round-trip SELECT inutil)
- BNR: ETag/If-None-Match integrat în getBnrRatesSafe
- Rate limit headers: citite proactiv (X-RateLimit-Remaining), nu doar reactiv (Retry-After)
- Logging: PII redactat automat + correlation ID propagat

## Secțiuni noi față de v2.0

- S4: HTTP Caching Headers & Conditional Requests
- S14: Streaming APIs (SSE + ReadableStream + Claude API example)
- S19: Webhook Fan-out & Event Router
- S20: MSW pentru teste fără API real
- S24: Correlation IDs + GDPR în logging
- S25: OpenAPI Type Generation (openapi-typescript + openapi-fetch)
