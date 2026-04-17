# PRD — Aplicație Generare Descrieri Produse (eCommerce)
**Versiunea:** 3.0 — MVP
**Data:** 17 aprilie 2026
**Stack:** Next.js + Tailwind CSS + Supabase + Claude API

---

## 1. Problema

Magazinele online românești scriu descrierile de produs inconsistent — fiecare angajat folosește alt stil, alt nivel de detaliu, alt ton. Rezultatul: un catalog neuniform care arată neprofesionist și reduce încrederea cumpărătorului. Nu există un standard aplicat automat, adaptat pieței locale.

**Ipoteză de validat (înainte de cod):** Managerii de catalog consideră inconsistența un blocaj suficient de dureros încât să plătească 39 RON/lună pentru a-l rezolva. A se valida prin minimum 5 interviuri cu potențiali utilizatori înainte de prima linie de implementare.

---

## 2. Soluția

O aplicație web care primește o imagine de produs + câteva câmpuri cheie și generează un draft de descriere profesională, consistent cu vocea brandului, optimizat pentru piața și marketplace-urile românești.

Outputul include un scor de completare și lista câmpurilor lipsă. Utilizatorul revizuiește, ajustează și publică manual.

**Aplicația este un co-pilot, nu un autopilot.**

---

## 3. Diferențiator

**Optimizat pentru piața românească** — nu un tool generic global:
- Cunoaște specificul marketplace-urilor locale: eMAG, OLX, Fashion Days, Altex
- Înțelege comportamentul cumpărătorului român (preț, garanție, livrare = factori cheie)
- Respectă legislația română pentru claim-uri (ANPC, OPC)
- Limbă română nativă — nu traducere din engleză
- Framework-uri de copywriting calibrate pe exemple și branduri din piața locală

**Moat pe termen mediu:** Regulile de business (ghidul intern `.md`) devin din ce în ce mai specifice pe verticale locale prin feedback real de la utilizatori — greu de replicat rapid de un concurent generic.

---

## 4. Context Competitiv

| Alternativă | Limitare față de această aplicație |
|---|---|
| ChatGPT / Claude direct | Fără Brand Voice persistent, fără framework per categorie, fără scoring |
| Copy.ai / Rytr | Generice, fără context piața română, fără imagine input |
| Copywriter freelancer | Cost 50–200 RON/descriere, timp 24–48h, inconsistență între persoane |
| Angajat intern | Cost fix lunar, inconsistență de stil, scalare dificilă |

**Concluzie:** Niciun concurent direct pe piața românească cu image input + Brand Voice + framework automat. Fereastra de oportunitate există acum.

---

## 5. Utilizator Țintă

**Primar:** Manager de catalog sau proprietar de magazin online (50–500 SKU-uri/lună), fără pregătire în copywriting, care vrea texte consistente și profesionale fără să angajeze un redactor.

**Secundar (extensii viitoare):** Magazine fizice, HoReCa, prestatori de servicii.

---

## 6. User Flow — MVP

```
ONBOARDING (o singură dată):
1. Utilizatorul creează cont (email + parolă)
2. Completează Brand Voice:
   - Descriere brand (2–3 propoziții)
   - 3 adjective de ton (ex: prietenos, direct, premium)
   - Ce evităm (ex: limbaj tehnic, superlative goale)

GENERARE DESCRIERE (flux repetat):
3. Încarcă imaginea produsului
4. Completează câmpurile cheie:
   - Nume produs + variantă
   - Categorie (dropdown)
   - 2–3 caracteristici invizibile în imagine
     (ex: material, greutate, garanție)
   - Limbă output (default: Română)
5. Click "Generează"
6. Loading (15–40 secunde):
   - Bara de progres animată cu 3 etape vizibile:
     "Analizez imaginea..." → "Aplic vocea brandului..." → "Finalizez descrierea..."
7. Output:
   - Descrierea completă (titlu + paragraf + bullet-uri)
     → în vocea brandului definită la onboarding
   - Scor de completare (0–100) cu detaliu pe categorii
   - Listă: câmpuri lipsă / îmbunătățiri recomandate
   - Butoane individuale de copiere: [Copiază titlu] [Copiază paragraf] [Copiază bullet-uri] [Copiază tot]
8. Utilizatorul copiază → paste în admin-ul magazinului
9. Opțional: salvează descrierea în istoricul contului
```

