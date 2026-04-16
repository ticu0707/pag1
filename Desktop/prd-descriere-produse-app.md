# PRD — Aplicație Generare Descrieri Produse (eCommerce)
**Versiunea:** 1.0 — MVP
**Data:** 16 aprilie 2026
**Stack:** Next.js + Tailwind CSS + Supabase + Claude API

---

## 1. Problema

Magazinele online scriu descrierile de produs inconsistent — fiecare angajat folosește alt stil, alt nivel de detaliu, alt ton. Rezultatul: un catalog neuniform care arată neprofesionist și reduce încrederea cumpărătorului. Nu există un standard aplicat automat.

---

## 2. Soluția

O aplicație web care primește o imagine de produs + câteva câmpuri cheie și generează un draft de descriere profesională, consistent, bazat pe framework-uri validate de copywriting (AIDA / FAB / PAS). Outputul include un scor de completare și lista câmpurilor lipsă. Utilizatorul revizuiește, ajustează și publică manual.

**Aplicația este un co-pilot, nu un autopilot.**

---

## 3. Utilizator țintă

**Primar:** Manager de catalog sau proprietar de magazin online (50–500 SKU-uri/lună), fără pregătire în copywriting, care vrea texte consistente fără să angajeze un redactor.

**Secundar (extensii viitoare):** Magazine fizice, HoReCa, prestatori de servicii.

---

## 4. User Flow — MVP

```
1. Utilizatorul încarcă o imagine de produs
2. Completează câmpurile cheie:
   - Nume produs
   - Categorie (dropdown: Haine / Electronice / Artizanal
                 / Accesorii / Cosmetice / Alimentar)
   - Preț (opțional)
   - 2–3 caracteristici invizibile în imagine
     (ex: material exact, greutate, garanție)
   - Limbă output (default: Română)
3. Aplicația sugerează framework-ul recomandat
   pentru categorie (ex: Cosmetice → PAS)
   → Utilizatorul poate schimba din dropdown
4. Click "Generează"
5. Output:
   - Descrierea completă (titlu + paragraf + bullet-uri)
   - Scor de completare (0–100)
   - Listă: câmpuri lipsă / îmbunătățiri recomandate
6. Utilizatorul copiază textul → paste în admin-ul magazinului
7. Opțional: salvează descrierea în istoric
```

---

## 5. Input — Specificații

| Câmp | Tip | Obligatoriu |
|---|---|---|
| Imagine produs | Upload (JPG/PNG/WEBP) | Da |
| Nume produs + variantă | Text | Da |
| Categorie | Dropdown | Da |
| Caracteristici invizibile | Text liber (max 3) | Recomandat |
| Preț | Număr | Opțional |
| Limbă output | Dropdown (RO default) | Da |
| Framework copywriting | Dropdown (auto-suggest) | Da |

---

## 6. Output — Specificații

**Descrierea generată conține:**
- Titlu optimizat SEO
- Paragraf introductiv (hook conform framework-ului ales)
- 3–7 bullet-uri Feature → Beneficiu
- Call-to-action (unde e relevant)
- Etichete interne [F] / [C] / [P] vizibile opțional (mod avansat)

**Scorul de completare (0–100):**
- 60p → toate câmpurile [CORE-MUST] acoperite
- +20p → câmpuri [SHOULD] completate
- +10p → proof ([P]) atașat pentru claim-uri
- +10p → imagine de calitate detectată

**Lista de îmbunătățiri:**
- „Lipsă: garanție produs [CORE-MUST]"
- „Recomandat: tabel mărimi pentru categoria Haine"
- „Claim fără dovadă: adaugă certificare sau review"

---

## 7. Framework-uri per Categorie (auto-suggest)

| Categorie | Framework sugerat | Alternativă |
|---|---|---|
| Haine | FAB | AIDA |
| Electronice | 4P (Picture-Promise-Prove-Push) | FAB |
| Artizanal | Feature–Benefit–Story | AIDA |
| Accesorii | AIDA | FAB |
| Cosmetice | PAS | FAB |
| Alimentar | AIDA | PAS |

---

## 8. Salvare & Istoric

- **Fără cont:** descrierile se păstrează în `localStorage` (sesiunea curentă + ultimele 10)
- **Cu cont opțional** (Supabase Auth): istoric complet, export CSV, regenerare
- Contul nu este obligatoriu pentru a folosi aplicația

---

## 9. Limbă

- Default: Română
- Selecție: EN, DE, HU, FR, IT, ES (extensibil)
- Promptul AI se adaptează automat la limba selectată
- Terminologia tehnică (ex: etichete [F]/[C]/[P]) rămâne internă, nu apare în output

---

## 10. Stack Tehnic

| Componentă | Tehnologie |
|---|---|
| Frontend | Next.js + Tailwind CSS |
| AI (generare text) | Claude API (claude-sonnet-4-6) |
| AI (analiză imagine) | Claude API (vision) |
| Baza de date | Supabase |
| Autentificare | Supabase Auth (opțional) |
| Deploy | Vercel |
| Regulile de business | Ghidul `.md` → system prompt structurat |

---

## 11. În Afara Scope-ului (MVP)

- Publicare automată în Shopify / WooCommerce / OLX
- Gestionare catalog (nu e un PIM)
- Generare imagini de produs
- Analiză concurență / SEO avansat
- Variante multiple de descriere simultan
- Aprobare în echipă / workflow multi-user

---

## 12. Succes — Cum Măsurăm

| Metric | Target MVP |
|---|---|
| Timp până la copy-paste | < 2 minute de la upload |
| Scor mediu descrieri generate | ≥ 75/100 |
| Editare manuală necesară | < 20% din text |
| Rata de salvare în istoric | > 40% din generări |

---

## 13. Extensii Post-MVP

1. **HoReCa / Servicii** — verticale noi cu framework-uri adaptate
2. **Bulk upload** — CSV cu mai multe produse, generare în lot
3. **Integrare Shopify/WooCommerce** — publish direct din aplicație
4. **Brand voice** — utilizatorul definește tonul brandului, aplicația îl aplică consistent
5. **A/B descriptions** — două variante generate simultan pentru testare
