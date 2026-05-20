# GHID COMPLET: Prompt Engineering pentru Vibe-Coding cu Claude
**v4.0 — Ediția Finală**
**Data:** Mai 2026 | **Nivel:** Beginner → Expert
**Timp realist:** 60 min citit + practică imediată pe proiectele tale

---

## TL;DR — 3 Lucruri Care Schimbă Totul

Dacă citești doar atât, reții esența:

1. **Context înainte de orice.** Claude nu vede ecranul, nu știe ce fișier ai deschis, nu ține minte sesiunile anterioare. Fiecare conversație e un slate curat. Fișier + stare + limite = 80% din calitatea răspunsului.

2. **Arată, nu descrie.** Un exemplu de cod din proiectul tău face mai mult decât orice instrucțiune verbală. Few-Shot > C-S-I-L-V > nimic.

3. **Descrie problema, nu soluția.** Când descrii CUM să rezolve, tai autonomia expertizei lui Claude. Când descrii CE trebuie rezolvat și CE nu trebuie atins, el găsește soluția mai bună decât ai putea specifica tu.

---

## Cum Să Folosești Ghidul

**Prima dată:** Citește liniar Bloc 1 + Bloc 2 (~25 min). Returnarea din investiție e imediată.

**În sesiunile de lucru:** Deschide direct Parte 13 (Flowchart) sau Parte 15 (Quick Reference).

**Când ceva nu merge:** Salt direct la Parte 9 (Diagnosticare + Tehnici Avansate).

**Dacă lucrezi cu Claude API în proiectele tale:** Citește și Parte 11 (Securitate).

---

## Learning Map

```
BLOC 1 — FUNDAMENTE
  [0]  Modelul Mental — mecanismul real + memoria între sesiuni
  [1]  Cele 2 Greșeli Fundamentale + Zona Optimă + Testul de Calibrare

BLOC 2 — TEHNICI (în ordinea impactului)
  [2]  Few-Shot Examples — tehnica #1, inclusiv când dăunează
  [3]  Formula C-S-I-L-V
  [4]  Gândește Pas cu Pas — Chain of Thought pentru calitate superioară  ★ NOU
  [5]  Control Format Output — mecanismul explicat
  [6]  Rolul / Persona — cu atenționare despre degradare

BLOC 3 — EXECUȚIE
  [7]  Template-uri — 8 scenarii gata de copiat
  [8]  Greșeli Comune — 8 exemple înainte/după
  [9]  Iterare: Diagnostic + Critic→Builder + Meta-Prompting + Pollution  ★ EXTINS
  [10] Strategia Sesiunii — Priming + arcul de 20-30 mesaje  ★ EXTINS

BLOC 4 — JUDECATĂ
  [11] Securitate și Confidențialitate ⚠️ CRITIC
  [12] Când NU Folosești Claude — inclusiv halucinația de încredere  ★ EXTINS

BLOC 5 — REFERINȚĂ
  [13] Flowchart Decizie Template
  [14] Sesiune Reală: Înainte vs. Expert
  [15] Quick Reference Card
```

---

## BLOC 1 — FUNDAMENTE

### PARTE 0 — Modelul Mental: Mecanismul Real

**Realitatea nr. 1:** Claude nu îți vede ecranul. Nu știe ce fișier ai deschis, ce s-a întâmplat în sesiunile anterioare, ce nu trebuie schimbat.

**Realitatea nr. 2 — adesea uitată:** Claude nu ține minte sesiunile anterioare. Fiecare conversație nouă e un slate curat. Deciziile, contextul și preferințele din ieri nu există pentru el azi dacă nu le spui din nou. Strategia pentru asta e în Parte 10.

**Mecanismul real:**

Claude citește tot ce i-ai dat și generează cel mai probabil răspuns bazat pe acel input. Nu "înțelege" în sensul uman — face pattern matching extrem de sofisticat pe un spațiu uriaș de text. Cu cât inputul tău e mai precis și mai structurat, cu atât răspunsul se îngustează spre ce vrei.

**Singura analogie din acest ghid:**

Ai angajat cel mai bun developer senior din lume. Îl aduci la birou, dar îl ții cu ochii închiși. Comunicați exclusiv prin text. Tot ce nu îi spui explicit = gol pe care îl completează el, uneori corect, uneori greșit. Cu cât îi dai mai mult context, cu atât mai puțin timp pierdut pe corecții.

Și mai important: **de fiecare dată când deschizi o fereastră de chat nouă, developer-ul a uitat tot ce ați discutat înainte.**

Această analogie rămâne valabilă pentru tot ghidul.

**Context Window — un singur lucru de reținut:**

Fiecare conversație are o limită de memorie. Într-o sesiune lungă (2+ ore, 20+ mesaje), conversația se comprimă automat. Claude poate pierde detalii tehnice din mesajele timpurii. Strategia pentru asta e în Parte 10.

**Concluzia practică:**
> Calitatea output-ului e direct proporțională cu calitatea input-ului.

---

### PARTE 1 — Cele 2 Greșeli Fundamentale + Calibrare

Există 2 greșeli opuse care distrug calitatea. Înțelege-le înainte de orice tehnică.

**Greșeala A: Prea vag**
```
"adaugă validare la formular"
```
Developer-ul cu ochii închiși completează golul cu propria interpretare. Câmpuri? Care câmpuri? Ce validare? Ce mesaje de eroare? Ce stil?

