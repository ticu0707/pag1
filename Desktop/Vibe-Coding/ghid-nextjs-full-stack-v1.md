# GHID PRACTIC: Next.js Full-Stack Development pentru Vibe-Coding
**Skill 6 — v2.0 · Ediție Expert**
**Data:** Mai 2026 | **Nivel:** Intermediate → Expert
**Timp realist:** 90 min citit + practică pe proiectele tale

---

## TL;DR — 3 Lucruri Care Schimbă Totul

1. **Tot ce nu scrie `'use client'` rulează pe server.** App Router inversează logica față de Pages Router — codul tău e server by default. Client Components sunt excepții, nu regula. Un `'use client'` pe `page.tsx` pentru un singur buton interactiv îți șterge toate beneficiile RSC.

2. **`getUser()` pe server, nu `getSession()`.** `getSession()` citește cookie-ul local fără verificare cu serverul Supabase — un atacator poate manipula cookie-ul și trece de orice `if (session)`. `getUser()` validează JWT-ul cu serverul la fiecare request. Nu există excepție.

3. **`import 'server-only'`** în orice fișier cu chei secrete sau logică server-only. Un import accidental în Client Component = `SERVICE_ROLE_KEY` în bundle JS, vizibil în DevTools de oricine. Linia asta provoacă eroare de build înainte să fie problema.

---

## Cum Să Folosești Ghidul

**Prima dată:** Citește liniar Bloc 1 + Bloc 2 (~30 min). Server vs Client e decizia cu cel mai mare impact — înțelege-o înainte de orice alt concept.

**Proiect nou:** Începe cu Parte 7 (Supabase SSR setup) + Parte 6 (Middleware) + Parte 14 (structura de proiect) — cele 3 fundații care trebuie puse corect de la start.

**Ceva nu funcționează:** Salt la Parte 12 (greșeli comune) — acoperă 90% din ce se strică în App Router.

**Referință rapidă:** Parte 17 (Quick Reference Card) — deschide în orice sesiune.

**Dacă lucrezi pe proiecte financiare** (ERP, FinanceOS): prioritizează Parte 3 (Server Actions + validare + useOptimistic) și Parte 9 (Caching + revalidare).

**Dashboard-uri complexe** (StudioFlow, Clinică): citește Parte 11 (Streaming + Parallel Routes + Intercepting Routes + next/dynamic).

---

## Learning Map

```
BLOC 1 — APP ROUTER: ARHITECTURA NOUĂ                    [TOATE proiectele]
  [0]  RSC Mental Model — cum gândești diferit față de Pages Router
  [1]  Server vs Client Components — regula de aur + Context Providers   ★★
  [2]  File Conventions — layout, loading, error, generateStaticParams, Route Groups

BLOC 2 — DATE ȘI ACȚIUNI
  [3]  Server Actions — formulare, bind(), useOptimistic, useTransition, Zod   ★
  [4]  Route Handlers — REST, webhooks, CORS, când NU să le folosești
  [5]  Data Fetching — parallel, React.cache(), nuqs, use(), unstable_cache     ★

BLOC 3 — SECURITATE
  [6]  Middleware — auth, rate limiting, matchers, edge limitations              ★
  [7]  Supabase SSR — server-only, createServerClient, getUser()                 ★★
  [8]  Variabile de mediu — NEXT_PUBLIC_, server-only, validare la startup

BLOC 4 — PERFORMANȚĂ
  [9]  Caching — 4 nivele, Router Cache, React.cache(), revalidare, use cache    ★
  [10] next/image (sizes, blur), next/font, next/script
  [11] Streaming, Suspense, Intercepting Routes, next/dynamic, Parallel Routes

BLOC 5 — DEBUGGING ȘI TOOLKIT
  [12] 18 Greșeli Comune App Router (before/after)
  [13] TypeScript — PageProps, Next.js 15, Server Actions types, Zod, use()
  [14] Structura de proiect — folder organization, naming conventions
  [15] Checklist Pre-Deploy
  [16] Deployment Vercel — CSP, security headers, env vars, Sentry
  [17] Quick Reference Card
```

`★` = Citit obligatoriu înainte de primul proiect Next.js + Supabase
`★★` = Cel mai mare risc — greșelile de aici sunt silențioase și greu de depanat

---

## BLOC 1 — App Router: Arhitectura Nouă

---

### Parte 0 — RSC Mental Model

**Ce s-a schimbat față de Pages Router:**

```
Pages Router:  tot codul poate rula pe client
               → getServerSideProps pentru excepțiile server
               → componente = implicit client

App Router:    tot codul rulează pe server implicit
               → 'use client' pentru excepțiile client
               → componente = implicit Server Components (RSC)
```

**Ce înseamnă concret un React Server Component (RSC):**
- Rulează exclusiv pe server — zero JS trimis în browser pentru această componentă
- Are acces direct la DB, sistem de fișiere, variabile de mediu secrete
- Nu poate folosi `useState`, `useEffect`, event handlers, browser APIs
- Rezultatul = HTML + RSC payload (structura arborelui, nu JS executabil)

**Ciclul unui request:**
```
Browser → cere /dashboard
  → Next.js rulează Server Components pe server
  → Generează HTML pentru First Contentful Paint imediat
  → Trimite RSC payload la client
  → Client hydratează NUMAI Client Components
  → Navigare ulterioară = fetch RSC payload + patch DOM (fără full reload)
```

**Navigare internă — API complet:**

```tsx
import Link from 'next/link'
import { useRouter, usePathname, useSearchParams } from 'next/navigation'
// ✓ Din 'next/navigation' — App Router
// ✗ NU din 'next/router' — acela e Pages Router (greșeală frecventă la migrare)

// Link — SPA navigation, prefetch automat, fără full reload
<Link href="/dashboard/invoices">Facturi</Link>
<Link href={`/invoices/${id}`} className="text-blue-600">Deschide</Link>
<Link href="/dashboard" prefetch={false}>Dashboard</Link>

// ✗ <a href> pentru rute interne = full page reload, pierde state client
<a href="/dashboard">Dashboard</a>  // ← nu face asta niciodată intern

// useRouter — navigare programatică din Client Components
'use client'
const router = useRouter()
router.push('/dashboard')           // navighezi programatic
router.replace('/login')            // fără history entry
router.back()                       // back în history
router.refresh()                    // re-fetch RSC payload, actualizează date server
                                    // NU invalidează Data Cache — pentru asta: revalidatePath()

// usePathname — ruta curentă (util pentru active nav links)
const pathname = usePathname()      // '/dashboard/invoices'

// redirect() — din Server Components, Server Actions, Route Handlers
import { redirect } from 'next/navigation'
redirect('/login')                  // 307 temporary
redirect('/login', 'replace')       // 307 + înlocuiește history

// notFound() — activează not-found.tsx cel mai apropiat
import { notFound } from 'next/navigation'
notFound()
```

---

### Parte 1 — Server vs Client Components

**Regula de decizie:**

```
Ai nevoie de:                        → Alegi:
─────────────────────────────────────────────────
useState, useReducer                 → 'use client'
useEffect, useCallback, useMemo      → 'use client'
Event handlers (onClick, onChange)   → 'use client'
Browser APIs (localStorage, window)  → 'use client'
Lib third-party client-only          → 'use client'
─────────────────────────────────────────────────
Orice altceva                        → Server Component (default)
Fetch din DB                         → Server Component
Variabile env secrete                → Server Component
Componente statice, layout           → Server Component
```

**Anti-pattern #1 — `'use client'` pe toată pagina:**

```tsx
// ✗ GREȘIT: toată pagina devine Client Component pentru un singur buton
'use client'
export default function InvoicesPage() {
  const [showModal, setShowModal] = useState(false)
  return (
    <>
      <InvoiceTable invoices={[]} />     {/* forțat la client */}
      <CreateModal open={showModal} />   {/* forțat la client */}
      <button onClick={() => setShowModal(true)}>Crează</button>
    </>
  )
}

// ✓ CORECT: izolezi exact ce e interactiv
export default async function InvoicesPage() {
  const invoices = await getInvoices()  // pe server, direct
  return (
    <>
      <InvoiceTable invoices={invoices} />  {/* Server Component */}
      <CreateInvoiceButton />              {/* Client Component izolat */}
    </>
  )
}

// components/CreateInvoiceButton.tsx
'use client'
export function CreateInvoiceButton() {
  const [open, setOpen] = useState(false)
  return (
    <>
      <button onClick={() => setOpen(true)}>Crează factură</button>
      {open && <CreateInvoiceModal onClose={() => setOpen(false)} />}
    </>
  )
}
```

**Composition pattern — Server Component ca `children` al unui Client Component:**

```tsx
// ClientWrapper.tsx — Client Component wrapper
'use client'
export function CollapsiblePanel({ children }: { children: React.ReactNode }) {
  const [open, setOpen] = useState(true)
  return (
    <div>
      <button onClick={() => setOpen(o => !o)}>{open ? 'Ascunde' : 'Arată'}</button>
      {open && children}
    </div>
  )
}

// page.tsx — Server Component
export default async function Dashboard() {
  const stats = await getHeavyStats()
  return (
    <CollapsiblePanel>
      <HeavyStatsTable data={stats} />  {/* rămâne Server Component */}
    </CollapsiblePanel>
  )
}
// ✓ CollapsiblePanel = Client, HeavyStatsTable = Server
// children e RSC payload, nu JS executabil — nu face parte din bundle
```

**Context Providers — problema nr. 1 la migrarea din Pages Router:**

Server Components nu pot folosi `useContext`. Orice Provider (`ThemeProvider`, `ToastProvider`, Supabase client context) trebuie izolat într-un Client Component:

```tsx
// ✗ GREȘIT: 'use client' pe root layout = tot arborele devine client
'use client'
import { ThemeProvider } from 'next-themes'

export default function RootLayout({ children }) {
  return (
    <html>
      <body>
        <ThemeProvider>{children}</ThemeProvider>
        {/* Acum page.tsx, layout-urile copil, totul = Client Component */}
        {/* Pierzi toate beneficiile RSC în întreaga aplicație */}
      </body>
    </html>
  )
}

// ✓ CORECT: Provider izolat în propriul Client Component
// components/Providers.tsx
'use client'
import { ThemeProvider } from 'next-themes'
import { Toaster } from 'sonner'

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <ThemeProvider attribute="class" defaultTheme="system">
      {children}
      <Toaster richColors />
    </ThemeProvider>
  )
}

// app/layout.tsx — rămâne Server Component
import { Providers } from '@/components/Providers'

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ro">
      <body>
        <Providers>
          {children}  {/* children = RSC, nu Client */}
        </Providers>
      </body>
    </html>
  )
}
// ✓ Providers = Client, dar page.tsx și toate layouturile copil rămân Server Components
```

**Granița `'use client'` — ce importă o componentă client devine client:**

```tsx
// ✗ GREȘIT: Server Component importat direct în Client Component
'use client'
import { HeavyServerTable } from './HeavyServerTable'
// HeavyServerTable + toate dependențele sale = în bundle JS

// ✓ CORECT: Server Component ca children (nu import direct)
// page.tsx (Server)
export default async function Page() {
  const data = await fetchData()
  return (
    <ClientWrapper>
      <HeavyServerTable data={data} />  {/* ✓ rămâne Server */}
    </ClientWrapper>
  )
}
```

**Props serializabile — ce poate trece server→client:**

