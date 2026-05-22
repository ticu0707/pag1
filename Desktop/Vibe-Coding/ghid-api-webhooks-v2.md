# Ghid API Integration & Webhooks v2.0
## Pentru Vibe-Coding — Next.js 14+ · TypeScript · Node.js ESM

**Mai 2026 · 22 secțiuni · 5 Blocuri · 38 greșeli critice**

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
procesează, dar connexiunea cade înainte să primești răspunsul. Retry-ul creează un duplicat.

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

**Pentru răspunsuri cu câmpuri opționale:**

```typescript
const TwilioCallSchema = z.object({
  sid: z.string(),
  status: z.enum(['queued', 'ringing', 'in-progress', 'completed', 'failed', 'busy', 'no-answer']),
  to: z.string(),
  from: z.string(),
  duration: z.string().nullable(),
  price: z.string().nullable(),
  error_code: z.string().nullable(),
  date_created: z.string()
})

// safeParse când vrei să gestionezi erorile explicit
const result = TwilioCallSchema.safeParse(rawData)
if (!result.success) {
  console.error('Invalid Twilio response:', result.error.flatten())
  return null
}
const call = result.data  // complet tipat
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

## BLOC 2 — Autentificare & Securitate

---

### S4 — Metode de Autentificare

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

**OAuth2 Client Credentials — detalii în S6 (token cache distribuit).**

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

### S5 — HMAC Signature Verification

**De ce e critic:** Fără verificare de semnătură, oricine poate POST la endpoint-ul tău și declanșa
acțiuni reale (programări medicale, plăți, modificări de date).

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
  // Verifici lungimea ÎNAINTE — bufferele trebuie să fie egale ca lungime
  // (hex HMAC are întotdeauna lungime fixă pentru același algoritm)
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
  // REGULA: citești body ca Buffer ÎNAINTE de orice — nu poți citi de două ori
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

### S6 — Token Cache Distribuit & Rotația Secretelor

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
  // Notă: inflightRequests e in-memory, deci deduplication e per-instanță.
  // Pentru serverless, aceasta e corect — instanțele nu partajează requests.
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

### S7 — Environment Variables & Validation la Startup

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

### S8 — fetch() Robust: Timeouts, Erori, AbortController

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

### S9 — Retry Logic, Backoff & Idempotency

**Când NU faci retry:**

```typescript
// 4xx (client errors) — retry nu rezolvă nimic:
// 400 Bad Request, 401 Unauthorized, 403 Forbidden, 404 Not Found, 422 Unprocessable
// EXCEPȚIE: 429 (rate limit) — faci retry cu delay din Retry-After header

// POST non-idempotent fără Idempotency-Key — poți crea duplicate
// Soluție: adaugă Idempotency-Key ÎNAINTE de retry (vezi S2)
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
    baseDelayMs = 1000,
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
        const retryAfter = (error.body as Record<string, unknown>)?.['retry_after']
        if (typeof retryAfter === 'number') {
          await sleep(retryAfter * 1000)
          continue
        }
      }

      // Exponential backoff + jitter (previne thundering herd)
      const exponential = baseDelayMs * Math.pow(2, attempt)
      const jitter = Math.random() * 1000
      await sleep(Math.min(exponential + jitter, maxDelayMs))
    }
  }

  throw lastError
}

const sleep = (ms: number) => new Promise(resolve => setTimeout(resolve, ms))
```

---

### S10 — Circuit Breaker Pattern

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
      await this.redis.expire(failuresKey, 300)

      if (failures >= this.config.threshold) {
        await this.redis.set(stateKey, { failures, openedAt: Date.now() }, {
          ex: Math.ceil(this.config.resetMs / 1000) * 2
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

### S11 — Caching Răspunsuri API

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

// IMPORTANT: calculul ține cont de timezone-ul României, nu UTC
function getSecondsUntilNextBnrUpdate(): number {
  const now = new Date()

  // România: EET = UTC+2 (iarnă), EEST = UTC+3 (vară)
  const isDST = now.getMonth() >= 2 && now.getMonth() <= 9
  const offsetHours = isDST ? 3 : 2
  const bucharestNow = new Date(now.getTime() + offsetHours * 3_600_000)

  const TARGET_HOUR = 14  // 14:00 ora României (1h buffer după publicarea BNR)
  const currentHour = bucharestNow.getUTCHours()
  const currentMinute = bucharestNow.getUTCMinutes()

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

### S12 — Serverless Gotchas: Next.js pe Vercel/Edge

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
// Edge Runtime NU are: fs, crypto (standard), Buffer (complet), net, dgram
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
| Stream procesare | Edge cu ReadableStream |

---

## BLOC 4 — Webhooks

---

### S13 — Webhook Fundamentals, Idempotency & Event Ordering

**Polling vs Webhooks:**

```
POLLING (ineficient):
Tu → API: "Sunt apeluri noi?" → NU  (repetat la fiecare N secunde)
Tu → API: "Sunt apeluri noi?" → DA