---

**Greșeala B: Prea specific (over-specification)**
```
"În StudioFlow (app.html), la linia 847, în funcția validateLeadForm(),
după verificarea câmpului companyName de la linia 852, înainte de
verificarea câmpului budget de la linia 861, adaugă o condiție care
verifică dacă câmpul email conține '@', dacă conține '.', dacă are
mai mult de 5 caractere, și dacă nu e null, undefined, sau string gol,
și dacă toate condițiile sunt false, apelează showFieldError cu
parametrii 'email' și 'Email invalid' și returnează false..."
```

Când un prompt are 50+ linii de constrângeri, Claude se ancorează pe primele și pierde punctul principal. Plus: descrii soluția — tai autonomia expertizei lui.

---

**Zona Optimă:**
```
PREA VAG ←————————————————→ PREA SPECIFIC
                    ↑
               ZONA OPTIMĂ:
         "validare email standard,
          mesaj roșu sub câmp,
          același stil ca celelalte câmpuri"
```

**Testul rapid de calibrare:**

> Dacă promptul tău răspunde la "CUM?" → e prea specific. Descrie PROBLEMA.
> Dacă promptul tău nu răspunde la "UNDE? CE?" → e prea vag.

**Regula completă:**
```
✓ Descrie PROBLEMA și CONTEXTUL
✓ Specifică LIMITE și CONSTRÂNGERI
✗ Nu descrie SOLUȚIA (asta e treaba lui Claude)
✗ Nu specifica IMPLEMENTAREA linie cu linie
```

---

## BLOC 2 — TEHNICI

### PARTE 2 — Few-Shot Examples: Tehnica #1

**De ce e #1:** Arăți un pattern în loc să îl descrii. Developer-ul cu ochii închiși imită ce vede în exemplu mai bine decât orice instrucțiune verbală.

**Sintaxa de bază:**
```
Vreau X ca în exemplul următor:

INPUT:  [exemplu intrare]
OUTPUT: [exemplu ieșire dorită]

Acum aplică pe: [cazul tău]
```

---

**Exemplu 1: Cod consecvent cu stilul existent**

Fără few-shot:
```
adaugă validare pe câmpul telefon
```

Cu few-shot:
```
Adaugă validare pe câmpul 'telefon', în același stil cu validarea existentă:

// Validare câmp email (deja în cod):
if (!email || !email.includes('@')) {
  showFieldError('email', 'Email invalid');
  return false;
}

Aplică același pattern pentru 'telefon':
condiție: minim 10 cifre, mesaj "Număr de telefon invalid".
```

Rezultat: cod care arată identic cu restul, fără să descrii stilul.

---

**Exemplu 2: Format de răspuns dorit**
```
Explică LocalStorage vs IndexedDB în formatul exact:

TEHNOLOGIE: LocalStorage
Bun pentru: [bullet-uri]
Slab pentru: [bullet-uri]
Folosit în proiectele mele la: [exemple]

TEHNOLOGIE: IndexedDB
...
```

---

**Exemplu 3: Reproduce un pattern dintr-un alt fișier**
```
Creează componenta InvoiceCard.tsx după același pattern ca ClientCard.tsx:

[paste ClientCard.tsx — 20-30 linii]

Noua componentă afișează: invoiceNumber, amount, dueDate, status.
Păstrează același pattern de props, styling Tailwind și export default.
```

---

### Când Few-Shot DĂUNEAZĂ — la fel de important

**Cazul 1: Exemplul ancorează o constrângere greșită**

Dacă arăți o validare simplă pentru un câmp simplu, dar câmpul tău are logică specială, Claude va replica pattern-ul simplu și va ignora ce e special la cazul tău.

→ Fix: înainte de exemplu, declară explicit: `Exemplul următor e pentru structură, nu pentru logică — logica mea e [X].`

**Cazul 2: Exemplu din context incompatibil**

Arăți un exemplu de validare din React Hook Form, dar proiectul tău folosește validare manuală. Claude va trage spre pattern-ul React Hook Form.

→ Fix: specifică explicit sursa: `Exemplul următor e din același fișier, același pattern de validare manuală.`

**Cazul 3: Exemple multiple contradictorii**

Dacă dai 3 exemple cu stiluri ușor diferite, Claude "mediază" între ele și produce ceva care nu seamănă cu niciunul.

→ Fix: **Un singur exemplu clar bate trei exemple ambigue.**

---

### PARTE 3 — Formula C-S-I-L-V

Structura de bază pentru orice prompt.

| Element | Întrebarea | Exemplu |
|---------|-----------|---------|
| **C** — Context | Unde ești în cod? | "StudioFlow, app.html, modulul sf-f2" |
| **S** — Stare | Ce există deja? | "Formularul salvează în IndexedDB" |
| **I** — Intenție | Ce vrei exact? | "Adaugă validare email" |
| **L** — Limite | Ce NU schimbi? | "Nu atinge stilul CSS existent" |
| **V** — Verificare | Cum știi că merge? | "Introduc 'test@' și apare eroare roșu" |

**Formula minimă (sarcini simple):**
```
[C + S] + [I] + [L]
```

**Formula completă (feature-uri noi sau decizii):**
```
[C + S] + [I] + [L] + [V] + [format output dorit]
```

