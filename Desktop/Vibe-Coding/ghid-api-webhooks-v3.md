# Ghid API Integration & Webhooks v3.0
## Pentru Vibe-Coding — Next.js 14+ · TypeScript · Node.js ESM

**Mai 2026 · 26 secțiuni · 5 Blocuri · 50 greșeli critice**

---

## BLOC 1 — Fundamente HTTP & REST

---

### S1 — Anatomia unui Request HTTP

Orice integrare API e un request HTTP. Nu există magie — doar text structurat pe TCP.

```
POST /api/v1/calls HTTP/1.1
Host: api.twilio.com
Authorization: Basic dXNlcjpwYXNz...
Content-Type: application/x-www-form-urlencoded
Content-Length: 45

To=%2B40721000000&From=%2B40312000000
```

**Componentele esențiale:**

| Componentă | Exemplu | Rol |
|---|---|---|
| Method | GET, POST, PUT, PATCH, DELETE | Intenția operației |
| URL | `https://api.twilio.com/v1/...` | Resursa țintă |
| Headers | `Authorization`, `Content-Type` | Metadata, auth, format |
| Body | JSON, form-urlencoded, XML | Date trimise (POST/PUT/PATCH) |

**Status codes esențiale:**

```
200 OK           — succes, body cu date
201 Created      — resursă creată (POST)
204 No Content   — succes, fără body (DELETE)
304 Not Modified — resursă neschimbată de la ultima cerere (vezi S4)
400 Bad Request  — datele tale sunt greșite
401 Unauthorized — lipsă auth sau token expirat
403 Forbidden    — autentificat dar fără permisiune
404 Not Found    — resursa nu există
409 Conflict     — duplicat, resursă există deja
422 Unprocessable— validare eșuată (Stripe, Twilio)
429 Too Many Req — rate limit depășit — trebuie retry cu backoff
500 Server Error — eroare API extern (nu e vina ta)
502/503/504      — API extern down sau timeout upstream
```

**Regula de aur:** `2xx` = succes. `4xx` = tu ai greșit (nu retry). `5xx` = ei au greșit (retry cu backoff).

---

### S2 — REST Patterns Esențiale & Idempotency Keys

**Structura URL:**
```
https://api.example.com/v2/resources/{id}/sub-resources?filter=value&page=2
         ─────────────  ── ─────────  ──  ────────────  ──────────────────
         base URL       ver colecție  id  sub-colecție  query params
```

**Pagination — 3 stiluri pe care le vei întâlni:**

```typescript
// 1. Offset-based (cel mai comun)
GET /invoices?limit=20&offset=40

// 2. Cursor-based (Stripe, Twitter — performant pe seturi mari)
GET /invoices?limit=20&starting_after=inv_xyz

// 3. Page-based
GET /invoices?page=3&per_page=20
```

**Pattern de fetch cu paginare completă:**

```typescript
async function fetchAllPages<T>(
  baseUrl: string,
  headers: HeadersInit,
  getNextCursor: (data: unknown) => string | null
): Promise<T[]> {
  const results: T[] = []
  let cursor: string | null = null

  do {
    const url = cursor ? `${baseUrl}&starting_after=${cursor}` : baseUrl
    const response = await fetch(url, { headers })
    if (!response.ok) throw new Error(`API error: ${response.status}`)
    const data = await response.json()
    results.push(...(data.data ?? []))
    cursor = getNextCursor(data)
  } while (cursor)

  return results
}
```

**Idempotency Keys — pentru POST-uri outbound (critical):**

Problema: faci un POST (inițiezi apel Twilio, creezi plată Stripe), serverul primește request-ul,
procesează, dar conexiunea cade înainte să primești răspunsul. Retry-ul creează un duplicat.

```typescript
import { randomUUID } from 'crypto'

// Stripe, Twilio, și multe alte API-uri suportă Idempotency-Key
async function createStripePaymentIntent(amount: number, idempotencyKey?: string): Promise<Stripe.PaymentIntent> {
  return stripe.paymentIntents.create(
    { amount, currency: 'ron' },
    { idempotencyKey: idempotencyKey ?? randomUUID() }
  )
}

// Pattern: generezi key-ul în DB ÎNAINTE de request și îl salvezi
// La retry, refolosești același key → API returnează același rezultat
async function createPaymentWithIdempotency(invoiceId: string, amount: number) {
  const { data: invoice } = await db
    .from('invoices')
    .select('payment_idempotency_key')
    .eq('id', invoiceId)
    .single()

  const key = invoice.payment_idempotency_key ?? randomUUID()

  if (!invoice.payment_idempotency_key) {
    await db.from('invoices').update({ payment_idempotency_key: key }).eq('id', invoiceId)
  }

  return createStripePaymentIntent(amount, key)
  // Dacă se retransmite cu același key, Stripe returnează același PaymentIntent
}
```

---

### S3 — TypeScript Types & Zod Validation

**Principiul:** validezi la boundary (intrare din exterior), niciodată în interiorul codului tău.

```typescript
import { z } from 'zod'

const BnrRateSchema = z.object({
  '#text': z.number(),
  '@_currency': z.string(),
  '@_multiplier': z.number().optional().default(1)
})

// CRITIC: fast-xml-parser returnează obiect (nu array) când XML are un singur <Rate>
// Fără acest transform, schema crapa dacă BNR trimite o singură monedă
const BnrXmlSchema = z.object({
  DataSet: z.object({
    Body: z.object({
      Cube: z.object({
        '@_date': z.string(),
        Rate: z.union([BnrRateSchema, z.array(BnrRateSchema)])
          .transform(r => Array.isArray(r) ? r : [r])
      })
    })
  })
})

type BnrRate = z.infer<typeof BnrRateSchema>
```

**Discriminated union pentru răspunsuri API cu success/error:**

```typescript
// Pattern pentru API-uri care returnează structuri diferite la succes vs eroare
const ApiResponseSchema = z.discriminatedUnion('success', [
  z.object({
    success: z.literal(true),
    data: z.object({ id: z.string(), status: z.string() })
  }),
  z.object({
    success: z.literal(false),
    error: z.object({ code: z.string(), message: z.string() })
  })
])

type ApiResponse = z.infer<typeof ApiResponseSchema>

function handleApiResponse(raw: unknown) {
  const response = ApiResponseSchema.parse(raw)
  if (!response.success) {
    // TypeScript știe că response.error există aici
    throw new Error(`API Error ${response.error.code}: ${response.error.message}`)
  }
  // TypeScript știe că response.data există aici
  return response.data
}
```

**`unknown` în loc de `any` pe date externe:**

```typescript
// Nu: async function processWebhook(body: any)
// Da:
async function processWebhook(body: unknown) {
  const event = WebhookEventSchema.parse(body)  // forțezi narrowing explicit
  // event e complet tipat de aici
}
```

---

### S4 — HTTP Caching Headers & Conditional Requests

**De ce contează:** fiecare fetch la BNR, GitHub API, sau orice API cu date periodice consumă
bandwidth și timp. HTTP caching headers permit serverului să răspundă cu 304 Not Modified
(fără body) când datele nu s-au schimbat — economisești bandwidth și timp de parsare.

**Cele 3 mecanisme:**

```
ETag: "abc123"          — identificator unic al versiunii resursei
Last-Modified: Thu, 22 May 2026 11:00:00 GMT  — data ultimei modificări
Cache-Control: max-age=3600  — cât timp să cache-uiești local (secunde)
```

**Cum funcționează conditional GET:**

```
Request 1 (fără cache):
  GET /nbrfxrates.xml
  ← 200 OK, body: <xml...>, ETag: "bnr-20260522", Last-Modified: Thu, 22 May 2026 11:00:00 GMT

Request 2 (cu ETag salvat):
  GET /nbrfxrates.xml
  If-None-Match: "bnr-20260522"
  ← 304 Not Modified (fără body — folosești datele din cache)

Request 3 (cu Last-Modified salvat):
  GET /nbrfxrates.xml
  If-Modified-Since: Thu, 22 May 2026 11:00:00 GMT
  ← 304 Not Modified (fără body)
```

**Implementare universală:**

```typescript
// lib/conditional-fetch.ts
interface ConditionalGetResult<T> {
  data: T | null       // null dacă 304
  notModified: boolean
  etag: string | null
  lastModified: string | null
}

export async function conditionalGet<T>(
  url: string,
  options: {
    cachedEtag?: string | null
    cachedLastModified?: string | null
    parseBody: (text: string) => T
    headers?: Record<string, string>
  }
): Promise<ConditionalGetResult<T>> {
  const requestHeaders: Record<string, string> = options.headers ?? {}

  if (options.cachedEtag) {
    requestHeaders['If-None-Match'] = options.cachedEtag
  } else if (options.cachedLastModified) {
    requestHeaders['If-Modified-Since'] = options.cachedLastModified
  }

  const response = await fetch(url, { headers: requestHeaders })

  if (response.status === 304) {
    return {
      data: null,
      notModified: true,
      etag: options.cachedEtag ?? null,
      lastModified: options.cachedLastModified ?? null
    }
  }

  if (!response.ok) throw new Error(`HTTP ${response.status}: ${url}`)

  const text = await response.text()
  return {
    data: options.parseBody(text),
    notModified: false,
    etag: response.headers.get('ETag'),
    lastModified: response.headers.get('Last-Modified')
  }
}
```

**Salvarea validatorilor în Redis alături de date:**

```typescript
interface CachedResource<T> {
  data: T
  etag: string | null
  lastModified: string | null
  cachedAt: string
}

async function getWithConditionalCache<T>(
  cacheKey: string,
  url: string,
  parseBody: (text: string) => T,
  ttlSeconds: number
): Promise<T> {
  const cached = await redis.get<CachedResource<T>>(cacheKey)

  const result = await conditionalGet<T>(url, {
    cachedEtag: cached?.etag ?? null,
    cachedLastModified: cached?.lastModified ?? null,
    parseBody
  })

  if (result.notModified && cached) {
    // Reîmprospătezi TTL-ul chiar dacă datele nu s-au schimbat
    await redis.expire(cacheKey, ttlSeconds)
    return cached.data
  }

  if (!result.data) throw new Error('No data and no cache')

  await redis.set(cacheKey, {
    data: result.data,
    etag: result.etag,
    lastModified: result.lastModified,
    cachedAt: new Date().toISOString()
  } satisfies CachedResource<T>, { ex: ttlSeconds })

  return result.data
}
```

**Cache-Control directives utile:**

```
Cache-Control: no-store       — nu cache-ui niciodată (webhooks, date sensibile)
Cache-Control: no-cache       — cache-ui dar verifică cu serverul la fiecare request
Cache-Control: max-age=3600   — cache-ui 1 oră local
Cache-Control: s-maxage=3600  — cache-ui 1 oră doar pe CDN/proxy (nu browser)
Cache-Control: stale-while-revalidate=300  — servești din cache și revalidezi în background
```