```tsx
// ✓ Serializabile (pot trece server → client)
string, number, boolean, null, undefined
Plain objects: { id: string, name: string, amount: number }
Arrays cu valori serializabile

// ✓ Date — ATENȚIE: convertești la string ISO, nu trimiți Date object
const dateString = invoice.created_at   // string ISO din Supabase ✓
// SAU formatezi pe server:
const formatted = new Intl.DateTimeFormat('ro-RO').format(new Date(invoice.created_at))

// ✗ Date object new Date() server→client = pierde metode (.toLocaleDateString devine eroare)
// ✗ Function, class instance, Map, Set, Symbol = eroare la runtime
// ✓ Server Actions ca props = serializabile (sunt referințe, nu funcții)
```

**Libs third-party client-only:**

```tsx
// Multe lib-uri npm presupun browser environment
// Dacă importezi direct în Server Component → eroare build

// ✓ Învelești în Client Component
'use client'
import { Toaster } from 'sonner'

// ✓ SAU lazy import cu next/dynamic
const ReactFlow = dynamic(() => import('reactflow'), { ssr: false })
```

---

### Parte 2 — File Conventions și Route Groups

**Fișierele speciale Next.js:**

| Fișier | Scop | Notă critică |
|---|---|---|
| `page.tsx` | UI pentru rută | Obligatoriu pentru orice rută |
| `layout.tsx` | Wrapper persistent (nav, sidebar) | **Nu se remontează** la navigare |
| `loading.tsx` | Skeleton la loading | Învelește automat în `<Suspense>` |
| `error.tsx` | UI pentru erori | **Trebuie** `'use client'` (error boundary) |
| `global-error.tsx` | Erori din root layout | **Trebuie** `'use client'` + `<html><body>` |
| `not-found.tsx` | Pagina 404 | Activat de `notFound()` din `next/navigation` |
| `template.tsx` | Ca layout, se **remontează** | Rar — când vrei reset state la navigare |
| `route.ts` | Route Handler (API) | Nu coexistă cu `page.tsx` în același folder |
| `default.tsx` | Fallback Parallel Routes | Obligatoriu când folosești `@slot` |
| `opengraph-image.tsx` | OG image generată | Afișată la share pe social media |
| `robots.ts` | Generare robots.txt | `export default function robots(): MetadataRoute.Robots` |
| `sitemap.ts` | Generare sitemap.xml | `export default function sitemap(): MetadataRoute.Sitemap` |

**Ierarhia de Error Boundaries:**

```tsx
// app/error.tsx — prinde erori din page.tsx + layout.tsx copii
// NU prinde erori din propriul layout.tsx (al aceluiași nivel)

// app/dashboard/error.tsx — 'use client' OBLIGATORIU
'use client'
export default function DashboardError({
  error,
  reset
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  return (
    <div className="flex flex-col items-center justify-center min-h-[400px] gap-4">
      <h2 className="text-xl font-semibold">Ceva nu a mers bine</h2>
      <p className="text-gray-600 text-sm">{error.message}</p>
      <button onClick={reset} className="px-4 py-2 bg-blue-600 text-white rounded">
        Încearcă din nou
      </button>
    </div>
  )
}

// app/global-error.tsx — prinde erori din root layout.tsx (error.tsx nu poate face asta)
'use client'
export default function GlobalError({
  error,
  reset
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  return (
    <html>    {/* ← OBLIGATORIU: înlocuiește tot root layout-ul */}
      <body>
        <h2>Aplicația a întâmpinat o eroare critică</h2>
        <button onClick={reset}>Reîncarcă</button>
      </body>
    </html>
  )
}
// ✓ global-error.tsx vizibil NUMAI în production (dev = overlay Next.js)
```

**`generateStaticParams` — SSG cu rute dinamice:**

```tsx
// app/blog/[slug]/page.tsx
// La BUILD: Next.js generează HTML static pentru fiecare slug
// La runtime: servit direct de CDN, zero compute, LCP instant

export async function generateStaticParams() {
  // Rulează pe server la build time
  const { data: posts } = await supabase
    .from('posts')
    .select('slug')
    .eq('published', true)
  return (posts ?? []).map(post => ({ slug: post.slug }))
}

// dynamicParams = true (default): sluguri noi → ISR (generare la prima cerere)
// dynamicParams = false: sluguri noi → 404
export const dynamicParams = true

export default async function BlogPost({ params }: { params: { slug: string } }) {
  const { data: post } = await supabase
    .from('posts').select('*').eq('slug', params.slug).maybeSingle()
  if (!post) notFound()
  return <PostContent post={post} />
}

// ✓ Util pentru: pagini publice (blog, produse, documente, landing pages)
// ✗ Nu are sens pentru pagini protejate cu date per-user (folosești dynamic acolo)
```

**Route Groups:**

```
app/
  (auth)/               ← grup: /login, nu /(auth)/login
    login/page.tsx      ← ruta: /login
    signup/page.tsx     ← ruta: /signup
    layout.tsx          ← layout NUMAI pentru auth pages (minimal, fără nav)
  (dashboard)/          ← grup: /dashboard, nu /(dashboard)/dashboard
    dashboard/page.tsx  ← ruta: /dashboard
    invoices/page.tsx   ← ruta: /invoices
    layout.tsx          ← layout cu sidebar + header
  layout.tsx            ← root layout (pentru toți)
```

**`notFound()` — pattern corect:**

```tsx
import { notFound } from 'next/navigation'
import { redirect } from 'next/navigation'

export default async function InvoicePage({ params }: { params: { id: string } }) {
  const supabase = await createServerClient()
  const { data: { user } } = await supabase.auth.getUser()
  if (!user) redirect('/login')

  const { data: invoice } = await supabase
    .from('invoices')
    .select('*')
    .eq('id', params.id)
    .eq('user_id', user.id)   // ← securitate: verifici ownership
    .maybeSingle()            // ← .maybeSingle() nu aruncă eroare dacă lipsește

  if (!invoice) notFound()   // ← aruncă NEXT_NOT_FOUND, prins de not-found.tsx

  return <InvoiceDetails invoice={invoice} />
}
```

**`loading.tsx` și `error.tsx`:**

```tsx
// app/dashboard/loading.tsx — afișat instant la navigare
export default function DashboardLoading() {
  return (
    <div className="animate-pulse space-y-4 p-6">
      <div className="h-8 bg-gray-200 rounded w-1/4" />
      <div className="grid grid-cols-3 gap-4">
        {[1, 2, 3].map(i => (
          <div key={i} className="h-32 bg-gray-200 rounded" />
        ))}
      </div>
    </div>
  )
}
// loading.tsx = shorthand pentru Suspense automat
// Suspense explicit în page.tsx → control granular per-secțiune (mai bun)
```

---

## BLOC 2 — Date și Acțiuni

---

### Parte 3 — Server Actions

**Pattern complet cu validare Zod:**

```ts
// app/actions/invoices.ts
'use server'

import { z } from 'zod'
import { revalidatePath, revalidateTag } from 'next/cache'
import { redirect } from 'next/navigation'
import { createServerClient } from '@/lib/supabase/server'

const CreateInvoiceSchema = z.object({
  client_name: z.string().min(1, 'Numele clientului este obligatoriu'),
  amount:      z.coerce.number().positive('Suma trebuie să fie pozitivă'),
  due_date:    z.string().optional()
})

type ActionResult = { error: string } | null

export async function createInvoice(
  _prevState: ActionResult,
  formData: FormData
): Promise<ActionResult> {
  const supabase = await createServerClient()
  const { data: { user } } = await supabase.auth.getUser()
  if (!user) redirect('/login')

  const parsed = CreateInvoiceSchema.safeParse({
    client_name: formData.get('client_name'),
    amount:      formData.get('amount'),
    due_date:    formData.get('due_date')
  })

  if (!parsed.success) {
    return { error: parsed.error.errors[0].message }
  }

  const { error } = await supabase.from('invoices').insert({
    user_id:     user.id,
    ...parsed.data,
    due_date:    parsed.data.due_date ?? null
  })

  if (error) return { error: error.message }

  revalidateTag('invoices')
  redirect('/dashboard/invoices')  // ✓ AFARĂ din try/catch
}
```

**CRITICAL: `redirect()` NU în try/catch:**

```ts
// ✗ GREȘIT: redirect() aruncă NEXT_REDIRECT — catch-ul o înghite
export async function save(formData: FormData) {
  try {
    await insertData(formData)
    redirect('/success')     // ← NEXT_REDIRECT prins de catch
  } catch (error) {
    return { error: 'failed' }  // ← prinde redirect-ul, nu erori reale
  }
}

// ✓ CORECT: try/catch numai pentru operații, redirect afară
export async function save(formData: FormData) {
  try {
    await insertData(formData)
  } catch (error) {
    return { error: 'A apărut o eroare la salvare' }
  }
  revalidateTag('invoices')
  redirect('/success')     // ← rulează după try/catch, funcționează
}
```

**`bind()` — argumente extra la Server Actions:**

```tsx
// ✓ bind() = pattern standard când ai nevoie de un ID la delete/update din form
// app/actions/invoices.ts
export async function deleteInvoice(id: string) {
  const supabase = await createServerClient()
  const { data: { user } } = await supabase.auth.getUser()
  if (!user) redirect('/login')

  const { error } = await supabase
    .from('invoices')
    .update({ deleted_at: new Date().toISOString() })
    .eq('id', id)
    .eq('user_id', user.id)

  if (error) throw error
  revalidateTag('invoices')
}

// InvoiceRow.tsx — Server Component (form cu bind())
export function InvoiceRow({ invoice }: { invoice: Invoice }) {
  const deleteWithId = deleteInvoice.bind(null, invoice.id)
  return (
    <tr>
      <td>{invoice.client_name}</td>
      <td>
        <form action={deleteWithId}>
          <button type="submit" className="text-red-600">Șterge</button>
        </form>
      </td>
    </tr>
  )
}
// ✓ Nu ai nevoie de Client Component pentru un simplu delete button
// ✓ Progressive enhancement: funcționează fără JS
```

**`useTransition` — Server Actions din event handlers (fără form):**

```tsx
// Când ai un buton care apelează Server Action dar nu e într-un <form>
// useTransition = pending state + non-blocking UI

'use client'
import { useTransition } from 'react'
import { deleteInvoice } from '@/actions/invoices'

export function DeleteButton({ id }: { id: string }) {
  const [isPending, startTransition] = useTransition()

  return (
    <button
      disabled={isPending}
      onClick={() => startTransition(() => deleteInvoice(id))}
      className={`text-red-600 text-sm ${isPending ? 'opacity-50 cursor-not-allowed' : ''}`}
    >
      {isPending ? 'Se șterge...' : 'Șterge'}
    </button>
  )
}

// ✓ startTransition() marchează tranzitia ca non-urgentă — React nu blochează UI
// ✓ isPending = true pe durata Server Action — previne double-click
// ✓ Alternativă la useOptimistic când nu ai nevoie de UI preview instant
// ✓ Funcționează fără <form> — util pentru butoane standalone, dropdown actions, etc.

// Diferență față de bind() + form:
// bind() + form → Server Component posibil, progressive enhancement
// useTransition → Client Component necesar, mai flexibil (logică condițională)
```

**`useOptimistic` — UI instant fără să aștepți serverul:**