**Combinat cu Few-Shot:**

C-S-I-L-V dă structura. Few-Shot dă pattern-ul vizual. Împreună = 90% din ce ai nevoie pentru orice prompt.

---

### PARTE 4 — Gândește Pas cu Pas

**Tehnica:** Ceri explicit lui Claude să raționeze înainte de a răspunde.

**De ce funcționează:** Claude generează răspunsuri token cu token. Dacă îl obligi să "gândească înainte de soluție", alocă mai multă capacitate de procesare analizei. Rezultatul: mai puțini pași sări, mai puține greșeli de logică, edge cases identificate proactiv.

**Unde face diferența reală:**

Nu pentru sarcini simple ("adaugă un buton"). Adaugă valoare masivă când:
- Debugging cu mai multe cauze posibile
- Decizie arhitecturală cu trade-offs
- Feature cu edge cases multiple
- Vrei să înțelegi DE CE ceva nu merge, nu doar fix-ul

**Sintaxa:**
```
[Prompt]. Gândește-te pas cu pas înainte de a răspunde.
```

sau pentru debug:
```
[Descriere bug]. Înainte de fix:
1. Listează 3 cauze posibile
2. Alege cea mai probabilă și explică de ce
3. Propune fix-ul

Nu sări direct la cod.
```

---

**Exemplu: Bug fără Chain of Thought**
```
Tu: "useEffect-ul se apelează în buclă infinită la StudioFlow"

Claude: [Propune imediat: missing dependency array]
→ Corect doar în 40% din cazuri. Tu aplici, nu merge.
```

**Exemplu: Bug cu Chain of Thought**
```
Tu: "useEffect-ul se apelează în buclă infinită la StudioFlow.
     Dependențe: [saveLead, leads].
     Gândește-te la 3 cauze posibile, alege cea mai probabilă."

Claude:
"1. saveLead e recreat la fiecare render (funcție inline) → dependency
   array o include, declanșează re-render
2. leads e un array nou la fiecare render (chiar dacă datele sunt identice)
3. Un setState în interiorul useEffect

Cel mai probabil: cauza 1 — saveLead e definit ca funcție inline.
Fix: wrappare în useCallback."

→ Corect din prima.
```

---

**Pattern: Spec-First pentru Feature-uri Complexe**

Înainte de orice implementare complexă:
```
Scrie spec-ul pentru [feature], nu codul.
Format:
- Ce face: [1 propoziție]
- Ce NU face: [limitele]
- Input/Output: [date intrate, date ieșite]
- Edge cases: [3-4 cazuri limită]
- Cum verific că funcționează: [criteriu în browser]

Confirmă spec-ul înainte să scrii codul.
```

Verifici spec-ul în 30 de secunde și previi 45 de minute de cod în direcția greșită.

---

### PARTE 5 — Control Format Output

**De ce funcționează (mecanismul):**

Claude generează text token cu token. Dacă specifici formatul explicit, îngustezi spațiul de generare — ca și cum dai developer-ului cu ochii închiși un template de completat în loc de o pagină albă. Fără format explicit, primești cod + introducere + explicație + concluzie = de 3x mai mult decât ai nevoie.

**6 Pattern-uri:**

**1. Doar codul — zero explicații:**
```
[Prompt]. Răspunde cu DOAR codul. Fără explicații, fără comentarii.
```

**2. Cod + explicație scurtă:**
```
[Prompt]. Format: codul complet, apoi maximum 3 bullet-uri cu ce ai făcut și de ce.
```

**3. Explicație înainte de cod:**
```
[Prompt]. Întâi 3 bullet-uri cu abordarea ta, abia după codul complet.
```

**4. Doar JSON valid:**
```
[Prompt]. Răspunde cu DOAR JSON valid. Fără text înconjurător, fără ```json wrapper.
```

**5. Diff — doar ce se schimbă:**
```
[Prompt]. Arată DOAR liniile modificate cu 2 linii context înainte/după.
Nu rescrie fișierul întreg.
```

**6. Opțiuni înainte de implementare:**
```
[Prompt decizie]. Nu implementa. Prezintă 2-3 abordări:

