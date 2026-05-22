---
name: project-ghid-auth-authorization
description: "Ghid Authentication & Authorization v4.0 — JWT, RBAC, Supabase RLS, MFA, Storage, Compliance, Testing; 28 secțiuni, 35 greșeli, v4.0 COMPLET"
metadata: 
  node_type: memory
  type: project
  originSessionId: a3fd517a-f93d-4269-830f-cf60e6caed19
---

Ghid Authentication & Authorization pentru vibe-coding, utilizabil pe toate tipurile de proiecte.

**Locație:** `C:\Users\admin\Desktop\Vibe-Coding\ghid-auth-authorization-v4.md`

**Versiune curentă:** v4.0 — Mai 2026 (28 secțiuni, 5 blocuri, 35 greșeli critice)

**Ce acoperă v4.0:**
- JWT anatomie, PKCE, OAuth callback cu open redirect prevention
- getUser() vs getSession() — regula de aur
- 3 Supabase clients + cookie security (httpOnly, SameSite: lax, Secure)
- Env vars validation cu Zod la startup
- Token lifecycle: rotație, stale JWT, logout cu scope explicit
- Password change → invalidare sesiuni active (scope: 'others')
- Auth Providers: social login, magic link, passkeys (WebAuthn)
- USING vs WITH CHECK + auth.jwt() vs subquery trade-off
- CRUD policies + IDOR în JOIN-uri
- Soft delete + RLS (`deleted_at IS NULL`)
- `TO authenticated` în politici
- Multi-tenant RLS (org_id) + ierarhic (manager > staff) + temporal
- RLS pe tabele de sistem (user_roles, audit_log) — privilege escalation prevention
- Supabase Storage RLS + signed URLs (bucket privat obligatoriu)
- Schema RBAC + trigger handle_new_user
- Clinic 3-role (CLINIC_PERMISSIONS, hasPermission)
- FinanceOS 6-role (FINANCE_PERMISSIONS, canDo, PermissionGuard)
- JWT Custom Claims Hook + stale JWT strategy
- Security Headers în next.config.ts (X-Frame-Options, CSP, HSTS, Permissions-Policy)
- Middleware cu matcher negativ (acoperă tot, exclude static)
- Layout auth O SINGURĂ DATĂ
- Server Actions: auth → rate limit → RBAC DB → Zod → acțiune → audit
- Webhook signature verification (HMAC timing-safe)
- MFA TOTP enrollment + recovery codes + AAL2 enforcement
- Passkeys (WebAuthn) — menționat, suport Supabase viitor
- HTML Vanilla: localStorage vs httpOnly, CSP meta, SRI pe CDN
- Session Management UI (vizualizare + revocare sesiuni)
- Audit logging complet (trigger + manual SELECT_SENSITIVE)
- Compliance: GDPR (retention + right to erasure), date medicale (fără valori în log), date financiare
- Testing Auth: setup cu Supabase local, teste RLS (izolare, privilege escalation, IDOR, anon), teste RBAC
- Operational Security: service_role rotation, Auth Logs, JWT debugging, incident response
- 35 greșeli critice + Security Checklist pre-deploy (8 categorii)

**Why:** Proiectele cu date medicale (Clinică) și financiare (FinanceOS, Vibe Budget) au nevoie de auth fără compromisuri. Breșele în aceste domenii sunt catastrofale.

**How to apply:** Înainte de orice implementare auth nouă sau audit al unui proiect existent. Checklist pre-deploy în S28.

**Legat de:** [[project_clinica_medicala]], [[project_erp_financiar]], [[project_vibe_budget]], [[reference_skill_nextjs_audit]], [[project_ghid_database_supabase]]