```tsx
// app/invoices/page.tsx — Server Component
export default async function InvoicesPage() {
  const invoices = await getCachedInvoices(userId)
  return <InvoiceList invoices={invoices} />
}

// components/InvoiceList.tsx — Client Component
'use client'
import { useOptimistic } from 'react'
import { deleteInvoice } from '@/actions/invoices'

export function InvoiceList({ invoices }: { invoices: Invoice[] }) {
  const [optimisticInvoices, removeOptimistic] = useOptimistic(
    invoices,
    (state, deletedId: string) => state.filter(inv => inv.id !== deletedId)
  )

  async function handleDelete(id: string) {
    removeOptimistic(id)   // UI se actualizează INSTANT — lista scurtează imediat
    await deleteInvoice(id) // Server Action în background
    // Dacă Server Action eșuează → React revine la starea anterioară automat
  }

  return (
    <ul>
      {optimisticInvoices.map(invoice => (
        <li key={invoice.id} className="flex justify-between p-4 border-b">
          <span>{invoice.client_name}</span>
          <button
            onClick={() => handleDelete(invoice.id)}
            className="text-red-600 text-sm"
          >
            Șterge
          </button>
        </li>
      ))}
    </ul>
  )
}
```

**`useFormStatus` — loading state în formulare:**

```tsx
// SubmitButton trebuie să fie COMPONENTĂ COPIL a <form> cu Server Action
// Nu funcționează dacă e în același component cu <form> sau dacă form folosește onSubmit

// ✓ CORECT: componentă separată
'use client'
import { useFormStatus } from 'react-dom'

export function SubmitButton({ label }: { label: string }) {
  const { pending } = useFormStatus()   // citește statusul formului parent
  return (
    <button type="submit" disabled={pending} className="...">
      {pending ? 'Se procesează...' : label}
    </button>
  )
}

// În form:
// <form action={createInvoice}>
//   <input name="client_name" />
//   <SubmitButton label="Crează factură" />  ← componentă copil ✓
// </form>
```

**`useActionState` — Next.js 15 / React 19:**

```tsx
'use client'
import { useActionState } from 'react'  // React 19 — din 'react', nu 'react-dom'
import { createInvoice } from '@/actions/invoices'

export function CreateInvoiceForm() {
  const [state, formAction, isPending] = useActionState(createInvoice, null)

  return (
    <form action={formAction} className="space-y-4">
      {state?.error && <p className="text-red-600 text-sm">{state.error}</p>}
      <input name="client_name" placeholder="Client" className="w-full border rounded px-3 py-2" />
      <input name="amount" type="number" step="0.01" className="w-full border rounded px-3 py-2" />
      <button type="submit" disabled={isPending} className="w-full bg-blue-600 text-white py-2 rounded disabled:opacity-50">
        {isPending ? 'Se creează...' : 'Crează factură'}
      </button>
    </form>
  )
}

// Next.js 14 / React 18: useFormState din 'react-dom' (diferit de useActionState)
// import { useFormState } from 'react-dom'
// const [state, formAction] = useFormState(createInvoice, null)
```

---

### Parte 4 — Route Handlers

**Când să folosești vs Server Actions:**

```
Server Actions (preferat pentru UI intern):
✓ Formulare și mutații din propriul UI Next.js
✓ Type-safe automat — apel direct TypeScript
✓ CSRF protejat automat de Next.js
✓ Progressive enhancement — funcționează fără JS

Route Handlers (pentru consumatori externi):
✓ Webhooks: Stripe, GitHub, Twilio, Supabase Edge Functions
✓ REST API pentru aplicație mobilă / third-party
✓ Streaming responses (Server-Sent Events)
✓ CORS necesar pentru domenii externe
✗ NU pentru mutații din propriul UI Next.js = overhead inutil
✗ NU sunt protejate CSRF automat (spre deosebire de Server Actions)
```

**Pattern de bază:**

```ts
// app/api/invoices/route.ts
import { NextRequest, NextResponse } from 'next/server'
import { createServerClient } from '@/lib/supabase/server'

export async function GET(request: NextRequest) {
  const supabase = await createServerClient()
  const { data: { user } } = await supabase.auth.getUser()
  if (!user) return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })

  const { searchParams } = new URL(request.url)
  const status = searchParams.get('status')

  let query = supabase.from('invoices').select('*').eq('user_id', user.id)
  if (status) query = query.eq('status', status)

  const { data, error } = await query
  if (error) return NextResponse.json({ error: error.message }, { status: 500 })

  return NextResponse.json(data ?? [])
}
```

**Webhook cu verificare signature (Stripe):**

```ts
// app/api/webhooks/stripe/route.ts
import Stripe from 'stripe'
import { headers } from 'next/headers'

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!)

export async function POST(request: NextRequest) {
  const body = await request.text()   // text raw — nu json! (pentru verificare signature)
  const headersList = await headers()
  const sig = headersList.get('stripe-signature')

  if (!sig) return NextResponse.json({ error: 'Missing signature' }, { status: 400 })

  let event: Stripe.Event
  try {
    event = stripe.webhooks.constructEvent(body, sig, process.env.STRIPE_WEBHOOK_SECRET!)
  } catch {
    return NextResponse.json({ error: 'Invalid signature' }, { status: 400 })
  }

  switch (event.type) {
    case 'payment_intent.succeeded':
      await handlePaymentSucceeded(event.data.object as Stripe.PaymentIntent)
      break
  }
  return NextResponse.json({ received: true })
}
```

**CORS pentru API public:**

```ts
// app/api/public/route.ts
const corsHeaders = {
  'Access-Control-Allow-Origin':  '*',          // sau domeniu specific
  'Access-Control-Allow-Methods': 'GET, POST',
  'Access-Control-Allow-Headers': 'Content-Type, Authorization'
}

export async function OPTIONS() {
  return new Response(null, { status: 200, headers: corsHeaders })
}

export async function GET() {
  return NextResponse.json({ data: [] }, { headers: corsHeaders })
}
```

---

### Parte 5 — Data Fetching Avansat

**Fetch direct în Server Component:**

```tsx
export default async function InvoicesPage() {
  const supabase = await createServerClient()
  const { data: { user } } = await supabase.auth.getUser()
  if (!user) redirect('/login')

  const { data: invoices, error } = await supabase
    .from('invoices')
    .select(`id, client_name, amount, status, created_at, clients(name, email)`)
    .eq('user_id', user.id)
    .is('deleted_at', null)
    .order('created_at', { ascending: false })

  if (error) throw error
  return <InvoiceList invoices={invoices ?? []} />
}
```

**`React.cache()` — memoizare per-request:**

```ts
// lib/data/user.ts
import { cache } from 'react'
import { createServerClient } from '@/lib/supabase/server'

// getCurrentUser e apelat în layout.tsx, page.tsx, orice Server Component
// → React.cache() garantează UN SINGUR request Supabase Auth per render tree
export const getCurrentUser = cache(async () => {
  const supabase = await createServerClient()
  const { data: { user }, error } = await supabase.auth.getUser()
  if (error || !user) return null
  return user
})

// layout.tsx: const user = await getCurrentUser()   → face request
// page.tsx:   const user = await getCurrentUser()   → din cache, zero request extra
// Orice Server Component: const user = await getCurrentUser() → din cache
```

**`React.cache()` vs `unstable_cache` — când folosești care:**

```
React.cache():
✓ Deduplicare în ACELAȘI render tree (per-request)
✓ Zero config, învelești funcția
✓ Se resetează la fiecare request nou (nu e persistent)
✓ Ideal pentru: getCurrentUser(), getTeam(), orice date partajate în ierarhie

unstable_cache():
✓ Cache PERSISTENT între request-uri (Data Cache)
✓ TTL configurabil (revalidate: 300)
✓ Invalidat prin revalidateTag()
✓ Ideal pentru: date care nu se schimbă des (lista de clienți, configurări)
→ Next.js 15: redenumit 'use cache' directive (vezi Parte 9)
```

**Parallel fetching cu error handling corect:**

```tsx
// ✗ GREȘIT: dacă ORICARE query eșuează → Promise.all aruncă eroare, pierzi TOATE datele
const [{ data: invoices }, { data: clients }] = await Promise.all([...])

// ✓ CORECT: error handling explicit, date parțiale utilizabile
export default async function DashboardPage() {
  const user = await getCurrentUser()
  if (!user) redirect('/login')

  const supabase = await createServerClient()
  const [invoicesResult, clientsResult, statsResult] = await Promise.all([
    supabase.from('invoices').select('*').eq('user_id', user.id),
    supabase.from('clients').select('*').eq('user_id', user.id),
    supabase.rpc('get_dashboard_stats', { p_user_id: user.id })
  ])

  if (invoicesResult.error) throw invoicesResult.error
  if (clientsResult.error)  throw clientsResult.error
  const stats = statsResult.error ? null : statsResult.data

  return (
    <Dashboard
      invoices={invoicesResult.data ?? []}
      clients={clientsResult.data  ?? []}
      stats={stats}
    />
  )
}
```

**`unstable_cache` pentru Supabase:**

```ts
// lib/data/invoices.ts
import { unstable_cache } from 'next/cache'

export const getCachedInvoices = unstable_cache(
  async (userId: string) => {
    const supabase = await createServerClient()
    const { data, error } = await supabase
      .from('invoices')
      .select('id, client_name, amount, status, created_at')
      .eq('user_id', userId)
      .is('deleted_at', null)
      .order('created_at', { ascending: false })
    if (error) throw error
    return data ?? []
  },
  ['user-invoices'],
  { revalidate: 300, tags: ['invoices'] }
)
// userId e inclus automat în cache key (prin argumentele funcției)
// Invalidare în Server Action: revalidateTag('invoices')
```

**`nuqs` — type-safe URL search params (filtre, paginare):**

```tsx
// npm install nuqs
// Problema: useSearchParams() returnează string pentru orice — page=1 e string, nu number
// nuqs rezolvă: parsing + serialization type-safe + sync cu URL

'use client'
import { useQueryState, parseAsString, parseAsInteger, parseAsStringEnum } from 'nuqs'

export function InvoiceFilters() {
  const [status, setStatus] = useQueryState(
    'status',
    parseAsStringEnum(['all', 'paid', 'sent', 'draft']).withDefault('all')
  )
  const [page, setPage]   = useQueryState('page', parseAsInteger.withDefault(1))
  const [q, setQ]         = useQueryState('q',    parseAsString.withDefault(''))

  return (
    <div className="flex gap-4">
      <input
        value={q}
        onChange={e => { setQ(e.target.value); setPage(1) }}
        placeholder="Caută..."
      />
      <select value={status} onChange={e => setStatus(e.target.value as typeof status)}>
        <option value="all">Toate</option>
        <option value="paid">Plătite</option>
        <option value="sent">Trimise</option>
      </select>
    </div>
  )
}
// URL: /invoices?status=paid&page=2&q=acme
// ✓ Type-safe: status = 'all'|'paid'|'sent'|'draft' (nu string!)
// ✓ URL partajabil, bookmarkabil, back-button corect
// ✓ Sync automat — nu ai nevoie de useState separat
```

**`use()` hook — citire Promise în Client Component (React 19):**

```tsx
// Util când Server Component pasează un Promise la Client Component
// Client Component suspendă până Promise se rezolvă

'use client'
import { use, Suspense } from 'react'

type UserAvatarProps = { userPromise: Promise<User | null> }

function UserAvatarInner({ userPromise }: UserAvatarProps) {
  const user = use(userPromise)  // suspendă componenta — Suspense boundary necesară
  if (!user) return null
  return <img src={user.avatar_url ?? ''} alt={user.full_name ?? ''} className="h-8 w-8 rounded-full" />
}

export function UserAvatar(props: UserAvatarProps) {
  return (
    <Suspense fallback={<div className="h-8 w-8 rounded-full bg-gray-200 animate-pulse" />}>
      <UserAvatarInner {...props} />
    </Suspense>
  )
}

// Server Component parent — NU await Promise-ul:
export default async function Layout({ children }: { children: React.ReactNode }) {
  const userPromise = getCurrentUser()  // ← fără await, pasezi Promise-ul
  return (
    <nav>
      <UserAvatar userPromise={userPromise} />  {/* Client Component */}
      {children}
    </nav>
  )
}
// ✓ Layout nu se blochează pentru user — UI-ul apare imediat cu fallback
// ✓ Paralel cu restul render tree-ului
```