---

## 7. Brand Voice — Specificații

Completat o singură dată la onboarding. Aplicat automat la fiecare generare.

| Câmp | Tip | Exemplu |
|---|---|---|
| Descriere brand | Text (2–3 prop.) | „Vindem haine pentru femei active, urban, 25–40 ani" |
| Ton (3 adjective) | Text | Prietenos, direct, inspirațional |
| Ce evităm | Text | Limbaj tehnic, superlative goale, englezisme |

Utilizatorul poate edita Brand Voice oricând din setări.

---

## 8. Input — Specificații

| Câmp | Tip | Obligatoriu |
|---|---|---|
| Imagine produs | Upload (JPG/PNG/WEBP, max 10MB) | Da |
| Nume produs + variantă | Text | Da |
| Categorie | Dropdown | Da |
| Caracteristici invizibile | Text liber (max 3) | Recomandat |
| Preț | Număr | Opțional |
| Limbă output | Dropdown (RO default) | Da |

> **Notă:** Framework-ul de copywriting este selectat automat de aplicație
> în funcție de categorie. Nu e expus utilizatorului (jargon intern).

---

## 9. Output — Specificații

**Descrierea generată conține:**
- Titlu optimizat SEO (pentru piața română)
- Paragraf introductiv (hook conform framework-ului categoriei)
- 3–7 bullet-uri Feature → Beneficiu
- Call-to-action adaptat marketplace-ului țintă
- Ton consistent cu Brand Voice-ul definit

**Copiere granulară:**
- [Copiază titlu] — copiază doar titlul SEO
- [Copiază paragraf] — copiază doar introductivul
- [Copiază bullet-uri] — copiază lista de beneficii
- [Copiază tot] — copiază întreaga descriere formatată

**Scorul de completare (0–100):**

| Criteriu | Punctaj | Condiție concretă |
|---|---|---|
| Câmpuri CORE completate | 60p | Nume + categorie + imagine + min. 1 caracteristică |
| Câmpuri SHOULD completate | +20p | Min. 2 caracteristici invizibile completate |
| Proof atașat pentru claim-uri | +10p | Garanție / certificare / review menționat explicit |
| Imagine de calitate | +10p | Rezoluție ≥ 800px, fundal curat (detectat automat) |

**Lista de îmbunătățiri:**
- „Lipsă: garanție produs [CORE-MUST]"
- „Recomandat: tabel mărimi pentru categoria Haine"
- „Claim fără dovadă: adaugă certificare sau review"

---

## 10. Framework-uri per Categorie (intern, auto-aplicat)

| Categorie | Framework aplicat |
|---|---|
| Haine | FAB |
| Electronice | 4P (Picture-Promise-Prove-Push) |
| Artizanal | Feature–Benefit–Story |
| Accesorii | AIDA |
| Cosmetice | PAS |
| Alimentar | AIDA |
| **Altele (fallback)** | **FAB — framework universal aplicat automat** |

> Categoriile neacoperite de dropdown primesc automat framework FAB.
> Post-MVP: extindere la 15+ categorii pe baza datelor reale de utilizare.

---

## 11. Stări de Eroare

