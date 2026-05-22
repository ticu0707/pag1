---
description: Audit API Integration & Webhooks — verifică 21 reguli critice (securitate chei API, resilience fetch, HMAC webhooks, SSE streaming, GDPR logging). Raportează BLOCKER / ATENȚIE / OK fără a modifica codul. Bazat pe ghid-api-webhooks-v3.md.
---

# /api-audit — Audit API Integration & Webhooks

**Scopul:** Analizează fișierele unui proiect pentru greșeli critice în integrări API și webhooks. Raportează BLOCKER / ATENȚIE / OK per regulă. Bazat pe ghid-api-webhooks-v3.md.

---

## PASUL 1 — Identifică directorul

**Dacă $ARGUMENTS conține o cale** (ex: `/api-audit Desktop/clinica-medicala`):
Lucrează în: `C:\Users\admin\$ARGUMENTS`

**Dacă $ARGUMENTS este gol:**
Întreabă utilizatorul: `Pe care proiect rulăm api-auditul? (ex: Desktop/clinica-medicala)`
Sau dacă există context clar din sesiune, folosește directorul curent.

---

## PASUL 2 — Detectează tipul de proiect și găsește fișierele relevante

Rulează în paralel cu Glob:
- `next.config.ts` sau `next.config.js` (rădăcina) → prezență = Next.js
- `**/*.ts` și `**/*.tsx` (exclude node_modules, .next, dist, .git)
- `**/*.html` și `**/*.js` (exclude node_modules, dist) → prezență exclusivă = HTML Vanilla
- `package.json` (rădăcina)
- `.env.local` sau `.env` (rădăcina)

Rulează în paralel cu Grep pentru detectarea integrărilor prezente:
- `fetch(` în fișierele TS/TSX/JS → **fetch prezent** (activează Categoria B)
- `webhook` (case-insensitive) în căi de fișiere sau conținut → **webhooks prezente** (activează Categoria C)
- `getReader()` sau `ReadableStream` sau `text/event-stream` → **SSE/streaming prezent** (activează Categoria D)
- `console\.log\(` în fișiere din `app/api/`, `actions/`, `lib/` → **logging server prezent** (activează Categoria E)

**Tip proiect detectat:**
- `next.config.*` prezent → **Next.js**
- Doar `.html` / `.js` fără `next.config.*` → **HTML Vanilla**
- Ambele → **Mix**

Dacă nu găsești niciun fișier TS/TSX și niciun HTML: raportează `EROARE: director gol sau cale greșită` și oprește.

Notează: Tip: [Next.js / HTML Vanilla / Mix] + [N] TS/TSX + [M] HTML/JS + fetch: [DA/NU] + webhooks: [DA/NU] + SSE: [DA/NU] + .env.local: [DA/NU]

---

## PASUL 3 — Rulează verificările pe 5 categorii

### CATEGORIA A — SECURITATE API KEYS (ÎNTOTDEAUNA)

**A1 — Chei API hardcodate în cod (nu în fișiere .env)**
Grep pentru pattern-uri de chei API reale în fișierele `.ts`, `.tsx`, `.js`, `.html` (exclude `.env*`, `*.md`, `*.test.*`):
- `sk_live_` sau `SK_LIVE` (Stripe live secret)
- `whsec_` (Stripe webhook secret)
- `sk-ant-` (Anthropic API key)
- `sk-proj-` (OpenAI API key)
- `(?:TOKEN|SECRET|KEY|WEBHOOK_SECRET)\s*=\s*["'][A-Za-z0-9_\-]{20,}["']` în fișiere non-.env (variabilă cu valoare hardcodată lungă)

- Oricare pattern găsit în fișier non-.env → **BLOCKER** (secret hardcodat în cod = în git forever; rotire imposibilă fără commit nou; `git log` expune cheia chiar după ștergere. Fix: mută valoarea în `.env.local` și accesează via `process.env.VARIABLE_NAME` — niciodată string literal în cod)
- Absent → **OK**

