# Ghid Authentication & Authorization v4.0
## JWT · RBAC · Supabase RLS · MFA · Audit · Compliance · Testing

**Stack:** Next.js 14+ App Router | Supabase v2 | React 18+ | TypeScript  
**Versiune:** 4.0 — Mai 2026  
**Acoperire:** JWT · PKCE · OAuth · Magic Links · Passkeys · RLS · Storage · RBAC · MFA · Session Management · Audit · GDPR · Testing · Operational Security

---

## BLOC 1 — Fundamentele Autentificării

### S1 — JWT Anatomia, PKCE și Securitatea Callback-ului OAuth

**Structura unui JWT Supabase:**
```
eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ1c2VyLXV1aWQiLCJpYXQiOjE3...}.signature
      HEADER                              PAYLOAD                   SIGNATURE
```

Claims standard: `sub` (user UUID), `iat` (emis la), `exp` (expiră la), `aud` (audiența)  
Claims Supabase: `email`, `phone`, `role`, `user_metadata`, `app_metadata`, `amr` (auth methods used)

**De ce există PKCE (Proof Key for Code Exchange):**

OAuth 2.0 clasic returnează un `authorization_code` în URL la redirect. Dacă URL-ul e interceptat (log files, browser history, malicious extensions), codul poate fi schimbat pentru tokens. PKCE adaugă:
1. `code_verifier` — secret aleator generat local înainte de redirect
2. `code_challenge` — hash SHA-256 al verifier-ului, trimis la provider
3. La callback, providerul verifică că cel care face schimbul deține verifier-ul original

`exchangeCodeForSession(code)` face exact această verificare — motiv pentru care e obligatoriu în callback, nu opțional.

**Callback OAuth — Open Redirect Prevention:**
```typescript
// app/auth/callback/route.ts
import { NextRequest, NextResponse } from 'next/server'
import { createServerClient } from '@supabase/ssr'
import { cookies } from 'next/headers'

export async function GET(request: NextRequest) {
  const { searchParams, origin } = new URL(request.url)
  const code = searchParams.get('code')
  const next = searchParams.get('next') ?? '/dashboard'

  // CRITIC: Validează că next e path relativ, nu URL absolut
  // Atac: /auth/callback?next=https://evil.com → redirect cu tokens la atacator
  const safeNext =
    next.startsWith('/') && !next.startsWith('//') ? next : '/dashboard'

  if (code) {
    const cookieStore = cookies()
    const supabase = createServerClient(
      process.env.NEXT_PUBLIC_SUPABASE_URL!,
      process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
      {
        cookies: {
          getAll: () => cookieStore.getAll(),
          setAll: (cookiesToSet) => {
            cookiesToSet.forEach(({ name, value, options }) =>
              cookieStore.set(name, value, options)
            )
          },
        },
      }
    )

    const { error } = await supabase.auth.exchangeCodeForSession(code)
    if (!error) return NextResponse.redirect(`${origin}${safeNext}`)
  }

  return NextResponse.redirect(`${origin}/auth/login?error=auth_failed`)
}
```

**Account Enumeration — Protecție:**

Supabase returnează mesaje diferite în funcție de existența emailului — permite enumerarea utilizatorilor valizi.

Configurare în Supabase Dashboard:
```
Authentication → Settings → Enable email confirmations: ON
Authentication → Settings → Secure email change: ON
Authentication → Settings → Minimum password length: 12
```

La client — mesaj uniform, indiferent de cauza erorii:
```typescript
// GREȘIT — dezvăluie dacă emailul există
if (error?.message === 'User already registered') {
  return { error: 'Acest email este deja înregistrat' }
}

// CORECT — mesaj identic pentru orice eroare de auth
if (error) {
  return { error: 'Email sau parolă incorectă. Verifică datele și încearcă din nou.' }
}
```

---

### S2 — getUser() vs getSession() — Regula de Aur

| | `getSession()` | `getUser()` |
|---|---|---|
| Sursă date | Cookie local / localStorage | Supabase server (live) |
| Viteză | Instant (no network) | ~50-100ms (network) |
| Siguranță server-side | **NU** — JWT din cookie, neverificat criptografic | **DA** — verificat live cu Supabase |
| Scenariul de atac | JWT falsificat în cookie → bypass auth | Imposibil — semnătura verificată server |
| Folosit în | Client Components (UI state) | Server Components, Server Actions, Middleware |

```typescript
// SERVER — întotdeauna getUser()
const supabase = createClient() // server client
const { data: { user }, error } = await supabase.auth.getUser()
if (error || !user) redirect('/auth/login')

// CLIENT — getSession() ok pentru state local UI
const supabase = createClient() // browser client
const { data: { session } } = await supabase.auth.getSession()
if (!session) router.push('/auth/login')
```

---

### S3 — Cei 3 Clienți Supabase + Cookie Security + Env Validation

**Validare env vars la startup — fail fast, nu crash la runtime:**
```typescript
// lib/env.ts — importat în layout.tsx sau app/page.tsx (primul fișier server)
import { z } from 'zod'

const envSchema = z.object({
  NEXT_PUBLIC_SUPABASE_URL: z.string().url('NEXT_PUBLIC_SUPABASE_URL trebuie să fie URL valid'),
  NEXT_PUBLIC_SUPABASE_ANON_KEY: z.string().min(1, 'NEXT_PUBLIC_SUPABASE_ANON_KEY lipsă'),
  SUPABASE_SERVICE_ROLE_KEY: z.string().min(1, 'SUPABASE_SERVICE_ROLE_KEY lipsă'),
})

// Rulat la build time și la startup — nu la fiecare request
export const env = envSchema.parse(process.env)
// Dacă validarea eșuează: ZodError cu mesaj clar înainte de orice request
```

**`lib/supabase/server.ts`** — Server Components & Server Actions:
```typescript
import { createServerClient } from '@supabase/ssr'
import { cookies } from 'next/headers'

export function createClient() {
  const cookieStore = cookies()

  return createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        getAll: () => cookieStore.getAll(),
        setAll: (cookiesToSet) => {
          try {
            cookiesToSet.forEach(({ name, value, options }) =>
              cookieStore.set(name, value, {
                ...options,
                httpOnly: true,                              // JS nu poate citi cookie-ul
                secure: process.env.NODE_ENV === 'production', // HTTPS only în prod
                sameSite: 'lax',                             // nu 'strict' — rupe OAuth redirects
                path: '/',
              })
            )
          } catch {
            // Server Components nu pot seta cookies — ignorat intenționat
          }
        },
      },
    }
  )
}
```

**`lib/supabase/client.ts`** — Client Components:
```typescript
import { createBrowserClient } from '@supabase/ssr'

export function createClient() {
  return createBrowserClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
  )
}
```

**`lib/supabase/middleware.ts`** — Middleware:
```typescript
import { createServerClient } from '@supabase/ssr'
import { NextRequest, NextResponse } from 'next/server'

export async function updateSession(request: NextRequest) {
  let supabaseResponse = NextResponse.next({ request })

  const supabase = createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        getAll: () => request.cookies.getAll(),
        setAll: (cookiesToSet) => {
          cookiesToSet.forEach(({ name, value }) =>
            request.cookies.set(name, value)
          )
          supabaseResponse = NextResponse.next({ request })
          cookiesToSet.forEach(({ name, value, options }) =>
            supabaseResponse.cookies.set(name, value, {
              ...options,
              httpOnly: true,
              secure: process.env.NODE_ENV === 'production',
              sameSite: 'lax',
            })
          )
        },
      },
    }
  )

  const { data: { user } } = await supabase.auth.getUser()
  return { supabase, supabaseResponse, user }
}
```

**De ce `SameSite: 'lax'` și nu `'strict'`:**
- `strict` blochează cookie-ul la orice redirect cross-site — inclusiv redirect-ul de la Google/GitHub înapoi la aplicație după OAuth
- `lax` permite cookie-ul la navigare top-level (OAuth redirect) dar blochează la `fetch`/XHR cross-site (CSRF mitigation)

**Type Safety — generare tipuri din schema DB:**
```bash
# Generează tipuri TypeScript din schema Supabase
npx supabase gen types typescript --project-id YOUR_PROJECT_ID > lib/database.types.ts

# Sau local (după supabase start)
npx supabase gen types typescript --local > lib/database.types.ts
```

```typescript
// Folosit în toată aplicația
import { Database } from '@/lib/database.types'

// Client tipat
const supabase = createClient<Database>()

// Query tipat — TypeScript știe forma rândului
const { data } = await supabase.from('invoices').select('*')
// data: Database['public']['Tables']['invoices']['Row'][] | null
```

---

### S4 — Token Lifecycle: Rotație, Stale JWT, Logout + Password Change

**Refresh Token Rotation (implicit în Supabase):**

La fiecare utilizare a refresh token-ului, Supabase emite unul nou și invalidează cel vechi. Dacă tokenul vechi e re-folosit (atac replay):
1. Supabase invalidează ambele sesiuni (legitimă + atacator)
2. Utilizatorul primește evenimentul `TOKEN_REFRESH_FAILED`

**TOKEN_REFRESH_FAILED — Handler Obligatoriu:**
```typescript
// Adăugat în layout root sau auth provider
supabase.auth.onAuthStateChange((event, session) => {
  if (event === 'TOKEN_REFRESH_FAILED') {
    console.error('Session refresh failed — possible replay attack')
    window.location.href = '/auth/login?reason=session_expired'
  }

  if (event === 'SIGNED_OUT') {
    queryClient?.clear() // curăță orice cache local
  }
})
```

**Stale JWT — Decizie:**

| Scenariul | Impact | Acțiune |
|---|---|---|
| Upgrade rol (viewer → staff) | Scăzut — permisiuni noi mai târziu | Opțional: forțează re-login |
| Downgrade rol (admin → viewer) | **CRITIC** — acces admin ~1h | Force signOut **OBLIGATORIU** |
| Revocare cont | **CRITIC** — cont activ ~1h | Force signOut **OBLIGATORIU** |
| Schimbare org_id | **CRITIC** — accesează org veche | Force signOut **OBLIGATORIU** |