---

## BLOC 2 — Autentificare & Securitate

---

### S5 — Metode de Autentificare

**API Key în Header:**
```typescript
fetch(url, {
  headers: { 'X-API-Key': process.env.OPENAI_API_KEY! }
})

// Varianta Bearer token
fetch(url, {
  headers: { 'Authorization': `Bearer ${process.env.STRIPE_SECRET_KEY}` }
})
```

**HTTP Basic Auth (Twilio):**
```typescript
function twilioAuthHeader(): string {
  const credentials = `${process.env.TWILIO_ACCOUNT_SID}:${process.env.TWILIO_AUTH_TOKEN}`
  return `Basic ${Buffer.from(credentials).toString('base64')}`
}
```

**OAuth2 Client Credentials — detalii în S7 (token cache distribuit).**

**mTLS (mutual TLS) — pentru API-uri financiare high-security:**
```typescript
// Unele API-uri bancare sau fintech cer certificat client TLS
// Node.js suportă nativ prin https.Agent
import https from 'https'
import fs from 'fs'

const agent = new https.Agent({
  cert: fs.readFileSync(process.env.CLIENT_CERT_PATH!),
  key: fs.readFileSync(process.env.CLIENT_KEY_PATH!),
  ca: fs.readFileSync(process.env.CA_CERT_PATH!)  // CA-ul provider-ului
})

// fetch nu suportă direct https.Agent — folosești node-fetch sau axios pentru mTLS
import fetch from 'node-fetch'
const response = await fetch(url, { agent } as any)
```

---

### S6 — HMAC Signature Verification

**De ce e critic:** Fără verificare de semnătură, oricine poate POST la endpoint-ul tău și declanșa
acțiuni reale (programări medicale, plăți, modificări de date).

**WHY body trebuie citit ca Buffer ÎNAINTE de orice parsare:**

`Request.body` este un `ReadableStream` — se consumă o singură dată. Dacă apelezi
`request.json()` sau `request.text()` ÎNAINTE de a verifica semnătura, stream-ul e
epuizat și nu mai poți calcula HMAC-ul pe datele raw. HMAC trebuie calculat pe bytes-ul
exact primit pe wire, nu pe JSON re-serializat (care poate reordona cheile).

```
Stream consumed:       request.json() → {...}  → request.arrayBuffer() → ERROR: body used
Stream consumed corect: request.arrayBuffer() → Buffer → JSON.parse(buffer)
```

**Pattern universal — verificare corectă:**

```typescript
import crypto from 'crypto'

function verifyHmacSignature(
  payload: Buffer,
  receivedSig: string,
  secret: string,
  algorithm: 'sha256' | 'sha1' = 'sha256'
): boolean {
  const expected = crypto
    .createHmac(algorithm, secret)
    .update(payload)
    .digest('hex')

  const expectedBuf = Buffer.from(expected)
  const receivedBuf = Buffer.from(receivedSig.replace(/^sha\d+=/, ''))

  // timingSafeEqual previne timing attacks
  // Bufferele trebuie să fie egale ca lungime (hex HMAC are lungime fixă pentru același algoritm)
  if (expectedBuf.length !== receivedBuf.length) return false
  return crypto.timingSafeEqual(expectedBuf, receivedBuf)
}
```

**Prevenirea replay attacks — timestamp validation:**

```typescript
function verifyTimestamp(timestampHeader: string, toleranceSeconds = 300): boolean {
  const timestamp = parseInt(timestampHeader, 10)
  if (isNaN(timestamp)) return false
  return Math.abs(Date.now() / 1000 - timestamp) < toleranceSeconds
}

// Next.js Route Handler — pattern complet
export async function POST(request: Request) {
  // REGULA: citești body ca Buffer ÎNAINTE de orice — stream-ul e consumabil o singură dată
  const payload = Buffer.from(await request.arrayBuffer())

  const signature = request.headers.get('X-Signature-SHA256') ?? ''
  const timestamp = request.headers.get('X-Timestamp') ?? ''

  if (!verifyTimestamp(timestamp)) {
    return Response.json({ error: 'Webhook expired' }, { status: 400 })
  }

  if (!verifyHmacSignature(payload, signature, process.env.WEBHOOK_SECRET!)) {
    return Response.json({ error: 'Invalid signature' }, { status: 401 })
  }

  const body = JSON.parse(payload.toString('utf-8'))
  // procesezi...
}
```

---

### S7 — Token Cache Distribuit & Rotația Secretelor

**Problema token cache-ului naiv:**

```typescript
// GREȘIT în serverless — stare în memorie resetată la fiecare cold start
// La trafic real: N instanțe serverless = N token fetches simultane = race condition
let tokenCache: { token: string; expiresAt: number } | null = null  // NU
```

**Versiunea corectă — Redis distribuit:**

```typescript
// lib/token-cache.ts
import { Redis } from '@upstash/redis'
const redis = Redis.fromEnv()

export async function getAccessToken(config: {
  tokenUrl: string
  clientId: string
  clientSecret: string
  scope: string
  cacheKey: string
}): Promise<string> {
  // 1. Verifici cache-ul distribuit
  const cached = await redis.get<string>(`oauth:token:${config.cacheKey}`)
  if (cached) return cached

  // 2. Fetch token nou
  const response = await fetch(config.tokenUrl, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      grant_type: 'client_credentials',
      client_id: config.clientId,
      client_secret: config.clientSecret,
      scope: config.scope
    })
  })

  if (!response.ok) throw new Error('OAuth2 token fetch failed')
  const data = await response.json()

  // 3. Salvezi în Redis cu TTL (minus 60s buffer pentru siguranță)
  const ttl = data.expires_in - 60
  await redis.set(`oauth:token:${config.cacheKey}`, data.access_token, { ex: ttl })

  return data.access_token
}
```

**Single-flight pattern — previne thundering herd la cache miss simultan:**

```typescript
// Dacă 50 de request-uri simultane văd cache miss, faci 50 token fetches
// Single-flight: primul fetch rulează, celelalte așteaptă rezultatul lui
// Notă: Map-ul e in-memory deci deduplication e per-instanță — corect pentru serverless
// Instanțele nu partajează requests, deci nu există thundering herd cross-instance

const inflightRequests = new Map<string, Promise<string>>()

export async function getAccessTokenSingleFlight(
  cacheKey: string,
  fetchFn: () => Promise<string>
): Promise<string> {
  const cached = await redis.get<string>(`oauth:token:${cacheKey}`)
  if (cached) return cached

  if (inflightRequests.has(cacheKey)) {
    return inflightRequests.get(cacheKey)!
  }

  const fetchPromise = fetchFn().finally(() => inflightRequests.delete(cacheKey))
  inflightRequests.set(cacheKey, fetchPromise)
  return fetchPromise
}
```

**Rotarea secretelor fără downtime:**

```typescript
// Suportă 2 secrete simultan în perioada de tranziție
// Flux: 1) adaugi NEW în env, 2) provider-ul schimbă la NEW, 3) ștergi OLD

function verifyWithRotation(payload: Buffer, signature: string): boolean {
  const secrets = [
    process.env.WEBHOOK_SECRET_NEW,
    process.env.WEBHOOK_SECRET_OLD
  ].filter(Boolean) as string[]

  return secrets.some(secret => verifyHmacSignature(payload, signature, secret))
}
```

---

### S8 — Environment Variables & Validation la Startup

```bash
# .env.local — NICIODATĂ în git
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=+40312000000
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
UPSTASH_REDIS_URL=https://...
UPSTASH_REDIS_TOKEN=...
WEBHOOK_SECRET=generate_with_openssl_rand_hex_32
BNR_RATES_URL=https://www.bnr.ro/nbrfxrates.xml
NODE_ENV=development
```

**Validare Zod la startup — eșuezi devreme, nu la primul request real:**

```typescript
// lib/env.ts
import { z } from 'zod'

const envSchema = z.object({
  TWILIO_ACCOUNT_SID: z.string().startsWith('AC').min(34),
  TWILIO_AUTH_TOKEN: z.string().min(32),
  TWILIO_PHONE_NUMBER: z.string().startsWith('+'),
  STRIPE_SECRET_KEY: z.string().startsWith('sk_'),
  STRIPE_WEBHOOK_SECRET: z.string().startsWith('whsec_'),
  UPSTASH_REDIS_URL: z.string().url(),
  UPSTASH_REDIS_TOKEN: z.string().min(1),
  WEBHOOK_SECRET: z.string().min(32),
  NODE_ENV: z.enum(['development', 'test', 'production']).default('development')
})

export const env = envSchema.parse(process.env)
// Dacă lipsește o variabilă, aruncă la startup cu mesaj clar:
// ZodError: TWILIO_AUTH_TOKEN: String must contain at least 32 character(s)
```

---

## BLOC 3 — Patterns de Request

---

### S9 — fetch() Robust: Timeouts, Erori, AbortController

**fetch() implicit nu are timeout.** Un API extern care nu răspunde blochează funcția ta pentru totdeauna.

```typescript
// lib/api-client.ts
export class ApiError extends Error {
  constructor(
    public status: number,
    public body: unknown,
    message: string
  ) {
    super(message)
    this.name = 'ApiError'
  }

  get isClientError() { return this.status >= 400 && this.status < 500 }
  get isServerError() { return this.status >= 500 }
  get isRateLimit() { return this.status === 429 }
}

export async function apiFetch<T>(
  url: string,
  options: RequestInit & { timeoutMs?: number } = {}
): Promise<T> {
  const { timeoutMs = 10_000, ...fetchOptions } = options

  const controller = new AbortController()
  const timeoutId = setTimeout(() => controller.abort(), timeoutMs)

  try {
    const response = await fetch(url, {
      ...fetchOptions,
      signal: controller.signal
    })

    clearTimeout(timeoutId)

    if (!response.ok) {
      const body = await response.json().catch(() => null)
      throw new ApiError(response.status, body, `HTTP ${response.status} on ${url}`)
    }

    return response.json() as Promise<T>
  } catch (error) {
    clearTimeout(timeoutId)
    if (error instanceof ApiError) throw error
    if (error instanceof Error && error.name === 'AbortError') {
      throw new Error(`Timeout after ${timeoutMs}ms: ${url}`)
    }
    throw error
  }
}
```

---

### S10 — Retry Logic, Backoff & Rate Limit Headers

**Când NU faci retry:**