| Situație | Ce vede utilizatorul |
|---|---|
| Imagine prea mare (>10MB) | „Imaginea depășește 10MB. Te rugăm să o comprimi și să reîncerci." |
| Format neacceptat | „Format nesuportat. Acceptăm JPG, PNG, WEBP." |
| Claude API timeout (>60s) | „Generarea a durat prea mult. Încearcă din nou — dacă problema persistă, contactează suportul." |
| Supabase indisponibil | „Salvarea a eșuat. Descrierea ta este afișată — copiaz-o acum înainte să închizi." |
| Stripe payment failure | „Plata nu a putut fi procesată. Încearcă alt card sau contactează banca." |
| Trial expirat | „Trial-ul tău de 14 zile a expirat. Alege un plan pentru a continua." (cu CTA către upgrade) |

---

## 12. Conturi & Autentificare

Contul este **obligatoriu** — Brand Voice-ul trebuie salvat și aplicat consistent.

- Înregistrare: email + parolă (Supabase Auth)
- Trial 14 zile: acces complet, fără card
- La expirare: upgrade la plan plătit sau pierdere acces
- La ștergerea contului: toate datele (descrieri, Brand Voice, imagini) sunt șterse în 30 de zile

---

## 13. Monetizare

| Plan | Preț | Include |
|---|---|---|
| **Trial** | Gratuit 14 zile | Acces complet, fără card |
| **Starter** | 39 RON/lună | 75 descrieri, 1 Brand Voice |
| **Pro** | 99 RON/lună | Nelimitat, 3 Brand Voice-uri, export CSV |

**Rațional de pricing:**
- 39 RON/lună ≈ costul unui singur text de la un copywriter freelancer
- Comparație: ChatGPT Plus ~25 RON/lună (fără Brand Voice persistent, fără image input, fără framework auto)
- Break-even intern la ~20 descrieri/lună pe Starter (vezi Secțiunea 15 — Unit Economics)

**Strategie conversie trial → plătit:**
- Email la ziua 7: „Ai generat X descrieri. Starter-ul tău costă mai puțin decât o oră de copywriter."
- Email la ziua 13: reminder cu ofertă first-month 50% (opțional)
- Target conversie: 8–12% (realist SaaS fără sales; 15% cu email nurturing activ)

---

## 14. Limbă

- Default: Română
- Selecție: EN, DE, HU, FR, IT, ES (extensibil)
- Promptul AI se adaptează automat la limba selectată
- Contextul pieței locale (marketplace-uri, legislație) rămâne activ indiferent de limbă

---

## 15. Unit Economics

**Cost estimat per descriere (Claude API):**

| Componentă | Estimare |
|---|---|
| Input tokens (system prompt + Brand Voice + câmpuri) | ~2.000 tokens |
| Image tokens (claude-sonnet-4-6 vision) | ~1.000–1.500 tokens |
| Output tokens (descriere generată) | ~500–800 tokens |
| **Cost total per apel** | **~$0.04–0.08** (la prețurile Anthropic Sonnet) |

**Marjă pe plan Starter (75 descrieri / 39 RON):**

| Element | Valoare |
|---|---|
| Venit lunar | 39 RON (~7.8 EUR) |
| Cost Claude API (75 apeluri × $0.06 avg) | $4.50 (~22.5 RON) |
| Cost infra (Supabase + Vercel prorated) | ~5 RON |
| **Marjă brută estimată** | **~11.5 RON / client Starter** |

> Marjă pozitivă dar subțire pe Starter. Profitabilitatea reală vine din planul Pro (nelimitat = ~200 descrieri tipice × $0.06 = $12 cost vs. 99 RON ~20 EUR venit) și din reducerea costului per token pe volum.

---

## 16. Conformitate GDPR

Aplicația procesează date personale (email, imagini de produs, descrieri generate).

| Obligație | Implementare MVP |
|---|---|
| Informare utilizator | Politică de confidențialitate clară la înregistrare |
| Procesator terț (Anthropic) | Menționat explicit că imaginile sunt procesate de Claude API |
| Retenție date | Descrierile și imaginile se șterg la 30 de zile după ștergerea contului |
| Drept la ștergere | Buton „Șterge contul și toate datele" în setări |
| Stocare | Date în Supabase EU (Frankfurt) — conform GDPR |