```typescript
// lib/supabase/admin.ts
import { createClient } from '@supabase/supabase-js'

if (typeof window !== 'undefined') {
  throw new Error('Admin client used in browser context!')
}

export const adminSupabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.SUPABASE_SERVICE_ROLE_KEY!,
  { auth: { autoRefreshToken: false, persistSession: false } }
)

export async function revokeUserSessions(targetUserId: string) {
  const { error } = await adminSupabase.auth.admin.signOut(targetUserId, 'global')
  if (error) throw new Error(`Failed to revoke: ${error.message}`)
}
```

**Password Change → Invalidare Sesiuni Active:**
```typescript
// app/account/actions/change-password.ts
'use server'
import { z } from 'zod'
import { createClient } from '@/lib/supabase/server'
import { adminSupabase } from '@/lib/supabase/admin'

const Schema = z.object({
  currentPassword: z.string().min(1),
  newPassword: z.string().min(12, 'Parola trebuie să aibă minim 12 caractere'),
})

export async function changePassword(formData: FormData) {
  const parsed = Schema.safeParse({
    currentPassword: formData.get('currentPassword'),
    newPassword: formData.get('newPassword'),
  })
  if (!parsed.success) return { error: parsed.error.errors[0].message }

  const supabase = createClient()
  const { data: { user } } = await supabase.auth.getUser()
  if (!user) return { error: 'Unauthorized' }

  // 1. Verifică parola curentă (re-autentificare)
  const { error: signInError } = await supabase.auth.signInWithPassword({
    email: user.email!,
    password: parsed.data.currentPassword,
  })
  if (signInError) return { error: 'Parola curentă incorectă' }

  // 2. Schimbă parola
  const { error } = await supabase.auth.updateUser({
    password: parsed.data.newPassword,
  })
  if (error) return { error: error.message }

  // 3. CRITIC: Revocă TOATE sesiunile active după schimbare parolă
  // Atacatorul care știa parola veche nu mai are acces
  await adminSupabase.auth.admin.signOut(user.id, 'others') // scope 'others' = toate except cea curentă

  return { success: true, message: 'Parolă schimbată. Toate celelalte sesiuni au fost deconectate.' }
}
```

**Logout Complet — scope explicit:**
```typescript
// scope: 'local' — revocă sesiunea curentă (acest device)
await supabase.auth.signOut({ scope: 'local' })

// scope: 'global' — revocă TOATE sesiunile (toate device-urile)
// Când: suspectezi compromitere, "logout din toate device-urile"
await supabase.auth.signOut({ scope: 'global' })

// scope: 'others' — revocă toate sesiunile EXCEPT cea curentă
// Când: schimbare parolă, "rămân pe acest device"
await supabase.auth.signOut({ scope: 'others' })
```

---

### S5 — Auth Providers, Magic Links și Passkeys

**Social Login — Account Linking și Edge Cases:**

Comportament Supabase la email identic:
- Email + Google cu același email: Supabase **nu linkuiește automat** — crează cont separat (risc: duplicate accounts)
- `link_identity` necesită autentificare activă (nu se poate face silențios)

```typescript
// Linkuire manuală după login cu provider nou
const { error } = await supabase.auth.linkIdentity({
  provider: 'google',
  options: {
    redirectTo: `${window.location.origin}/auth/callback?next=/account/linked`,
  },
})

// Verificare identități legate
const { data: { user } } = await supabase.auth.getUser()
const identities = user?.identities ?? []
// [{ provider: 'email', ... }, { provider: 'google', ... }]
```

OAuth scopes — solicită minimul necesar:
```typescript
await supabase.auth.signInWithOAuth({
  provider: 'google',
  options: {
    scopes: 'openid email profile', // nu 'https://www.googleapis.com/auth/contacts'
    redirectTo: `${window.location.origin}/auth/callback`,
  },
})
```

**Magic Link — Securitate:**
```typescript
// Trimitere magic link
const { error } = await supabase.auth.signInWithOtp({
  email: userEmail,
  options: {
    emailRedirectTo: `${window.location.origin}/auth/callback`,
    shouldCreateUser: false, // nu crează cont nou dacă emailul nu există
  },
})

// REGULI PENTRU MAGIC LINKS:
// 1. Single-use: Supabase invalidează automat după prima utilizare
// 2. Expiry: 1h default — configurabil în Dashboard → Auth Settings → OTP Expiry
// 3. NU logui link-ul magic în server logs (conține token sensibil):
//    console.log('Magic link sent to', email)    ✓
//    console.log('Magic link:', magicLinkUrl)    ✗ — token expus în logs

// Mesaj uniform indiferent dacă emailul există sau nu (anti-enumeration)
return { message: 'Dacă emailul există, vei primi un link de autentificare.' }
```

**Passkeys (WebAuthn) — Autentificare Fără Parolă:**

Supabase suportă passkeys din versiunea 2.x. Avantaje față de TOTP:
- Phishing-resistant — legat criptografic de domeniu
- Nu necesită app terță (Google Authenticator etc.)
- Experiență mai bună pe mobile (Touch ID, Face ID)

```typescript
// Înregistrare passkey (în pagina de securitate cont)
const { error } = await supabase.auth.mfa.enroll({
  factorType: 'phone', // sau 'webauthn' când disponibil în SDK
})

// Verificare disponibilitate passkeys în browser
const isWebAuthnAvailable =
  window.PublicKeyCredential &&
  await PublicKeyCredential.isUserVerifyingPlatformAuthenticatorAvailable()
```

---

## BLOC 2 — Row Level Security

### S6 — USING vs WITH CHECK + Strategia JWT vs DB

**Diferența fundamentală:**

| Clauza | Când rulează | Scopul |
|---|---|---|
| `USING` | La citire (SELECT, DELETE, UPDATE — filtrare rânduri) | "Ce rânduri pot vedea / șterge?" |
| `WITH CHECK` | La scriere (INSERT, UPDATE — date noi) | "Ce date pot scrie?" |

**UPDATE are nevoie de ambele — fără WITH CHECK apare vulnerability:**
```sql
-- GREȘIT — permite "furt" de înregistrare prin schimbare user_id
CREATE POLICY "update_own" ON expenses
  FOR UPDATE USING (user_id = auth.uid());
-- Atacatorul face: UPDATE expenses SET user_id = victim_id WHERE id = 'xxx'
-- USING verifică că poate modifica rândul (e al lui) → DA
-- Dar nu verifică că user_id rămâne al lui după modificare → vulnerability

-- CORECT
CREATE POLICY "update_own" ON expenses
  FOR UPDATE
  USING (user_id = auth.uid())
  WITH CHECK (user_id = auth.uid());
```

**auth.jwt() vs Subquery DB:**
```sql
-- VARIANTA 1: auth.jwt() — zero DB hit, dar stale până la 1h
CREATE POLICY "admin_access" ON invoices
  FOR ALL USING (
    (auth.jwt() -> 'app_metadata' ->> 'role') = 'admin'
  );

-- VARIANTA 2: Subquery DB — fresh întotdeauna, costă 1 query
CREATE POLICY "admin_access" ON invoices
  FOR ALL USING (
    EXISTS (
      SELECT 1 FROM user_roles
      WHERE user_id = auth.uid() AND role = 'admin'
    )
  );

-- INDEX OBLIGATORIU dacă folosești subquery
CREATE INDEX idx_user_roles_lookup ON user_roles(user_id, role);
```

**Ghid de decizie:**

| Situație | Recomandare |
|---|---|
| Date publice / low-stakes | `auth.jwt()` — performanță |
| Date financiare / medicale | Subquery DB — freshness critică |
| Middleware (routing) | `auth.jwt()` — performance, stale ok |
| Server Actions cu mutații critice | Subquery DB |
| After downgrade rol | Subquery DB + Force signOut |

---

### S7 — CRUD Policies + IDOR + Soft Delete + `TO authenticated`

**`TO authenticated` — Target Explicit:**
```sql
-- FĂRĂ TO: politica se aplică la toți utilizatorii inclusiv anon
CREATE POLICY "select_own" ON expenses
  FOR SELECT USING (user_id = auth.uid());

-- CU TO authenticated: politica se aplică DOAR utilizatorilor autentificați
CREATE POLICY "select_own" ON expenses
  FOR SELECT TO authenticated
  USING (user_id = auth.uid());

-- Politică separată pentru anon (public) dacă e necesar
CREATE POLICY "public_read" ON products
  FOR SELECT TO anon
  USING (is_published = true);
```

**Pattern complet CRUD:**
```sql
ALTER TABLE expenses ENABLE ROW LEVEL SECURITY;

CREATE POLICY "select_own" ON expenses
  FOR SELECT TO authenticated
  USING (
    user_id = auth.uid() AND
    deleted_at IS NULL AND  -- soft delete: înregistrările șterse nu sunt vizibile
    org_id IN (SELECT org_id FROM user_orgs WHERE user_id = auth.uid())
  );

CREATE POLICY "insert_own" ON expenses
  FOR INSERT TO authenticated
  WITH CHECK (
    user_id = auth.uid() AND
    deleted_at IS NULL AND
    org_id IN (SELECT org_id FROM user_orgs WHERE user_id = auth.uid())
  );

CREATE POLICY "update_own" ON expenses
  FOR UPDATE TO authenticated
  USING (user_id = auth.uid() AND deleted_at IS NULL)
  WITH CHECK (user_id = auth.uid() AND org_id = org_id);

-- Soft delete: UPDATE deleted_at, nu DELETE efectiv
CREATE POLICY "soft_delete_own" ON expenses
  FOR UPDATE TO authenticated
  USING (user_id = auth.uid())
  WITH CHECK (user_id = auth.uid()); -- permite setarea deleted_at

-- Admin vede și înregistrările șterse (pentru audit/restore)
CREATE POLICY "admin_all_including_deleted" ON expenses
  FOR ALL TO authenticated
  USING (
    EXISTS (
      SELECT 1 FROM user_roles
      WHERE user_id = auth.uid() AND role IN ('admin', 'super_admin')
    )
  );
```