```typescript
// 4xx (client errors) — retry nu rezolvă nimic:
// 400 Bad Request, 401 Unauthorized, 403 Forbidden, 404 Not Found, 422 Unprocessable
// EXCEPȚIE: 429 (rate limit) — faci retry cu delay din Retry-After header

// POST non-idempotent fără Idempotency-Key — poți crea duplicate
// Soluție: adaugă Idempotency-Key ÎNAINTE de retry (vezi S2)
```

**Cititul proactiv al rate limit headers:**

```typescript
interface RateLimitInfo {
  remaining: number | null
  reset: Date | null
  limit: number | null
}

function parseRateLimitHeaders(response: Response): RateLimitInfo {
  // Diferite API-uri folosesc headere diferite:
  // GitHub: X-RateLimit-Remaining, X-RateLimit-Reset (Unix timestamp)
  // Stripe: Stripe-Ratelimit-Remaining, Stripe-Ratelimit-Reset
  // Twilio: nu expune rate limit headers în mod explicit
  const remaining =
    response.headers.get('X-RateLimit-Remaining') ??
    response.headers.get('RateLimit-Remaining') ??
    response.headers.get('Stripe-Ratelimit-Remaining')

  const resetHeader =
    response.headers.get('X-RateLimit-Reset') ??
    response.headers.get('RateLimit-Reset')

  const limit =
    response.headers.get('X-RateLimit-Limit') ??
    response.headers.get('RateLimit-Limit')

  return {
    remaining: remaining ? parseInt(remaining) : null,
    reset: resetHeader ? new Date(parseInt(resetHeader) * 1000) : null,
    limit: limit ? parseInt(limit) : null
  }
}

// Folosire: loghezi proactiv când ești aproape de limită
async function apiFetchWithRateLimitMonitoring<T>(url: string, options?: RequestInit): Promise<T> {
  const response = await fetch(url, options)
  const rateLimit = parseRateLimitHeaders(response)

  if (rateLimit.remaining !== null && rateLimit.remaining < 10) {
    console.warn(`Rate limit warning: ${rateLimit.remaining} requests remaining until ${rateLimit.reset?.toISOString()}`)
  }

  if (!response.ok) {
    const body = await response.json().catch(() => null)
    throw new ApiError(response.status, body, `HTTP ${response.status}`)
  }

  return response.json() as Promise<T>
}
```

**Exponential backoff cu jitter:**

```typescript
export async function withRetry<T>(
  fn: () => Promise<T>,
  options: {
    retries?: number
    baseDelayMs?: number
    maxDelayMs?: number
    isRetryable?: (error: unknown) => boolean
  } = {}
): Promise<T> {
  const {
    retries = 3,
    baseDelayMs = 500,  // 500ms base — mai realist decât 1000ms
    maxDelayMs = 30_000,
    // Default: retry DOAR pe 5xx și 429, NU pe 4xx
    isRetryable = (e) => e instanceof ApiError && (e.isServerError || e.isRateLimit)
  } = options

  let lastError: unknown

  for (let attempt = 0; attempt <= retries; attempt++) {
    try {
      return await fn()
    } catch (error) {
      lastError = error
      if (attempt === retries || !isRetryable(error)) throw error

      // Respectă Retry-After header pe 429
      if (error instanceof ApiError && error.isRateLimit) {
        const retryAfterBody = (error.body as Record<string, unknown>)?.['retry_after']
        if (typeof retryAfterBody === 'number') {
          await sleep(retryAfterBody * 1000)
          continue
        }
      }

      // Exponential backoff + jitter (previne thundering herd)
      const exponential = baseDelayMs * Math.pow(2, attempt)
      const jitter = Math.random() * 500
      await sleep(Math.min(exponential + jitter, maxDelayMs))
    }
  }

  throw lastError
}

const sleep = (ms: number) => new Promise(resolve => setTimeout(resolve, ms))
```

---

### S11 — Circuit Breaker Pattern

**Problema:** fără circuit breaker, dacă BNR e down 2 ore, fiecare request la aplicația ta face
un fetch + timeout de 10s + 3 retry-uri = 40s blocat per request. Serverul tău devine inutilizabil.

**Circuit breaker — 3 stări:**
```
CLOSED → funcționare normală, request-urile trec
  ↓ (N eșecuri consecutive)
OPEN → toate request-urile sunt blocate instant (fără să mai aștepte)
  ↓ (după resetTimeMs)
HALF-OPEN → permite 1 request de test; dacă reușește → CLOSED, dacă nu → OPEN
```

**Implementare cu Redis (distribuit — funcționează în serverless):**

```typescript
// lib/circuit-breaker.ts
import { Redis } from '@upstash/redis'

interface BreakerState {
  failures: number
  openedAt: number
}

export class CircuitBreaker {
  constructor(
    private redis: Redis,
    private name: string,
    private config = { threshold: 5, resetMs: 60_000 }
  ) {}

  async execute<T>(fn: () => Promise<T>): Promise<T> {
    const stateKey = `circuit:${this.name}:state`
    const failuresKey = `circuit:${this.name}:failures`
    // TTL aliniat cu config.resetMs — nu hardcodat
    const failuresTtlSeconds = Math.ceil(this.config.resetMs / 1000)

    const state = await this.redis.get<BreakerState>(stateKey)

    if (state) {
      const isExpired = Date.now() - state.openedAt > this.config.resetMs
      if (!isExpired) {
        throw new Error(`Circuit OPEN: ${this.name} — serviciu temporar indisponibil`)
      }
      // Half-open: ștergem state-ul, permitem 1 request de test
      await this.redis.del(stateKey)
    }

    try {
      const result = await fn()
      await this.redis.del(failuresKey)
      return result
    } catch (error) {
      const failures = await this.redis.incr(failuresKey)
      // TTL aliniat cu config, nu hardcodat la 300
      await this.redis.expire(failuresKey, failuresTtlSeconds)

      if (failures >= this.config.threshold) {
        await this.redis.set(stateKey, { failures, openedAt: Date.now() }, {
          ex: failuresTtlSeconds * 2
        })
      }
      throw error
    }
  }
}

// Folosire:
const bnrBreaker = new CircuitBreaker(redis, 'bnr-api', {
  threshold: 3,     // 3 eșecuri consecutive → OPEN
  resetMs: 120_000  // 2 minute până la HALF-OPEN
})

export async function getBnrRatesWithBreaker() {
  return bnrBreaker.execute(() => fetchBnrRates())
}
```

---

### S12 — Caching Răspunsuri API

**Next.js Server Components — request deduplication automat:**

```typescript
async function getBnrRatesNextjs() {
  const response = await fetch(env.BNR_RATES_URL, {
    next: { revalidate: 3600 }  // ISR: revalidare la fiecare oră
  })
  if (!response.ok) throw new Error('BNR fetch failed')
  return response.text()
}
```

**Upstash Redis — pentru Server Actions și Route Handlers:**

```typescript
async function getCachedBnrRates(): Promise<BnrResponse> {
  const CACHE_KEY = 'bnr:rates:daily'

  const cached = await redis.get<BnrResponse>(CACHE_KEY)
  if (cached) return cached

  const raw = await fetchBnrXml()
  const rates = parseBnrXml(raw)

  // BNR publică la ~13:00 ora României — cache expiră la 14:00 ora României
  const ttl = getSecondsUntilNextBnrUpdate()
  await redis.set(CACHE_KEY, rates, { ex: ttl })

  return rates
}

// FIX v3: folosește Intl API — gestionează DST automat, fără aproximări manuale
// v2 folosea: isDST = now.getMonth() >= 2 && now.getMonth() <= 9 (greșit pentru
// 1-24 martie și 28-31 octombrie când ora efectivă nu s-a schimbat încă)
function getSecondsUntilNextBnrUpdate(): number {
  const now = new Date()

  // Intl detectează exact dacă e EEST (UTC+3) sau EET (UTC+2) — inclusiv în weekend-urile
  // de tranziție din ultima duminică din martie / ultima duminică din octombrie
  const parts = new Intl.DateTimeFormat('en-CA', {
    timeZone: 'Europe/Bucharest',
    hour: 'numeric',
    minute: 'numeric',
    hour12: false
  }).formatToParts(now)

  const currentHour = parseInt(parts.find(p => p.type === 'hour')?.value ?? '0')
  const currentMinute = parseInt(parts.find(p => p.type === 'minute')?.value ?? '0')

  const TARGET_HOUR = 14  // 14:00 ora României (1h buffer după publicarea BNR)

  if (currentHour < TARGET_HOUR) {
    return (TARGET_HOUR - currentHour) * 3600 - currentMinute * 60
  } else {
    const untilMidnight = (24 - currentHour) * 3600 - currentMinute * 60
    return untilMidnight + TARGET_HOUR * 3600
  }
}
```

**Nu cache-ui Date objects — serializarea pierde timezone:**
```typescript
// Nu:
await redis.set(key, { date: new Date() })

// Da:
await redis.set(key, { date: new Date().toISOString() })
```

---

### S13 — Serverless Gotchas: Next.js pe Vercel/Edge

**Aceasta e secțiunea pe care o omit 90% din ghiduri și care mușcă în producție.**

**GOTCHA #1 — fire-and-forget ucis după response:**

```typescript
// GREȘIT pe Vercel serverless — processCallEvent e ucis imediat după return
export async function POST(request: Request) {
  void processCallEvent(callSid, status)  // PERICULOS: ucis după return
  return new Response(twiml, { headers: { 'Content-Type': 'text/xml' } })
}

// CORECT — waitUntil spune runtime-ului să aștepte această promisiune
import { waitUntil } from '@vercel/functions'

export async function POST(request: Request) {
  waitUntil(processCallEvent(callSid, status))  // runtime-ul așteaptă
  return new Response(twiml, { headers: { 'Content-Type': 'text/xml' } })
}

// ALTERNATIVA robustă — job queue extern (BullMQ, Inngest, Trigger.dev)
// Adaugi job în queue și returnezi 200 instant
// Worker separat (non-serverless) procesează jobul
```

**GOTCHA #2 — stare in-memory nu persistă:**

```typescript
// GREȘIT: variabile module-level resetate la fiecare cold start
let cache: Map<string, unknown> = new Map()  // goală la fiecare instanță
let rateLimiter: RateLimiter = new RateLimiter(1, 1000)  // per-instanță, nu global

// CORECT: starea merge în Redis (Upstash)
// Fiecare instanță serverless citește și scrie aceeași stare
```

**GOTCHA #3 — cold starts pe routes cu inițializare greoaie:**

```typescript
// Da — inițializare module-level (o singură dată per instanță):
const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!)

export async function POST(request: Request) {
  // stripe e deja inițializat
}

// Nu — reinițializat la fiecare request:
export async function POST(request: Request) {
  const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!)
}
```

**GOTCHA #4 — timeout Vercel pe funcții serverless:**

