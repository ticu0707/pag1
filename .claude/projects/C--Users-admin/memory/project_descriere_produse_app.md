---
name: Proiect Aplicație Generare Descrieri Produse
description: Web app AI pentru generare descrieri produse eCommerce — Next.js + Claude API + Supabase, PRD v1.0 complet, implementare neîncepută
type: project
originSessionId: 621d397b-dabf-4adf-867f-97978492702a
---
## Stare curentă

- **Faza:** PRD complet, implementare neîncepută
- **PRD:** `C:\Users\admin\Desktop\prd-descriere-produse-app.md`
- **Ghid business:** `C:\Users\admin\Desktop\descriere produse.md`
- **Stack:** Next.js + Tailwind CSS + Claude API (claude-sonnet-4-6) + Supabase + Vercel

---

## Decizii cheie din PRD

| Dimensiune | Decizie |
|---|---|
| Utilizator principal | Manager catalog / proprietar magazin online |
| Problema rezolvată | Inconsistență descrieri — lipsă voce de brand unitară |
| Platforma | Web app (browser) |
| Input | Imagine produs + câmpuri cheie (nume, categorie, 2-3 caracteristici) |
| Output | Descriere + scor completare (0-100) + listă câmpuri lipsă |
| Framework copywriting | Auto-suggest per categorie, user poate schimba |
| Limbă | Română default + orice limbă la cerere |
| Salvare | Opțional — localStorage fără cont / Supabase Auth cu cont |
| Limita | Draft pentru aprobare umană, nu publicare automată |

---

## Framework-uri per Categorie

| Categorie | Sugerat | Alternativă |
|---|---|---|
| Haine | FAB | AIDA |
| Electronice | 4P | FAB |
| Artizanal | Feature-Benefit-Story | AIDA |
| Accesorii | AIDA | FAB |
| Cosmetice | PAS | FAB |
| Alimentar | AIDA | PAS |

---

## Scor completare (logica din ghid)

- 60p → câmpuri [CORE-MUST] acoperite
- +20p → câmpuri [SHOULD] completate
- +10p → proof [P] atașat pentru claim-uri
- +10p → imagine de calitate detectată
- Prag publicare: ≥85

---

## Extensii Post-MVP planificate

1. HoReCa / Servicii / Magazine fizice
2. Bulk upload (CSV)
3. Integrare Shopify/WooCommerce
4. Brand voice personalizat
5. A/B descriptions

---

**Why:** Proiect nou identificat în sesiunea din 16 apr 2026 — utilizatorul a văzut aplicații similare și vrea să construiască una proprie, pornind de la un ghid detaliat de copywriting eCommerce.
**How to apply:** La reluarea sesiunii → citește PRD-ul de pe Desktop și începe cu setup-ul proiectului Next.js.