**Funcție helper pentru soft delete (nu DELETE fizic):**
```typescript
// lib/db/soft-delete.ts
export async function softDelete(table: string, id: string, userId: string) {
  const supabase = createClient()
  return supabase
    .from(table as never)
    .update({ deleted_at: new Date().toISOString(), deleted_by: userId })
    .eq('id', id)
}
```

**IDOR în JOIN-uri — Vulnerabilitate Frecvent Omisă:**

RLS filtrează rândurile tabelei principale, dar JOIN-urile pot expune date din tabele cu politici slabe:
```typescript
// PERICOL — dacă payments nu are RLS propriu
const { data } = await supabase
  .from('invoices')
  .select('*, payments(*)')  // JOIN implicit
  .eq('id', invoiceId)
// Un utilizator din org A poate vedea plăți din org B prin relații indirecte
```

**Regula:** Orice tabel referențiat în JOIN trebuie să aibă politici RLS proprii, testate independent:
```sql
ALTER TABLE payments ENABLE ROW LEVEL SECURITY;

CREATE POLICY "select_payments_scoped" ON payments
  FOR SELECT TO authenticated
  USING (
    invoice_id IN (
      SELECT id FROM invoices
      WHERE org_id IN (
        SELECT org_id FROM user_orgs WHERE user_id = auth.uid()
      )
    )
  );
```

---

### S8 — Multi-tenant, Ierarhic și Temporal RLS

**Pattern org_id (ERP, Clinică):**
```sql
CREATE OR REPLACE FUNCTION get_user_org_id()
RETURNS UUID AS $$
  SELECT (auth.jwt() -> 'app_metadata' ->> 'org_id')::UUID;
$$ LANGUAGE SQL STABLE;

CREATE POLICY "tenant_isolation" ON invoices
  FOR ALL TO authenticated
  USING (org_id = get_user_org_id());
```

**RLS Ierarhic — Manager vede echipa sa:**
```sql
-- user_hierarchy: (manager_id, staff_id) — cine raportează la cine
CREATE TABLE user_hierarchy (
  manager_id UUID REFERENCES auth.users(id),
  staff_id   UUID REFERENCES auth.users(id),
  PRIMARY KEY (manager_id, staff_id)
);

CREATE INDEX idx_hierarchy_manager ON user_hierarchy(manager_id);

-- Staff reports: staff vede propriile, manager vede ale echipei, admin vede tot
CREATE POLICY "reports_hierarchical" ON staff_reports
  FOR SELECT TO authenticated
  USING (
    user_id = auth.uid()  -- propriile rapoarte
    OR
    user_id IN (          -- rapoartele subordonaților direcți
      SELECT staff_id FROM user_hierarchy WHERE manager_id = auth.uid()
    )
    OR
    EXISTS (              -- admin vede tot
      SELECT 1 FROM user_roles WHERE user_id = auth.uid() AND role IN ('admin', 'super_admin')
    )
  );
```

**RLS Temporal — Date vizibile doar în interval de timp:**
```sql
-- Exemple: oferte cu expiry, contracte active, documente cu validity period
CREATE POLICY "active_contracts_only" ON contracts
  FOR SELECT TO authenticated
  USING (
    org_id = get_user_org_id() AND
    start_date <= NOW() AND
    (end_date IS NULL OR end_date >= NOW()) -- NULL = fără expiry
  );

-- Înregistrări medicale vizibile doar în ziua consultației (receptioner)
CREATE POLICY "receptioner_day_view" ON appointments
  FOR SELECT TO authenticated
  USING (
    EXISTS (
      SELECT 1 FROM user_roles WHERE user_id = auth.uid() AND role = 'receptioner'
    ) AND
    scheduled_at::DATE = CURRENT_DATE  -- doar ziua curentă
  );
```

**Pattern clinică — roluri cu acces diferențiat:**
```sql
CREATE POLICY "clinic_appointments_access" ON appointments
  FOR SELECT TO authenticated
  USING (
    EXISTS (
      SELECT 1 FROM user_roles
      WHERE user_id = auth.uid() AND role = 'receptioner'
    )
    OR doctor_id = auth.uid()
    OR patient_id = auth.uid()
  );
```

**SECURITY DEFINER — Regula Strictă:**
```sql
-- SAFE: SQL static, fără interpolare input utilizator
CREATE OR REPLACE FUNCTION get_patient_appointments(p_patient_id UUID)
RETURNS TABLE(scheduled_at TIMESTAMPTZ, doctor_name TEXT) AS $$
  SELECT a.scheduled_at, u.full_name
  FROM appointments a
  JOIN profiles u ON u.id = a.doctor_id
  WHERE a.patient_id = p_patient_id;
$$ LANGUAGE SQL SECURITY DEFINER STABLE;

-- PERICOL: SQL dinamic = SQL Injection cu privilegii postgres
CREATE OR REPLACE FUNCTION bad_search(table_name TEXT) AS $$
BEGIN
  EXECUTE 'SELECT * FROM ' || table_name;  -- SQL Injection garantat
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
```

---

### S9 — RLS pe Tabele de Sistem — Privilege Escalation Prevention

**Dacă `user_roles` nu are RLS, oricine poate face:**
```sql
INSERT INTO user_roles (user_id, role) VALUES (auth.uid(), 'admin');
-- Privilege escalation trivial
```

**Politici obligatorii pentru `user_roles`:**
```sql
ALTER TABLE user_roles ENABLE ROW LEVEL SECURITY;

CREATE POLICY "read_own_role" ON user_roles
  FOR SELECT TO authenticated USING (user_id = auth.uid());

-- NICIUN utilizator nu poate face mutații direct
CREATE POLICY "block_insert" ON user_roles
  FOR INSERT WITH CHECK (false);

CREATE POLICY "block_update" ON user_roles
  FOR UPDATE USING (false);

CREATE POLICY "block_delete" ON user_roles
  FOR DELETE USING (false);

-- Super admin citește toate rolurile
CREATE POLICY "super_admin_read_all" ON user_roles
  FOR SELECT TO authenticated USING (
    EXISTS (
      SELECT 1 FROM user_roles ur
      WHERE ur.user_id = auth.uid() AND ur.role = 'super_admin'
    )
  );
```

**Politici obligatorii pentru `audit_log`:**
```sql
ALTER TABLE audit_log ENABLE ROW LEVEL SECURITY;

CREATE POLICY "read_own_audit" ON audit_log
  FOR SELECT TO authenticated USING (user_id = auth.uid());

CREATE POLICY "no_direct_insert" ON audit_log
  FOR INSERT WITH CHECK (false);

CREATE POLICY "no_update" ON audit_log
  FOR UPDATE USING (false);

CREATE POLICY "no_delete" ON audit_log
  FOR DELETE USING (false);

CREATE POLICY "admin_read_all" ON audit_log
  FOR SELECT TO authenticated USING (
    EXISTS (
      SELECT 1 FROM user_roles
      WHERE user_id = auth.uid() AND role IN ('admin', 'super_admin')
    )
  );
```

---

### S10 — Supabase Storage: RLS și Signed URLs

**Bucket public pentru fișiere private = breach silențios.** Fișierele medicale, financiare, contractele — niciodată în bucket public.

**Configurare bucket privat:**
```typescript
// Creat o singură dată (migration sau setup script)
const { data, error } = await adminSupabase.storage.createBucket('documents', {
  public: false,          // NICIODATĂ true pentru fișiere sensibile
  fileSizeLimit: 10485760, // 10MB
  allowedMimeTypes: ['application/pdf', 'image/jpeg', 'image/png'],
})
```

**RLS pe Storage (în Supabase Dashboard → Storage → Policies):**
```sql
-- Utilizatorii citesc doar propriile fișiere
CREATE POLICY "users_read_own_files" ON storage.objects
  FOR SELECT TO authenticated
  USING (
    bucket_id = 'documents' AND
    (storage.foldername(name))[1] = auth.uid()::TEXT
  );
-- Convenție path: documents/{user_id}/{filename}

-- Utilizatorii uploadează doar în folderul propriu
CREATE POLICY "users_upload_own" ON storage.objects
  FOR INSERT TO authenticated
  WITH CHECK (
    bucket_id = 'documents' AND
    (storage.foldername(name))[1] = auth.uid()::TEXT
  );

-- Admin citește tot
CREATE POLICY "admin_read_all_files" ON storage.objects
  FOR SELECT TO authenticated
  USING (
    bucket_id = 'documents' AND
    EXISTS (
      SELECT 1 FROM user_roles
      WHERE user_id = auth.uid() AND role IN ('admin', 'super_admin')
    )
  );
```

**Upload cu path corect:**
```typescript
// app/documents/actions/upload.ts
'use server'
export async function uploadDocument(formData: FormData) {
  const supabase = createClient()
  const { data: { user } } = await supabase.auth.getUser()
  if (!user) return { error: 'Unauthorized' }

  const file = formData.get('file') as File
  if (!file) return { error: 'Fișier lipsă' }

  // Path: {user_id}/{timestamp}_{filename} — user_id în cale = RLS funcționează
  const path = `${user.id}/${Date.now()}_${file.name}`

  const { error } = await supabase.storage
    .from('documents')
    .upload(path, file, { upsert: false })

  if (error) return { error: error.message }
  return { success: true, path }
}
```

**Signed URLs — acces temporar la fișiere private:**
```typescript
// Signed URL — expiră după N secunde, nu necesită auth header
export async function getSignedUrl(filePath: string, userId: string) {
  const supabase = createClient()
  const { data: { user } } = await supabase.auth.getUser()
  if (!user || user.id !== userId) return { error: 'Forbidden' }

  const { data, error } = await supabase.storage
    .from('documents')
    .createSignedUrl(filePath, 3600) // expiră în 1h

  if (error) return { error: error.message }
  return { url: data.signedUrl }
}

// NU folosi getPublicUrl() pentru fișiere private — returnează URL permanent accesibil
// const { data } = supabase.storage.from('documents').getPublicUrl(path) ← GREȘIT pentru private
```