```
Vercel Hobby: 10 secunde timeout
Vercel Pro: 60 secunde timeout
Vercel Enterprise: 900 secunde timeout

Implicație pentru webhooks: 200 OK trebuie returnat ÎNAINTE de timeout
Implicație pentru BullMQ workers: nu rulează pe Vercel serverless — trebuie VPS/Railway
```

**GOTCHA #5 — Edge Runtime are subset de Node.js APIs:**

```typescript
// Edge Runtime NU are: fs, crypto (standard Node.js), Buffer (complet), net, dgram
// Folosești: Web Crypto API, ReadableStream, TextEncoder

// În middleware sau Edge routes:
const key = await crypto.subtle.importKey(...)  // Web Crypto, nu Node.js crypto
// NU: crypto.createHmac(...)  — nu există în Edge Runtime
```

**Tabel de decizie runtime:**

| Nevoie | Runtime recomandat |
|---|---|
| Webhook cu HMAC (Node.js crypto) | Node.js serverless |
| Auth middleware simplu (JWT verify) | Edge (mai rapid) |
| BullMQ worker | Node.js long-running (Railway, VPS) |
| Fetch extern simplu | Edge sau Node.js |
| Stream procesare SSE | Edge cu ReadableStream (vezi S14) |

---

### S14 — Streaming APIs: SSE & ReadableStream

**Când folosești streaming:** API-uri AI (Claude, OpenAI), progress updates, live feeds.
Serverul trimite date în bucăți pe măsură ce le generează — nu aștepți răspunsul complet.

**SSE (Server-Sent Events) vs WebSockets:**

```
SSE:       Server → Client (one-way), text, HTTP/1.1 compatible, auto-reconnect, simplu
WebSocket: Server ↔ Client (bidirectional), binary+text, upgrade protocol, complex
→ Folosești SSE pentru streaming AI responses, progress, notifications
→ Folosești WebSocket pentru chat real-time, collaborative editing, gaming
```

**Consumarea SSE cu fetch() + ReadableStream (universal — funcționează și în Edge Runtime):**

```typescript
// lib/sse-client.ts
export async function* readSSEStream(
  url: string,
  options: RequestInit = {}
): AsyncGenerator<Record<string, string>> {
  const response = await fetch(url, {
    ...options,
    headers: { ...options.headers, Accept: 'text/event-stream' }
  })

  if (!response.ok) throw new Error(`SSE error: HTTP ${response.status}`)
  if (!response.body) throw new Error('Response has no body')

  const reader = response.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''

  try {
    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n')
      buffer = lines.pop() ?? ''  // ultimul element poate fi incomplet

      const event: Record<string, string> = {}
      for (const line of lines) {
        if (line === '') {
          // Linie goală = end of event
          if (Object.keys(event).length > 0) yield event
          Object.keys(event).forEach(k => delete event[k])
        } else if (line.startsWith('data: ')) {
          event['data'] = line.slice(6)
        } else if (line.startsWith('event: ')) {
          event['event'] = line.slice(7)
        } else if (line.startsWith('id: ')) {
          event['id'] = line.slice(4)
        }
        // Ignorăm: retry:, comments (:)
      }
    }
  } finally {
    reader.releaseLock()
  }
}
```

**Streaming Claude API — exemplu complet:**

```typescript
// lib/claude-stream.ts
import Anthropic from '@anthropic-ai/sdk'

const client = new Anthropic()  // singleton module-level

export async function* streamClaudeResponse(prompt: string): AsyncGenerator<string> {
  const stream = await client.messages.stream({
    model: 'claude-opus-4-7',
    max_tokens: 1024,
    messages: [{ role: 'user', content: prompt }]
  })

  for await (const event of stream) {
    if (
      event.type === 'content_block_delta' &&
      event.delta.type === 'text_delta'
    ) {
      yield event.delta.text
    }
  }
}

// Next.js Route Handler — streaming spre browser
export async function POST(request: Request) {
  const { prompt } = await request.json()

  const encoder = new TextEncoder()
  const readable = new ReadableStream({
    async start(controller) {
      try {
        for await (const chunk of streamClaudeResponse(prompt)) {
          // SSE format
          controller.enqueue(encoder.encode(`data: ${JSON.stringify({ text: chunk })}\n\n`))
        }
        controller.enqueue(encoder.encode('data: [DONE]\n\n'))
        controller.close()
      } catch (error) {
        controller.enqueue(encoder.encode(`data: ${JSON.stringify({ error: 'Stream failed' })}\n\n`))
        controller.close()
      }
    }
  })

  return new Response(readable, {
    headers: {
      'Content-Type': 'text/event-stream',
      'Cache-Control': 'no-cache',
      'Connection': 'keep-alive'
    }
  })
}
```

**Consumare în React (browser):**

```typescript
// hooks/use-streaming.ts
import { useState, useCallback } from 'react'

export function useStreaming() {
  const [text, setText] = useState('')
  const [isStreaming, setIsStreaming] = useState(false)

  const startStream = useCallback(async (prompt: string) => {
    setIsStreaming(true)
    setText('')

    try {
      const response = await fetch('/api/claude/stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt })
      })

      if (!response.ok || !response.body) throw new Error('Stream failed')

      const reader = response.body.getReader()
      const decoder = new TextDecoder()

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        const chunk = decoder.decode(value, { stream: true })
        for (const line of chunk.split('\n')) {
          if (!line.startsWith('data: ')) continue
          const data = line.slice(6)
          if (data === '[DONE]') break

          try {
            const parsed = JSON.parse(data)
            if (parsed.text) setText(prev => prev + parsed.text)
          } catch { /* skip malformed */ }
        }
      }
    } finally {
      setIsStreaming(false)
    }
  }, [])

  return { text, isStreaming, startStream }
}
```

---

## BLOC 4 — Webhooks

---

### S15 — Webhook Fundamentals, Idempotency & Event Ordering

**Polling vs Webhooks:**

```
POLLING (ineficient):
Tu → API: "Sunt apeluri noi?" → NU  (repetat la fiecare N secunde)
Tu → API: "Sunt apeluri noi?" → DA

WEBHOOK (event-driven):
API → Tu: "Tocmai a venit un apel" (instant, când se întâmplă)
```

**Idempotența — pattern corect cu INSERT + 23505 (fără round-trip SELECT):**

```typescript
// v2 folosea SELECT ... then INSERT — două round-trip-uri, race condition în teorie
// v3 fix: INSERT direct, 23505 = duplicat OK, mai puțin cod, același rezultat
async function processWebhookEvent(eventId: string, event: WebhookEvent) {
  const { error } = await db.from('webhook_events').insert({
    event_id: eventId,
    type: event.type,
    received_at: new Date().toISOString()
  })

  // 23505 = unique constraint violation — eveniment deja primit (provider retry)
  if (error?.code === '23505') {
    console.log(`Duplicate webhook ignored: ${eventId}`)
    return
  }
  if (error) throw error

  await handleEvent(event)

  await db.from('webhook_events')
    .update({ processed_at: new Date().toISOString() })
    .eq('event_id', eventId)
}
```

**Event ordering — webhooks nu ajung în ordine:**

```typescript
// Scenariul problematic:
// 1. call.in-progress → UPDATE calls SET status='in-progress'
// 2. call.completed   → UPDATE calls SET status='completed'
// Dacă completed ajunge primul, in-progress îl suprascrie greșit.

// Soluție: folosești timestamp din eveniment, nu din procesare
async function updateCallStatus(callSid: string, status: string, eventTimestamp: string) {
  await db.from('calls')
    .update({ status, last_event_at: eventTimestamp })
    .eq('twilio_sid', callSid)
    .lt('last_event_at', eventTimestamp)  // actualizezi DOAR dacă evenimentul e mai nou
}
```

---

### S16 — Primirea Webhooks în Next.js

**Fluxul complet cu toate pattern-urile corecte:**

```typescript
// app/api/webhooks/[provider]/route.ts
import { waitUntil } from '@vercel/functions'

export async function POST(request: Request) {
  // PASUL 1: citești body ca Buffer ÎNAINTE de orice — stream-ul e consume-once
  const payload = Buffer.from(await request.arrayBuffer())

  // PASUL 2: verifici semnătura IMEDIAT
  if (!verifyHmacSignature(payload, request.headers.get('X-Signature') ?? '', env.WEBHOOK_SECRET)) {
    return Response.json({ error: 'Invalid signature' }, { status: 401 })
  }

  // PASUL 3: timestamp check
  const timestamp = request.headers.get('X-Timestamp') ?? ''
  if (!verifyTimestamp(timestamp)) {
    return Response.json({ error: 'Webhook expired' }, { status: 400 })
  }

  // PASUL 4: parsezi DUPĂ verificare
  const body = JSON.parse(payload.toString('utf-8'))
  const eventId = body.id ?? body.event_id

  // PASUL 5: returnezi 200 INSTANT
  // waitUntil permite procesarea să continue după return (Vercel serverless)
  waitUntil(processWebhookEvent(eventId, body))

  return Response.json({ received: true }, { status: 200 })
}
```

**Când procesarea durează mult — job queue cu Inngest:**

```typescript
import { Inngest } from 'inngest'
const inngest = new Inngest({ id: 'my-app' })

export async function POST(request: Request) {
  const payload = Buffer.from(await request.arrayBuffer())
  if (!verifySignature(payload, request.headers)) {
    return Response.json({ error: 'Unauthorized' }, { status: 401 })
  }

  const event = JSON.parse(payload.toString())

  await inngest.send({
    id: event.id,           // idempotency key — Inngest ignoră duplicate
    name: `webhook/${event.type}`,
    data: event
  })

  return Response.json({ received: true })
}

// inngest/functions/process-webhook.ts — rulează în background, nu serverless
export const processWebhook = inngest.createFunction(
  { id: 'process-webhook', retries: 5 },
  { event: 'webhook/payment.completed' },
  async ({ event, step }) => {
    await step.run('update-database', () => updatePaymentInDb(event.data))
    await step.run('send-confirmation-email', () => sendEmail(event.data))
    // Fiecare step e idempotent și retryable independent
  }
)
```

---

### S17 — Verificare Semnătură per Provider

**Twilio — folosești SDK-ul oficial, nu implementare manuală:**

```typescript
// GREȘIT — implementare manuală e fragilă la query params, proxy headers, trailing slash
// URL-ul poate fi greșit dacă există proxy sau query params adăugați de infra

// CORECT — SDK-ul Twilio gestionează toate edge case-urile
import twilio from 'twilio'

function verifyTwilioSignature(request: Request, rawBody: string): boolean {
  const signature = request.headers.get('X-Twilio-Signature') ?? ''
  const webhookUrl = `${env.NEXT_PUBLIC_APP_URL}${new URL(request.url).pathname}`
  const params = Object.fromEntries(new URLSearchParams(rawBody))

  return twilio.validateRequest(
    env.TWILIO_AUTH_TOKEN,
    signature,
    webhookUrl,
    params  // SDK include params în semnătură, sortați alfabetic
  )
}
```