**A2 — NEXT_PUBLIC_ pe variabile secrete**
Grep pentru `NEXT_PUBLIC_` în fișierele `.env*`, `.ts`, `.tsx` (exclude `.env.example`, `*.md`).
Caută `NEXT_PUBLIC_` urmat de cuvinte sensibile: `SECRET`, `PRIVATE`, `SERVICE_ROLE`, `AUTH_TOKEN`, `WEBHOOK`, `TWILIO_AUTH`, `STRIPE_SECRET`, `ANTHROPIC`, `OPENAI_API`, `API_KEY`.
Pattern: `NEXT_PUBLIC_.*(?:SECRET|PRIVATE|SERVICE_ROLE|AUTH_TOKEN|WEBHOOK|TWILIO_AUTH|STRIPE_SECRET|ANTHROPIC|OPENAI_API|API_KEY)`
- Găsit → **BLOCKER** (prefix `NEXT_PUBLIC_` include variabila în bundle-ul JavaScript livrat browser-ului — secretul devine public, vizibil în `View Page Source`. Fix: elimină prefixul `NEXT_PUBLIC_`; variabilele secrete se accesează exclusiv server-side, niciodată în componente client sau în `window`)
- Absent sau HTML Vanilla (unde nu e relevant) → **OK** / `— (nu se aplică HTML Vanilla)`

**A3 — Env vars validate cu Zod la startup**
Glob pentru `**/env.ts`, `**/env.js`, `**/config/env.ts`, `**/lib/env.ts`.
Grep pentru `z.string()` sau `z.object({` sau `envSchema` în aceste fișiere.
Dacă nu există validare centralizată, numără accesările `process.env.` pentru variabile externe:
Grep pentru `process\.env\.(?:TWILIO|STRIPE|ANTHROPIC|OPENAI|WEBHOOK|BNR|SENDGRID|MAILGUN)` în fișierele TS/TSX.
- Zero fișier de validare Zod ȘI mai mult de 3 accesări directe ale env-urilor externe → **ATENȚIE** (variabilă `.env` lipsă sau greșită = `undefined` silențios la runtime; aplicația cade cu eroare criptică în producție, nu la startup. Fix: creează `lib/env.ts` cu schema Zod — `z.string().min(1)` pe fiecare variabilă externă — și importă din el peste tot)
- Validare Zod prezentă sau accesări puține → **OK**

**A4 — `unknown` nu `any` pe răspunsuri API externe**
Grep pentru `as any` sau `\): any` sau `: any =` în fișierele `.ts`, `.tsx` care conțin și `.json()` sau `response\.data`.
- Pattern găsit în fișier cu apeluri API → **ATENȚIE** (pierdere completă a protecției TypeScript pe date externe; `response.data.nonExistentField` compilează fără eroare, cade în producție. Fix: înlocuiește cu `unknown` și parsează cu Zod: `const result = ApiResponseSchema.parse(await response.json())`)
- Absent → **OK**

**A5 — Zod validation pe răspuns API extern (nu tipizare manuală)**
Grep pentru `z\.object\(` sau `z\.array\(` sau `\.safeParse\(` sau `\.parse\(` în fișierele care conțin `fetch(` și `.json()`.
- Fișiere cu `fetch(` + `.json()` dar zero schemă Zod în întregul proiect → **ATENȚIE** (interface TypeScript manuală fără validare runtime = crash neașteptat când API extern schimbă structura răspunsului. Fix: adaugă `ResponseSchema = z.object({...})` și înlocuiește `response.json() as MyType` cu `ResponseSchema.parse(await response.json())`)
- Zod prezent sau proiect fără apeluri API externe → **OK**

---

### CATEGORIA B — RESILIENCE FETCH() (dacă fetch detectat)

*Se aplică dacă există `fetch(` în fișiere TS/TSX/JS.*
*Dacă absent: marchează toată categoria cu `— (fetch() negăsit în proiect)`*

**B1 — AbortController pe fetch() extern**
Grep pentru `fetch(` în fișierele `.ts`, `.tsx` din `app/`, `lib/`, `utils/`, `actions/` (exclude `node_modules`, `.next`, fișiere de test).
Pentru fiecare fișier cu `fetch(`, verifică prezența `AbortController` sau `signal:` sau `AbortSignal\.timeout\(` în același fișier.
- Fișier cu `fetch(` spre URL extern (`http` sau `https` sau `process.env`) fără `signal:` sau `AbortController` → **BLOCKER** (fetch fără timeout nu se termină niciodată dacă API-ul extern nu răspunde; funcția serverless consumă tot timpul alocat și expiră cu eroare opacă; alte requests sunt blocate. Fix: `const controller = new AbortController(); setTimeout(() => controller.abort(), 10_000); const response = await fetch(url, { signal: controller.signal })` — sau mai simplu: `fetch(url, { signal: AbortSignal.timeout(10_000) })`)
- `signal:` sau `AbortSignal.timeout(` prezent → **OK**