**Streaming cu Suspense:**

```tsx
// page.tsx — date independente se încarcă în paralel
import { Suspense } from 'react'

export default function DashboardPage() {
  return (
    <div className="space-y-6 p-6">
      <DashboardHeader />
      <div className="grid grid-cols-3 gap-4">
        <Suspense fallback={<CardSkeleton />}><RevenueCard /></Suspense>
        <Suspense fallback={<CardSkeleton />}><InvoiceCountCard /></Suspense>
        <Suspense fallback={<CardSkeleton />}><ClientCountCard /></Suspense>
      </div>
      <Suspense fallback={<TableSkeleton rows={8} />}>
        <RecentInvoicesTable />   {/* query lent — nu blochează cardurile */}
      </Suspense>
    </div>
  )
}

async function RecentInvoicesTable() {
  const user = await getCurrentUser()
  if (!user) return null
  const invoices = await getCachedInvoices(user.id)
  return <InvoiceTable rows={invoices} />
}
```

---

## BLOC 3 — Securitate

---

### Parte 6 — Middleware

```ts
// middleware.ts — LA RĂDĂCINA PROIECTULUI (nu în /app, nu în /src/app)
import { NextRequest, NextResponse } from 'next/server'
import { createServerClient } from '@supabase/ssr'

export async function middleware(request: NextRequest) {
  let supabaseResponse = NextResponse.next({ request })

  const supabase = createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        getAll: () => request.cookies.getAll(),
        setAll: (cookiesToSet) => {
          cookiesToSet.forEach(({ name, value }) => request.cookies.set(name, value))
          supabaseResponse = NextResponse.next({ request })
          cookiesToSet.forEach(({ name, value, options }) =>
            supabaseResponse.cookies.set(name, value, options)
          )
        }
      }
    }
  )

  // OBLIGATORIU: refresh session (actualizează cookie dacă expiră curând)
  const { data: { user } } = await supabase.auth.getUser()

  if (!user && isProtectedRoute(request.nextUrl.pathname)) {
    const url = request.nextUrl.clone()
    url.pathname = '/login'
    url.searchParams.set('redirectTo', request.nextUrl.pathname)
    return NextResponse.redirect(url)
  }

  if (user && isAuthRoute(request.nextUrl.pathname)) {
    return NextResponse.redirect(new URL('/dashboard', request.url))
  }

  return supabaseResponse  // ✓ supabaseResponse, nu NextResponse.next() nou
}

function isProtectedRoute(pathname: string): boolean {
  return ['/dashboard', '/invoices', '/clients', '/settings']
    .some(path => pathname.startsWith(path))
}

function isAuthRoute(pathname: string): boolean {
  return ['/login', '/signup'].includes(pathname)
}

export const config = {
  matcher: [
    '/((?!_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp)$).*)'
  ]
}
```

**Notă performanță — `getUser()` în middleware:**

```ts
// supabase.auth.getUser() face request HTTP la Supabase Auth Server PER REQUEST
// La trafic mare (>500 req/min), latența se adună

// Opțiunea pragmatică: getUser() în middleware e OK pentru majoritatea proiectelor
// La trafic mare: evaluezi verificare JWT locală cu 'jose' (no HTTP call)
// Tradeoff: jose nu refreshează automat cookie-ul — gestionezi expirations manual
// import { jwtVerify } from 'jose'
// const secret = new TextEncoder().encode(process.env.SUPABASE_JWT_SECRET)
// await jwtVerify(token, secret)
```

**Rate limiting cu Upstash Redis (edge-compatible):**

```ts
// npm install @upstash/ratelimit @upstash/redis
// Env: UPSTASH_REDIS_REST_URL, UPSTASH_REDIS_REST_TOKEN (din Upstash dashboard)
import { Ratelimit } from '@upstash/ratelimit'
import { Redis } from '@upstash/redis'

const ratelimit = new Ratelimit({
  redis: Redis.fromEnv(),
  limiter: Ratelimit.slidingWindow(10, '10 s')  // 10 req per 10 secunde per IP
})

export async function middleware(request: NextRequest) {
  // Rate limit numai pentru API routes (nu pentru pagini statice)
  if (request.nextUrl.pathname.startsWith('/api/')) {
    const ip = request.ip
      ?? request.headers.get('x-forwarded-for')?.split(',')[0]
      ?? '127.0.0.1'
    const { success } = await ratelimit.limit(ip)
    if (!success) {
      return NextResponse.json(
        { error: 'Prea multe cereri. Încearcă din nou în câteva secunde.' },
        { status: 429, headers: { 'Retry-After': '10' } }
      )
    }
  }
  // ... restul middleware-ului
}
```

**Limitările Edge Runtime:**

```ts
// ✗ Nu există pe Edge
import { readFileSync } from 'fs'
import { PrismaClient } from '@prisma/client'
import Redis from 'ioredis'  // Node TCP sockets

// ✓ Edge-compatible
import { createServerClient } from '@supabase/ssr'
import { Redis } from '@upstash/redis'   // HTTP-based
import { jwtVerify } from 'jose'         // edge crypto
```

**Middleware ≠ Autentificare completă:**

```ts
// ✓ Middleware = redirect rapid pentru UI
// ✓ Server Actions + Route Handlers = validare getUser() la fiecare operație sensibilă
// Chiar dacă middleware blochează ruta, verifici din nou în Server Action:
export async function deleteInvoice(id: string) {
  const { data: { user } } = await supabase.auth.getUser()
  if (!user) redirect('/login')  // ← nu te baza NUMAI pe middleware
}
```

---

### Parte 7 — Supabase SSR: Setup Corect

**Instalare:**

```bash
npm install @supabase/ssr @supabase/supabase-js
# Nu mai folosi @supabase/auth-helpers-nextjs — deprecated
```

**`lib/supabase/server.ts` — cu `server-only`:**

```ts
// lib/supabase/server.ts
import 'server-only'
// Dacă importat accidental în Client Component → eroare la BUILD (nu runtime)
// Previne scurgerea SUPABASE_SERVICE_ROLE_KEY sau oricărei chei secrete în browser

import { createServerClient as createClient } from '@supabase/ssr'
import { cookies } from 'next/headers'
import type { Database } from '@/types/supabase'

export async function createServerClient() {
  const cookieStore = await cookies()
  return createClient<Database>(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        getAll:  () => cookieStore.getAll(),
        setAll: (cookiesToSet) => {
          try {
            cookiesToSet.forEach(({ name, value, options }) =>
              cookieStore.set(name, value, options)
            )
          } catch {
            // Server Component: cookies() read-only — ignorăm safe
          }
        }
      }
    }
  )
}
```

**Client admin cu Service Role:**

```ts
// lib/supabase/admin.ts
import 'server-only'
import { createClient } from '@supabase/supabase-js'
import type { Database } from '@/types/supabase'

// Bypasses RLS — folosit NUMAI pentru operații privilegiate (webhooks, jobs, admin)
export function createAdminClient() {
  return createClient<Database>(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.SUPABASE_SERVICE_ROLE_KEY!,  // ← SECRET, niciodată NEXT_PUBLIC_
    { auth: { autoRefreshToken: false, persistSession: false } }
  )
}
```

**`lib/supabase/client.ts` — pentru Client Components:**

```ts
// lib/supabase/client.ts
import { createBrowserClient } from '@supabase/ssr'
import type { Database } from '@/types/supabase'

export function createSupabaseBrowserClient() {
  return createBrowserClient<Database>(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
  )
}
```

**`getUser()` vs `getSession()`:**

```ts
// ✗ getSession() — citește cookie local, validare JWT offline, bypass-abil
const { data: { session } } = await supabase.auth.getSession()

// ✓ getUser() — request la Supabase Auth server, validare online
const { data: { user } } = await supabase.auth.getUser()
if (!user) redirect('/login')
```

**`router.refresh()` după Supabase Realtime:**

```tsx
// Client Component care ascultă Realtime și re-fetchează date server
'use client'
import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { createSupabaseBrowserClient } from '@/lib/supabase/client'

export function RealtimeInvoiceSync({ userId }: { userId: string }) {
  const router = useRouter()
  const supabase = createSupabaseBrowserClient()

  useEffect(() => {
    const channel = supabase
      .channel('invoices-changes')
      .on(
        'postgres_changes',
        { event: '*', schema: 'public', table: 'invoices', filter: `user_id=eq.${userId}` },
        () => router.refresh()  // re-fetch RSC payload → date actualizate pe pagină
      )
      .subscribe()

    return () => { supabase.removeChannel(channel) }
  }, [userId, router, supabase])

  return null  // componentă invizibilă — doar sincronizare
}
// ✓ router.refresh() re-renderizează Server Components cu date noi din DB
// ✓ Nu invalidează Data Cache (unstable_cache) — pentru asta: revalidateTag() din Server Action
```

**Auth flow complet:**

```ts
// app/actions/auth.ts
'use server'
import { redirect } from 'next/navigation'
import { createServerClient } from '@/lib/supabase/server'

export async function signIn(_: unknown, formData: FormData) {
  const supabase = await createServerClient()
  const { error } = await supabase.auth.signInWithPassword({
    email:    String(formData.get('email')    ?? ''),
    password: String(formData.get('password') ?? '')
  })
  if (error) return { error: error.message }
  redirect('/dashboard')
}

export async function signOut() {
  const supabase = await createServerClient()
  await supabase.auth.signOut()
  redirect('/login')
}
```

```ts
// app/auth/callback/route.ts — OAuth + email confirmation
import { NextRequest, NextResponse } from 'next/server'
import { createServerClient } from '@/lib/supabase/server'

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url)
  const code = searchParams.get('code')
  const next = searchParams.get('next') ?? '/dashboard'

  // ✓ Validezi redirectTo — previne Open Redirect attack
  const safeNext = next.startsWith('/') ? next : '/dashboard'

  if (code) {
    const supabase = await createServerClient()
    const { error } = await supabase.auth.exchangeCodeForSession(code)
    if (!error) return NextResponse.redirect(new URL(safeNext, request.url))
  }
  return NextResponse.redirect(new URL('/login?error=auth-failed', request.url))
}
```

---

### Parte 8 — Variabile de Mediu

```bash
# .env.local — niciodată în Git!

# NEXT_PUBLIC_ = bundluit în JS, vizibil în browser
NEXT_PUBLIC_SUPABASE_URL=https://xyz.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJ...
NEXT_PUBLIC_APP_URL=http://localhost:3000

# Fără prefix = server-only
SUPABASE_SERVICE_ROLE_KEY=eyJ...   # ⛔ bypasses RLS — SUPER SECRET
ANTHROPIC_API_KEY=sk-ant-...       # ⛔ SUPER SECRET
STRIPE_SECRET_KEY=sk_live_...      # ⛔ SUPER SECRET
STRIPE_WEBHOOK_SECRET=whsec_...    # ⛔ server-only
SUPABASE_JWT_SECRET=your-jwt-secret  # ⛔ server-only (din Supabase → Settings → JWT)
```

**Validare la startup:**