**GitHub Webhooks:**

```typescript
function verifyGithubSignature(payload: Buffer, header: string): boolean {
  const expected = 'sha256=' + crypto
    .createHmac('sha256', env.GITHUB_WEBHOOK_SECRET)
    .update(payload)
    .digest('hex')

  if (expected.length !== header.length) return false
  return crypto.timingSafeEqual(Buffer.from(expected), Buffer.from(header))
}
```

**Stripe — SDK face totul:**

```typescript
import Stripe from 'stripe'
const stripe = new Stripe(env.STRIPE_SECRET_KEY!)

export async function POST(request: Request) {
  // Stripe SDK cere string (text), nu Buffer
  const payload = await request.text()
  const signature = request.headers.get('Stripe-Signature')!

  let event: Stripe.Event
  try {
    event = stripe.webhooks.constructEvent(payload, signature, env.STRIPE_WEBHOOK_SECRET)
  } catch {
    return Response.json({ error: 'Invalid signature' }, { status: 400 })
  }

  switch (event.type) {
    case 'payment_intent.succeeded':
      await handlePaymentSucceeded(event.data.object)
      break
    case 'payment_intent.payment_failed':
      await handlePaymentFailed(event.data.object)
      break
  }

  return Response.json({ received: true })
}
```

---

### S18 — Delivery Guarantees, Dead Letter & Payload Limits

**Ce garantează un provider webhook:**

| Provider | Retry policy | Timeout per request | Dead letter |
|---|---|---|---|
| Twilio | 4 ore, exponential backoff | 15 secunde | Logat în Console |
| Stripe | 3 zile, 15 încercări | 30 secunde | Events dashboard |
| GitHub | 3 încercări, 1h | 10 secunde | Recent Deliveries în Settings |

**Payload size limits — important pe serverless:**

```
Vercel serverless: 4.5MB body limit (implicit)
Twilio: payload standard ~1-5KB; recording/transcription callbacks pot ajunge la >100KB
Stripe: payload standard <10KB
GitHub push events cu multe fișiere: pot ajunge la câteva sute de KB

Dacă depășești limita Vercel:
→ Response 413 Payload Too Large
→ Soluție: mărești limita cu config sau procesezi în streaming
```

```typescript
// next.config.ts — pentru payload-uri mari
export default {
  experimental: {
    serverActions: {
      bodySizeLimit: '10mb'  // default 1mb pentru Server Actions
    }
  }
} satisfies NextConfig
```

**Idempotency table — design corect:**

```sql
-- Retention: 7 zile acoperă orice provider (Stripe = 3 zile max)
CREATE TABLE webhook_events (
  event_id      TEXT PRIMARY KEY,
  type          TEXT NOT NULL,
  received_at   TIMESTAMPTZ DEFAULT NOW(),
  processed_at  TIMESTAMPTZ,
  failed_at     TIMESTAMPTZ,
  error_message TEXT,
  raw_payload   JSONB
);

-- Index pentru cleanup periodic
CREATE INDEX ON webhook_events (received_at);
```

**Dead letter queue — evenimentele care nu s-au putut procesa:**

```typescript
async function processWithDeadLetter(eventId: string, event: WebhookEvent) {
  try {
    await processWebhookEvent(eventId, event)
  } catch (error) {
    await db.from('webhook_events').upsert({
      event_id: eventId,
      type: event.type,
      received_at: new Date().toISOString(),
      failed_at: new Date().toISOString(),
      error_message: error instanceof Error ? error.message : 'Unknown',
      raw_payload: event
    })
    console.error(`DEAD_LETTER: webhook ${eventId} (${event.type}) failed permanently`)
    // Alertă Slack/PagerDuty/email pentru echipă
  }
}

// Reprocessing manual din dead letter (după ce ai fixat bug-ul):
async function replayDeadLetterEvents(since: Date) {
  const { data: failedEvents } = await db
    .from('webhook_events')
    .select('*')
    .not('failed_at', 'is', null)
    .gt('received_at', since.toISOString())

  for (const event of failedEvents ?? []) {
    await db.from('webhook_events').update({ failed_at: null }).eq('event_id', event.event_id)
    await processWebhookEvent(event.event_id, event.raw_payload)
  }
}
```

---

### S19 — Webhook Fan-out & Event Router

**Problema:** un singur endpoint primește evenimente cu tipuri diferite, fiecare tip trebuind
procesat de mai mulți handlere independenți. Dacă un handler eșuează, ceilalți trebuie
să continue.

```typescript
// lib/webhook-router.ts
type EventHandler = (event: WebhookEvent) => Promise<void>
type EventType = string

const eventHandlers = new Map<EventType, EventHandler[]>([
  ['payment.completed', [
    updateInvoiceStatus,
    sendConfirmationEmail,
    notifyAccountingSystem
  ]],
  ['payment.failed', [
    updateInvoiceStatus,
    notifyCustomer,
    alertSalesTeam
  ]],
  ['call.completed', [
    updateCallRecord,
    generateCallSummary,
    scheduleFollowUp
  ]]
])

export async function routeWebhookEvent(event: WebhookEvent): Promise<void> {
  const handlers = eventHandlers.get(event.type) ?? []

  if (handlers.length === 0) {
    console.warn(`No handler registered for event type: ${event.type}`)
    return
  }

  // Promise.allSettled — toți handlerii rulează indiferent dacă unul eșuează
  const results = await Promise.allSettled(
    handlers.map(handler => handler(event))
  )

  const failures = results.filter((r): r is PromiseRejectedResult => r.status === 'rejected')

  if (failures.length > 0) {
    failures.forEach((f, i) => {
      console.error(`Handler ${i} failed for ${event.type}:`, f.reason)
    })
    // Arunci doar dacă TOȚI handlerii au eșuat — altfel evenimentul e parțial procesat
    if (failures.length === handlers.length) {
      throw new Error(`All ${handlers.length} handlers failed for event ${event.type}`)
    }
  }
}

// Înregistrare dinamică — util pentru module/plugin systems
export function registerHandler(eventType: EventType, handler: EventHandler): void {
  const existing = eventHandlers.get(eventType) ?? []
  eventHandlers.set(eventType, [...existing, handler])
}
```

**Fan-out cu izolare completă (fiecare handler în propriul try/catch cu dead letter):**

```typescript
export async function routeWithIsolation(event: WebhookEvent): Promise<void> {
  const handlers = eventHandlers.get(event.type) ?? []

  await Promise.allSettled(
    handlers.map(async (handler, index) => {
      try {
        await handler(event)
        log({ level: 'info', type: 'webhook_processed', provider: 'router',
              eventType: event.type, eventId: event.id })
      } catch (error) {
        // Fiecare handler eșuat → propriul dead letter entry
        await db.from('webhook_handler_failures').insert({
          event_id: event.id,
          event_type: event.type,
          handler_index: index,
          error_message: error instanceof Error ? error.message : 'Unknown',
          failed_at: new Date().toISOString(),
          raw_payload: event
        })
      }
    })
  )
}
```

---

### S20 — Testare Webhooks Local + MSW

**Opțiunea 1 — ngrok (universal):**

```bash
npm install -g ngrok
ngrok authtoken YOUR_TOKEN
ngrok http 3000
# → https://abc123.ngrok.io — copiezi în provider console
```

**Opțiunea 2 — Twilio CLI:**

```bash
npm install -g twilio-cli
twilio login
twilio phone-numbers:update +40312000000 \
  --voice-url https://abc123.ngrok.io/api/webhooks/twilio/voice \
  --status-callback-url https://abc123.ngrok.io/api/webhooks/twilio/status
```

**Opțiunea 3 — MSW (Mock Service Worker) pentru teste fără API real:**

MSW interceptează `fetch()` la nivel de Node.js în teste — nu pornești niciun server, nu ai
dependențe externe, testele rulează în CI fără chei reale.

```bash
npm install -D msw
```

```typescript
// __tests__/mocks/handlers.ts
import { http, HttpResponse } from 'msw'

const BNR_XML_FIXTURE = `<?xml version="1.0" encoding="utf-8"?>
<DataSet><Body><Cube date="2026-05-22">
  <Rate currency="EUR" multiplier="1">4.974</Rate>
  <Rate currency="USD" multiplier="1">4.532</Rate>
  <Rate currency="CHF" multiplier="100">510.30</Rate>
</Cube></Body></DataSet>`

export const handlers = [
  http.get('https://www.bnr.ro/nbrfxrates.xml', () => {
    return new HttpResponse(BNR_XML_FIXTURE, {
      headers: {
        'Content-Type': 'text/xml',
        'ETag': '"bnr-20260522"',
        'Last-Modified': 'Thu, 22 May 2026 11:00:00 GMT'
      }
    })
  }),

  http.post('https://api.twilio.com/2010-04-01/Accounts/:sid/Calls.json', () => {
    return HttpResponse.json({ sid: 'CA_test_123', status: 'queued' })
  }),

  http.post('https://api.stripe.com/v1/payment_intents', () => {
    return HttpResponse.json({ id: 'pi_test_123', status: 'requires_payment_method' })
  })
]
```

```typescript
// __tests__/setup.ts
import { setupServer } from 'msw/node'
import { handlers } from './mocks/handlers'

export const server = setupServer(...handlers)

beforeAll(() => server.listen({ onUnhandledRequest: 'error' }))
afterEach(() => server.resetHandlers())
afterAll(() => server.close())
```

```typescript
// __tests__/bnr-fallback.test.ts
import { server } from './setup'
import { http, HttpResponse } from 'msw'
import { getBnrRatesSafe } from '@/lib/bnr-client'

test('folosește DB fallback când BNR e down', async () => {
  server.use(
    http.get('https://www.bnr.ro/nbrfxrates.xml', () => {
      return new HttpResponse(null, { status: 503 })
    })
  )

  const result = await getBnrRatesSafe()
  expect(result.source).toBe('database')
  expect(result.rates.length).toBeGreaterThan(0)
})

test('returnează 304 și folosește cache când ETag se potrivește', async () => {
  server.use(
    http.get('https://www.bnr.ro/nbrfxrates.xml', ({ request }) => {
      if (request.headers.get('If-None-Match') === '"bnr-20260522"') {
        return new HttpResponse(null, { status: 304 })
      }
      return new HttpResponse(BNR_XML_FIXTURE, { headers: { ETag: '"bnr-20260522"' } })
    })
  )
  // Primul fetch — populează cache
  await getBnrRatesSafe()
  // Al doilea fetch — ar trebui să primească 304 și să folosească cache
  const result = await getBnrRatesSafe()
  expect(result.source).toBe('redis')
})
```