**B2 — Retry exclusiv pe 5xx și 429, NU pe 4xx**
Grep pentru logică de retry în fișierele cu `fetch(`: cuvinte cheie `retry`, `retryFetch`, `fetchWithRetry`, `attempt`, plus pattern `while.*attempt` sau `for.*retry`.
Dacă logică de retry detectată, citește condițiile de trigger:
- Condiție `status >= 400` sau `status < 500` sau `statusCode >= 400` ca trigger pentru retry → **BLOCKER** (retry pe 4xx e inutil și periculos: 401 rămâne 401 la oricâte retry-uri; 403 rămâne 403; risc de ban automat de cont la provider dacă trimiți sute de request-uri invalide. Fix: `if (status >= 400 && status < 500 && status !== 429) throw new NonRetryableError(...)` — retry DOAR pe `>= 500` și `=== 429`)
- Retry condiționat corect pe 5xx/429 sau fără logică de retry → **OK**

**B3 — Idempotency-Key pe POST-uri retryable**
Grep pentru `method:\s*['"]POST['"]` sau `method:\s*["']POST["']` în fișierele cu logică de retry.
Dacă POST în context cu retry, verifică prezența `Idempotency-Key` sau `idempotency-key` sau `idempotencyKey` în headers ale aceluiași request.
- `method: 'POST'` cu retry logic fără `Idempotency-Key` header → **ATENȚIE** (POST retried fără idempotency key = operație dublă: plată dublă Stripe, apel Twilio dublu, email duplicat. Fix: `headers: { 'Idempotency-Key': idempotencyKey }` unde `idempotencyKey` e generat O SINGURĂ DATĂ înainte de prima încercare și reutilizat la retry)
- `Idempotency-Key` prezent sau POST fără retry → **OK**

**B4 — Fără state in-memory pentru operații distribuite în serverless**
Grep pentru variabile la nivel de modul în fișiere route handler (`app/api/**/*.ts`, `pages/api/**/*.ts`):
- `^let ` sau `^const .* = new Map\(` sau `^const .* = new Set\(` sau `^let counter` sau `^let cache` la nivel de top-level (nu în funcții)
Grep separat pentru `class RateLimiter` sau `class CircuitBreaker` definite local (nu importate din `@upstash` sau `ioredis`).
- State in-memory definit la nivel de modul în route handler → **BLOCKER** (serverless: fiecare instanță are propriul state izolat; rate limiter in-memory permite `N_instanțe × limita` request-uri; la cold start, counter-ul e resetat la 0 — protecție iluzorie. Fix: mută state-ul distribuit în Redis/Upstash: `@upstash/redis` pentru token cache, `@upstash/ratelimit` pentru rate limiting, circuit breaker cu chei Redis)
- Fără state in-memory în route handlers sau state importat din Redis/Upstash → **OK**

---

### CATEGORIA C — WEBHOOKS (dacă webhook handlers detectate)

*Se aplică dacă există fișiere cu `webhook` în cale (glob: `**/webhook*`) sau grep pentru `createHmac` ori `validateRequest` ori `constructEvent` în TS/TSX.*
*Dacă absent: marchează toată categoria cu `— (Webhook handlers negăsiți în proiect)`*

**Notă SDK**: dacă `twilio.validateRequest(` sau `stripe.webhooks.constructEvent(` detectat, C1 și C2 sunt automat **OK** — SDK-ul gestionează rawBody și comparare.

**C1 — rawBody citit ÎNAINTE de verificarea semnăturii**
Glob pentru `**/webhook*/route.ts`, `**/webhooks*/route.ts`.
Citește fișierele găsite și verifică ordinea operațiunilor:
- `request\.json()` sau `req\.json()` sau `request\.text()` folosit ÎNAINTE de `createHmac` sau signature check, fără salvare prealabilă a body-ului raw → **BLOCKER** (`.json()` consumă stream-ul ReadableStream al body-ului — nu poate fi citit a doua oară; HMAC calculat pe bytes raw va eșua întotdeauna dacă body-ul e deja consumat. Fix: `const rawBody = await request.text()` SAU `Buffer.from(await request.arrayBuffer())` ca PRIMA operație din handler, APOI `JSON.parse(rawBody)`)
- `rawBody` sau `arrayBuffer()` citit primul; sau SDK utilizat → **OK**