```ts
// lib/env.ts — importat în app/layout.tsx
const requiredServer = ['SUPABASE_SERVICE_ROLE_KEY', 'ANTHROPIC_API_KEY'] as const
const requiredPublic  = ['NEXT_PUBLIC_SUPABASE_URL', 'NEXT_PUBLIC_SUPABASE_ANON_KEY'] as const

if (typeof window === 'undefined') {
  for (const key of requiredServer) {
    if (!process.env[key]) {
      throw new Error(`[Config] Missing server env var: ${key}`)
    }
  }
}
for (const key of requiredPublic) {
  if (!process.env[key]) throw new Error(`[Config] Missing public env var: ${key}`)
}
```

```ts
// env.d.ts
declare global {
  namespace NodeJS {
    interface ProcessEnv {
      NODE_ENV: 'development' | 'production' | 'test'
      NEXT_PUBLIC_SUPABASE_URL:      string
      NEXT_PUBLIC_SUPABASE_ANON_KEY: string
      NEXT_PUBLIC_APP_URL:           string
      SUPABASE_SERVICE_ROLE_KEY:     string
      SUPABASE_JWT_SECRET:           string
      ANTHROPIC_API_KEY:             string
      STRIPE_SECRET_KEY?:            string
      STRIPE_WEBHOOK_SECRET?:        string
    }
  }
}
export {}
```

---

## BLOC 4 — Performanță

---

### Parte 9 — Caching în Next.js

**4 nivele — relația dintre ele:**

```
1. Request Memoization   → per-render tree, automat, resetat după request
   Tool: React.cache()   → deduplicare explicită

2. Data Cache            → persistent între request-uri
   Tool: fetch() cache   → fetch nativ
         unstable_cache  → Supabase SDK / orice funcție async
         'use cache'     → Next.js 15 stable API (înlocuiește unstable_cache)

3. Full Route Cache      → pagini statice, cached la build pe CDN
   Control: dynamic = 'force-dynamic', revalidate = 0/N

4. Router Cache          → client-side, RSC payloads prefetchate
   Durate: static = 5 min, dynamic = 30 sec (Next.js 14)
   Invalidat de: revalidatePath(), revalidateTag(), router.refresh()
```

**`React.cache()` — per-request deduplication:**

```ts
import { cache } from 'react'

export const getCurrentUser = cache(async () => {
  const supabase = await createServerClient()
  const { data: { user } } = await supabase.auth.getUser()
  return user ?? null
})
// Apelat de N ori în același render tree = 1 singur request Supabase Auth
// Resetat automat între request-uri (nu e persistent)
```

**`unstable_cache` — persistent Data Cache:**

```ts
export const getCachedInvoices = unstable_cache(
  async (userId: string) => { /* query Supabase */ },
  ['user-invoices'],
  { revalidate: 300, tags: ['invoices'] }
)
// Persistă 5 minute, supraviețuiește între request-uri
// Invalidat explicit de revalidateTag('invoices') după mutație
```

**`use cache` — Next.js 15 (stable API, înlocuiește `unstable_cache`):**

```ts
// Next.js 15 introduce 'use cache' directive la nivel de funcție sau fișier
// ATENȚIE: require experimental.dynamicIO = true în next.config.ts

// lib/data/invoices.ts
import { cacheTag, cacheLife } from 'next/cache'

async function getInvoicesFromDB(userId: string) {
  'use cache'              // ← directive la nivel de funcție
  cacheTag('invoices')    // echivalent cu tags: ['invoices']
  cacheLife('minutes')    // profile predefinit: minutes = revalidate 60s
  // sau: cacheLife({ revalidate: 300, expire: 3600 })

  const supabase = await createServerClient()
  const { data, error } = await supabase.from('invoices').select('*').eq('user_id', userId)
  if (error) throw error
  return data ?? []
}
// Invalidare: revalidateTag('invoices') — identic cu unstable_cache
// unstable_cache rămâne valid în Next.js 14 și funcționează în 15
```

**Full Route Cache — control explicit:**

```tsx
export const dynamic = 'force-dynamic'   // mereu server-render (niciodată static)
export const revalidate = 0              // echivalent cu force-dynamic pentru date
export const revalidate = 3600           // ISR — re-build la fiecare oră
// Pagina devine dynamic automat dacă folosești: cookies(), headers(), searchParams
```

**Router Cache — date stale pe client:**

```ts
// PROBLEMĂ FRECVENTĂ: după revalidatePath() pe server, clientul poate vedea date vechi
// Router Cache păstrează RSC payload 30 sec (dynamic) sau 5 min (static)
// router.refresh() forțează re-fetch RSC payload — dar NU invalidează Data Cache

// Control Router Cache (Next.js 15 next.config.ts):
// experimental: { staleTimes: { dynamic: 0, static: 300 } }
// dynamic: 0 → dezactivezi client cache pentru pagini dynamic

// Pattern practic:
// Server Action → revalidateTag('invoices')   → invalidează Data Cache
// Client Component → router.refresh()          → re-fetch RSC payload cu date noi
// Împreună: data e mereu fresh
```

**`revalidatePath` vs `revalidateTag`:**

```ts
revalidatePath('/dashboard/invoices')           // o pagină exactă
revalidatePath('/dashboard', 'layout')          // layout + toate paginile copil
revalidateTag('invoices')                       // toate unstable_cache cu tag 'invoices'
revalidateTag(`invoice-${id}`)                  // tag granular per resursă
```

---

### Parte 10 — next/image, next/font, next/script

**next/image — cu `sizes` și `placeholder`:**

```tsx
import Image from 'next/image'

// ✓ Dimensiuni fixe + priority pentru above-the-fold
<Image src="/hero.jpg" alt="Hero" width={1200} height={600} priority />

// ✓ Fill + sizes — OBLIGATORIU pentru imagini responsive
// sizes îi spune browser-ului ce dimensiune să downloadeze pentru viewport curent
<div className="relative h-48 w-full overflow-hidden rounded">
  <Image
    src={product.imageUrl}
    alt={product.name}
    fill
    sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 33vw"
    // ↑ mobile: 100% din viewport, tablet: 50%, desktop: 33%
    // Fără sizes: browser downloadează mereu la dimensiunea maximă = LCP lent
    className="object-cover"
  />
</div>

// ✓ placeholder="blur" — previne layout shift + experiență vizuală mai bună
// Local images: Next.js generează blurDataURL automat
import localHero from '/public/hero.jpg'
<Image src={localHero} alt="Hero" placeholder="blur" />

// Remote images: blurDataURL manual (string base64 ~40px)
<Image
  src={user.avatarUrl}
  alt={user.name ?? ''}
  width={40} height={40}
  placeholder="blur"
  blurDataURL="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
/>
```

```ts
// next.config.ts
images: {
  remotePatterns: [
    { protocol: 'https', hostname: '*.supabase.co' },
    { protocol: 'https', hostname: 'lh3.googleusercontent.com' },
    { protocol: 'https', hostname: 'avatars.githubusercontent.com' }
  ]
}
```

**next/font:**

```tsx
import { Inter } from 'next/font/google'
const inter = Inter({ subsets: ['latin'], variable: '--font-inter', display: 'swap' })

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ro" className={inter.variable}>
      <body className="font-sans antialiased">{children}</body>
    </html>
  )
}
// Font descărcat la build time, self-hosted, fără cereri Google la runtime
// Zero layout shift garantat
```

**next/script:**

```tsx
import Script from 'next/script'

// afterInteractive — după hydration (Google Analytics, Hotjar)
<Script src="https://gtm.js" strategy="afterInteractive" />

// lazyOnload — când browser e idle (chat widgets, help tools)
<Script src="https://widget.intercom.io/widget/xxx" strategy="lazyOnload" />

// beforeInteractive — înainte de hydration, rar necesar (critical polyfills)
<Script src="/critical-polyfill.js" strategy="beforeInteractive" />
```

---

### Parte 11 — Streaming, Suspense, Intercepting Routes, next/dynamic

**`next/dynamic` — code splitting și componente browser-only:**

```tsx
import dynamic from 'next/dynamic'

// ✓ Lazy load — se downloadează numai când e în view
const RevenueChart = dynamic(
  () => import('@/components/RevenueChart'),
  { loading: () => <div className="animate-pulse h-64 bg-gray-100 rounded" /> }
)
// Bundle-ul principal nu include RevenueChart + Recharts
// Se downloadează separat, la prima afișare

// ✓ ssr: false — componente incompatibile cu server rendering
const RichTextEditor = dynamic(
  () => import('@/components/RichTextEditor'),
  { ssr: false, loading: () => <div className="h-32 bg-gray-100 animate-pulse rounded" /> }
)
const LeafletMap = dynamic(
  () => import('@/components/Map'),
  { ssr: false }  // Leaflet accesează window — crash pe server fără ssr: false
)
```

**Streaming cu Suspense:**

```tsx
// page.tsx — nu await nimic la nivel de pagină
export default function DashboardPage() {
  return (
    <div className="space-y-6 p-6">
      <DashboardHeader />  {/* instant — fără fetch */}
      <div className="grid grid-cols-3 gap-4">
        <Suspense fallback={<CardSkeleton />}><RevenueCard /></Suspense>
        <Suspense fallback={<CardSkeleton />}><InvoiceCount /></Suspense>
        <Suspense fallback={<CardSkeleton />}><ClientCount /></Suspense>
      </div>
      <Suspense fallback={<TableSkeleton rows={8} />}>
        <RecentInvoices />   {/* query lent — nu blochează cardurile */}
      </Suspense>
    </div>
  )
}
```

**Intercepting Routes — modal routing pattern:**

```
Scenariu: /invoices (lista) → click pe factură → modal overlay (URL se schimbă la /invoices/123)
           Dacă accesezi /invoices/123 direct → pagina completă (nu modal)

app/
  (dashboard)/
    invoices/
      page.tsx                    ← /invoices (lista completa)
      [id]/
        page.tsx                  ← /invoices/123 accesat DIRECT = pagina completă
      @modal/
        (.)invoices/[id]/
          page.tsx                ← /invoices/123 accesat DIN /invoices = modal overlay
        default.tsx               ← null — slot gol când nu e activ
      layout.tsx                  ← primește slot @modal
```

```tsx
// app/(dashboard)/invoices/layout.tsx
export default function InvoicesLayout({
  children,
  modal
}: {
  children: React.ReactNode
  modal:    React.ReactNode
}) {
  return (
    <>
      {children}
      {modal}   {/* modal e null din default.tsx când nu e activ */}
    </>
  )
}

// app/(dashboard)/invoices/@modal/default.tsx
export default function ModalDefault() { return null }

// app/(dashboard)/invoices/@modal/(.)invoices/[id]/page.tsx
import { InvoiceModal } from '@/components/InvoiceModal'

export default async function InvoiceModalPage({ params }: { params: { id: string } }) {
  const invoice = await getInvoice(params.id)
  if (!invoice) notFound()
  return <InvoiceModal invoice={invoice} />
}

// InvoiceModal.tsx — se închide cu router.back()
'use client'
export function InvoiceModal({ invoice }: { invoice: Invoice }) {
  const router = useRouter()
  return (
    <div className="fixed inset-0 bg-black/50 z-50" onClick={() => router.back()}>
      <div className="bg-white rounded-lg p-6 max-w-lg mx-auto mt-20" onClick={e => e.stopPropagation()}>
        <h2>{invoice.client_name}</h2>
        {/* ... */}
      </div>
    </div>
  )
}
// (.) = interceptează ruta din același nivel (invoices)
// (..) = din nivelul parent
// ✓ URL se schimbă → shareable, back-button funcționează
// ✓ Acces direct la URL → pagina completă (nu modal)
```

**Parallel Routes — slot-uri independente:**