Opțiunea [A/B/C]: [nume scurt]
- Pro: [lista]
- Contra: [lista]
- Complexitate: Mică / Medie / Mare
```

---

### PARTE 6 — Rolul / Persona

**Mecanismul:** Persona calibrează tonul și tipul de feedback. "Senior developer critic" produce output diferit față de "asistent helpful" pentru același cod. Setezi o dată la începutul sesiunii — ține pentru tot parcursul conversației.

**5 Roluri Practice:**

**Rolul 1: Code Reviewer critic**
```
Ești un senior developer care face code review pentru producție.
Prioritizează: securitate → logică → performanță → stil.
Dacă ceva e bun, spune în o propoziție. Dacă ceva e prost, explică de ce și cum fix-uiești.
Nu valida dacă există probleme reale.
```

**Rolul 2: Teacher calibrat**
```
Ești un developer senior care explică unui developer beginner-intermediate
cu cunoștințe de Next.js și Supabase. Fără jargon fără explicație.
Analogii simple când conceptul e abstract.
```

**Rolul 3: Architect cu constrângeri reale**
```
Ești arhitect software specializat în aplicații pentru IMM-uri românești.
Cunoști constrângerile de buget, nevoia de simplitate operațională
și specificul local (TVA, e-Factura ANAF, GDPR).
```

**Rolul 4: QA Tester**
```
Ești QA senior. Gândește-te la toate modurile în care codul poate eșua:
null values, empty arrays, concurrent writes, date invalide, edge cases de business.
Semnalează ce poate merge prost, nu ce merge bine.
```

**Rolul 5: Rubber Duck (debugging fără soluții)**
```
Sunt blocat. Nu propune soluții — pune-mi întrebări ca să identific problema singur.
Bug: [descriere]
Am verificat deja: [ce ai încercat]
```

---

**⚠️ Atenționare: Persona Degradation**

Persona se menține bine primele 10-15 mesaje. Într-o sesiune lungă (20+ mesaje), Claude rebalansează implicit spre comportamentul default helpful. Code review-ul "critic" devine treptat mai îngăduitor fără să îți dai seama.

**Fix:** la fiecare ~15 mesaje, re-setează explicit:
```
Reminder: ești în continuare [rolul]. Menține același standard.
```

---

## BLOC 3 — EXECUȚIE

### PARTE 7 — Template-uri per Tip de Sarcină

---

**Template 1: Feature Nou**
```
[ROL opțional]

Proiect: [proiect]
Fișier: [path]
Există deja: [ce funcționează relevant]

Feature: [problema de rezolvat — nu soluția]
Comportament așteptat: [utilizator face X → se întâmplă Y]

NU schimba: [lista explicită]
Verific că funcționează când: [criteriu în browser]
Format răspuns: [cod complet / doar funcția / opțiuni mai întâi]

Dacă îți lipsesc informații înainte de implementare, întreabă. Nu ghici.
```

---

**Template 2: Bug Fix**
```
Proiect: [proiect], fișier: [fișier]

BUG:       [ce se întâmplă — comportamentul observat]
EXPECTED:  [ce ar trebui să se întâmple]
REPRODUCE: [pași exacți]
CONTEXT:   [după ce modificare a apărut?]

Eroare din consolă (copiată literal):
[paste]

Cod relevant:
[paste]

Gândește-te la 3 cauze posibile înainte de fix. Explică pe care o alegi și de ce.
Dacă nu ești sigur de cauză, spune explicit — nu ghici cu încredere falsă.
```

---

**Template 3: Refactoring**
```
Proiect: [proiect], fișier: [fișier]

[paste cod]

Scop refactoring: [lizibilitate / performanță / reutilizare — un singur scop]
Invariante — NU schimba:
- Comportamentul extern (input/output identic)
- Funcțiile care apelează: [listezi]
- [alte constrângeri]

Format: codul refactorizat + 3 bullet-uri cu ce ai schimbat și de ce.
```

---

**Template 4: Explicație Cod**
```
Ești teacher pentru developer beginner-intermediate.

[paste cod]

Specific vreau să înțeleg: [întrebarea exactă]
Explică DE CE există logica asta, nu doar ce face.
Analogii simple dacă conceptul e abstract.
```

---

**Template 5: Decizie Arhitecturală**
```
Ești arhitect software pentru aplicații SaaS cu constrângeri de buget.

Proiect: [descriere]
Stack: [tehnologii]
Decizie: [A] vs [B] vs [C opțional]

Context decisiv:
- Utilizatori: [număr]
- Volum date: [estimare]
- Offline necesar: [da/nu]
- Complexitate tolerată: [mică/medie/mare]

Format: tabel Avantaje / Dezavantaje / Potrivire pentru cazul meu.
Recomandare finală cu motivare în 2 propoziții.
Dacă îți lipsesc informații pentru o decizie bună, întreabă înainte de a recomanda.
```

---

**Template 6: Git & Deployment**
```
Proiect: [proiect] la [path]
Repo: [url]
Branch curent: [branch]

Vreau: [commit / push / deploy / create branch]
Ce s-a schimbat: [descriere modificări]

Dă comenzile exacte. Spune ce output să aștept după fiecare comandă.
```

---

**Template 7: Continuare Sesiune**
```
=== SETUP SESIUNE [Proiect] — [Data] ===
Stack: [tehnologii + versiuni]
Fișier principal: [path]
Terminat: [ce funcționează complet]
În progres: [ce e parțial implementat]
Decizii arhitecturale active: [3-4 decizii de reținut]
=======================================

Obiectiv azi: [ce construim]
Metodă: un pas pe rând, confirm după fiecare.
Primul pas: [sau "propune tu primul pas"]
```

---

**Template 8: Code Review Pre-Commit**
```
Ești senior developer, code review pentru producție.
Prioritate: securitate → logică → performanță → stil.
Semnalează problemele CRITICE prima dată, indiferent de ce am cerut.

Cod:
[paste]