---

## BLOC 3 — RBAC Patterns

### S11 — Schema RBAC + Trigger Onboarding

```sql
CREATE TYPE user_role AS ENUM (
  'super_admin', 'admin', 'manager', 'accountant', 'staff', 'viewer', 'guest'
);

CREATE TABLE user_roles (
  id         UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id    UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  role       user_role NOT NULL DEFAULT 'viewer',
  org_id     UUID REFERENCES organizations(id) ON DELETE CASCADE,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(user_id, org_id)
);

CREATE INDEX idx_user_roles_lookup ON user_roles(user_id, role, org_id);

-- Trigger: rol implicit la signup
CREATE OR REPLACE FUNCTION handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO public.user_roles (user_id, role)
  VALUES (NEW.id, 'viewer')
  ON CONFLICT (user_id, org_id) DO NOTHING; -- idempotent la retry
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION handle_new_user();
```

**Server Action schimbare rol cu audit:**
```typescript
// app/admin/actions/change-role.ts
'use server'
import { z } from 'zod'
import { createClient } from '@/lib/supabase/server'
import { adminSupabase, revokeUserSessions } from '@/lib/supabase/admin'
import { logAuditEvent } from '@/lib/audit'

const Schema = z.object({
  targetUserId: z.string().uuid(),
  newRole: z.enum(['admin', 'manager', 'accountant', 'staff', 'viewer', 'guest']),
})

export async function changeUserRole(formData: FormData) {
  const parsed = Schema.safeParse({
    targetUserId: formData.get('targetUserId'),
    newRole: formData.get('newRole'),
  })
  if (!parsed.success) return { error: 'Invalid input' }

  const supabase = createClient()
  const { data: { user } } = await supabase.auth.getUser()
  if (!user) return { error: 'Unauthorized' }

  // Verificare caller din DB — fresh
  const { data: callerRole } = await supabase
    .from('user_roles').select('role').eq('user_id', user.id).single()

  if (!callerRole || !['admin', 'super_admin'].includes(callerRole.role)) {
    return { error: 'Forbidden' }
  }

  const { data: targetCurrentRole } = await adminSupabase
    .from('user_roles').select('role').eq('user_id', parsed.data.targetUserId).single()

  const { error } = await adminSupabase
    .from('user_roles')
    .update({ role: parsed.data.newRole, updated_at: new Date().toISOString() })
    .eq('user_id', parsed.data.targetUserId)

  if (error) return { error: error.message }

  const privilegedRoles = ['admin', 'manager', 'accountant']
  const wasPrivileged = targetCurrentRole && privilegedRoles.includes(targetCurrentRole.role)
  const isDowngrade = wasPrivileged && !privilegedRoles.includes(parsed.data.newRole)

  if (isDowngrade || parsed.data.newRole === 'guest') {
    await revokeUserSessions(parsed.data.targetUserId)
  }

  await logAuditEvent({
    userId: user.id,
    action: 'CHANGE_USER_ROLE',
    resourceId: parsed.data.targetUserId,
    metadata: {
      from: targetCurrentRole?.role,
      to: parsed.data.newRole,
      sessions_revoked: isDowngrade,
    },
  })

  return { success: true }
}
```

---

### S12 — Pattern Clinică (3 Roluri)

```typescript
// lib/permissions/clinic.ts
export type ClinicRole = 'doctor' | 'nurse' | 'receptioner'

export const CLINIC_PERMISSIONS = {
  view_patient_records:    ['doctor', 'nurse'],
  edit_patient_records:    ['doctor'],
  delete_patient_records:  ['doctor'],
  view_appointments:       ['doctor', 'nurse', 'receptioner'],
  create_appointments:     ['doctor', 'nurse', 'receptioner'],
  cancel_appointments:     ['doctor', 'receptioner'],
  view_billing:            ['receptioner'],
  process_billing:         ['receptioner'],
  view_reports:            ['doctor'],
  prescribe_medication:    ['doctor'],
  administer_medication:   ['doctor', 'nurse'],
} as const satisfies Record<string, ClinicRole[]>

export type ClinicPermission = keyof typeof CLINIC_PERMISSIONS

export function hasPermission(role: ClinicRole, permission: ClinicPermission): boolean {
  return (CLINIC_PERMISSIONS[permission] as readonly ClinicRole[]).includes(role)
}
```

---

### S13 — Pattern FinanceOS (6 Roluri)

```typescript
// lib/permissions/finance.ts
export type FinanceRole = 'super_admin' | 'admin' | 'accountant' | 'manager' | 'staff' | 'viewer'

export const FINANCE_PERMISSIONS = {
  view_invoices:        ['super_admin', 'admin', 'accountant', 'manager', 'staff', 'viewer'],
  create_invoices:      ['super_admin', 'admin', 'accountant', 'staff'],
  edit_invoices:        ['super_admin', 'admin', 'accountant'],
  delete_invoices:      ['super_admin', 'admin'],
  approve_invoices:     ['super_admin', 'admin', 'manager'],
  view_expenses:        ['super_admin', 'admin', 'accountant', 'manager'],
  approve_expenses:     ['super_admin', 'admin', 'manager'],
  view_reports:         ['super_admin', 'admin', 'accountant', 'manager'],
  export_reports:       ['super_admin', 'admin', 'accountant'],
  manage_users:         ['super_admin', 'admin'],
  view_audit_log:       ['super_admin', 'admin'],
  manage_org_settings:  ['super_admin'],
  manage_integrations:  ['super_admin', 'admin'],
} as const satisfies Record<string, FinanceRole[]>

export type FinancePermission = keyof typeof FINANCE_PERMISSIONS

export function canDo(role: FinanceRole, action: FinancePermission): boolean {
  return (FINANCE_PERMISSIONS[action] as readonly FinanceRole[]).includes(role)
}

export function PermissionGuard({
  role,
  permission,
  children,
  fallback = null,
}: {
  role: FinanceRole
  permission: FinancePermission
  children: React.ReactNode
  fallback?: React.ReactNode
}) {
  if (!canDo(role, permission)) return <>{fallback}</>
  return <>{children}</>
}
```

---

### S14 — JWT Custom Claims + Strategia Stale JWT

**Custom Access Token Hook:**
```sql
CREATE OR REPLACE FUNCTION custom_access_token_hook(event JSONB)
RETURNS JSONB AS $$
DECLARE
  claims JSONB;
  user_role TEXT;
  user_org_id TEXT;
BEGIN
  claims := event -> 'claims';

  SELECT ur.role::TEXT, ur.org_id::TEXT
  INTO user_role, user_org_id
  FROM public.user_roles ur
  WHERE ur.user_id = (event ->> 'user_id')::UUID
  LIMIT 1;

  claims := jsonb_set(claims, '{app_metadata,role}', to_jsonb(COALESCE(user_role, 'viewer')));
  claims := jsonb_set(claims, '{app_metadata,org_id}', to_jsonb(COALESCE(user_org_id, '')));

  RETURN jsonb_set(event, '{claims}', claims);
END;
$$ LANGUAGE plpgsql STABLE SECURITY DEFINER;
-- Activare: Dashboard → Authentication → Hooks → Custom Access Token
```

**Strategia: Unde citești rolul?**

| Locație | Sursă | Freshness | Cost |
|---|---|---|---|
| Middleware (routing) | `auth.jwt() -> 'app_metadata'` | Max 1h stale | Zero DB |
| Server Components (display) | `auth.jwt()` | Max 1h | Zero |
| Server Actions cu mutații | Subquery DB | Fresh întotdeauna | 1 query |
| RLS date medicale / financiare | Subquery DB | Fresh întotdeauna | Per query |

---

## BLOC 4 — Next.js App Router

### S15 — Security Headers + Middleware cu Matcher Explicit

**Security Headers în `next.config.js` — Primul strat de apărare:**
```typescript
// next.config.ts
import type { NextConfig } from 'next'

const nextConfig: NextConfig = {
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          // Blochează embedding în iframe (clickjacking)
          { key: 'X-Frame-Options', value: 'DENY' },

          // Blochează MIME type sniffing
          { key: 'X-Content-Type-Options', value: 'nosniff' },

          // Referrer limitat la origin în cross-site
          { key: 'Referrer-Policy', value: 'strict-origin-when-cross-origin' },

          // HSTS — forțează HTTPS (activat doar în producție)
          ...(process.env.NODE_ENV === 'production' ? [{
            key: 'Strict-Transport-Security',
            value: 'max-age=63072000; includeSubDomains; preload',
          }] : []),

          // Limitare access la funcții browser sensibile
          {
            key: 'Permissions-Policy',
            value: 'camera=(), microphone=(), geolocation=(), payment=()',
          },

          // CSP — via header HTTP (mai puternic decât meta tag)
          {
            key: 'Content-Security-Policy',
            value: [
              "default-src 'self'",
              "script-src 'self' 'unsafe-eval' 'unsafe-inline'", // unsafe-eval necesar pentru Next.js dev
              `connect-src 'self' https://${process.env.NEXT_PUBLIC_SUPABASE_URL?.replace('https://', '')} wss://*.supabase.co`,
              "style-src 'self' 'unsafe-inline'",
              "img-src 'self' data: https:",
              "font-src 'self'",
              "frame-ancestors 'none'",
            ].join('; '),
          },
        ],
      },
    ]
  },
}

export default nextConfig
```

**Middleware — Matcher Explicit + Auth + RBAC + MFA:**
```typescript
// middleware.ts
import { NextRequest, NextResponse } from 'next/server'
import { updateSession } from '@/lib/supabase/middleware'