```typescript
// Opțiunea 4 — teste unit cu Request mock (pentru webhook handlers):
function generateTestSignature(payload: string, secret: string): string {
  return crypto.createHmac('sha256', secret).update(payload).digest('hex')
}

test('returns 401 on invalid signature', async () => {
  const request = new Request('http://localhost:3000/api/webhooks/generic', {
    method: 'POST',
    headers: { 'X-Signature-SHA256': 'invalid', 'Content-Type': 'application/json' },
    body: JSON.stringify({ type: 'test' })
  })
  const response = await POST(request)
  expect(response.status).toBe(401)
})

test('processes valid webhook', async () => {
  const payload = JSON.stringify({ id: 'evt_123', type: 'call.completed', callSid: 'CA123' })
  const signature = generateTestSignature(payload, process.env.WEBHOOK_SECRET!)

  const request = new Request('http://localhost:3000/api/webhooks/generic', {
    method: 'POST',
    headers: {
      'X-Signature-SHA256': signature,
      'X-Timestamp': Math.floor(Date.now() / 1000).toString(),
      'Content-Type': 'application/json'
    },
    body: payload
  })
  const response = await POST(request)
  expect(response.status).toBe(200)
})
```

**Opțiunea 5 — webhook.site pentru inspecție manuală:**
```
https://webhook.site → URL temporar → copiezi în provider → inspectezi request-urile live
```

---

## BLOC 5 — Integrări Specifice & Operațional

---

### S21 — Twilio IVR: Integrare Completă

**Arhitectura IVR:**

```
Apelant → Twilio → POST /api/webhooks/twilio/voice (TwiML response)
                 → Apasă 1 → POST /api/webhooks/twilio/gather
                 → Transfer → POST /api/webhooks/twilio/dial-status
                 → Final → POST /api/webhooks/twilio/status
```

**TwiML builders:**

```typescript
// lib/twiml.ts
export function buildIvrMenu(): string {
  return `<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <Say language="ro-RO" voice="Polly.Carmen">
    Bun venit la Clinica Medicală.
    Apăsați 1 pentru programări.
    Apăsați 2 pentru urgențe.
    Apăsați 0 pentru operator.
  </Say>
  <Gather numDigits="1" action="/api/webhooks/twilio/gather" method="POST" timeout="10">
    <Say language="ro-RO">Vă rugăm selectați opțiunea.</Say>
  </Gather>
  <Say language="ro-RO">Nu am primit nicio selecție. Vă rugăm sunați din nou.</Say>
  <Hangup/>
</Response>`
}

export function buildTransfer(agentPhone: string): string {
  return `<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <Say language="ro-RO">Vă transferăm. Vă rugăm așteptați.</Say>
  <Dial timeout="30" action="/api/webhooks/twilio/dial-status" method="POST">
    <Number>${agentPhone}</Number>
  </Dial>
  <Say language="ro-RO">Operatorul nu este disponibil. Vă rugăm sunați mai târziu.</Say>
</Response>`
}
```

**Route handlers:**

```typescript
// app/api/webhooks/twilio/voice/route.ts
import { waitUntil } from '@vercel/functions'
import twilio from 'twilio'

export async function POST(request: Request) {
  const rawBody = await request.text()

  if (!twilio.validateRequest(
    env.TWILIO_AUTH_TOKEN,
    request.headers.get('X-Twilio-Signature') ?? '',
    `${env.NEXT_PUBLIC_APP_URL}/api/webhooks/twilio/voice`,
    Object.fromEntries(new URLSearchParams(rawBody))
  )) {
    return new Response('Unauthorized', { status: 401 })
  }

  const params = new URLSearchParams(rawBody)
  const callSid = params.get('CallSid')!
  const from = params.get('From')!

  waitUntil(
    db.from('calls').insert({
      twilio_sid: callSid,
      caller_phone: normalizePhone(from),
      status: 'ringing',
      started_at: new Date().toISOString()
    })
  )

  return new Response(buildIvrMenu(), {
    headers: { 'Content-Type': 'text/xml; charset=utf-8' }
  })
}

// app/api/webhooks/twilio/gather/route.ts
export async function POST(request: Request) {
  const rawBody = await request.text()
  if (!verifyTwilioSignature(request, rawBody)) {
    return new Response('Unauthorized', { status: 401 })
  }

  const params = new URLSearchParams(rawBody)
  const digit = params.get('Digits')

  const responses: Record<string, () => string> = {
    '1': buildAppointmentFlow,
    '2': buildEmergencyFlow,
    '0': () => buildTransfer(env.CLINIC_AGENT_PHONE)
  }

  const twiml = responses[digit ?? '']?.() ?? `<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <Say language="ro-RO">Opțiune invalidă.</Say>
  <Redirect method="POST">/api/webhooks/twilio/voice</Redirect>
</Response>`

  return new Response(twiml, { headers: { 'Content-Type': 'text/xml; charset=utf-8' } })
}

// app/api/webhooks/twilio/status/route.ts
export async function POST(request: Request) {
  const rawBody = await request.text()
  if (!verifyTwilioSignature(request, rawBody)) {
    return new Response('Unauthorized', { status: 401 })
  }

  const params = new URLSearchParams(rawBody)
  const callSid = params.get('CallSid')!
  const status = params.get('CallStatus')!
  const duration = params.get('CallDuration')
  const eventTimestamp = params.get('Timestamp') ?? new Date().toISOString()

  waitUntil(
    db.from('calls')
      .update({
        status,
        duration_seconds: duration ? parseInt(duration) : null,
        ended_at: new Date().toISOString(),
        last_event_at: eventTimestamp
      })
      .eq('twilio_sid', callSid)
      .lt('last_event_at', eventTimestamp)  // protecție event ordering
  )

  return new Response('', { status: 204 })
}
```

**Normalizare număr + outbound call:**

```typescript
export function normalizePhone(phone: string): string {
  const digits = phone.replace(/\D/g, '')
  if (digits.startsWith('40') && digits.length === 11) return `+${digits}`
  if (digits.startsWith('0') && digits.length === 10) return `+4${digits}`
  if (digits.length === 9) return `+40${digits}`
  throw new Error(`Invalid phone number: ${phone}`)
}

export async function initiateCall(to: string, webhookBaseUrl: string): Promise<string> {
  const call = await twilioClient.calls.create({
    to: normalizePhone(to),
    from: env.TWILIO_PHONE_NUMBER,
    url: `${webhookBaseUrl}/api/webhooks/twilio/voice`,
    statusCallback: `${webhookBaseUrl}/api/webhooks/twilio/status`,
    statusCallbackMethod: 'POST'
  })
  return call.sid
}
```

---

### S22 — BNR API: Cursuri Valutare cu Conditional Requests

**Parser complet cu toate fix-urile:**

```typescript
// lib/bnr-client.ts
import { XMLParser } from 'fast-xml-parser'
import { z } from 'zod'

const BnrRateSchema = z.object({
  '#text': z.number(),
  '@_currency': z.string(),
  '@_multiplier': z.number().optional().default(1)
})

const BnrXmlSchema = z.object({
  DataSet: z.object({
    Body: z.object({
      Cube: z.object({
        '@_date': z.string(),
        // FIX: fast-xml-parser returnează obiect când există un singur <Rate>
        Rate: z.union([BnrRateSchema, z.array(BnrRateSchema)])
          .transform(r => Array.isArray(r) ? r : [r])
      })
    })
  })
})

export interface ExchangeRate {
  currency: string
  rateToRON: number
  multiplier: number
  date: string
}

export async function fetchBnrRates(cachedEtag?: string | null): Promise<{
  rates: ExchangeRate[] | null
  notModified: boolean
  etag: string | null
}> {
  const headers: Record<string, string> = {
    'User-Agent': 'FinanceOS/1.0 (contact@example.com)'
  }
  if (cachedEtag) headers['If-None-Match'] = cachedEtag

  const response = await fetch(env.BNR_RATES_URL, {
    next: { revalidate: 0 },  // nu cache-ui la Next.js level — gestionăm noi
    headers
  })

  // BNR poate răspunde cu 304 dacă datele nu s-au schimbat
  if (response.status === 304) {
    return { rates: null, notModified: true, etag: cachedEtag ?? null }
  }

  if (!response.ok) throw new Error(`BNR HTTP ${response.status}`)

  const xml = await response.text()
  const parser = new XMLParser({ ignoreAttributes: false, attributeNamePrefix: '@_' })
  const parsed = BnrXmlSchema.parse(parser.parse(xml))
  const cube = parsed.DataSet.Body.Cube

  const rates = cube.Rate.map(rate => ({
    currency: rate['@_currency'],
    // FIX: multiplier — CHF are multiplier=100, deci rata e împărțită la 100
    rateToRON: rate['#text'] / rate['@_multiplier'],
    multiplier: rate['@_multiplier'],
    date: cube['@_date']
  }))

  const newEtag = response.headers.get('ETag') ?? response.headers.get('Last-Modified')
  return { rates, notModified: false, etag: newEtag }
}

export function convertToRON(amount: number, currency: string, rates: ExchangeRate[]): number {
  if (currency === 'RON') return amount
  const rate = rates.find(r => r.currency === currency)
  if (!rate) throw new Error(`Monedă necunoscută: ${currency}`)
  return Number((amount * rate.rateToRON).toFixed(4))
}

export function convertFromRON(amountRON: number, toCurrency: string, rates: ExchangeRate[]): number {
  if (toCurrency === 'RON') return amountRON
  const rate = rates.find(r => r.currency === toCurrency)
  if (!rate) throw new Error(`Monedă necunoscută: ${toCurrency}`)
  return Number((amountRON / rate.rateToRON).toFixed(4))
}
```

**Fallback stratificat cu ETag integrat:**