Context: [ce face modulul, cine îl apelează, date sensibile implicate?]
```

---

### PARTE 8 — Greșeli Comune

**Greșeala 1: Lipsă context fișier**
❌ `adaugă un buton de salvare`
✅ `StudioFlow (app.html), toolbar header zona butoanelor globale. Adaugă "Salvează manual" → apelează saveCurrentLead(). Stil: clasa btn-secondary identică cu butonul "Exportă" existent.`

---

**Greșeala 2: Totul dintr-un prompt**
❌ `adaugă auth, admin panel cu roluri, notificări email și export PDF`
✅ `Pasul 1/4 — DOAR autentificare: FinanceOS, Next.js 14 App Router + Supabase. Login/register email+parolă. Redirect după login: /dashboard. NU construi restul — vine în pașii următori.`

---

**Greșeala 3: Comportament vag**
❌ `fă butonul să funcționeze mai bine`
✅ `StudioFlow sf-f2, butonul "Adaugă Lead": când formularul e invalid, nu se întâmplă nimic vizibil. Vreau: câmpuri invalide → border roșu + mesaj "Completează câmpurile obligatorii" deasupra butonului, timp de 3 secunde.`

---

**Greșeala 4: Fără limite — Claude refactorizează tot**
❌ `refactorizează funcția de calcul`
✅ `Refactorizează DOAR calculateScore() (linia ~890) pentru lizibilitate. NU schimba: parametrii, return type, logica de scoring, nicio altă funcție.`

---

**Greșeala 5: Stack nespecificat**
❌ `cum adaug autentificare?`
✅ `FinanceOS: Next.js 14 App Router (NU Pages Router) + Supabase. Auth cu 6 roluri. Fără librării extra — Supabase Auth + RLS.`

---

**Greșeala 6: Resetezi în loc să refinezi**
❌ `șterge tot și ia de la capăt`
✅ `Structura e corectă. Problema e validarea email (linia 45): acceptă "test@" ca valid. Înlocuiește DOAR acea condiție cu regex standard. Restul rămâne.`

---

**Greșeala 7: Prompturi ca rugăminți**
❌ `ai putea poate să adaugi un buton?`
❌ `nu știu dacă e posibil, dar aș vrea să...`
✅ `Adaugă butonul X cu comportamentul Y.`
✅ `Implementează funcția Z care face W.`

Prompturile ezitante generează răspunsuri ezitante. Prompturile directive generează soluții directe.

---

**Greșeala 8: Descrii când poți arăta**
❌ `adaugă validare similară cu celelalte câmpuri`
✅
```
Adaugă validare în același stil:
// Pattern existent:
if (!value || value.length < 2) { showError(field, 'Câmp obligatoriu'); return; }
Aplică pe câmpul email cu condiția: email.includes('@') && email.includes('.')
```

---

### PARTE 9 — Iterare: Diagnostic + Tehnici Avansate

**5 tipuri de eroare, 5 fix-uri diferite:**

```
TIP 1 — AMBIGUITATE
  Simptom: Claude a înțeles altceva decât voiai
  Fix: "Am vrut [X specific], nu [ce a înțeles].
       [Reformulare mai precisă]."

TIP 2 — CONTEXT LIPSĂ
  Simptom: soluție corectă generic, greșită pentru cazul tău
  Fix: "Știind că [constrângerea specifică],
       cum se schimbă soluția?"

TIP 3 — LIMITĂ NESPECIFICATĂ
  Simptom: a modificat mai mult decât ai cerut
  Fix: "Revino — [ce era ok] e bun.
       [Funcția/componenta X] trebuie exact cum era."

TIP 4 — SCOPE CREEP
  Simptom: a adăugat îmbunătățiri nepuse
  Fix (pentru data viitoare): "Fă STRICT ce cer.
       Zero optimizări sau îmbunătățiri necerute explicit."

TIP 5 — HALLUCINATION
  Simptom: funcții care nu există, API-uri inventate
  Fix: "[Funcția X] nu există în [librărie vY].
       Verifică și propune alternativa corectă."
```

**Formula de rafinare universală:**
```
[Ce e bine: 1 propoziție] — [tipul erorii + locul exact] — [instrucțiunea de corecție]

Exemplu real:
"Structura componentei e corectă.
Problema: useLayoutEffect pe linia 23 — ar trebui useEffect (efectul e async).
Înlocuiește doar acea linie. Restul rămâne."
```

---

**Tehnica Critic → Builder: Claude verifică propriul output**

Cel mai eficient mod de a prinde greșeli înainte să le aplici:

```
[Primești cod de la Claude]

Acum joacă rolul unui senior developer care face code review critic
pe codul de mai sus. Ce probleme găsești?
Prioritate: securitate → logică → edge cases.
```

sau mai scurt:
```
Ce poate merge prost în codul de mai sus?
```

Funcționează pentru că Claude "vede" propriul cod diferit când schimbi framing-ul. Găsești edge cases, null checks lipsă sau probleme de logică pe care nu le-ai observat la prima lectură.

---

**Meta-Prompting: Claude îți îmbunătățește promptul**

Când nu știi cum să formulezi ce vrei:
```
Vreau să obțin [X] de la Claude, dar nu știu cum să formulez.
Ce informații ar trebui să includ în prompt pentru cel mai bun rezultat?
```

sau:
```
Iată promptul meu: [paste prompt]
Cum l-ai reformula pentru a obține un răspuns mai precis?
```

Meta-prompting e ca a cere developer-ului cu ochii închiși să îți spună ce lipsea din instrucțiunile tale.

---

**⚠️ Context Pollution — semnalul real de reset**

Nu resetezi după X iterații. Resetezi când apare **context pollution**.

**Definiție:** Claude continuă să facă referire la cod greșit din mesajele anterioare și interferează cu ce ceri acum.

**Simptome:**
- Propune soluții bazate pe o versiune a codului care nu mai există
- Contrazice o decizie luată explicit în același chat
- Răspunsurile devin mai confuze, nu mai clare, pe măsură ce iterezi

**Cum resetezi corect:**
```
Reset complet — ignoră tot ce am discutat anterior.