```
app/
  dashboard/
    @metrics/
      default.tsx     ← obligatoriu (fallback când slot-ul nu are match)
      page.tsx
    @activity/
      default.tsx
      page.tsx
    layout.tsx
    page.tsx
```

```tsx
// app/dashboard/layout.tsx
export default function DashboardLayout({
  children,
  metrics,
  activity
}: {
  children:  React.ReactNode
  metrics:   React.ReactNode
  activity:  React.ReactNode
}) {
  return (
    <div className="p-6 space-y-6">
      {children}
      <div className="grid grid-cols-2 gap-6">
        {metrics}
        {activity}
      </div>
    </div>
  )
}
// @metrics și @activity se încarcă complet independent
// Error/loading separat per slot
```

---

## BLOC 5 — Debugging și Toolkit

---

### Parte 12 — 18 Greșeli Comune App Router

**G1 — `'use client'` pe page.tsx pentru un singur element interactiv**

```tsx
// ✗ Toată pagina la client pentru un buton
'use client'
export default function InvoicesPage() {
  const [open, setOpen] = useState(false)
  /* ... */
}

// ✓ Izolezi exact butonul
export default async function InvoicesPage() {
  const invoices = await getInvoices()
  return <><InvoiceTable invoices={invoices} /><CreateButton /></>
}
// CreateButton.tsx cu 'use client'
```

**G2 — `redirect()` în try/catch**

```ts
// ✗ NEXT_REDIRECT prins de catch → redirect nu se face niciodată
try { await save(); redirect('/') } catch (e) { return { error: 'failed' } }

// ✓ redirect() afară din try/catch
try { await save() } catch (e) { return { error: 'failed' } }
redirect('/')
```

**G3 — `getSession()` server-side pentru autentificare**

```ts
// ✗ Bypass-abil cu JWT manipulat
const { data: { session } } = await supabase.auth.getSession()

// ✓ Validare server-side
const { data: { user } } = await supabase.auth.getUser()
```

**G4 — Context Provider cu `'use client'` pe root layout**

```tsx
// ✗ Tot arborele devine client
'use client'
export default function RootLayout({ children }) {
  return <ThemeProvider>{children}</ThemeProvider>
}

// ✓ Provider izolat în components/Providers.tsx cu 'use client'
// app/layout.tsx rămâne Server Component
```

**G5 — `Date` object server→client**

```tsx
// ✗ Date object pierde metode după serializare — eroare la runtime
const date = new Date()
return <ClientComponent date={date} />

// ✓ Trimite string ISO (cum vine din Supabase)
return <ClientComponent date={invoice.created_at} />
// SAU formatezi pe server:
const formatted = new Intl.DateTimeFormat('ro-RO').format(new Date(invoice.created_at))
return <ClientComponent date={formatted} />
```

**G6 — `useSearchParams()` fără Suspense — build error în producție**

```tsx
// ✗ Next.js 14: build fail fără Suspense
'use client'
export default function Page() { const params = useSearchParams() }

// ✓ Învelești în Suspense
export default function Page() {
  return <Suspense fallback={<div>Se încarcă...</div>}><SearchComponent /></Suspense>
}
'use client'
function SearchComponent() { const params = useSearchParams() }
```

**G7 — `revalidatePath()` / `revalidateTag()` uitată după mutație**

```ts
// ✗ UI rămâne stale — cache-ul nu e invalidat
export async function createClient(formData: FormData) {
  await supabase.from('clients').insert({ /* ... */ })
  redirect('/clients')  // datele vechi în cache
}

// ✓ Invalidezi ÎNAINTE de redirect
export async function createClient(formData: FormData) {
  await supabase.from('clients').insert({ /* ... */ })
  revalidateTag('clients')
  redirect('/clients')
}
```

**G8 — `NEXT_PUBLIC_` prefix pe chei secrete**

```bash
# ✗ Expus în bundle JS — vizibil în DevTools
NEXT_PUBLIC_ANTHROPIC_API_KEY=sk-ant-...

# ✓ Server-only
ANTHROPIC_API_KEY=sk-ant-...
```

**G9 — `middleware.ts` în `/app` în loc de rădăcină**

```
✗ app/middleware.ts     → ignorat complet, fără eroare!
✓ middleware.ts         → lângă package.json
```

**G10 — `Promise.all` fără error handling**

```ts
// ✗ Dacă ORICARE query eșuează → toate datele pierdute
const [{ data: a }, { data: b }] = await Promise.all([...])

// ✓ Verifici fiecare eroare separat
const [resultA, resultB] = await Promise.all([queryA, queryB])
if (resultA.error) throw resultA.error
if (resultB.error) throw resultB.error
```

**G11 — Lipsă `import 'server-only'` în lib server**

```ts
// ✗ Fără protecție: lib/supabase/server.ts importat în Client Component
// → SUPABASE_SERVICE_ROLE_KEY în bundle JS

// ✓ Prima linie în orice fișier server-only
import 'server-only'  // → eroare la BUILD, nu la runtime
```

**G12 — `async/await` în `useEffect` fără cleanup**

```tsx
// ✗ Race condition + setState pe componentă unmounted
useEffect(() => {
  async function load() {
    const data = await fetchData(id)
    setData(data)  // poate rula pentru un id vechi
  }
  load()
}, [id])

// ✓ Flag de cleanup
useEffect(() => {
  let cancelled = false
  async function load() {
    const data = await fetchData(id)
    if (!cancelled) setData(data)
  }
  load()
  return () => { cancelled = true }
}, [id])
```

**G13 — Layout cu fetch expensive ne-cached**

```tsx
// ✗ Layout rulează la fiecare request — query costisitor = latency pe tot dashboard-ul
export default async function DashboardLayout({ children }) {
  const perms = await getFullPermissionMatrix()  // 300ms la fiecare request
}

// ✓ Date minime în layout + React.cache() pentru ce se repetă
export default async function DashboardLayout({ children }) {
  const user = await getCurrentUser()   // React.cache() → memoizat per request
  return <Sidebar user={user}>{children}</Sidebar>
}
```

**G14 — `<a>` pentru navigare internă**

```tsx
// ✗ Full page reload, pierde state
<a href="/dashboard/invoices">Facturi</a>

// ✓ SPA navigation, prefetch automat
<Link href="/dashboard/invoices">Facturi</Link>
```

**G15 — Hydration mismatch cu valori non-deterministe**

```tsx
// ✗ Server render ≠ Client render = eroare hydration
'use client'
export function Badge() {
  return <span>ID: {Math.random()}</span>
  // sau: {new Date().toLocaleString()} — diferit server vs client
}

// ✓ Calculezi în useEffect (după hydration)
'use client'
export function CurrentTime() {
  const [time, setTime] = useState('')
  useEffect(() => setTime(new Date().toLocaleString('ro-RO')), [])
  return <span>{time}</span>
}

// ✓ SAU folosești suppressHydrationWarning (pentru valori time-sensitive)
<span suppressHydrationWarning>{new Date().toLocaleString()}</span>
```

**G16 — `router.refresh()` confundat cu `revalidatePath()`**

```tsx
// DIFERENȚA CRITICĂ:
// router.refresh() = re-fetch RSC payload CLIENT-SIDE, nu invalidează Data Cache
// revalidatePath()  = invalidează Data Cache SERVER-SIDE, router-ul primește date noi

// ✗ Dacă faci router.refresh() după insert → primești date DIN CACHE, nu noul rând
const router = useRouter()
await createInvoice(formData)
router.refresh()   // re-fetchează RSC, dar Data Cache e intact = date vechi posibile

// ✓ Server Action invalidează cache → router.refresh() obține date noi
// În Server Action:
//   revalidateTag('invoices')   → Data Cache invalidat
//   redirect('/invoices')       → sau lași clientul să facă router.refresh()

// ✓ Când e corect router.refresh():
// - Supabase Realtime → schimbare externă → vrei să re-fetch-ezi date server
// - Operații care nu trec prin propriile Server Actions (ex: alt tab a modificat)
```

**G17 — Server Action apelat din `useEffect`**

```tsx
// ✗ GREȘIT: Server Actions nu sunt pentru efecte — sunt pentru mutații user-triggered
useEffect(() => {
  logPageView()          // Server Action într-un effect = anti-pattern
}, [])

// ✓ Server Actions = răspuns la acțiuni utilizator (click, submit)
// Pentru logging/tracking automat → Route Handler sau analytics library
// Pentru date inițiale → fetch direct în Server Component (nu useEffect)
```

**G18 — Double-submit: lipsă pending state după Server Action**

```tsx
// ✗ User poate click de mai multe ori — creează N înregistrări
async function handleSubmit() {
  await createInvoice(data)   // fără loading state → butonul e activ
}

// ✓ useTransition previne double-submit
'use client'
const [isPending, startTransition] = useTransition()

<button
  onClick={() => startTransition(() => createInvoice(data))}
  disabled={isPending}
>
  {isPending ? 'Se salvează...' : 'Salvează'}
</button>

// SAU: useActionState cu isPending (React 19)
// const [state, formAction, isPending] = useActionState(createInvoice, null)
```

---

### Parte 13 — TypeScript pentru Next.js

**PageProps:**

```tsx
// Next.js 14 — sincron
type PageProps = {
  params:       { id: string }
  searchParams: { [key: string]: string | string[] | undefined }
}

export default async function Page({ params, searchParams }: PageProps) {
  const { id } = params
  const status = typeof searchParams.status === 'string' ? searchParams.status : undefined
}

// Next.js 15 — params și searchParams devin Promise (BREAKING CHANGE)
type PageProps15 = {
  params:       Promise<{ id: string }>
  searchParams: Promise<{ [key: string]: string | string[] | undefined }>
}
export default async function Page({ params, searchParams }: PageProps15) {
  const { id } = await params
  const { status } = await searchParams
}

// ✓ Verifici versiunea Next.js în package.json înainte de a migra
// ✓ Ambele sintaxe coexistă pe perioade — Next.js 14 sintaxa funcționează în 15 cu deprecation warning
```

**Server Action return type:**

```ts
type ActionResult<T = void> =
  | { success: true;  data: T }
  | { success: false; error: string }

export async function createInvoice(
  _prev: ActionResult<Invoice> | null,
  formData: FormData
): Promise<ActionResult<Invoice>> {
  if (error) return { success: false, error: error.message }
  return { success: true, data: invoice }
}
// Client: discriminated union → TypeScript știe exact ce câmpuri există
```

**Types din Supabase generate + Zod integration:**

```bash
npx supabase gen types typescript --project-id your-id > types/supabase.ts
npx supabase gen types typescript --local > types/supabase.ts
```

```ts
type Invoice       = Database['public']['Tables']['invoices']['Row']
type InvoiceInsert = Database['public']['Tables']['invoices']['Insert']
type CreateInvoiceInput = Omit<InvoiceInsert, 'id' | 'created_at' | 'updated_at' | 'user_id'>

// ✓ z.infer — derivă tipul din Zod schema (single source of truth)
const InvoiceSchema = z.object({
  client_name: z.string().min(1),
  amount:      z.coerce.number().positive(),
  status:      z.enum(['draft', 'sent', 'paid'])
})
type InvoiceFormData = z.infer<typeof InvoiceSchema>
// Nu declari tipul manual — Zod îl generează automat din schema validare

// ✓ satisfies — tip strict fără widening
const config = {
  supabase: { url: process.env.NEXT_PUBLIC_SUPABASE_URL! }
} satisfies Record<string, Record<string, string>>
// typeof config rămâne precis (nu widened la Record)
```

**`use()` hook — types:**