**C2 — timingSafeEqual la comparare semnătură**
Grep pentru `createHmac` sau `createHash` în fișierele webhook.
Dacă hash manual detectat, verifică prezența `timingSafeEqual` sau `crypto\.timingSafeEqual` în același fișier.
- `createHmac` sau `createHash` prezent fără `timingSafeEqual` → **BLOCKER** (comparare cu `===` e vulnerabilă la timing attacks: atacatorul măsoară microsecunde de diferență în răspuns și ghicește HMAC-ul byte-cu-byte. Fix: `crypto.timingSafeEqual(Buffer.from(receivedSig, 'hex'), Buffer.from(expectedSig, 'hex'))` — timp constant indiferent de câți bytes coincid)
- `timingSafeEqual` prezent sau SDK utilizat → **OK**

**C3 — Timestamp validation (prevenire replay attacks)**
Grep pentru `Date\.now()` sau `Math\.abs(` sau verificare `timestamp` în fișierele webhook handlers.
Verifică dacă există o condiție care limitează vârsta request-ului (ex: `> 300`, `> 5 * 60`, `300_000`).
- Webhook handler fără nicio validare de timestamp lângă verificarea semnăturii → **BLOCKER** (request capturat poate fi re-trimis oricând în viitor — atacatorul replays plăți confirmate, apeluri Twilio, sau comenzi deja procesate. Fix: `const age = Math.abs(Date.now() / 1000 - Number(webhookTimestamp)); if (age > 300) return new Response('Replay detected', { status: 400 })`)
- Timestamp check prezent sau SDK utilizat → **OK**

**C4 — waitUntil() în loc de void fire-and-forget**
Grep pentru `void ` (cu spațiu sau paranteză) în route handlers (`app/api/**/*.ts`, `pages/api/**/*.ts`).
Verifică contextul: `void someAsyncFunction(` sau `void process` sau `void handle` (nu `void 0` sau comentarii).
- `void asyncFn()` găsit în route handler → **BLOCKER** (Vercel/serverless termină procesul imediat după `return Response(...)`; procesarea async cu `void` e oprită la jumătate — date scrise parțial în DB, emailuri netrimise, log-uri corupte. Fix: `import { waitUntil } from '@vercel/functions'; waitUntil(processAsync(data))` înaintea `return` — sau procesează complet sincron înainte de return)
- `waitUntil(` utilizat sau procesare completă înainte de return → **OK**

**C5 — Promise.allSettled în fan-out (nu Promise.all)**
Grep pentru `Promise\.all\(` în fișierele webhook handlers sau event routers.
Verifică contextul: `Promise.all([handler1(event)`, `Promise.all(handlers.map(h => h(event)` sau array de funcții apelate cu același eveniment.
- `Promise.all(` cu array de handler calls → **BLOCKER** (un singur handler care aruncă eroare anulează toate celelalte via rejection; evenimentul e marcat ca eșuat deși 9 din 10 handlere au reușit — provider-ul re-trimite și tot ciclul se repetă. Fix: înlocuiește cu `Promise.allSettled(` și loghează separat `results.filter(r => r.status === 'rejected')`)
- `Promise.allSettled(` utilizat sau un singur handler → **OK**

**C6 — Idempotency în DB pentru webhook events**
Grep pentru `webhook_events` sau `processed_events` sau `event_id` în fișierele TS/TSX sau SQL.
Dacă tabel/câmp de idempotency detectat, verifică pattern-ul de verificare:
- `SELECT` + `INSERT` (SELECT înainte de INSERT pentru verificare duplicat) → **ATENȚIE** (round-trip inutil + race condition dacă provider-ul trimite aceeași livrare în paralel — ambele SELECT văd lipsa, ambele INSERT → eroare sau duplicat. Fix: elimină SELECT; folosește direct `INSERT ... ON CONFLICT DO NOTHING` sau catch pe `error?.code === '23505'`)
- Fără niciun mecanism de idempotency și webhook handler cu side effects → **ATENȚIE** (retry automat al provider-ului va duplica procesarea. Fix: adaugă coloana `UNIQUE(event_id)` pe tabelul de events și INSERT + 23505 catch)
- `INSERT` cu `23505` catch sau `ON CONFLICT` → **OK**