```typescript
// FIX CRITIC: rate hardcodate devin stale și cauzează calcule greșite în tăcere
// Soluția: 3 niveluri de fallback + conditional GET pentru economisire bandwidth

interface BnrCacheEntry {
  rates: ExchangeRate[]
  etag: string | null
}

export async function getBnrRatesSafe(): Promise<{
  rates: ExchangeRate[]
  source: 'live' | 'redis' | 'database' | 'emergency'
  date: string
}> {
  // Nivel 1: Redis cache (cu ETag salvat pentru conditional GET)
  const cached = await redis.get<BnrCacheEntry>('bnr:rates')
  if (cached) return { rates: cached.rates, source: 'redis', date: cached.rates[0]?.date ?? 'unknown' }

  // Nivel 2: Fetch live de la BNR (cu circuit breaker + conditional GET)
  try {
    const cachedEntry = await redis.get<BnrCacheEntry>('bnr:rates:meta')
    const result = await bnrBreaker.execute(() => fetchBnrRates(cachedEntry?.etag))

    if (result.notModified && cachedEntry) {
      // Date neschimbate — reîmprospătăm TTL-ul fără re-parsare
      const ttl = getSecondsUntilNextBnrUpdate()
      await redis.set('bnr:rates', { rates: cachedEntry.rates, etag: cachedEntry.etag }, { ex: ttl })
      return { rates: cachedEntry.rates, source: 'live', date: cachedEntry.rates[0]?.date ?? 'unknown' }
    }

    if (result.rates) {
      const ttl = getSecondsUntilNextBnrUpdate()
      const entry: BnrCacheEntry = { rates: result.rates, etag: result.etag }
      await redis.set('bnr:rates', entry, { ex: ttl })
      await redis.set('bnr:rates:meta', entry, { ex: 86400 * 7 })  // 7 zile pentru ETag
      await saveRatesToDatabase(result.rates)
      return { rates: result.rates, source: 'live', date: result.rates[0]?.date ?? 'unknown' }
    }
  } catch (error) {
    console.error('BNR live fetch failed:', error)
  }

  // Nivel 3: Ultimele rate valide din DB
  const { data: dbRates } = await db
    .from('exchange_rates_snapshots')
    .select('*')
    .order('snapshot_date', { ascending: false })
    .limit(1)
    .maybeSingle()

  if (dbRates) {
    console.warn(`BNR: using DB fallback from ${dbRates.snapshot_date}`)
    return { rates: dbRates.rates, source: 'database', date: dbRates.snapshot_date }
  }

  // Nivel 4: Rate de urgență — DOAR ca ultimă soluție, cu alertă explicită
  // IMPORTANT: actualizezi EMERGENCY_RATES_DATE ori de câte ori schimbi ratele
  console.error('CRITICAL: BNR unavailable AND no DB snapshot — using emergency hardcoded rates!')
  return { rates: EMERGENCY_HARDCODED_RATES, source: 'emergency', date: EMERGENCY_RATES_DATE }
}

async function saveRatesToDatabase(rates: ExchangeRate[]) {
  const date = rates[0]?.date
  if (!date) return
  await db.from('exchange_rates_snapshots').upsert({
    snapshot_date: date,
    rates,
    created_at: new Date().toISOString()
  }, { onConflict: 'snapshot_date' })
}

// Schema DB pentru snapshots:
// CREATE TABLE exchange_rates_snapshots (
//   id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
//   snapshot_date DATE NOT NULL UNIQUE,
//   rates JSONB NOT NULL,
//   created_at TIMESTAMPTZ DEFAULT NOW()
// );

// IMPORTANT: actualizezi data și ratele împreună — ratele stale cu o dată veche
// sunt mai periculoase decât ratele stale fără dată (cel puțin știi că sunt vechi)
const EMERGENCY_RATES_DATE = '2026-05-22'  // actualizezi manual când schimbi ratele
const EMERGENCY_HARDCODED_RATES: ExchangeRate[] = [
  { currency: 'EUR', rateToRON: 4.974, multiplier: 1, date: EMERGENCY_RATES_DATE },
  { currency: 'USD', rateToRON: 4.532, multiplier: 1, date: EMERGENCY_RATES_DATE },
  { currency: 'GBP', rateToRON: 5.812, multiplier: 1, date: EMERGENCY_RATES_DATE },
  { currency: 'CHF', rateToRON: 5.103, multiplier: 1, date: EMERGENCY_RATES_DATE },
]
```

---

### S23 — Distributed Rate Limiting & SDK Patterns

**Rate limiting distribuit — Upstash Ratelimit:**

```typescript
import { Ratelimit } from '@upstash/ratelimit'
import { Redis } from '@upstash/redis'

// Funcționează pe TOATE instanțele serverless — starea e în Redis, nu în memorie
const twilioOutboundLimit = new Ratelimit({
  redis: Redis.fromEnv(),
  limiter: Ratelimit.slidingWindow(1, '1 s'),
  prefix: 'ratelimit:twilio:outbound'
})

const bnrFetchLimit = new Ratelimit({
  redis: Redis.fromEnv(),
  limiter: Ratelimit.fixedWindow(10, '1 d'),
  prefix: 'ratelimit:bnr'
})

export async function rateLimitedTwilioFetch<T>(url: string, options?: RequestInit): Promise<T> {
  const { success, reset } = await twilioOutboundLimit.limit('global')

  if (!success) {
    await sleep(Math.max(reset - Date.now(), 0))
    return rateLimitedTwilioFetch(url, options)
  }

  return apiFetch<T>(url, {
    ...options,
    headers: { ...options?.headers, 'Authorization': twilioAuthHeader() }
  })
}
```

**SDK vs raw HTTP — decizie:**

| Criteriu | SDK | Raw fetch |
|---|---|---|
| Autentificare complexă (Basic, OAuth2) | SDK | — |
| Retry + rate limiting automat | SDK | Manual |
| Webhooks + signature verification | SDK (dacă există) | Manual |
| Bundle size mic | — | fetch |
| Control total pe request | — | fetch |
| API simplu (BNR, REST CRUD) | — | fetch |

**Singleton pattern pentru SDK-uri:**

```typescript
// lib/stripe.ts
import Stripe from 'stripe'
export const stripe = new Stripe(env.STRIPE_SECRET_KEY, {
  apiVersion: '2024-06-20',
  typescript: true,
  maxNetworkRetries: 3,
  timeout: 10_000
})

// lib/twilio.ts
import Twilio from 'twilio'
export const twilioClient = Twilio(env.TWILIO_ACCOUNT_SID, env.TWILIO_AUTH_TOKEN)
// Folosit pentru outbound (calls, SMS, lookup) — NU pentru webhook handling
```

**Paginare automată cu Stripe SDK:**

```typescript
const customers: Stripe.Customer[] = []
for await (const customer of stripe.customers.list({ limit: 100 })) {
  customers.push(customer)
}
// SDK-ul gestionează automat cursors, N request-uri, rate limiting
```

---

### S24 — Logging, Correlation IDs, Tracing & GDPR

**Correlation ID — debugging cross-service:**

Fără correlation ID, nu poți trasa un apel Twilio prin handler → DB → email → Slack.
Cu correlation ID, filtrezi toate log-urile unui request cu o singură interogare.

```typescript
// lib/correlation.ts
import { randomUUID } from 'crypto'

// Adaugi X-Correlation-ID la toate request-urile outbound
export function createCorrelatedFetch(correlationId: string) {
  return async function<T>(url: string, options: RequestInit = {}): Promise<T> {
    return apiFetch<T>(url, {
      ...options,
      headers: {
        ...options.headers,
        'X-Correlation-ID': correlationId
      }
    })
  }
}

// În webhook handler — extragi sau generezi correlation ID
export async function POST(request: Request) {
  // Dacă provider-ul trimite un ID propriu, îl folosești pentru trasabilitate end-to-end
  const correlationId =
    request.headers.get('X-Correlation-ID') ??
    request.headers.get('X-Request-ID') ??
    randomUUID()

  const payload = Buffer.from(await request.arrayBuffer())
  // ... verificare semnătură ...
  const body = JSON.parse(payload.toString())

  waitUntil(processWebhookEvent(body.id, body, correlationId))

  return Response.json({ received: true, correlationId })
}

// processWebhookEvent propagă correlationId la toate operațiunile descendente
async function processWebhookEvent(eventId: string, event: WebhookEvent, correlationId: string) {
  log({ level: 'info', type: 'webhook_received', provider: 'generic',
        eventId, eventType: event.type, correlationId })
  // ...
}
```

**GDPR — redactarea PII din log-uri:**

```typescript
// lib/logger.ts — versiunea GDPR-compliant
type LogLevel = 'info' | 'warn' | 'error'

interface ApiLog {
  level: LogLevel
  type: 'api_request' | 'api_response' | 'webhook_received' | 'webhook_processed' | 'webhook_failed'
  provider: string
  url?: string
  method?: string
  status?: number
  durationMs?: number
  eventId?: string
  eventType?: string
  correlationId?: string
  error?: string
}

// Redactare PII — nu loghezi numere de telefon, emailuri, CNP, date carduri
const PII_PATTERNS: Array<{ pattern: RegExp; replacement: string }> = [
  { pattern: /\+?[0-9]{10,15}/g, replacement: '[PHONE]' },
  { pattern: /[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/g, replacement: '[EMAIL]' },
  { pattern: /\b4[0-9]{12}(?:[0-9]{3})?\b/g, replacement: '[CARD]' },    // Visa
  { pattern: /\b5[1-5][0-9]{14}\b/g, replacement: '[CARD]' },            // Mastercard
  { pattern: /\b[0-9]{13}\b/g, replacement: '[CNP]' },                   // CNP românesc
]

function redactPII(str: string): string {
  return PII_PATTERNS.reduce(
    (s, { pattern, replacement }) => s.replace(pattern, replacement),
    str
  )
}

export function log(data: ApiLog) {
  const entry = {
    timestamp: new Date().toISOString(),
    ...data,
    // Redactare automată pe câmpurile care pot conține PII
    error: data.error ? redactPII(data.error) : undefined,
    url: data.url ? redactPII(data.url) : undefined,
  }
  if (data.level === 'error') console.error(JSON.stringify(entry))
  else console.log(JSON.stringify(entry))
}

export async function trackedFetch<T>(
  provider: string,
  url: string,
  options?: RequestInit & { correlationId?: string }
): Promise<T> {
  const { correlationId, ...fetchOptions } = options ?? {}
  const start = Date.now()

  log({ level: 'info', type: 'api_request', provider,
        url: redactPII(url), method: fetchOptions.method ?? 'GET', correlationId })

  try {
    const data = await apiFetch<T>(url, fetchOptions)
    log({ level: 'info', type: 'api_response', provider,
          status: 200, durationMs: Date.now() - start, correlationId })
    return data
  } catch (error) {
    log({
      level: 'error',
      type: 'api_response',
      provider,
      status: error instanceof ApiError ? error.status : 0,
      durationMs: Date.now() - start,
      error: error instanceof Error ? redactPII(error.message) : 'Unknown',
      correlationId
    })
    throw error
  }
}
```

---

### S25 — OpenAPI Type Generation & API Contracts

**De ce contează:** când integrezi un API nou (Stripe, Twilio, orice provider cu documentație),
nu scrii interfețele TypeScript manual. Le generezi din specificația OpenAPI a provider-ului.
Tipurile generate sunt garantat sincronizate cu API-ul real.