```ts
// Server Component — pasează Promise la Client
type Props = { userPromise: Promise<User | null> }

// Client Component — consumă cu use()
'use client'
import { use } from 'react'
function Component({ userPromise }: Props) {
  const user = use(userPromise)  // User | null (TypeScript știe tipul)
}
```

**Metadata:**

```tsx
export const metadata: Metadata = { title: 'Facturi' }

export async function generateMetadata({ params }: { params: { id: string } }): Promise<Metadata> {
  const invoice = await getInvoice(params.id)
  if (!invoice) return { title: 'Factură negăsită' }
  return { title: `#${invoice.number} — ${invoice.client_name}` }
}
```

---

### Parte 14 — Structura de Proiect

```
my-app/
├── app/
│   ├── (auth)/
│   │   ├── login/page.tsx
│   │   ├── signup/page.tsx
│   │   ├── layout.tsx           ← layout minimal (fără nav)
│   │   └── auth/callback/route.ts
│   ├── (dashboard)/
│   │   ├── dashboard/page.tsx
│   │   ├── invoices/
│   │   │   ├── @modal/          ← Intercepting Routes (modals)
│   │   │   │   ├── (.)invoices/[id]/page.tsx
│   │   │   │   └── default.tsx
│   │   │   ├── page.tsx
│   │   │   ├── loading.tsx
│   │   │   ├── error.tsx        ← 'use client' obligatoriu
│   │   │   └── [id]/page.tsx
│   │   ├── clients/page.tsx
│   │   └── layout.tsx           ← layout cu sidebar + header
│   ├── api/
│   │   └── webhooks/stripe/route.ts
│   ├── layout.tsx               ← Root Layout (fonts, Providers)
│   ├── not-found.tsx
│   ├── global-error.tsx         ← 'use client' + <html><body>
│   └── error.tsx
│
├── components/
│   ├── ui/                      ← Button, Input, Modal, Badge, Skeleton
│   ├── dashboard/               ← Componente specifice dashboard
│   ├── forms/
│   └── Providers.tsx            ← Context Providers ('use client')
│
├── lib/
│   ├── supabase/
│   │   ├── server.ts            ← createServerClient() + 'server-only'
│   │   ├── client.ts            ← createBrowserClient()
│   │   └── admin.ts             ← createAdminClient() + 'server-only'
│   ├── data/
│   │   ├── user.ts              ← getCurrentUser() cu React.cache()
│   │   ├── invoices.ts          ← getCachedInvoices() cu unstable_cache
│   │   └── clients.ts
│   ├── utils.ts                 ← cn(), formatCurrency(), formatDate()
│   └── env.ts                   ← validare env vars la startup
│
├── actions/                     ← Server Actions (separate de /app)
│   ├── invoices.ts
│   ├── clients.ts
│   └── auth.ts
│
├── types/
│   ├── supabase.ts              ← generat de CLI Supabase
│   └── index.ts
│
├── hooks/                       ← Custom hooks ('use client')
│   └── useDebounce.ts
│
├── middleware.ts                ← LA RĂDĂCINĂ (nu în /app!)
├── next.config.ts
├── env.d.ts
├── .env.local                   ← gitignored
└── .env.example                 ← commituit (fără valori reale)
```

**Convenții:**
```
Componente:   PascalCase       → InvoiceTable.tsx
Pagini/Rute:  kebab-case       → invoice-details/
Hooks:        camelCase + use  → useDebounce.ts
Actions:      camelCase verbe  → createInvoice, deleteClient
Lib/utils:    camelCase        → formatCurrency, getCurrentUser
Types:        PascalCase       → Invoice, ActionResult
```

---

### Parte 15 — Checklist Pre-Deploy

**Securitate:**
- [ ] `getUser()` (nu `getSession()`) pentru orice validare auth server-side
- [ ] `import 'server-only'` în `lib/supabase/server.ts` și `lib/supabase/admin.ts`
- [ ] Nicio variabilă secretă cu prefix `NEXT_PUBLIC_`
- [ ] Server Actions validează input (Zod sau manual)
- [ ] Route Handlers returnează 401 pentru neautentificați
- [ ] RLS activat + FORCE RLS pe toate tabelele Supabase
- [ ] Auth callback validează `redirectTo` (previne Open Redirect)
- [ ] `.env.local` în `.gitignore`
- [ ] Security headers în `next.config.ts` (inclusiv **CSP**)
- [ ] Rate limiting pe API routes expuse public (Upstash)

**Performanță:**
- [ ] Fetch-uri independente cu `Promise.all()` (nu sequential)
- [ ] Date inițiale în Server Components (nu `useEffect + fetch`)
- [ ] `React.cache()` pentru funcții apelate din mai multe locuri
- [ ] `unstable_cache` pentru query-uri Supabase frecvente
- [ ] `next/image` cu `sizes` prop pentru imagini responsive
- [ ] `next/font` în loc de Google Fonts CDN
- [ ] `next/dynamic` cu `ssr: false` pentru browser-only (charts, maps, editors)
- [ ] `Suspense` boundaries pentru componente cu fetch lent
- [ ] `revalidateTag` / `revalidatePath` după fiecare mutație

**Build:**
- [ ] `npm run build` fără erori TypeScript sau ESLint critice
- [ ] `useSearchParams()` învelit în `<Suspense>`
- [ ] `middleware.ts` la rădăcina proiectului (nu în `/app`)
- [ ] `remotePatterns` în `next.config.ts` pentru imagini externe
- [ ] `.env.example` commituit
- [ ] `global-error.tsx` prezent (pentru erori în root layout)

**Config:**
- [ ] Toate variabilele de mediu în Vercel (Production + Preview)
- [ ] Supabase Auth: redirect URLs adăugate (Settings → URL Configuration)
- [ ] Sentry DSN configurat dacă folosești error monitoring

---

### Parte 16 — Deployment Vercel

**Comenzi esențiale:**

```bash
vercel                          # Preview deployment
vercel --prod                   # Production deployment
vercel env pull .env.local      # Descarcă env vars din Vercel local
vercel logs <url> --follow      # Logs live
vercel inspect <url>            # Detalii deployment + build logs
vercel rollback [deployment-id] # Rollback la deployment anterior
```

**Security headers complet în `next.config.ts` (inclusiv CSP):**

```ts
import type { NextConfig } from 'next'

const nextConfig: NextConfig = {
  images: {
    remotePatterns: [{ protocol: 'https', hostname: '*.supabase.co' }]
  },

  async headers() {
    // CSP adaptat pentru Next.js + Supabase + Tailwind
    // unsafe-inline: necesar pentru Next.js hydration inline scripts
    // Ideal: nonce-uri generate în middleware pentru CSP strict (advanced)
    const ContentSecurityPolicy = [
      "default-src 'self'",
      "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://vercel.live",
      "style-src 'self' 'unsafe-inline'",
      "img-src 'self' blob: data: https://*.supabase.co https://lh3.googleusercontent.com https://avatars.githubusercontent.com",
      "font-src 'self'",
      "connect-src 'self' https://*.supabase.co wss://*.supabase.co https://vitals.vercel-insights.com",
      "frame-ancestors 'none'",
      "base-uri 'self'",
      "form-action 'self'"
    ].join('; ')

    return [
      {
        source: '/(.*)',
        headers: [
          { key: 'Content-Security-Policy',   value: ContentSecurityPolicy },
          { key: 'X-Frame-Options',           value: 'DENY' },
          { key: 'X-Content-Type-Options',    value: 'nosniff' },
          { key: 'Referrer-Policy',           value: 'strict-origin-when-cross-origin' },
          { key: 'Permissions-Policy',        value: 'camera=(), microphone=(), geolocation=()' },
          { key: 'Strict-Transport-Security', value: 'max-age=63072000; includeSubDomains; preload' }
        ]
      }
    ]
  }
}

export default nextConfig
```

**Vercel Analytics (1 linie):**

```tsx
// app/layout.tsx
import { Analytics }     from '@vercel/analytics/react'
import { SpeedInsights } from '@vercel/speed-insights/next'

export default function RootLayout({ children }) {
  return (
    <html><body>
      {children}
      <Analytics />
      <SpeedInsights />
    </body></html>
  )
}
```

**Sentry pentru Next.js (error monitoring):**

```bash
npx @sentry/wizard@latest -i nextjs
# Wizard configurează automat:
# - sentry.client.config.ts
# - sentry.server.config.ts
# - next.config.ts instrumentare
```

```ts
// Variabile necesare în Vercel:
// SENTRY_DSN=https://...@sentry.io/...
// SENTRY_ORG, SENTRY_PROJECT (pentru source maps în producție)
```

**Environment Variables în Vercel:**

```
Production: URL real, DB prod, Stripe live keys
Preview:    URL staging, DB test, Stripe test keys
Development: din .env.local (nu din Vercel)
```

---

### Parte 17 — Quick Reference Card

```
══ SUPABASE CLIENT ════════════════════════════════
Server Components / Actions / Route Handlers:
  import { createServerClient } from '@/lib/supabase/server'
  const supabase = await createServerClient()
  const { data: { user } } = await supabase.auth.getUser()
  if (!user) redirect('/login')

Client Components:
  import { createSupabaseBrowserClient } from '@/lib/supabase/client'
  const supabase = createSupabaseBrowserClient()

══ SERVER ACTION (pattern complet) ════════════════
  'use server'
  export async function action(_prev, formData: FormData) {
    const supabase = await createServerClient()
    const { data: { user } } = await supabase.auth.getUser()
    if (!user) redirect('/login')
    // validare Zod → insert/update/delete
    revalidateTag('tag')
    redirect('/path')       ← AFARĂ din try/catch
  }

══ bind() PENTRU ARGUMENTE EXTRA ══════════════════
  const deleteWithId = deleteInvoice.bind(null, id)
  <form action={deleteWithId}><button type="submit">Șterge</button></form>

══ useTransition — SERVER ACTION DIN BUTTON ══════
  const [isPending, startTransition] = useTransition()
  <button
    disabled={isPending}
    onClick={() => startTransition(() => serverAction(id))}
  >
    {isPending ? 'Se procesează...' : 'Acțiune'}
  </button>

══ PARALLEL FETCH CU ERROR HANDLING ═══════════════
  const [invResult, cliResult] = await Promise.all([
    supabase.from('invoices').select('*'),
    supabase.from('clients').select('*')
  ])
  if (invResult.error) throw invResult.error
  if (cliResult.error) throw cliResult.error

══ React.cache() vs unstable_cache ════════════════
  React.cache():    per-render tree, resetat după request
                    → getCurrentUser(), date partajate în ierarhie
  unstable_cache(): persistent între request-uri, TTL + tags
                    → date Supabase cache-uite minute/ore

══ STREAMING PAGE ═════════════════════════════════
  export default function Page() {
    return (
      <>
        <StaticContent />
        <Suspense fallback={<Skeleton />}>
          <AsyncServerComponent />
        </Suspense>
      </>
    )
  }

══ next/dynamic ════════════════════════════════════
  const Chart = dynamic(() => import('./Chart'), {
    loading: () => <Skeleton />,
    ssr: false  // pentru browser-only (charts, maps, editors)
  })

══ useOptimistic ═══════════════════════════════════
  const [optimistic, addOptimistic] = useOptimistic(
    items,
    (state, removedId) => state.filter(i => i.id !== removedId)
  )
  async function handleDelete(id) {
    addOptimistic(id)     // UI instant
    await deleteItem(id)  // server în background
  }