---

### CATEGORIA D — STREAMING SSE (dacă ReadableStream/SSE detectat)

*Se aplică dacă există `getReader()` sau `ReadableStream` sau `text/event-stream` în fișiere.*
*Dacă absent: marchează toată categoria cu `— (SSE/Streaming negăsit în proiect)`*

**D1 — reader.releaseLock() în finally**
Grep pentru `getReader()` sau `\.getReader()` în fișierele `.ts`, `.tsx`, `.js`.
Pentru fiecare apariție, citește funcția înconjurătoare și verifică dacă `releaseLock()` apare într-un bloc `finally`.
- `getReader()` fără `releaseLock()` în `finally` → **BLOCKER** (la orice eroare din bucla de citire, reader-ul rămâne locked; orice apel ulterior pe același stream aruncă `TypeError: ReadableStreamDefaultReader: stream is already locked` permanent. Fix: `const reader = stream.getReader(); try { /* citire */ } finally { reader.releaseLock() }` — `finally` garantează cleanup chiar la eroare)
- `releaseLock()` în `finally` prezent → **OK**

**D2 — Buffer acumulativ pe SSE (nu split simplu pe '\n')**
Grep pentru `\.split\(['"]\\n['"]` sau `\.split\(['"]\\n\\n['"]` în fișierele cu `ReadableStream` sau `getReader()`.
Verifică contextul: split aplicat direct pe `chunk` sau `decoded` (nu pe buffer acumulat).
- `.split('\n')` aplicat direct pe chunk-ul decodat fără buffer prealabil → **BLOCKER** (chunk-urile ReadableStream nu coincid cu granițele evenimentelor SSE; un eveniment pe 3 linii poate fi tăiat la jumătate între două chunk-uri — parsare coruptă, JSON invalid la `JSON.parse()`. Fix: `buffer += decoder.decode(value, { stream: true }); const lines = buffer.split('\n'); buffer = lines.pop() ?? ''` — ultimul element incomplet rămâne în buffer)
- Buffer acumulativ (`buffer +=`) sau bibliotecă SSE dedicată → **OK**

**D3 — EventSource nativ cu headers de autentificare**
Grep pentru `new EventSource\(` în fișierele `.ts`, `.tsx`, `.js`, `.html`.
Dacă găsit, verifică în proximity: referințe la `Authorization`, `Bearer`, `token`, `apiKey`, `headers`.
- `new EventSource(` în context unde auth e necesară (URL cu token în query sau comentariu cu header auth) → **ATENȚIE** (API nativ `EventSource` nu suportă custom headers; `withCredentials: true` funcționează doar pentru cookie-uri, nu pentru Bearer tokens — autentificarea eșuează silențios sau tokenul ajunge în URL (log-uri, history). Fix: înlocuiește cu `fetch(url, { headers: { Authorization: \`Bearer ${token}\` } })` + `ReadableStream` pentru citire SSE manuală)
- `EventSource` fără auth sau auth exclusiv via cookie → **OK**

---

### CATEGORIA E — LOGGING & GDPR (dacă console.log server-side detectat)

*Se aplică dacă există `console\.log\(` în fișiere din `app/api/`, `actions/`, `lib/` (server-side).*
*Dacă absent: marchează toată categoria cu `— (console.log server-side negăsit)`*

**E1 — PII redactat din log-uri**
Grep pentru `console\.log\(` în fișierele server-side (`app/api/`, `actions/`, `lib/`, `utils/`).
Verifică dacă în proximity (același bloc de cod) apar variabile sau proprietăți cu potențial PII: `phone`, `email`, `body`, `payload`, `request`, `user`, `customer`, `cnp`, `card`, `iban`, `address`.
Verifică separat prezența unei funcții `redactPII` sau `sanitize` sau `maskPII` în același fișier sau importată.
- `console.log(` cu variabile PII-adjacent fără funcție de redactare → **ATENȚIE** (telefoane, emailuri, CNP-uri loggate = GDPR breach automat; log-urile sunt adesea stocate necriptat și accesate de echipe multiple. Fix: `function redactPII(s: string) { return s.replace(/\+?[0-9]{10,15}/g, '[PHONE]').replace(/[\w._%+-]+@[\w.-]+\.[a-zA-Z]{2,}/g, '[EMAIL]') }` aplicat pe orice string logat)
- `redactPII` aplicat sau `console.log` fără variabile PII → **OK**