export async function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl

  const publicRoutes = [
    '/auth/login',
    '/auth/register',
    '/auth/callback',
    '/auth/reset-password',
    '/api/webhooks',
    '/',          // landing page
  ]
  const isPublicRoute = publicRoutes.some(r => pathname === r || pathname.startsWith(r + '/'))

  const { supabase, supabaseResponse, user } = await updateSession(request)

  if (!isPublicRoute && !user) {
    const url = new URL('/auth/login', request.url)
    url.searchParams.set('next', pathname)
    return NextResponse.redirect(url)
  }

  if (user) {
    // MFA pentru rute critice
    const mfaRoutes = ['/admin', '/finance/approve', '/patients/records', '/finance/export']
    if (mfaRoutes.some(r => pathname.startsWith(r))) {
      const { data: aal } = await supabase.auth.mfa.getAuthenticatorAssuranceLevel()
      if (aal?.currentLevel !== 'aal2') {
        return NextResponse.redirect(new URL('/auth/mfa-challenge', request.url))
      }
    }

    // RBAC din JWT (performanță — stale ok pentru routing)
    const role = (user.app_metadata as { role?: string })?.role
    if (pathname.startsWith('/admin') && !['admin', 'super_admin'].includes(role ?? '')) {
      return NextResponse.redirect(new URL('/unauthorized', request.url))
    }
  }

  return supabaseResponse
}

