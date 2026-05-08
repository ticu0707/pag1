---
name: FinanceOS — ERP Financiar Intern
description: PRD v3.0 final, aprobat — management financiar intern RO, Next.js 14 + Supabase + Vercel
type: project
originSessionId: 496d82f1-cba9-4cae-890d-81350091d785
---
Aplicație ERP financiar intern pentru firmă producție/mixtă, 5+ utilizatori.
**Nume aplicație:** FinanceOS

**Stack:** Next.js 14 App Router + Supabase (PostgreSQL + Auth + Storage) + Vercel

---

## Poziționare

FinanceOS = strat de management intern. Nu înlocuiește SmartBill/Saga pentru facturare legală — le completează.
e-Factura ANAF = v2 (arhitectura pregătită cu coloane în invoices_issued).

## Decizii arhitecturale

- Monedă: RON implicit + EUR/USD/GBP/CHF selectabile; cursuri BNR auto-fetch zilnic (Edge Function)
- Facturi: tabele SEPARATE — invoices_issued + invoices_received
- Import: CSV/Excel manual (PapaParse + XLSX, pattern Vibe Budget)
- Contabilitate: primară — fără note contabile, extensibil
- Firmă: o singură firmă (company_settings)
- Hosting: Supabase + Vercel (online)
- Notificări: in-app (badge + toast), extensibil cu email în v2
- HR: DOAR pontaj + concedii + export Excel — fără calcul salarial (complexitate legislativă RO)
- Serii numere: funcție PG atomică (fără duplicate sub concurență)

## Roluri RBAC

admin, manager, contabil, vanzari, depozit, hr

## Ordinea implementare

- Faza 0 — Fundament: Next.js + Supabase schema + Auth + RBAC + layout
- Faza 1 — Modul 1: Facturi & Plăți (clienți, furnizori, facturi emise/primite, storno, proformă, plăți, reconciliere bancară)
- Faza 2 — Modul 2: Stocuri & Inventar (produse, NIR, mișcări, depozite)
- Faza 3 — Modul 6: HR — pontaj + concedii + export Excel
- Faza 4 — Modul 3: Comenzi & Producție (BOM, ordine producție)
- Faza 5 — Modul 4: P&L + Cash Flow + Bugete (PostgreSQL views)
- Faza 6 — Modul 5: Vânzări & Bonusuri per agent

## Ce NU e în v1 (explicit)

- e-Factura ANAF/SPV (v2 — coloane pregătite)
- Calcul stat de plată (export Excel pentru contabil)
- Note contabile (v2)
- SAF-T / D406 (v2)
- Integrare API bancară (v2)

## Schema DB — tabele cheie

**Fundament:** company_settings, bank_accounts, number_sequences (atomic RPC), exchange_rates (BNR), units_of_measure, product_categories, audit_log

**Modul 1:** clients, suppliers, invoices_issued (cu tip: factura/proforma/storno), invoices_issued_items, invoices_received, invoices_received_items, payments, bank_transactions, payment_allocations, cash_register

**Modul 2:** products, warehouses, nir, nir_items, stock_movements (cu pret_unitar pentru COGS)

**Modul 3:** orders, order_items, bom, production_orders

**Modul 4:** budgets (P&L calculat via PostgreSQL views)

**Modul 5:** sales_targets (vânzări calculate via views)

**Modul 6:** employees, timesheets, leave_requests

**Câmpuri comune toate tabelele:** created_at, created_by, updated_at, updated_by, deleted_at (soft delete)

## UX cheie

- Quick actions bar (factură/NIR/plată/comandă în 2 click-uri)
- Notificări badge sidebar (roșu=scadente, portocaliu=stoc minim, albastru=concedii)
- Global search cross-module
- Atașamente PDF/imagine pe orice document (Supabase Storage)
- Perioade contabile închise (luna trecută = read-only)
- Sold curent client/furnizor (PostgreSQL VIEW)
- TVA dashboard (colectat vs. deductibil)
- Reconciliere bancară semi-automată (matching sumă + dată ±2 zile)

## Status

PRD v3.0 aprobat. Implementare neîncepută. Urmează Faza 0 (setup proiect + schema DB).