Situația reală actuală:
[Context block complet + codul curent]

Lecție din ce am încercat: [abordarea X nu a funcționat pentru că Y]
Noua abordare: [direcția]

[Prompt curat]
```

---

### PARTE 10 — Strategia Sesiunii: Arcul de 20-30 Mesaje

Calitatea mesajului 20 depinde de ce s-a stabilit în mesajul 3. O sesiune bună e construită, nu improvizată.

**Priming — prima propoziție contează mai mult decât crezi:**

Înainte de orice instrucțiune detaliată, o singură propoziție calibrează TOATE răspunsurile din sesiune:

```
Lucrăm la cod de producție — prioritizează corectitudinea față de completitudine.
```
```
Nivel: beginner — explică fiecare decizie tehnică non-trivială.
```
```
Context: IMM românesc, constrângeri de buget — evită soluții over-engineered.
```

Priming-ul nu înlocuiește contextul tehnic, dar setează tonul general înainte să dai instrucțiunile detaliate.

---

**Cele 4 Faze ale unei Sesiuni Experte:**

```
FAZA 1 — SETUP (mesajele 1-2)
  ✓ Priming (o propoziție calibratoare, dacă e nevoie)
  ✓ Context Block complet (proiect, stack, stare, decizii active)
  ✓ Rol/Persona setat dacă e nevoie
  ✓ Obiectivul sesiunii declarat explicit
  ✓ Metodă: "un pas pe rând, confirm după fiecare"

FAZA 2 — EXECUȚIE (mesajele 3-14)
  ✓ Un singur lucru per prompt
  ✓ Verificare în browser după fiecare pas
  ✓ Confirmi explicit înainte de pasul următor

FAZA 3 — CHECKPOINT (mesajul ~15)
  ✓ Rezumă ce s-a terminat
  ✓ Confirmă starea curentă a codului
  ✓ Re-setează persona dacă ai folosit una
  ✓ Identifică context pollution dacă există

FAZA 4 — ÎNCHIDERE (ultimele 2-3 mesaje)
  ✓ "Rezumă toate modificările din această sesiune pentru mesajul de commit"
  ✓ "Generează setup-ul pentru sesiunea următoare, cu starea curentă și ce urmează"
```

**Template Setup — Mesajul 1 din orice sesiune:**
```
[Priming dacă e nevoie]

=== SETUP SESIUNE [Proiect] — [Data] ===
Stack: [tehnologii + versiuni exacte]
Fișier principal: [path]
Stare: [ce funcționează, ce e în progres, ce e broken]
Decizii arhitecturale active:
  - [Decizie 1]: [motivul]
  - [Decizie 2]: [motivul]
=======================================

Obiectiv azi: [ce construim]
Metodă: un pas pe rând, confirm după fiecare.
Primul pas: [sau "propune tu"]
```

**Template Checkpoint — Mesajul ~15:**
```
Checkpoint — să ne sincronizăm:
Terminat: [lista]
Stare curentă: [fișiere modificate, ce funcționează]
Continuăm cu: [pasul următor]
Ai pierdut vreun context important din setup-ul de la început?
```

**Template Închidere — ultimul mesaj productiv:**
```
Sesiunea se termină. Generează:
1. Rezumatul modificărilor (pentru commit message)
2. Starea curentă în format Context Block (pentru sesiunea viitoare)
3. Primul pas recomandat pentru sesiunea următoare
```

---

## BLOC 4 — JUDECATĂ

### PARTE 11 — Securitate și Confidențialitate ⚠️

**Aceasta e secțiunea pe care cei mai mulți o ignoră. Nu ignora-o.**

**Regula fundamentală:**
> Nimic ce nu ai vrea să postezi public pe internet nu intră în prompturi Claude.

---

**❌ NICIODATĂ în prompturi:**

```
// Chei API reale:
ANTHROPIC_API_KEY=sk-ant-api03-...
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIs...
JWT_SECRET=parola-mea-secreta-de-productie

// Date reale de producție:
- Date ale pacienților (nume, CNP, diagnostic, istoric medical)
- Date financiare reale ale firmei (facturi, conturi bancare, solduri)
- Parole sau hash-uri de parole
- Date de card bancar

// Credențiale de acces:
- Connection strings de baze de date
- Token-uri OAuth active
- Credențiale de admin Supabase
```

---

**✅ CE faci în schimb:**

```
// În loc de date reale → date fictive sau structura goală:
❌ "Ion Popescu, CNP 1850312180045, diagnostic: hipertensiune"
✅ "un pacient cu câmpurile: id, name, cnp, diagnosis — schema tabelului e:"

// În loc de chei reale → descrie structura:
❌ ANTHROPIC_API_KEY=sk-ant-xyz
✅ "am variabila ANTHROPIC_API_KEY în fișierul .env"