**E2 — Webhook body complet absent din log-uri**
Grep pentru `console\.log\(` cu `body` sau `payload` sau `event` sau `webhookData` în fișierele webhook handlers.
Verifică contextul: `console.log(body)` sau `console.log('Received:', event)` sau `console.log(JSON.stringify(payload))` fără selecție de câmpuri.
- Body complet logat în webhook handler fără redactare sau selecție de câmpuri → **ATENȚIE** (webhook body Stripe/Twilio conține date sensibile: email client, detalii plată, numere de telefon, adrese. Fix: loghează doar câmpuri non-sensibile: `console.log({ type: event.type, id: event.id, created: event.created })` — niciodată body-ul complet)
- Logat selectiv (tip + id) sau absent → **OK**

**E3 — Correlation ID propagat în operații async**
Grep pentru `X-Correlation-ID` sau `correlationId` sau `x-request-id` sau `requestId` în fișierele server-side.
Verifică dacă ID-ul e generat la intrarea request-ului și inclus în log-uri și headers outbound.
- Proiect cu multiple apeluri API/webhook fără niciun mecanism de correlation ID → **ATENȚIE** (fără ID comun, un log de eroare din adâncul stack-ului nu poate fi corelat cu request-ul original în Vercel/Datadog/Sentry — debugging în producție devine investigație CSI. Fix: `const correlationId = request.headers.get('X-Correlation-ID') ?? crypto.randomUUID()` la intrare; include în toate `console.log`-urile și în headers outbound: `'X-Correlation-ID': correlationId`)
- Correlation ID prezent sau proiect simplu cu un singur serviciu extern → **OK**

---

## PASUL 4 — Raportează în formatul exact de mai jos

```
=== API-AUDIT: [director / proiect] ===
Tip proiect: [Next.js / HTML Vanilla / Mix]
Fișiere analizate: [N] TS/TSX + [M] HTML/JS + fetch: [DA/NU] + webhooks: [DA/NU] + SSE: [DA/NU] + .env.local: [DA/NU]

── A. SECURITATE API KEYS ───────────────────────
  [✓/✗]   A1 Chei API nu hardcodate în cod        [status + fișier:linie dacă BLOCKER]
  [✓/✗]   A2 NEXT_PUBLIC_ nu pe secrete           [status + variabilă afectată dacă BLOCKER]
  [✓/!]   A3 Env vars validate cu Zod startup     [status + nr. accesări neprotejate dacă ATENȚIE]
  [✓/!]   A4 unknown nu any pe răspuns API        [status + fișier dacă ATENȚIE]
  [✓/!]   A5 Zod schema pe răspuns API extern     [status]

── B. RESILIENCE FETCH() ────────────────────────
  [✓/✗]   B1 AbortController pe fetch extern      [status + fișier:linie dacă BLOCKER]
  [✓/✗]   B2 Retry exclusiv pe 5xx + 429          [status + condiția greșită dacă BLOCKER]
  [✓/!]   B3 Idempotency-Key pe POST retryable    [status + fișier dacă ATENȚIE]
  [✓/✗]   B4 Fără state in-memory în serverless   [status + ce variabilă + fișier dacă BLOCKER]
  (sau: — fetch() negăsit în proiect)

── C. WEBHOOKS ──────────────────────────────────
  [✓/✗]   C1 rawBody înainte de HMAC              [status + fișier:linie dacă BLOCKER]
  [✓/✗]   C2 timingSafeEqual la semnătură         [status + fișier dacă BLOCKER]
  [✓/✗]   C3 Timestamp validation (max 5 min)     [status + fișier dacă BLOCKER]
  [✓/✗]   C4 waitUntil() nu void fire-and-forget  [status + fișier:linie dacă BLOCKER]
  [✓/✗]   C5 Promise.allSettled în fan-out        [status + fișier:linie dacă BLOCKER]
  [✓/!]   C6 Idempotency DB (INSERT + 23505)      [status + pattern găsit dacă ATENȚIE]
  (sau: — Webhook handlers negăsiți în proiect)

── D. STREAMING SSE ─────────────────────────────
  [✓/✗]   D1 reader.releaseLock() în finally      [status + fișier:linie dacă BLOCKER]
  [✓/✗]   D2 Buffer acumulativ SSE (nu split \n)  [status + fișier:linie dacă BLOCKER]
  [✓/!]   D3 EventSource fără custom headers      [status + fișier dacă ATENȚIE]
  (sau: — SSE/Streaming negăsit în proiect)

── E. LOGGING & GDPR ────────────────────────────
  [✓/!]   E1 PII redactat din log-uri             [status + variabile afectate + fișier dacă ATENȚIE]
  [✓/!]   E2 Webhook body absent din log-uri      [status + fișier:linie dacă ATENȚIE]
  [✓/!]   E3 Correlation ID propagat              [status]
  (sau: — console.log server-side negăsit)

══════════════════════════════════════════════════
BLOCKER-e: [N]  |  ATENȚIE: [M]  |  OK: [K]

VERDICT: [BLOCKER ✗ / ATENȚIE ⚠ / CLEAN ✓]

Fix-uri necesare (BLOCKER-e în ordinea impactului):
  1. [A1/A2/C2/...] descriere exactă + codul de adăugat/modificat
  2. ...

Verificări manuale necesare (nu detectabile static):
  - Rate limit headers proactive (X-RateLimit-Remaining) → loghezi warning când Remaining < 10% din limită
  - Circuit breaker TTL aliniat cu config.resetMs → `failuresTtlSeconds = Math.ceil(config.resetMs / 1000)`
  - BNR multiplier aplicat corect → `rateToRON = parseFloat(value) / (multiplier ?? 1)` (CHF, JPY: multiplier=100)
  - ETag/If-None-Match salvat împreună cu datele pentru conditional GET pe API-uri cu polling frecvent
  - Dead letter queue configurat în DB pentru webhook events eșuate (retention min. 3 zile)
  - TypeScript types generate din OpenAPI spec → `npx openapi-typescript spec.json -o src/types/api.d.ts`
  - MSW configurat în test suite (`msw/node`) pentru teste fără API real
```