WEBHOOK (event-driven):
API → Tu: "Tocmai a venit un apel" (instant, când se întâmplă)
```

**Idempotența — provider-ul retrimite același eveniment de 2-3 ori la network error:**

```typescript
async function processWebhookEvent(eventId: string, event: WebhookEvent) {
  const existing = await db
    .from('webhook_events')
    .select('id')
    .eq('event_id', eventId)
    .maybeSingle()

  if (existing.data) {
    console.log(`Duplicate webhook ignored: ${eventId}`)
    return
  }

  // Inserezi ÎNAINTE de procesare (insert-then-process)
  const { error } = await db.from('webhook_events').insert({
    event_id: eventId,
    type: event.type,
    received_at: new Date().toISOString()
  })

  if (error?.code === '23505') return  // unique constraint — race condition, ignorat corect
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

### S14 — Primirea Webhooks în Next.js

**Fluxul complet cu toate pattern-urile corecte:**

```typescript
// app/api/webhooks/[provider]/route.ts
import { waitUntil } from '@vercel/functions'

export async function POST(request: Request) {
  // PASUL 1: citești body ca Buffer ÎNAINTE de orice — nu poți citi de două ori
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

### S15 — Verificare Semnătură per Provider

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

### S16 — Delivery Guarantees, Dead Letter & Retention

**Ce garantează un provider webhook:**

| Provider | Retry policy | Timeout per request | Dead letter |
|---|---|---|---|
| Twilio | 4 ore, exponential backoff | 15 secunde | Logat în Console |
| Stripe | 3 zile, 15 încercări | 30 secunde | Events dashboard |
| GitHub | 3 încercări, 1h | 10 secunde | Recent Deliveries în Settings |

**Idempotency table — design corect:**

```sql
-- Retention: 7 zile acoperă orice provider (Stripe = 3 zile max)
CREATE TABLE webhook_events (
  event_id    TEXT PRIMARY KEY,
  type        TEXT NOT NULL,
  received_at TIMESTAMPTZ DEFAULT NOW(),
  processed_at TIMESTAMPTZ,
  failed_at   TIMESTAMPTZ,
  error_message TEXT,
  raw_payload JSONB
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

### S17 — Testare Webhooks Local

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

**Opțiunea 3 — teste unit cu Request mock:**

```typescript
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

**Opțiunea 4 — webhook.site pentru inspecție manuală:**
```
https://webhook.site → URL temporar → copiezi în provider → inspectezi request-urile live
```

---

## BLOC 5 — Integrări Specifice & Operațional

---

### S18 — Twilio IVR: Integrare Completă

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

### S19 — BNR API: Cursuri Valutare

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

export async function fetchBnrRates(): Promise<ExchangeRate[]> {
  const response = await fetch(env.BNR_RATES_URL, {
    next: { revalidate: 3600 },
    headers: { 'User-Agent': 'FinanceOS/1.0 (contact@example.com)' }
  })

  if (!response.ok) throw new Error(`BNR HTTP ${response.status}`)

  const xml = await response.text()
  const parser = new XMLParser({ ignoreAttributes: false, attributeNamePrefix: '@_' })
  const parsed = BnrXmlSchema.parse(parser.parse(xml))
  const cube = parsed.DataSet.Body.Cube

  return cube.Rate.map(rate => ({
    currency: rate['@_currency'],
    rateToRON: rate['#text'] / rate['@_multiplier'],
    multiplier: rate['@_multiplier'],
    date: cube['@_date']
  }))
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

**Fallback stratificat — ultimele rate din DB, nu constante hardcodate:**

```typescript
// FIX CRITIC: rate hardcodate devin stale și cauzează calcule greșite în tăcere
// Soluția: 3 niveluri de fallback

export async function getBnrRatesSafe(): Promise<{
  rates: ExchangeRate[]
  source: 'live' | 'redis' | 'database' | 'emergency'
  date: string
}> {
  // Nivel 1: Redis cache
  const cached = await redis.get<ExchangeRate[]>('bnr:rates')
  if (cached) return { rates: cached, source: 'redis', date: cached[0]?.date ?? 'unknown' }

  // Nivel 2: Fetch live de la BNR (cu circuit breaker)
  try {
    const rates = await bnrBreaker.execute(() => fetchBnrRates())
    const ttl = getSecondsUntilNextBnrUpdate()
    await redis.set('bnr:rates', rates, { ex: ttl })
    await saveRatesToDatabase(rates)
    return { rates, source: 'live', date: rates[0]?.date ?? 'unknown' }
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

// Rate de urgență — documentate explicit cu data la care au fost setate
const EMERGENCY_RATES_DATE = '2026-05-22'
const EMERGENCY_HARDCODED_RATES: ExchangeRate[] = [
  { currency: 'EUR', rateToRON: 4.974, multiplier: 1, date: EMERGENCY_RATES_DATE },
  { currency: 'USD', rateToRON: 4.532, multiplier: 1, date: EMERGENCY_RATES_DATE },
  { currency: 'GBP', rateToRON: 5.812, multiplier: 1, date: EMERGENCY_RATES_DATE },
  { currency: 'CHF', rateToRON: 5.103, multiplier: 1, date: EMERGENCY_RATES_DATE },
]
```

---

### S20 — Distributed Rate Limiting & SDK Patterns

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

### S21 — Logging, Monitoring & Debugging

**Logging structurat:**

```typescript
// lib/logger.ts
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
  error?: string
}

export function log(data: ApiLog) {
  const entry = { timestamp: new Date().toISOString(), ...data }
  if (data.level === 'error') console.error(JSON.stringify(entry))
  else console.log(JSON.stringify(entry))
}

export async function trackedFetch<T>(provider: string, url: string, options?: RequestInit): Promise<T> {
  const start = Date.now()
  log({ level: 'info', type: 'api_request', provider, url, method: options?.method ?? 'GET' })

  try {
    const data = await apiFetch<T>(url, options)
    log({ level: 'info', type: 'api_response', provider, url, status: 200, durationMs: Date.now() - start })
    return data
  } catch (error) {
    log({
      level: 'error',
      type: 'api_response',
      provider, url,
      status: error instanceof ApiError ? error.status : 0,
      durationMs: Date.now() - start,
      error: error instanceof Error ? error.message : 'Unknown'
    })
    throw error
  }
}
```

**Debugging Twilio:**
```bash
# Console Twilio → Monitor → Logs → Calls / Messages / Errors
# Toate request-urile webhook, TwiML responses, erori vizibile în UI

# Test outbound call local
twilio api:core:calls:create \
  --to "+40721000000" \
  --from "+40312000000" \
  --url "https://abc123.ngrok.io/api/webhooks/twilio/voice"
```

**Debugging BNR:**
```bash
# Test live XML
curl https://www.bnr.ro/nbrfxrates.xml | head -30

# Verifică multiplier pe CHF — dacă e 100, rata fără ajustare e de 100x greșită
curl https://www.bnr.ro/nbrfxrates.xml | grep -A1 'CHF'
# <Rate currency="CHF" multiplier="100">510.30</Rate>
# rateToRON = 510.30 / 100 = 5.103 RON per CHF
```

---

### S22 — Greșeli Critice & Checklist Pre-Deploy

**38 Greșeli Critice:**

**HTTP & Requests:**
1. `fetch()` fără timeout — blochează serverless lambda indefinit la provider down
2. `response.json()` fără `response.ok` check — parsezi body-ul de eroare ca date valide
3. `||` pentru fallback la string/număr din API — `""` și `0` devin false (folosești `??`)
4. `await` lipsă pe `response.json()` — returnezi `Promise<T>`, nu `T`
5. Nu verifici `Content-Type` înainte de `.json()` pe răspuns potențial binar
6. Niciun `AbortController` — nu poți cancela requests la timeout
7. Idempotency key absent pe POST outbound retryable — duplicate la network failure

**Authentication:**
8. API key în URL query param — apare în access logs, server logs, browser history
9. `process.env.API_KEY` fără validare Zod la startup — crash la primul request, nu la boot
10. Token OAuth2 re-fetched la fiecare request (cache in-memory în serverless) — epuizezi rate limit de auth
11. Race condition pe token cache — N instanțe serverless fac N fetches simultane la cache miss
12. HTTP Basic credentials hardcodate — detectate de git-secrets, intră în git history

**Webhooks:**
13. `JSON.parse(await request.json())` înainte de verificare semnătură — pierzi Buffer raw necesar HMAC
14. `===` în loc de `timingSafeEqual` — timing attack posibil
15. Niciun timestamp check — replay attacks cu request-uri capturate
16. Procesare sincronă în handler — timeout la provider (Twilio: 15s, Stripe: 30s)
17. `void fn()` fire-and-forget în serverless (Vercel) — ucis imediat după `return` (folosești `waitUntil`)
18. Fără idempotency check în DB — duplicate la retry automat al provider-ului
19. URL webhook hardcodat ca `http://` în producție — semnătura include protocolul
20. Implementare manuală Twilio signature în loc de SDK — fragilă la query params și proxy
21. Procesare fără event ordering — event vechi suprascrie event nou

**Serverless:**
22. State in-memory (rate limiter, cache, counter) în serverless — stare per-instanță, resetată la cold start
23. `RateLimiter` sau `CircuitBreaker` in-memory în serverless — limita efectivă e `N_instanțe × limita`
24. Inițializare SDK în interiorul handler-ului — reinițializat la fiecare request
25. Ignorare timeout Vercel Hobby (10s) — funcțiile cu retry + backoff depășesc limita

**Rate Limiting & Retry:**
26. Retry pe `4xx` client errors — retry nu rezolvă erori de input (400, 401, 403, 404)
27. Retry pe POST non-idempotent fără Idempotency-Key — duplicate (plăți duble, apeluri duble)
28. Retry fără jitter — thundering herd la erori simultane pe N utilizatori
29. Ignorare `Retry-After` header pe 429 — risc de ban cont

**Caching:**
30. Token cache in-memory în serverless — resetat la cold start
31. Cache pe `Date` objects — serializare pierde timezone (folosești `.toISOString()`)
32. BNR fallback cu rate hardcodate — stale, cauzează calcule financiare greșite în tăcere
33. `getSecondsUntilMidnight()` fără timezone România — cache expiră la ora greșită

**BNR & XML:**
34. `multiplier` ignorat în parsare BNR — CHF, JPY au `multiplier="100"` → rate greșite cu factor 100
35. `z.array(BnrRateSchema)` fără `.transform()` — crash dacă XML are un singur `<Rate>`

**TypeScript:**
36. `any` pe răspuns API — pierzi protecția la compile time
37. `Number(undefined)` pe câmp lipsă — `NaN` în calcule financiare, fără eroare vizibilă
38. Interface definită manual fără comparare cu schema reală — drift garantat

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
- [ ] Idempotency check în DB pentru webhook events

## Resilience & Serverless
- [ ] Timeout setat pe toate fetch()-urile externe
- [ ] Retry DOAR pe 5xx și 429, NU pe 4xx
- [ ] Idempotency-Key pe POST-uri outbound retryable
- [ ] waitUntil() în loc de void fire-and-forget (Vercel)
- [ ] Niciun state in-memory pentru distributed operations (Redis în schimb)
- [ ] Circuit breaker configurat pentru API-uri critice (BNR, Twilio)

## BNR Specific
- [ ] multiplier aplicat la parsare (rateToRON = value / multiplier)
- [ ] XML array transform în schema Zod
- [ ] Fallback din DB, nu constante hardcodate
- [ ] Cache expiră la ora 14:00 ora României (nu UTC midnight)

## Twilio IVR
- [ ] Numere normalizate la format E.164 (+407XX)
- [ ] Content-Type: text/xml pe toate răspunsurile TwiML
- [ ] language="ro-RO" pe toate <Say>
- [ ] StatusCallback URL setat la /api/webhooks/twilio/status
- [ ] SDK Twilio pentru signature verification (nu implementare manuală)
- [ ] Event ordering protejat cu last_event_at + .lt() check

## Testare
- [ ] Webhook-urile testate cu ngrok local
- [ ] Semnătură invalidă → 401
- [ ] Timestamp expirat → 400
- [ ] Duplicate event → 200 fără re-procesare
- [ ] BNR fallback testat cu URL incorect → date din DB
- [ ] waitUntil verificat că rulează după return
```

---

*Ghid API Integration & Webhooks v2.0 — Mai 2026*
*Proiecte de referință: Clinică Medicală (Twilio IVR) · ERP Financiar (BNR + Stripe) · Vibe Budget · orice proiect cu integrări externe*