// În loc de date cu valori → schema goală:
❌ SELECT * FROM invoices (cu date reale)
✅ CREATE TABLE invoices (id, client_id, amount, due_date) — fără date
```

---

**De ce contează special pentru proiectele tale:**

| Proiect | Risc specific |
|---------|--------------|
| Clinică medicală | Date medicale = GDPR categorie specială. Breach = amenzi până la 4% din cifra de afaceri globală. |
| FinanceOS | Date financiare ale firmei = confidențiale legal și comercial. |
| Vibe Budget | Date financiare personale ale utilizatorilor = responsabilitate contractuală. |
| StudioFlow | Date de ofertare și prețuri = informații comerciale sensibile față de concurență. |

**Regula practică simplă:**
```
Schema și structura → OK în prompturi
Date reale de producție → NICIODATĂ
Chei și credențiale → NICIODATĂ
```

---

### PARTE 12 — Când NU Folosești Claude

**1. Documentație actuală a librăriilor**

Claude are un knowledge cutoff. Pentru API-ul exact al Supabase v2, Tailwind v4, Next.js 15 — mergi direct la documentația oficială. Claude poate inventa funcții care nu există.

→ Regula: Verifică docs înainte să implementezi cu librării recent actualizate.

---

**2. Răspuns sigur-de-sine pe detalii tehnice specifice — halucinația periculoasă**

Aceasta e halucinația de care nu te ferești, pentru că nu arată ca o halucinație. Claude confirmă cu mare siguranță ceva despre comportamentul specific al unui sistem pe care îl cunoști parțial — și sună corect.

*Exemplu real:* "Da, Supabase RLS policies se aplică și la realtime subscriptions" — sună corect, Claude e sigur, dar pentru versiuni sau configurații specifice comportamentul poate fi diferit.

Halucinația evidentă (funcție inventată) o prinzi imediat. Halucinația de încredere trece de radar și ajungi cu un bug în producție.

→ Regula: Dacă Claude confirmă cu mare siguranță un detaliu tehnic specific pe care nu îl poți verifica mental, testează sau verifică în docs. Adaugă în prompturi critice: `"Dacă nu ești sigur de comportamentul exact, spune explicit în loc să ghicești."`

---

**3. Debug fără eroarea exactă din consolă**

"Ceva nu merge" fără mesajul din consolă = conversație circulară de 4-5 mesaje.

→ Regula: Deschide consola browser-ului sau terminalul, copiază eroarea literal, ATUNCI vii la Claude.

---

**4. Operații repetitive și predictibile**

200 de rânduri CSV cu o regulă fixă → Excel sau un script de 10 linii. Nu consuma context window cu task-uri mecanice.

---

**5. Cod pe care nu îl înțelegi și nu îl poți valida**

Dacă primești 200 de linii pe care nu le înțelegi, nu le pune în producție.

→ Regula: Cere explicația. Înțelege. Abia atunci aplică.
> *Nu pune în producție cod pe care nu îl poți citi.*

---

**6. Decizii de business care depind de realitatea ta specifică**

"Ar trebui să lansez produsul luna asta?" — Claude nu îți cunoaște cashflow-ul real, relațiile cu clienții, contextul pieței locale. Poate răspunde plauzibil, nu corect.

---

## BLOC 5 — REFERINȚĂ

### PARTE 13 — Flowchart Decizie Template

Deschizi ghidul în mijlocul unei sesiuni. Folosești flowchart-ul, nu citești tot ghidul.

```
Ce tip de sarcină am?
        ↓
┌─────────────────────────────────────────────────────┐
│ Construiesc ceva nou              → Template 1      │
│ Am un bug de rezolvat             → Template 2      │
│ Vreau să curăț cod existent       → Template 3      │
│ Vreau să înțeleg cod              → Template 4      │
│ Trebuie să iau o decizie tehnică  → Template 5      │
│ Vreau să fac commit/push/deploy   → Template 6      │
│ Reiau o sesiune anterioară        → Template 7      │
│ Verific cod înainte de commit     → Template 8      │
└─────────────────────────────────────────────────────┘
        ↓
Am un exemplu de cod similar care arată ce vreau?
  DA  → Adaugă Few-Shot (Parte 2) + C-S-I-L-V
  NU  → Folosește C-S-I-L-V singur
        ↓
Sarcina implică analiză, debugging sau decizie?
  DA  → Adaugă "Gândește pas cu pas" (Parte 4)
  NU  → Continuă fără
        ↓
Vreau un format specific de răspuns?
  DA  → Adaugă pattern din Parte 5
  NU  → Continuă fără
        ↓
E sesiune nouă sau mai lungă de 60 min?
  DA  → Adaugă Context Block (Template 7 / Parte 10)
  NU  → Continuă fără
        ↓
Promptul conține date sensibile sau credențiale?
  DA  → Înlocuiește cu date fictive / structură (Parte 11)
  NU  → Trimite
```

---

### PARTE 14 — Sesiune Reală: Înainte vs. Expert

**Task identic:** Adaugă buton Export CSV pe pagina Tranzacții din Vibe Budget.

---

**SESIUNEA SLABĂ — 38 de minute, feature nefuncțional:**

```
Tu → Claude:
"adaugă export CSV la tranzacții"

Claude:
[Generează cod cu librăria csv-parse, care nu e instalată în proiect.
Plasează butonul în header, nu lângă filtre. Stil diferit față de UI.]

Tu → Claude:
"nu arată bine și dă eroare"