---

## Reguli de verdict

| Condiție | Verdict |
|---|---|
| Cel puțin un BLOCKER | **BLOCKER ✗** — listezi fix-ul complet pentru fiecare |
| Zero BLOCKER-e, cel puțin un ATENȚIE | **ATENȚIE ⚠** — informezi, utilizatorul decide |
| Toate OK sau INFO | **CLEAN ✓** |

---

## Note de execuție

- **Nu modifica niciun fișier** — doar raportezi; utilizatorul decide ce și când fixează
- **Specifică întotdeauna fișier + linie** pentru BLOCKER și ATENȚIE — nu raporta vag
- **Ordinea fix-urilor la BLOCKER**: A1 (hardcodat) > A2 (NEXT_PUBLIC_) > C2 (timingSafeEqual) > C1 (rawBody) > C3 (timestamp) > C4 (void/waitUntil) > B1 (AbortController) > B2 (retry 4xx) > B4 (state in-memory) > C5 (allSettled) > D1 (releaseLock) > D2 (SSE buffer) — securitate înainte de resilience
- **Categorii inactive**: dacă `fetch()` absent → B marchează `—`; webhooks absente → C marchează `—`; SSE absent → D marchează `—`; logging absent → E marchează `—` — nu e eroare, e informație despre structura proiectului
- **SDK providers**: dacă `twilio.validateRequest(` sau `stripe.webhooks.constructEvent(` detectat → C1 și C2 sunt automat **OK** (SDK-ul gestionează rawBody și comparare constant-time)
- **HTML Vanilla**: A1 și A3 se aplică în fișierele `.js`; A2 marchează `— (nu se aplică HTML Vanilla)`; B, C, D, E se aplică dacă pattern-urile relevante există; pentru E3 e mai puțin relevant dacă e aplicație single-page
- **Proiecte fără webhooks și fără SSE**: C și D marchează `—` — e normal pentru proiecte cu API integration unidirecțională (doar fetch outbound)
- **Fals pozitive A4**: `as any` în fișiere de tip `.d.ts` sau în biblioteci externe — ignoră, verifică doar în fișierele proiectului