> **Notă:** Imagini de produs nu conțin date personale în mod tipic, dar politica acoperă și cazurile excepționale (ex: model în imagine).

---

## 17. Salvare & Istoric

- Descrierile generate se salvează automat în contul utilizatorului
- Poate regenera, edita sau exporta din istoric
- Export CSV disponibil pe planul Pro

---

## 18. Stack Tehnic

| Componentă | Tehnologie |
|---|---|
| Frontend | Next.js + Tailwind CSS |
| AI (generare text) | Claude API (claude-sonnet-4-6) |
| AI (analiză imagine) | Claude API (vision) |
| Baza de date | Supabase (PostgreSQL) — EU Frankfurt |
| Autentificare | Supabase Auth |
| Plăți | Stripe |
| Deploy | Vercel |
| Regulile de business | Ghidul `.md` → system prompt structurat |

---

## 19. În Afara Scope-ului (MVP)

- Publicare automată în Shopify / WooCommerce / OLX / eMAG
- Gestionare catalog (nu e un PIM)
- Generare imagini de produs
- Analiză concurență / SEO avansat
- Variante multiple de descriere simultan
- Aprobare în echipă / workflow multi-user
- Brand Voice structurat complet (tone guide, cuvinte interzise per câmp, exemple)

---

## 20. Succes — Cum Măsurăm

| Metric | Target MVP |
|---|---|
| Timp până la copy-paste | < 2 minute de la upload |
| Scor mediu descrieri generate | ≥ 75/100 |
| Completare onboarding Brand Voice | > 80% din utilizatori noi |
| Retenție la 30 de zile | > 40% |
| Conversie trial → plătit | > 8% (realist) / >12% (cu email nurturing) |

---

## 21. Validare Pre-Implementare (obligatorie)

Înainte de prima linie de cod:

1. **5 interviuri** cu manageri de catalog / proprietari de magazine online
2. **Întrebări cheie:** Cât timp petreci pe descrieri/săptămână? Ai un standard de stil? Ai plăti 39 RON/lună pentru consistență automată?
3. **Semnal verde pentru implementare:** Minimum 3 din 5 persoane confirmă problema și willingness-to-pay
4. **Test de preț:** Arată mockup-urile și întreabă „Cât ai plăti?" înainte de a menționa prețul

---

## 22. Extensii Post-MVP

1. **Brand Voice avansat** — tone guide complet, cuvinte interzise, exemple de fraze
2. **Bulk upload** — CSV cu mai multe produse, generare în lot
3. **Integrare eMAG / OLX** — publish direct din aplicație
4. **HoReCa / Servicii / Magazine fizice** — verticale noi
5. **A/B descriptions** — două variante generate simultan pentru testare

---

## 23. Modificări față de v2.0

| Element | v2.0 | v3.0 |
|---|---|---|
| Validare piață | Absent | Secțiune obligatorie pre-implementare (Sec. 21) |
| Unit economics | Absent | Calculator detaliat cost/marjă per plan (Sec. 15) |
| GDPR | Absent | Secțiune completă cu obligații și implementare (Sec. 16) |
| Analiza competitivă | Absent | Tabel comparativ 4 alternative (Sec. 4) |
| Stări de eroare | Absent | 6 scenarii de eroare cu mesaj exact (Sec. 11) |
| Latență / UX generare | Nespecificat | 3 etape vizibile în loading (Sec. 6) |
| Copiere output | „Copy-paste" generic | 4 butoane granulare per componentă (Sec. 9) |
| Scoring | Criteriu vag imagine | Condiție concretă: rezoluție ≥800px, fundal curat (Sec. 9) |
| Categorii fallback | Absent | FAB aplicat automat pentru categorii neacoperite (Sec. 10) |
| Pricing rationale | Prețuri fără justificare | Comparativ copywriter + ChatGPT + break-even (Sec. 13) |
| Target conversie | 15% (wishful) | 8–12% cu strategie email definită (Sec. 13) |