export const config = {
  matcher: [
    // Acoperă TOT — inclusiv /api/* — exclude doar static assets
    '/((?!_next/static|_next/image|favicon.ico|robots.txt|sitemap.xml|public/).*)',
  ],
}
```

**De ce matcher-ul e critic:**
Un matcher de tip `['/dashboard/:path*']` lasă `/api/admin/*` complet neprotejat. Un singur endpoint admin neprotejat poate compromite toată aplicația. Matcher-ul negativ (exclude ce e public) e mai sigur decât matcher-ul pozitiv (specifici ce e protejat) — nou-adăugate sunt protejate implicit.

---

### S16 — Layout Auth: O Singură Verificare

```typescript
// app/dashboard/layout.tsx
import { redirect } from 'next/navigation'
import { createClient } from '@/lib/supabase/server'

export default async function DashboardLayout({ children }: { children: React.ReactNode }) {
  const supabase = createClient()
  const { data: { user } } = await supabase.auth.getUser()
  if (!user) redirect('/auth/login')

  const { data: roleData } = await supabase
    .from('user_roles')
    .select('role')
    .eq('user_id', user.id)
    .single()

  return (
    <UserRoleProvider user={user} role={roleData?.role ?? 'viewer'}>
      <DashboardNav />
      <main>{children}</main>
    </UserRoleProvider>
  )
}

// Paginile sub layout NU re-verifică auth — layout deja face asta
// Citesc din context:
// const { role } = useUserRole()
```

---

### S17 — Server Actions: Validare Completă + Rate Limiting

```typescript
// app/finance/actions/approve-invoice.ts
'use server'
import { z } from 'zod'
import { createClient } from '@/lib/supabase/server'
import { canDo } from '@/lib/permissions/finance'
import { rateLimit } from '@/lib/rate-limit'
import { logAuditEvent } from '@/lib/audit'

const Schema = z.object({
  invoiceId: z.string().uuid(),
  notes: z.string().max(500).optional(),
})

export async function approveInvoice(formData: FormData) {
  // 1. Validare input (Zod)
  const parsed = Schema.safeParse({
    invoiceId: formData.get('invoiceId'),
    notes: formData.get('notes'),
  })
  if (!parsed.success) return { error: 'Invalid input' }

  // 2. Auth — user_id EXCLUSIV din getUser()
  const supabase = createClient()
  const { data: { user } } = await supabase.auth.getUser()
  if (!user) return { error: 'Unauthorized' }

  // 3. Rate limiting
  const rl = await rateLimit(`approve:${user.id}`)
  if (!rl.success) return { error: 'Prea multe cereri. Încearcă în 1 minut.' }

  // 4. RBAC din DB — fresh, obligatoriu pentru acțiuni financiare
  const { data: roleData } = await supabase
    .from('user_roles').select('role').eq('user_id', user.id).single()
  if (!roleData || !canDo(roleData.role as FinanceRole, 'approve_invoices')) {
    return { error: 'Forbidden' }
  }

  // 5. MFA check
  const { data: aal } = await supabase.auth.mfa.getAuthenticatorAssuranceLevel()
  if (aal?.currentLevel !== 'aal2') return { error: 'MFA_REQUIRED' }

  // 6. Acțiunea
  const { data: invoice, error } = await supabase
    .from('invoices')
    .update({ status: 'approved', approved_by: user.id, approved_at: new Date().toISOString() })
    .eq('id', parsed.data.invoiceId)
    .select().single()

  if (error) return { error: error.message }

  // 7. Audit
  await logAuditEvent({
    userId: user.id,
    action: 'APPROVE_INVOICE',
    resourceId: parsed.data.invoiceId,
    tableName: 'invoices',
    metadata: { amount: invoice.amount, notes: parsed.data.notes },
  })

  return { success: true, invoice }
}
```

**Rate Limiting cu Upstash Redis:**
```typescript
// lib/rate-limit.ts
import { Ratelimit } from '@upstash/ratelimit'
import { Redis } from '@upstash/redis'

const ratelimit = new Ratelimit({
  redis: Redis.fromEnv(),
  limiter: Ratelimit.slidingWindow(10, '1 m'),
})

export async function rateLimit(identifier: string) {
  return ratelimit.limit(identifier)
}
```

**Notă CSRF:** Server Actions Next.js verifică automat header-ul `Origin`. Route Handlers (`/api/*`) nu au această protecție — validează `Origin` manual dacă acceptă mutații:
```typescript
// app/api/data/route.ts
export async function POST(request: Request) {
  const origin = request.headers.get('origin')
  if (origin !== process.env.NEXT_PUBLIC_APP_URL) {
    return new Response('Forbidden', { status: 403 })
  }
  // ...
}
```

---

### S18 — useAuth Hook: State Complet

```typescript
// hooks/use-auth.ts
'use client'
import { useEffect, useState, useCallback } from 'react'
import { User, Session } from '@supabase/supabase-js'
import { createClient } from '@/lib/supabase/client'
import { useRouter } from 'next/navigation'

interface AuthState {
  user: User | null
  session: Session | null
  mfaLevel: 'aal1' | 'aal2' | null
  isLoading: boolean
}

export function useAuth() {
  const [state, setState] = useState<AuthState>({
    user: null, session: null, mfaLevel: null, isLoading: true,
  })
  const router = useRouter()
  const supabase = createClient()

  const getMFALevel = useCallback(async () => {
    const { data } = await supabase.auth.mfa.getAuthenticatorAssuranceLevel()
    return (data?.currentLevel ?? null) as AuthState['mfaLevel']
  }, [supabase])

  useEffect(() => {
    let cancelled = false

    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      async (event, session) => {
        if (cancelled) return

        if (event === 'TOKEN_REFRESH_FAILED') {
          setState({ user: null, session: null, mfaLevel: null, isLoading: false })
          router.push('/auth/login?reason=session_expired')
          return
        }

        const mfaLevel = session ? await getMFALevel() : null
        setState({ user: session?.user ?? null, session, mfaLevel, isLoading: false })
      }
    )

    supabase.auth.getSession().then(async ({ data: { session } }) => {
      if (cancelled) return
      const mfaLevel = session ? await getMFALevel() : null
      setState({ user: session?.user ?? null, session, mfaLevel, isLoading: false })
    })

    return () => { cancelled = true; subscription.unsubscribe() }
  }, [supabase, router, getMFALevel])

  return state
}
```

---

### S19 — Webhooks Security — Verificare Semnătură

**Supabase Database Webhooks și Auth Hooks — fără verificare semnătură, oricine poate apela endpoint-ul:**

```typescript
// app/api/webhooks/supabase/route.ts
import { NextRequest, NextResponse } from 'next/server'
import crypto from 'crypto'

// Secret setat în Supabase Dashboard → Database → Webhooks → Secret
const WEBHOOK_SECRET = process.env.SUPABASE_WEBHOOK_SECRET!

function verifyWebhookSignature(payload: string, signature: string): boolean {
  const hmac = crypto.createHmac('sha256', WEBHOOK_SECRET)
  hmac.update(payload)
  const expectedSig = hmac.digest('hex')

  // Comparație timing-safe (previne timing attacks)
  return crypto.timingSafeEqual(
    Buffer.from(signature, 'hex'),
    Buffer.from(expectedSig, 'hex')
  )
}

export async function POST(request: NextRequest) {
  const signature = request.headers.get('x-supabase-signature') ?? ''
  const rawBody = await request.text()

  if (!verifyWebhookSignature(rawBody, signature)) {
    return new NextResponse('Invalid signature', { status: 401 })
  }

  const payload = JSON.parse(rawBody)

  // Procesează evenimentul
  if (payload.type === 'INSERT' && payload.table === 'invoices') {
    await handleNewInvoice(payload.record)
  }

  return NextResponse.json({ received: true })
}
```

---

## BLOC 5 — Securitate Avansată

### S20 — MFA TOTP Complet + Recovery Codes + Passkeys

**Enrollment cu recovery codes:**
```typescript
// components/mfa/MFAEnrollment.tsx
'use client'
import { useState } from 'react'
import { createClient } from '@/lib/supabase/client'
import QRCode from 'react-qr-code'

export function MFAEnrollment({ onComplete }: { onComplete: () => void }) {
  const [step, setStep] = useState<'init' | 'verify' | 'recovery'>('init')
  const [factorId, setFactorId] = useState('')
  const [qrCode, setQrCode] = useState('')
  const [secret, setSecret] = useState('')
  const [code, setCode] = useState('')
  const [recoveryCodes, setRecoveryCodes] = useState<string[]>([])
  const [error, setError] = useState('')
  const supabase = createClient()

  async function startEnrollment() {
    const { data, error } = await supabase.auth.mfa.enroll({
      factorType: 'totp',
      friendlyName: 'Authenticator App',
    })
    if (error) { setError(error.message); return }
    setQrCode(data.totp.qr_code)
    setSecret(data.totp.secret)
    setFactorId(data.id)
    setStep('verify')
  }

  async function verifyEnrollment() {
    const { data: challenge, error: ce } = await supabase.auth.mfa.challenge({ factorId })
    if (ce) { setError(ce.message); return }

    const { error: ve } = await supabase.auth.mfa.verify({
      factorId, challengeId: challenge.id, code,
    })
    if (ve) { setError('Cod incorect. Verifică aplicația.'); return }

    // Generare recovery codes — salvate hashed în DB, afișate o singură dată
    const codes = Array.from({ length: 10 }, () =>
      `${Math.random().toString(36).slice(2, 6)}-${Math.random().toString(36).slice(2, 6)}`.toUpperCase()
    )
    // TODO: salvează codes hashed în tabel recovery_codes (bcrypt sau SHA-256)
    setRecoveryCodes(codes)
    setStep('recovery')
  }

  if (step === 'init') return (
    <div>
      <h2>Activare autentificare în 2 pași</h2>
      <p>Vei avea nevoie de o aplicație TOTP: Google Authenticator, Authy, sau 1Password.</p>
      <button onClick={startEnrollment}>Continuă</button>
    </div>
  )

  if (step === 'verify') return (
    <div>
      <h2>Scanează QR Code</h2>
      <QRCode value={qrCode} />
      <p>Sau introdu manual: <code style={{ userSelect: 'all' }}>{secret}</code></p>
      <input
        value={code} onChange={e => setCode(e.target.value.replace(/\D/g, ''))}
        placeholder="Cod 6 cifre" maxLength={6} autoFocus
      />
      {error && <p style={{ color: 'red' }}>{error}</p>}
      <button onClick={verifyEnrollment} disabled={code.length !== 6}>Activează</button>
    </div>
  )

  return (
    <div>
      <h2>⚠️ Salvează codurile de recuperare</h2>
      <p><strong>IMPORTANT:</strong> Dacă pierzi accesul la aplicația de autentificare, acestea sunt singura modalitate de a accesa contul. Fiecare cod se poate folosi o singură dată.</p>
      <div style={{ fontFamily: 'monospace', background: '#f5f5f5', padding: '1rem' }}>
        {recoveryCodes.map(c => <div key={c}>{c}</div>)}
      </div>
      <button onClick={() => navigator.clipboard.writeText(recoveryCodes.join('\n'))}>
        Copiază toate
      </button>
      <button onClick={onComplete}>Am salvat codurile — Continuă</button>
    </div>
  )
}
```

**Challenge/Verify la login:**
```typescript
export async function verifyMFA(code: string): Promise<{ success?: boolean; error?: string }> {
  const supabase = createClient()
  const { data: factors } = await supabase.auth.mfa.listFactors()
  const totp = factors?.totp?.[0]
  if (!totp) return { error: 'Niciun factor MFA configurat' }

  const { data: challenge, error: ce } = await supabase.auth.mfa.challenge({ factorId: totp.id })
  if (ce) return { error: ce.message }

  const { error } = await supabase.auth.mfa.verify({
    factorId: totp.id, challengeId: challenge.id, code,
  })
  return error ? { error: 'Cod incorect sau expirat' } : { success: true }
}
```

**Enforcement AAL2 în Server Actions critice:**
```typescript
const { data: aal } = await supabase.auth.mfa.getAuthenticatorAssuranceLevel()
if (aal?.currentLevel !== 'aal2') {
  return { error: 'MFA_REQUIRED', message: 'Acțiunea necesită autentificare în 2 pași.' }
}
```

**Passkeys — Avantaje și Roadmap:**
- Phishing-resistant (legat criptografic de domeniu — nu poți fi păcălit să introduci pe site fals)
- Fără aplicație terță (Touch ID, Face ID, Windows Hello)
- Supabase: suport passkeys în roadmap — verifică `supabase.auth.mfa.enroll({ factorType: 'webauthn' })` în versiunile viitoare
- La nivel de browser: `PublicKeyCredential.isUserVerifyingPlatformAuthenticatorAvailable()`

---

### S21 — HTML Vanilla: Modelul de Securitate

| | localStorage | Cookie httpOnly |
|---|---|---|
| Acces JavaScript | DA | NU |
| Vulnerabil XSS | DA — orice script injectat fură tokenul | NU |
| CSRF | NU | DA (mitigat cu SameSite=Lax) |
| Supabase CDN default | **localStorage** | Necesită @supabase/ssr + backend |

**CSP + Subresource Integrity:**
```html
<!-- CSP via meta tag (alternativă la header HTTP) -->
<meta http-equiv="Content-Security-Policy" content="
  default-src 'self';
  script-src 'self' https://cdn.jsdelivr.net;
  connect-src 'self' https://*.supabase.co wss://*.supabase.co;
  style-src 'self' 'unsafe-inline';
  img-src 'self' data: https:;
  frame-ancestors 'none';
">

<!-- SRI — verifică integritatea scriptului CDN -->
<!-- CDN compromis + SRI absent = cod malițios rulat în browser -->
<script
  src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2/dist/umd/supabase.js"
  integrity="sha384-[HASH_DIN_LOCKFILE]"
  crossorigin="anonymous">
</script>
```

**TOKEN_REFRESH_FAILED + innerHTML prevention:**
```javascript
const PROJECT_REF = 'your-project-ref'

supabase.auth.onAuthStateChange((event) => {
  if (event === 'TOKEN_REFRESH_FAILED') {
    localStorage.removeItem(`sb-${PROJECT_REF}-auth-token`)
    window.location.href = '/login.html?reason=session_expired'
  }
})

// XSS Prevention — niciodată innerHTML cu date utilizator
function renderUserName(name) {
  const el = document.getElementById('username')
  el.textContent = name      // CORECT
  // el.innerHTML = name     // GREȘIT — XSS garantat cu input malițios
}
```

---

### S22 — Session Management UI — Vizualizare și Revocare

```typescript
// app/account/sessions/page.tsx
import { createClient } from '@/lib/supabase/server'
import { adminSupabase } from '@/lib/supabase/admin'

export default async function SessionsPage() {
  const supabase = createClient()
  const { data: { user } } = await supabase.auth.getUser()
  if (!user) redirect('/auth/login')

  // Lista sesiunilor active (via Admin API)
  const sessions = await getActiveSessions(user.id)

  return (
    <div>
      <h1>Sesiuni active</h1>
      <p>Dacă recunoști o sesiune suspectă, o poți revoca imediat.</p>
      {sessions.map(session => (
        <SessionCard key={session.id} session={session} />
      ))}
      <RevokeAllOtherSessionsButton />
    </div>
  )
}

// Revocă o sesiune specifică
// app/account/sessions/actions.ts
'use server'
export async function revokeSession(sessionId: string) {
  const supabase = createClient()
  const { data: { user } } = await supabase.auth.getUser()
  if (!user) return { error: 'Unauthorized' }

  // Supabase nu expune revocare per-session în SDK client
  // Alternativă: signOut global + re-login pe device-ul curent
  await supabase.auth.signOut({ scope: 'global' })
  return { success: true, message: 'Toate sesiunile au fost revocate. Reconectează-te.' }
}

export async function revokeAllOtherSessions() {
  const supabase = createClient()
  const { data: { user } } = await supabase.auth.getUser()
  if (!user) return { error: 'Unauthorized' }

  await supabase.auth.signOut({ scope: 'others' })
  return { success: true, message: 'Toate celelalte sesiuni au fost revocate.' }
}
```

---

### S23 — Audit Logging Complet

```sql
CREATE TABLE audit_log (
  id          UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id     UUID REFERENCES auth.users(id) ON DELETE SET NULL, -- SET NULL la ștergere cont
  action      TEXT NOT NULL,
  table_name  TEXT,
  record_id   UUID,
  old_values  JSONB,
  new_values  JSONB,
  ip_address  INET,
  user_agent  TEXT,
  metadata    JSONB,
  created_at  TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_audit_user ON audit_log(user_id, created_at DESC);
CREATE INDEX idx_audit_action ON audit_log(action, created_at DESC);
CREATE INDEX idx_audit_record ON audit_log(table_name, record_id);

-- Trigger automat pentru mutații
CREATE OR REPLACE FUNCTION audit_trigger_fn()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO public.audit_log(user_id, action, table_name, record_id, old_values, new_values)
  VALUES (
    auth.uid(), TG_OP, TG_TABLE_NAME,
    COALESCE(NEW.id, OLD.id),
    CASE WHEN TG_OP IN ('UPDATE','DELETE') THEN to_jsonb(OLD) ELSE NULL END,
    CASE WHEN TG_OP IN ('INSERT','UPDATE') THEN to_jsonb(NEW) ELSE NULL END
  );
  RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Aplică pe tabele sensibile
CREATE TRIGGER audit_invoices
  AFTER INSERT OR UPDATE OR DELETE ON invoices
  FOR EACH ROW EXECUTE FUNCTION audit_trigger_fn();

CREATE TRIGGER audit_user_roles
  AFTER INSERT OR UPDATE OR DELETE ON user_roles
  FOR EACH ROW EXECUTE FUNCTION audit_trigger_fn();
```

**Logging manual pentru SELECT sensibil:**
```typescript
// lib/audit.ts
export async function logAuditEvent(params: {
  userId: string
  action: string
  resourceId?: string
  tableName?: string
  metadata?: Record<string, unknown>
}) {
  const supabase = createClient()
  const { error } = await supabase.from('audit_log').insert({
    user_id: params.userId,
    action: params.action,
    table_name: params.tableName,
    record_id: params.resourceId,
    metadata: params.metadata,
  })
  // Nu arunci eroarea — audit failure nu blochează operația principală
  if (error) console.error('Audit log failed:', error)
}

// Usage pentru SELECT sensibil
await logAuditEvent({
  userId: user.id,
  action: 'SELECT_SENSITIVE',
  tableName: 'patients',
  resourceId: patientId,
  metadata: { reason: 'consultation_view', ip: request.headers.get('x-forwarded-for') },
})
```

---

### S24 — Compliance: GDPR, Date Medicale, Date Financiare

**GDPR — Retention și Right to Erasure:**
```sql
-- Retention policy — rulat prin pg_cron sau job extern
DELETE FROM audit_log WHERE created_at < NOW() - INTERVAL '24 months';
```

```typescript
// Server Action: Right to Erasure
export async function processErasureRequest(targetUserId: string) {
  const admin = adminSupabase

  // 1. Anonimizare audit log (nu ștergere — integritate financiară/legală)
  await admin.from('audit_log')
    .update({ user_id: null, metadata: { anonymized: true, reason: 'gdpr_erasure' } })
    .eq('user_id', targetUserId)

  // 2. Ștergere date personale
  await admin.from('user_profiles').delete().eq('user_id', targetUserId)

  // 3. Revocare sesiuni
  await admin.auth.admin.signOut(targetUserId, 'global')

  // 4. Ștergere cont auth (ireversibil — ultimul pas)
  await admin.auth.admin.deleteUser(targetUserId)
}
```

**Date Medicale — Audit fără conținut sensibil:**
```sql
-- Loghezi CĂ s-a schimbat, nu CE s-a schimbat
CREATE OR REPLACE FUNCTION audit_medical_fn()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO public.audit_log(user_id, action, table_name, record_id, metadata)
  VALUES (
    auth.uid(), TG_OP, TG_TABLE_NAME,
    COALESCE(NEW.id, OLD.id),
    jsonb_build_object(
      'changed_fields',
      (SELECT array_agg(key) FROM jsonb_each(to_jsonb(NEW))
       WHERE to_jsonb(NEW)->>key IS DISTINCT FROM to_jsonb(OLD)->>key)
    )
    -- NU old_values/new_values — diagnostic, prescripție = date hipersensibile
  );
  RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
```

**Date Financiare — Checklist:**
- Nicio valoare de card stocată — Stripe/procesator e responsabil
- Audit pe fiecare tranzacție, aprobare, respingere cu user_id + timestamp + amount
- Hash SHA-256 pe rapoartele generate (validitate legală la contestații)
- Backup-uri criptate: Dashboard → Settings → Database → Point-in-Time Recovery activat

---

### S25 — Testarea Auth: Pattern-uri Obligatorii

**Setup:**
```typescript
// tests/setup/auth.ts
import { createClient } from '@supabase/supabase-js'

export const adminClient = createClient(
  'http://localhost:54321',
  process.env.SUPABASE_TEST_SERVICE_ROLE_KEY!
)

export async function createTestUser(email: string, role: string) {
  const { data: { user } } = await adminClient.auth.admin.createUser({
    email, password: 'TestPass123!', email_confirm: true,
  })
  if (user) await adminClient.from('user_roles').insert({ user_id: user.id, role })
  return user
}

export async function signInAs(email: string) {
  const client = createClient('http://localhost:54321', process.env.SUPABASE_TEST_ANON_KEY!)
  await client.auth.signInWithPassword({ email, password: 'TestPass123!' })
  return client
}
```

**Teste RLS — izolare, privilege escalation, IDOR:**
```typescript
// tests/rls/invoices.test.ts
describe('RLS: invoices', () => {
  let userA: string, userB: string, invoiceAId: string

  beforeAll(async () => {
    const a = await createTestUser('a@test.com', 'staff')
    const b = await createTestUser('b@test.com', 'staff')
    userA = a!.id; userB = b!.id

    const { data } = await adminClient
      .from('invoices').insert({ user_id: userA, amount: 100, org_id: 'org-a' })
      .select().single()
    invoiceAId = data!.id
  })

  it('user vede doar propriile invoice-uri', async () => {
    const client = await signInAs('a@test.com')
    const { data } = await client.from('invoices').select()
    expect(data?.every(inv => inv.user_id === userA)).toBe(true)
  })

  it('user B nu poate vedea invoice-urile lui A', async () => {
    const client = await signInAs('b@test.com')
    const { data } = await client.from('invoices').select().eq('id', invoiceAId)
    expect(data).toHaveLength(0) // RLS returnează 0 rânduri, nu eroare
  })

  it('user nu poate escalada rolul direct', async () => {
    const client = await signInAs('b@test.com')
    const { error } = await client
      .from('user_roles').insert({ user_id: userB, role: 'admin' })
    expect(error).toBeTruthy()
  })

  it('UPDATE nu poate schimba user_id la altcineva', async () => {
    const client = await signInAs('a@test.com')
    const { error } = await client
      .from('invoices').update({ user_id: userB }).eq('id', invoiceAId)
    expect(error).toBeTruthy()
  })

  it('utilizator anonim nu poate vedea niciun invoice', async () => {
    const anonClient = createClient('http://localhost:54321', process.env.SUPABASE_TEST_ANON_KEY!)
    const { data } = await anonClient.from('invoices').select()
    expect(data).toHaveLength(0)
  })

  afterAll(async () => {
    await adminClient.auth.admin.deleteUser(userA)
    await adminClient.auth.admin.deleteUser(userB)
  })
})
```

**Teste RBAC:**
```typescript
describe('RBAC: FinanceOS', () => {
  it('viewer nu poate aproba invoice-uri', () => {
    expect(canDo('viewer', 'approve_invoices')).toBe(false)
  })
  it('manager poate aproba', () => {
    expect(canDo('manager', 'approve_invoices')).toBe(true)
  })
  it('staff nu gestionează utilizatori', () => {
    expect(canDo('staff', 'manage_users')).toBe(false)
  })
  it('super_admin poate orice', () => {
    const all = Object.keys(FINANCE_PERMISSIONS) as FinancePermission[]
    all.forEach(p => expect(canDo('super_admin', p)).toBe(true))
  })
})
```

---

### S26 — Operational Security

**`service_role` Key:**
```typescript
// lib/supabase/admin.ts — server-side ONLY, verificare la import
if (typeof window !== 'undefined') {
  throw new Error('Admin client used in browser context!')
}

export const adminSupabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.SUPABASE_SERVICE_ROLE_KEY! // fără NEXT_PUBLIC_ prefix
)
```

Rotire: Dashboard → Settings → API → Service Role Key → Regenerate  
Când: angajat cu acces pleacă, scurgere suspectată, minim anual

**Supabase Auth Logs:**

Dashboard → Authentication → Logs:
- `sign_in_failed` repetat de pe același IP → brute force activ
- `token_refresh_failed` repetat → sesiune posibil compromisă
- Export CSV pentru analiză incident retrospectiv

**JWT Debugging (development only):**
```typescript
export function debugJWT(token: string) {
  if (process.env.NODE_ENV !== 'development') return
  const [, payload] = token.split('.')
  const decoded = JSON.parse(atob(payload))
  console.table({
    role: decoded.app_metadata?.role,
    org_id: decoded.app_metadata?.org_id,
    exp: new Date(decoded.exp * 1000).toISOString(),
    aal: decoded.amr,
  })
}
// jwt.io: NICIODATĂ cu production tokens — site extern, poate caching
```

**Incident Response — Acțiuni Rapide:**
1. Cont compromis: `adminSupabase.auth.admin.signOut(userId, 'global')`
2. `service_role` expusă: Rotire imediată + audit code pentru toate apelurile admin
3. XSS detectat: Revocă sesiuni active + rotire `SUPABASE_ANON_KEY` + CSP review
4. Breach date: Notificare ANSPDCP în 72h + notificare utilizatori afectați

---

### S27 — 35 Greșeli Critice

**BLOC 1: Auth Fundamentals**

**G1 — getSession() pe server**
```typescript
// Greșit: JWT neverificat server-side
const { data: { session } } = await supabase.auth.getSession()
// Corect
const { data: { user } } = await supabase.auth.getUser()
```

**G2 — user_id din request body**
```typescript
// Greșit: bypass auth trivial
const userId = formData.get('user_id')
// Corect
const { data: { user } } = await supabase.auth.getUser()
const userId = user?.id
```

**G3 — service_role cu prefix NEXT_PUBLIC_**
```bash
NEXT_PUBLIC_SUPABASE_SERVICE_ROLE_KEY=...  # Greșit — expus în bundle
SUPABASE_SERVICE_ROLE_KEY=...              # Corect
```

**G4 — await lipsă la auth calls**
```typescript
// Greșit — returnează Promise {}, nu date
const { data: { user } } = supabase.auth.getUser()
```

**G5 — Open Redirect în auth callback**
```typescript
// Greșit: /callback?next=https://evil.com
const safeNext = next.startsWith('/') && !next.startsWith('//') ? next : '/dashboard'
```

**G6 — Account enumeration prin mesaje specifice**
```typescript
// Corect — mesaj uniform pentru orice eroare de auth
if (error) return { error: 'Email sau parolă incorectă. Verifică datele.' }
```

**G7 — Magic link loggat în server logs**
```typescript
console.log('Magic link:', magicLinkUrl) // Greșit — token sensibil în logs
console.log('Magic link sent to:', email) // Corect
```

**BLOC 2: RLS**

**G8 — UPDATE fără WITH CHECK**
```sql
-- Greșit: permite schimbare user_id
FOR UPDATE USING (user_id = auth.uid())
-- Corect
FOR UPDATE USING (user_id = auth.uid()) WITH CHECK (user_id = auth.uid())
```

**G9 — Tabel fără RLS activat**
```sql
ALTER TABLE salary_data ENABLE ROW LEVEL SECURITY; -- obligatoriu pe orice tabel cu date user
```

**G10 — user_roles fără RLS → Privilege Escalation**
```sql
-- Fără RLS, oricine face: INSERT INTO user_roles VALUES (auth.uid(), 'admin')
CREATE POLICY "block_insert" ON user_roles FOR INSERT WITH CHECK (false);
```

**G11 — Politici RLS fără `TO authenticated`**
```sql
-- Fără TO: se aplică și la anon
-- Cu TO: explicit și mai sigur
FOR SELECT TO authenticated USING (...)
```

**G12 — Subquery RLS fără index**
```sql
-- Full table scan la fiecare query
CREATE INDEX idx_user_roles_lookup ON user_roles(user_id, role); -- obligatoriu
```

**G13 — SECURITY DEFINER cu SQL dinamic**
```sql
EXECUTE 'SELECT * FROM ' || table_name; -- SQL Injection cu privilegii postgres
```

**G14 — JOIN fără RLS pe tabela join-uită (IDOR)**
```typescript
// payments poate expune date cross-tenant dacă nu are politici RLS proprii
.from('invoices').select('*, payments(*)')
```

**G15 — Soft delete fără `deleted_at IS NULL` în USING**
```sql
-- Fără filtru, înregistrările "șterse" sunt vizibile
USING (user_id = auth.uid() AND deleted_at IS NULL) -- obligatoriu
```

**BLOC 3: RBAC**

**G16 — RBAC din JWT la mutații critice**
```typescript
// Stale max 1h — pentru mutații critice verifică din DB
const { data } = await supabase.from('user_roles').select('role').eq('user_id', user.id).single()
```

**G17 — Downgrade rol fără revocare sesiuni**
```typescript
await supabase.from('user_roles').update({ role: 'viewer' }).eq('user_id', id)
await revokeUserSessions(id) // OBLIGATORIU după downgrade
```

**G18 — Permisiuni hardcodate în componente**
```typescript
if (role === 'admin' || role === 'manager') { ... } // inconsistent
if (canDo(role, 'approve_invoices')) { ... }         // centralizat
```

**BLOC 4: Next.js**

**G19 — Middleware matcher incomplet**
```typescript
matcher: ['/dashboard/:path*']   // Greșit — /api/admin/* neprotejat
matcher: ['/((?!_next/static|_next/image|favicon.ico|public/).*)',] // Corect
```

**G20 — Security headers absente**
```typescript
// X-Frame-Options, X-Content-Type-Options, HSTS, CSP
// — adăugate în next.config.ts headers()
```

**G21 — Verificare auth duplicată în pagini sub layout**

Layout verifică O SINGURĂ DATĂ. Paginile citesc din context.

**G22 — Server Action fără auth check**
```typescript
// Oricine poate apela Server Actions direct prin fetch
const { data: { user } } = await supabase.auth.getUser() // obligatoriu în fiecare action
```

**G23 — Route Handler fără validare Origin**
```typescript
// Server Actions au CSRF automat — Route Handlers NU
const origin = request.headers.get('origin')
if (origin !== process.env.NEXT_PUBLIC_APP_URL) return new Response('Forbidden', { status: 403 })
```

**G24 — TOKEN_REFRESH_FAILED ignorat**
```typescript
if (event === 'TOKEN_REFRESH_FAILED') window.location.href = '/login?reason=session_expired'
```

**G25 — Logout fără scope explicit**
```typescript
await supabase.auth.signOut()              // Greșit — refresh token valid pe server
await supabase.auth.signOut({ scope: 'local' }) // Corect
```

**G26 — Password change fără revocare sesiuni**
```typescript
await supabase.auth.updateUser({ password: newPassword })
await adminSupabase.auth.admin.signOut(user.id, 'others') // Obligatoriu
```

**BLOC 5: Securitate Avansată**

**G27 — MFA absent pe acțiuni critice**
```typescript
const { data: aal } = await supabase.auth.mfa.getAuthenticatorAssuranceLevel()
if (aal?.currentLevel !== 'aal2') return { error: 'MFA_REQUIRED' }
```

**G28 — Recovery codes absente la MFA enrollment**

Fără recovery codes: pierderea device-ului = cont inaccesibil permanent.

**G29 — Bucket Storage public pentru fișiere private**
```typescript
createBucket('documents', { public: false }) // niciodată public pentru fișiere sensibile
```

**G30 — getPublicUrl() pentru fișiere private**
```typescript
// Returnează URL permanent — GREȘIT pentru private
supabase.storage.from('documents').getPublicUrl(path)
// Corect: signed URL cu expiry
supabase.storage.from('documents').createSignedUrl(path, 3600)
```

**G31 — innerHTML cu date utilizator (XSS)**
```javascript
element.innerHTML = userInput  // Greșit
element.textContent = userInput // Corect
```

**G32 — CSP absent în HTML Vanilla**

Fără CSP, XSS fură tokenul din localStorage.

**G33 — SRI absent la CDN**
```html
<script src="..." integrity="sha384-[HASH]" crossorigin="anonymous"></script>
```

**G34 — Audit log cu date medicale sensibile**
```sql
-- Greșit: stochezi diagnostic în old_values
-- Corect: loghezi câmpurile modificate, nu valorile
jsonb_build_object('changed_fields', array_agg(key))
```

**G35 — Teste RLS absente**

RLS fără teste = politici care pot fi dezactivate silențios printr-o migrare. Suite de teste pentru izolare tenant, privilege escalation, IDOR = obligatorii.

---

### S28 — Security Checklist Pre-Deploy

**Auth Setup**
- [ ] `getUser()` pe toate server paths — niciodată `getSession()` server-side
- [ ] `user_id` exclusiv din `supabase.auth.getUser()` — niciodată din params/body
- [ ] `SUPABASE_SERVICE_ROLE_KEY` fără prefix `NEXT_PUBLIC_`
- [ ] Env vars validate la startup (Zod schema)
- [ ] Auth callback cu `safeNext` validat (no open redirect)
- [ ] `TOKEN_REFRESH_FAILED` handler activ în `onAuthStateChange`
- [ ] Logout cu `scope: 'local'` sau `scope: 'global'` explicit
- [ ] Password change revocă sesiunile celorlalte device-uri
- [ ] Mesaje eroare generice (no account enumeration)
- [ ] Rate limiting pe login / register / password-reset (min 5 încercări / 15 min)
- [ ] Magic link: `shouldCreateUser: false` dacă nu vrei signup via magic link

**Security Headers**
- [ ] `X-Frame-Options: DENY` (anti-clickjacking)
- [ ] `X-Content-Type-Options: nosniff`
- [ ] `Referrer-Policy: strict-origin-when-cross-origin`
- [ ] `Strict-Transport-Security` în producție
- [ ] `Content-Security-Policy` via header HTTP (nu meta tag)
- [ ] `Permissions-Policy` limitează camera / microfon / geolocation

**RLS**
- [ ] `ENABLE ROW LEVEL SECURITY` pe toate tabelele cu date utilizator
- [ ] Politici pe `user_roles`, `audit_log`, `profiles` (tabele de sistem)
- [ ] Politici cu `TO authenticated` (nu aplicate implicit la `anon`)
- [ ] UPDATE cu `USING` + `WITH CHECK`
- [ ] Soft delete: `deleted_at IS NULL` în `USING`
- [ ] Index pe coloanele din subquery (`user_id`, `org_id`)
- [ ] Tabele join-uite au propriile politici RLS (no IDOR)
- [ ] `SECURITY DEFINER` — SQL static, niciodată input interpolat
- [ ] Teste RLS: izolare tenant, privilege escalation, IDOR, anon access

**RBAC**
- [ ] Matrice de permisiuni centralizată (`canDo()` / `hasPermission()`)
- [ ] Acțiuni critice verifică rolul din DB (nu JWT)
- [ ] Downgrade / revocare rol → `revokeUserSessions()` apelat
- [ ] `user_roles` INSERT/UPDATE/DELETE blocat (`WITH CHECK (false)`)

**Storage**
- [ ] Bucket privat (`public: false`) pentru documente sensibile
- [ ] RLS pe `storage.objects` pentru bucket-urile private
- [ ] `createSignedUrl()` cu expiry — niciodată `getPublicUrl()` pentru private
- [ ] Path include `user_id` sau `org_id` pentru RLS corect

**Middleware & Next.js**
- [ ] Matcher negativ acoperă tot (inclusiv `/api/*`)
- [ ] Verificare auth O SINGURĂ DATĂ în layout
- [ ] Server Actions: auth → rate limit → RBAC DB → Zod → acțiune → audit
- [ ] Route Handlers validează `Origin` header (nu au auto-CSRF)
- [ ] MFA (AAL2) enforced pe acțiuni critice financiare / medicale
- [ ] Webhook endpoint verifică semnătura HMAC

**MFA**
- [ ] Enrollment cu recovery codes afișate și salvate (hash în DB)
- [ ] Challenge/verify flow implementat și testat
- [ ] AAL2 verificat în Server Actions critice
- [ ] `mfaLevel` state în `useAuth` hook

**HTML Vanilla**
- [ ] CSP meta tag prezent
- [ ] Subresource Integrity pe scripturile CDN
- [ ] `TOKEN_REFRESH_FAILED` handler prezent
- [ ] `textContent` / `innerText` — niciodată `innerHTML` cu date utilizator

**Audit Logging**
- [ ] Trigger pe tabelele sensibile (invoices, patients, user_roles)
- [ ] `logAuditEvent` pentru SELECT sensibil (min: dosare medicale, aprobare financiară)
- [ ] `audit_log` blochează INSERT/UPDATE/DELETE direct de la utilizatori
- [ ] Date medicale: loghezi câmpurile modificate, nu valorile
- [ ] Retention policy configurată (ex: 24 luni)

**Compliance**
- [ ] Right to Erasure endpoint implementat (GDPR — deadline 30 zile)
- [ ] `user_id` → SET NULL la ștergere cont (ON DELETE SET NULL)
- [ ] Backup-uri criptate activate în Supabase Dashboard
- [ ] Nicio valoare de card stocată local
- [ ] Privacy Policy actualizată cu tipurile de date procesate

**Operational Security**
- [ ] `SUPABASE_SERVICE_ROLE_KEY` absent din git history (`git log -S 'service_role'`)
- [ ] `.env.local` și `.env*.local` în `.gitignore`
- [ ] Plan de rotire chei documentat (frecvență + responsabil)
- [ ] Supabase Auth Logs verificate înainte de launch
- [ ] Incident response plan: cine / ce / în cât timp / per tip de incident
- [ ] TypeScript types generate din DB schema (`supabase gen types typescript`)

---

*Versiune: 4.0 — Mai 2026*  
*Stack: Next.js 14+ App Router · Supabase v2 · React 18+ · TypeScript*  
*28 secțiuni · 5 blocuri · 35 greșeli critice*