══ nuqs — TYPE-SAFE URL PARAMS ════════════════════
  const [status, setStatus] = useQueryState(
    'status', parseAsString.withDefault('all')
  )
  const [page, setPage] = useQueryState(
    'page', parseAsInteger.withDefault(1)
  )

══ router.refresh() vs revalidatePath() ══════════
  revalidatePath('/path')   → SERVER: invalidează Data Cache
  router.refresh()          → CLIENT: re-fetch RSC payload
  Împreună: date mereu fresh după mutație

══ NAVIGARE ════════════════════════════════════════
  import { useRouter, usePathname } from 'next/navigation'  // ← App Router
  // ✗ NU din 'next/router' — acela e Pages Router
  <Link href="/path">Text</Link>         ← intern (SPA)
  <a href="https://ext.com">Text</a>     ← extern
  redirect('/path')                      ← Server (action/page)
  router.push('/path')                   ← Client Component
  router.refresh()                       ← re-fetch RSC payload
  notFound()                             ← activează not-found.tsx

══ FILE CONVENTIONS ════════════════════════════════
  page.tsx          → ruta
  layout.tsx        → persistent (nu se remontează)
  loading.tsx       → Suspense automat
  error.tsx         → Error Boundary ('use client' obligatoriu)
  global-error.tsx  → erori root layout ('use client' + <html><body>)
  not-found.tsx     → 404 (activat de notFound())
  route.ts          → API endpoint
  middleware.ts     → LA RĂDĂCINĂ, nu în /app

══ SECURITATE ══════════════════════════════════════
  import 'server-only'         în lib/supabase/server.ts
  getUser()    ✓ validat server-side
  getSession() ✗ bypass-abil
  NEXT_PUBLIC_ numai pentru chei non-secrete
  redirect()   afară din try/catch
  CSP header   în next.config.ts headers()

══ CACHING ═════════════════════════════════════════
  revalidatePath('/path')               → invalidează pagina
  revalidateTag('tag')                  → invalidează cu acel tag
  export const revalidate = 3600        → ISR la nivel de segment
  export const dynamic = 'force-dynamic' → mereu server-render
  staleTimes: { dynamic: 0 }           → dezactivezi Router Cache (Next.js 15)
```

---

## Appendix — Starter Template: CRUD Complet

Schema de fișiere + cod complet pentru un modul CRUD real:

```ts
// lib/supabase/server.ts
import 'server-only'
import { createServerClient as createClient } from '@supabase/ssr'
import { cookies } from 'next/headers'
import type { Database } from '@/types/supabase'

export async function createServerClient() {
  const cookieStore = await cookies()
  return createClient<Database>(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        getAll:  () => cookieStore.getAll(),
        setAll: (list) => {
          try { list.forEach(({ name, value, options }) => cookieStore.set(name, value, options)) }
          catch {}
        }
      }
    }
  )
}
```

```ts
// lib/data/user.ts
import { cache } from 'react'
import { createServerClient } from '@/lib/supabase/server'

export const getCurrentUser = cache(async () => {
  const supabase = await createServerClient()
  const { data: { user } } = await supabase.auth.getUser()
  return user ?? null
})
```

```ts
// lib/data/invoices.ts
import 'server-only'
import { unstable_cache } from 'next/cache'
import { createServerClient } from '@/lib/supabase/server'
import type { Database } from '@/types/supabase'

type Invoice = Database['public']['Tables']['invoices']['Row']

export const getCachedInvoices = unstable_cache(
  async (userId: string): Promise<Invoice[]> => {
    const supabase = await createServerClient()
    const { data, error } = await supabase
      .from('invoices').select('*')
      .eq('user_id', userId).is('deleted_at', null)
      .order('created_at', { ascending: false })
    if (error) throw error
    return data ?? []
  },
  ['user-invoices'],
  { revalidate: 300, tags: ['invoices'] }
)
```

```ts
// actions/invoices.ts
'use server'
import { z } from 'zod'
import { revalidateTag } from 'next/cache'
import { redirect } from 'next/navigation'
import { getCurrentUser } from '@/lib/data/user'
import { createServerClient } from '@/lib/supabase/server'

const InvoiceSchema = z.object({
  client_name: z.string().min(1),
  amount:      z.coerce.number().positive(),
  status:      z.enum(['draft', 'sent', 'paid']).default('draft')
})
type InvoiceFormData = z.infer<typeof InvoiceSchema>

type Result<T = void> = { success: true; data: T } | { success: false; error: string }

export async function createInvoice(_: unknown, formData: FormData): Promise<Result> {
  const user = await getCurrentUser()
  if (!user) redirect('/login')

  const parsed = InvoiceSchema.safeParse(Object.fromEntries(formData))
  if (!parsed.success) return { success: false, error: parsed.error.errors[0].message }

  const supabase = await createServerClient()
  const { error } = await supabase.from('invoices').insert({ user_id: user.id, ...parsed.data })
  if (error) return { success: false, error: error.message }

  revalidateTag('invoices')
  redirect('/dashboard/invoices')
}

export async function deleteInvoice(id: string) {
  const user = await getCurrentUser()
  if (!user) redirect('/login')

  const supabase = await createServerClient()
  const { error } = await supabase
    .from('invoices').update({ deleted_at: new Date().toISOString() })
    .eq('id', id).eq('user_id', user.id)
  if (error) throw error
  revalidateTag('invoices')
}
```

```tsx
// app/(dashboard)/invoices/page.tsx
import { Suspense } from 'react'
import { redirect } from 'next/navigation'
import { getCurrentUser } from '@/lib/data/user'
import { getCachedInvoices } from '@/lib/data/invoices'
import { InvoiceList } from '@/components/dashboard/InvoiceList'
import { CreateInvoiceButton } from '@/components/dashboard/CreateInvoiceButton'
import { TableSkeleton } from '@/components/skeletons'

export const metadata = { title: 'Facturi' }

export default async function InvoicesPage() {
  const user = await getCurrentUser()
  if (!user) redirect('/login')

  const invoices = await getCachedInvoices(user.id)

  return (
    <div className="p-6 space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Facturi</h1>
        <CreateInvoiceButton />
      </div>
      <Suspense fallback={<TableSkeleton rows={8} />}>
        <InvoiceList invoices={invoices} />
      </Suspense>
    </div>
  )
}
```

```tsx
// components/dashboard/InvoiceList.tsx
'use client'
import { useOptimistic, useTransition } from 'react'
import { deleteInvoice } from '@/actions/invoices'
import type { Database } from '@/types/supabase'

type Invoice = Database['public']['Tables']['invoices']['Row']

export function InvoiceList({ invoices }: { invoices: Invoice[] }) {
  const [optimistic, removeOptimistic] = useOptimistic(
    invoices,
    (state, deletedId: string) => state.filter(inv => inv.id !== deletedId)
  )
  const [isPending, startTransition] = useTransition()

  function handleDelete(id: string) {
    startTransition(async () => {
      removeOptimistic(id)   // UI instant
      await deleteInvoice(id)
    })
  }

  if (optimistic.length === 0) {
    return <p className="text-gray-500 text-center py-12">Nu ai facturi încă.</p>
  }

  return (
    <div className="border rounded-lg overflow-hidden">
      <table className="w-full">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-4 py-3 text-left text-sm font-medium text-gray-600">Client</th>
            <th className="px-4 py-3 text-left text-sm font-medium text-gray-600">Sumă</th>
            <th className="px-4 py-3 text-left text-sm font-medium text-gray-600">Status</th>
            <th className="px-4 py-3" />
          </tr>
        </thead>
        <tbody className="divide-y">
          {optimistic.map(invoice => (
            <tr key={invoice.id} className="hover:bg-gray-50">
              <td className="px-4 py-3">{invoice.client_name}</td>
              <td className="px-4 py-3">{invoice.amount.toLocaleString('ro-RO')} RON</td>
              <td className="px-4 py-3">
                <span className={`px-2 py-1 rounded text-xs font-medium ${
                  invoice.status === 'paid'  ? 'bg-green-100 text-green-700' :
                  invoice.status === 'sent'  ? 'bg-blue-100 text-blue-700'  :
                  'bg-gray-100 text-gray-600'
                }`}>
                  {invoice.status}
                </span>
              </td>
              <td className="px-4 py-3 text-right">
                <button
                  onClick={() => handleDelete(invoice.id)}
                  disabled={isPending}
                  className="text-red-500 hover:text-red-700 text-sm disabled:opacity-50"
                >
                  Șterge
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
```

---

*Proiecte de referință: Vibe Budget · ERP Financiar · Clinică Medicală · StudioFlow · Descrieri Produse*
*Actualizat: Mai 2026 — v2.0 cu rafinări exhaustive expert:*

**Fix-uri v1.1 (prima rundă):**
- *ADĂUGAT: `import 'server-only'` + admin client cu service role*
- *ADĂUGAT: Context Providers pattern — izolat în Client Component*
- *ADĂUGAT: `React.cache()` vs `unstable_cache` persistent*
- *ADĂUGAT: `bind()` pattern + `useOptimistic` + `next/dynamic`*
- *ADĂUGAT: `Link`, `notFound()`, `sizes` + `blur`, security headers, CORS, Open Redirect*
- *FIX: `Promise.all` cu error handling per query, Date objects, useFormStatus*

**Fix-uri v2.0 (a doua rundă — exhaustivă):**
- *FIX REGRESIE: G15 `useflowsuppressHydrationWarning` → `suppressHydrationWarning` corect*
- *FIX: G7 structura cod ✗/✓ separată corect în funcții distincte*
- *ADĂUGAT: `useRouter` / `usePathname` din `next/navigation` (nu `next/router`)*
- *ADĂUGAT: `router.refresh()` — distincție față de `revalidatePath()` + pattern Realtime*
- *ADĂUGAT: `generateStaticParams` + `dynamicParams` — SSG cu rute dinamice*
- *ADĂUGAT: `global-error.tsx` — distincție față de `error.tsx`, ierarhie completă*
- *ADĂUGAT: `useTransition` + `startTransition` — Server Actions din event handlers*
- *ADĂUGAT: `nuqs` — type-safe URL search params pentru filtre/paginare*
- *ADĂUGAT: `use()` hook React 19 — citire Promise în Client Component*
- *ADĂUGAT: Rate limiting cu Upstash Redis în Middleware*
- *ADĂUGAT: Notă performanță middleware — `getUser()` HTTP call per request*
- *ADĂUGAT: Router Cache control — `staleTimes`, `router.refresh()` vs server revalidation*
- *ADĂUGAT: `use cache` directive Next.js 15 — `cacheTag()`, `cacheLife()`*
- *ADĂUGAT: Intercepting Routes — modal routing pattern `(.)` complet*
- *ADĂUGAT: G16 `router.refresh()` vs `revalidatePath()`, G17 Server Action în useEffect, G18 double-submit*
- *ADĂUGAT: `z.infer<typeof Schema>` + `satisfies` operator în TypeScript section*
- *ADĂUGAT: Next.js 15 breaking changes — `params`/`searchParams` ca Promises*
- *ADĂUGAT: CSP (Content Security Policy) — cel mai important header, absent în v1.1*
- *ADĂUGAT: Sentry integration pentru Next.js (error monitoring producție)*
- *ADĂUGAT: `SUPABASE_JWT_SECRET` în env vars (pentru verificare JWT locală)*
- *ACTUALIZAT: Appendix cu `useTransition` + `z.infer` + `global-error.tsx` în structura proiect*
- *ACTUALIZAT: Checklist Pre-Deploy cu CSP + global-error.tsx + rate limiting + Sentry*
- *ACTUALIZAT: Quick Reference Card cu toate pattern-urile noi*