```bash
# Instalare
npm install -D openapi-typescript openapi-fetch

# Generare tipuri din spec URL (ex: Stripe)
npx openapi-typescript https://raw.githubusercontent.com/stripe/openapi/master/openapi/spec3.json \
  -o src/types/stripe-api.d.ts

# Sau din fișier local descărcat
npx openapi-typescript ./openapi.json -o src/types/api.d.ts
```

**Client type-safe cu openapi-fetch:**

```typescript
// lib/typed-client.ts
import createClient from 'openapi-fetch'
import type { paths } from '@/types/api'  // generat automat

const client = createClient<paths>({
  baseUrl: 'https://api.example.com',
  headers: {
    'Authorization': `Bearer ${env.API_KEY}`,
    'X-Correlation-ID': randomUUID()
  }
})

// Complet type-safe — TypeScript cunoaște parametrii, body și response pentru fiecare endpoint
async function getInvoice(id: string) {
  const { data, error } = await client.GET('/invoices/{id}', {
    params: { path: { id } }
  })
  // data: typed ca schema 200 response
  // error: typed ca schema 4xx/5xx response
  if (error) throw new Error(`API Error: ${error.message}`)
  return data
}

async function createInvoice(payload: { customer_id: string; amount: number }) {
  const { data, error } = await client.POST('/invoices', {
    body: payload  // TypeScript verifică că body-ul e conform schemei
  })
  if (error) throw new Error(`Create invoice failed: ${error.message}`)
  return data
}
```

**Generare Zod din OpenAPI (validare runtime):**

```bash
npm install -D openapi-zod-client
npx openapi-zod-client ./openapi.json -o src/lib/api-schemas.ts
# Generează automat schema Zod pentru fiecare endpoint
```

**Când API-ul nu are spec OpenAPI — workflow manual:**

```typescript
// 1. Inspectezi răspunsul real în devtools / Postman / httpie
// 2. Generezi schema Zod din structura observată
// 3. Inferezi tipul TypeScript din schema Zod (nu invers)

// Nu:
interface ProviderResponse {  // scris manual, se desincronizează
  id: string
  status: string
}

// Da:
const ProviderResponseSchema = z.object({
  id: z.string(),
  status: z.enum(['active', 'inactive', 'pending'])
})
type ProviderResponse = z.infer<typeof ProviderResponseSchema>  // derivat din Zod
```

---

### S26 — 50 Greșeli Critice & Checklist Pre-Deploy

**50 Greșeli Critice:**

**HTTP & Requests:**
1. `fetch()` fără timeout — blochează serverless lambda indefinit la provider down
2. `response.json()` fără `response.ok` check — parsezi body-ul de eroare ca date valide
3. `||` pentru fallback la string/număr din API — `""` și `0` devin false (folosești `??`)
4. `await` lipsă pe `response.json()` — returnezi `Promise<T>`, nu `T`
5. Nu verifici `Content-Type` înainte de `.json()` pe răspuns potențial binar sau XML
6. Niciun `AbortController` — nu poți cancela requests la timeout, lambda rămâne deschis
7. Idempotency key absent pe POST outbound retryable — duplicate la network failure

**Authentication:**
8. API key în URL query param — apare în access logs, server logs, browser history
9. `process.env.API_KEY` fără validare Zod la startup — crash la primul request, nu la boot
10. Token OAuth2 re-fetched la fiecare request (cache in-memory în serverless) — epuizezi rate limit de auth
11. Race condition pe token cache — N instanțe serverless fac N fetches simultane la cache miss
12. HTTP Basic credentials hardcodate — detectate de git-secrets, intră în git history

**Webhooks — Securitate:**
13. `JSON.parse(await request.json())` înainte de verificare semnătură — pierzi Buffer raw necesar HMAC
14. `===` în loc de `timingSafeEqual` — timing attack posibil
15. Niciun timestamp check — replay attacks cu request-uri capturate săptămâni mai târziu
16. Procesare sincronă în handler — timeout la provider (Twilio: 15s, Stripe: 30s)
17. `void fn()` fire-and-forget în serverless (Vercel) — ucis imediat după `return`
18. Fără idempotency check în DB — duplicate la retry automat al provider-ului
19. URL webhook hardcodat ca `http://` în producție — semnătura include protocolul
20. Implementare manuală Twilio signature în loc de SDK — fragilă la query params și proxy
21. Procesare fără event ordering — event vechi suprascrie event nou (status call greșit)

**Webhooks — Operațional:**
22. Niciun dead letter queue — evenimentele care nu se procesează sunt pierdute definitiv
23. Retention sub 3 zile — nu poți replay events Stripe după failure (Stripe ține 3 zile)
24. Niciun handler pentru tipuri de evenimente noi — provider adaugă event type și aplicația ignoră silențios
25. Fan-out cu Promise.all în loc de Promise.allSettled — un handler eșuat ucide toți ceilalți
26. Payload >4.5MB pe Vercel fără configurare body size limit — 413 Payload Too Large silențios

**Serverless:**
27. State in-memory (rate limiter, cache, counter) în serverless — stare per-instanță, resetată la cold start
28. `RateLimiter` sau `CircuitBreaker` in-memory în serverless — limita efectivă e `N_instanțe × limita`
29. Inițializare SDK în interiorul handler-ului — reinițializat la fiecare request
30. Ignorare timeout Vercel Hobby (10s) — funcțiile cu retry + backoff depășesc limita

**Rate Limiting & Retry:**
31. Retry pe `4xx` client errors — retry nu rezolvă erori de input (400, 401, 403, 404)
32. Retry pe POST non-idempotent fără Idempotency-Key — duplicate (plăți duble, apeluri duble)
33. Retry fără jitter — thundering herd la erori simultane pe N utilizatori
34. Ignorare `Retry-After` header pe 429 — risc de ban cont
35. Rate limit headers ignorate complet — nu știi când ești aproape de limită (proactiv)

**Caching:**
36. Token cache in-memory în serverless — resetat la cold start, N token fetches simultane
37. Cache pe `Date` objects — serializare pierde timezone (folosești `.toISOString()`)
38. BNR fallback cu rate hardcodate fără dată — stale, cauze calcule financiare greșite silențios
39. `getSecondsUntilMidnight()` fără timezone România — cache expiră la ora greșită
40. DST calculat manual (`month >= 2 && month <= 9`) — greșit în weekendurile de tranziție (martie/octombrie)

**BNR & XML:**
41. `multiplier` ignorat în parsare BNR — CHF, JPY au `multiplier="100"` → rate greșite cu factor 100
42. `z.array(BnrRateSchema)` fără `.transform()` — crash dacă XML are un singur `<Rate>`
43. Niciun fallback DB — la BNR down aplicația cade complet în loc să servească date recente
44. Ignorarea `source` din getBnrRatesSafe — nu avertizezi utilizatorul când rate-le vin din fallback

**Streaming:**
45. `EventSource` cu custom headers — API nativ nu suportă headers (folosești fetch + ReadableStream)
46. `reader.releaseLock()` absent în finally — ReadableStream blocat permanent după eroare
47. Parsare SSE cu split `\n` simplu — evenimentele multi-linie sunt corupte (trebuie buffer acumulativ)

**TypeScript & Tipuri:**
48. `any` pe răspuns API — pierzi protecția la compile time
49. `Number(undefined)` pe câmp lipsă — `NaN` în calcule financiare, fără eroare vizibilă
50. Interface definită manual fără comparare cu schema reală sau fără generare din OpenAPI spec — drift garantat

---

**Checklist Pre-Deploy — API Integration:**

```markdown
## Secrets & Config
- [ ] Toate cheile API în .env.local, validate cu Zod la startup
- [ ] .env.local în .gitignore + `git log -S "SK_LIVE"` = 0 rezultate
- [ ] URL-uri webhook setate cu HTTPS în provider console
- [ ] Niciun NEXT_PUBLIC_ pe secrete

## Security
- [ ] Signature verification pe toate webhook endpoints
- [ ] timingSafeEqual folosit (nu ===)
- [ ] Timestamp validation (max 5 minute)
- [ ] Idempotency check în DB pentru webhook events (INSERT + 23505, fără SELECT)

## Resilience & Serverless
- [ ] Timeout setat pe toate fetch()-urile externe (default 10s)
- [ ] Retry DOAR pe 5xx și 429, NU pe 4xx
- [ ] Idempotency-Key pe POST-uri outbound retryable
- [ ] waitUntil() în loc de void fire-and-forget (Vercel)
- [ ] Niciun state in-memory pentru distributed operations (Redis în schimb)
- [ ] Circuit breaker configurat pentru API-uri critice (BNR, Twilio)
- [ ] failuresKey TTL aliniat cu config.resetMs în CircuitBreaker

## Caching & HTTP
- [ ] DST calculat cu Intl.DateTimeFormat Europe/Bucharest (nu manual)
- [ ] ETag/Last-Modified salvat alături de date pentru conditional GET
- [ ] Date serializate ca ISO string, nu ca Date object

## BNR Specific
- [ ] multiplier aplicat la parsare (rateToRON = value / multiplier)
- [ ] XML array transform în schema Zod
- [ ] Fallback din DB (nu constante hardcodate)
- [ ] EMERGENCY_RATES_DATE actualizată când schimbi ratele hardcodate
- [ ] Cache expiră la ora 14:00 ora României cu Intl (nu UTC midnight)

## Twilio IVR
- [ ] Numere normalizate la format E.164 (+407XX)
- [ ] Content-Type: text/xml pe toate răspunsurile TwiML
- [ ] language="ro-RO" pe toate <Say>
- [ ] StatusCallback URL setat la /api/webhooks/twilio/status
- [ ] SDK Twilio pentru signature verification (nu implementare manuală)
- [ ] Event ordering protejat cu last_event_at + .lt() check

## Streaming
- [ ] ReadableStream cu reader.releaseLock() în finally
- [ ] Buffer acumulativ pentru SSE (nu split simplu \n)
- [ ] [DONE] sentinel verificat înainte de JSON.parse

## Logging & GDPR
- [ ] PII redactat din log-uri (telefoane, emailuri, date card)
- [ ] Correlation ID propagat prin toate operațiunile unui request
- [ ] Nu loghezi body-ul complet al webhook-urilor (conține PII)

## Testare
- [ ] MSW configurat pentru teste fără API real
- [ ] Webhook-urile testate cu ngrok local
- [ ] Semnătură invalidă → 401
- [ ] Timestamp expirat → 400
- [ ] Duplicate event → 200 fără re-procesare
- [ ] BNR fallback testat cu handler MSW override → source: 'database'
- [ ] waitUntil verificat că rulează după return
```

---

*Ghid API Integration & Webhooks v3.0 — Mai 2026*
*Proiecte de referință: Clinică Medicală (Twilio IVR) · ERP Financiar (BNR + Stripe) · Vibe Budget · orice proiect cu integrări externe*