Claude:
[Modifică stilul dar folosește clase Tailwind care nu există în proiect.
Nu rezolvă eroarea de librărie.]

Tu → Claude:
"încearcă altfel"

Claude:
[Rescrie componenta complet. Modifică și logica de fetch care funcționa.
Introduce un bug nou pe filtre.]

Tu → Claude:
"ai stricat fetch-ul, întoarce-te la varianta de dinainte"

Claude:
[Încearcă să reconstruiască fetch-ul din memorie. Nu mai știe exact cum era.]

Tu → Claude:
"lasă, o iau de la capăt mâine"
```

**Rezultat:** 38 minute. Feature nefuncțional. Un bug nou introdus în cod care mergea.

---

**SESIUNEA EXPERTĂ — 7 minute, feature funcțional:**

```
Tu → Claude:
"Proiect: Vibe Budget (app/transactions/page.tsx).
Pagina afișează lista tranzacțiilor cu filtre active — fetch-ul funcționează,
nu atinge logica de date.

Vreau un buton Export CSV care descarcă tranzacțiile vizibile (după filtrele
active) ca fișier .csv.

Few-shot — buton existent în același fișier, referință de stil:
<button
  onClick={handleAutoCategize}
  className='px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700'
>
  Auto-categorizează
</button>

Butonul Export CSV: același stil, plasat lângă butonul de mai sus.
CSV: coloanele date, descriere, suma, categoria.
Fără librării noi — folosesc API-ul nativ Blob + URL.createObjectURL.

NU schimba: logica de fetch, filtrele existente, restul componentei.
Verific că funcționează: apăs butonul → se descarcă fișier .csv cu datele
vizibile după filtrele active.

Format răspuns: doar funcția handleExportCSV + JSX-ul butonului."

Claude:
[Returnează exact funcția + butonul. 18 linii. Stil identic. Fără librării noi.
Fetch-ul și filtrele intacte.]

Tu → Claude:
"funcționează. fă commit."
```

**Rezultat:** 7 minute. Feature complet funcțional. Zero modificări necerute.

> **Notă realistă:** Chiar și cu un prompt expert, poți uneori ajunge la 2 iterații. Diferența față de sesiunea slabă: știi exact ce să corectezi, nu reîncepi de la zero.

---

**Ce a făcut diferența în 5 puncte:**
1. Context exact — fișier, stare curentă, ce nu trebuie atins
2. Few-Shot — butonul existent ca referință de stil
3. Constrângere tehnică explicită — fără librării noi
4. Limite clare — nu atinge fetch-ul, filtrele
5. Format output — doar ce am nevoie, nu toată componenta rescrisă

---

### PARTE 15 — Quick Reference Card

```
╔═══════════════════════════════════════════════════════╗
║       VIBE-CODING CU CLAUDE — Quick Reference v4.0   ║
╠═══════════════════════════════════════════════════════╣
║  ÎNAINTE DE ORICE PROMPT                              ║
║  □ Date sensibile / credențiale? → înlocuiește        ║
║  □ Librărie recentă? → verifică docs întâi            ║
║  □ Eroare de debug? → copiaz-o literal din consolă    ║
║  □ Sesiune nouă? → Claude nu ține minte de ieri       ║
╠═══════════════════════════════════════════════════════╣
║  AM UN EXEMPLU SIMILAR ÎN COD?                        ║
║  DA  → Few-Shot + C-S-I-L-V      (Parte 2 + 3)        ║
║  NU  → C-S-I-L-V singur          (Parte 3)            ║
╠═══════════════════════════════════════════════════════╣
║  FORMULA C-S-I-L-V                                    ║
║  C Context    → fișier + stare curentă                ║
║  S Stare      → ce există și funcționează             ║
║  I Intenție   → PROBLEMA (nu soluția)                 ║
║  L Limite     → ce NU schimbi                         ║
║  V Verificare → cum testez în browser                 ║
╠═══════════════════════════════════════════════════════╣
║  TEHNICI SUPLIMENTARE                                 ║
║  Few-Shot       → un exemplu din cod > orice descriere║
║  Gândește P-cu-P→ debug, decizii, edge cases (Parte 4)║
║  Critic→Builder → "ce poate merge prost aici?"        ║
║  Meta-Prompting → "cum reformulez acest prompt?"      ║
║  Persona        → setezi la msg 1, re-setezi la ~15   ║
║  Checkpoint     → la mesajul ~15                      ║
╠═══════════════════════════════════════════════════════╣
║  CEVA NU MERGE?                                       ║
║  Diagnostichează: Ambiguitate / Context / Limită /    ║
║  Scope Creep / Hallucination                          ║
║  Formula: "[ce e bine] — [eroarea exactă] —           ║
║            [instrucțiunea de corecție]"               ║
║  Reset DOAR la context pollution, nu după N iterații  ║
╠═══════════════════════════════════════════════════════╣
║  NU FOLOSI CLAUDE PENTRU                              ║
║  × docs librărie actualizată                          ║
║  × debug fără eroarea din consolă                     ║
║  × confirmare sigur-de-sine pe detalii tehnice specifice║
║  × cod pe care nu îl poți valida                      ║
╚═══════════════════════════════════════════════════════╝
```

---

*v4.0 — Mai 2026 · Bazat pe 15 proiecte reale: HoReCa, arhitectură, medical, finanțe, SaaS*
