# Ghid Git & Deployment Workflow
## Pentru Vibe-Coding cu Claude — v1.0

**Public țintă:** Vibe-coder cu proiecte funcționale local dar nedeploiate sau neîmpinse pe GitHub. Dai skip la teorie, vrei să fie live azi.

**Stack acoperit:** Git + GitHub · Vercel (Next.js) · Netlify (HTML static) · Supabase env vars · Windows 10 + Claude Code

---

## TL;DR — 3 lucruri care schimbă totul

**1. Push după fiecare sesiune = backup real**
`git add + commit` salvează pe calculatorul tău. `git push` salvează pe GitHub. Dacă laptopul moare sau fișierele se corup, orice commit nepush-uit dispare. Commit-uri locale = muncă neprotejată.

**2. Vercel conectat la GitHub = deploy automat**
Setup o singură dată. După aia: `git push` → Vercel detectează → build → live în ~30 secunde. Fără comenzi de deploy, fără FTP, fără SSH. Orice push pe `main` = producție nouă.

**3. `.env.local` nu intră niciodată în commit — `.env.example` întotdeauna intră**
O singură greșeală și cheia ta Supabase sau Anthropic e publică pe GitHub pentru totdeauna (inclusiv în history). `.env.example` cu valori placeholder se commitează — e documentația variabilelor necesare.

---

## Primul proiect live — Walkthrough complet

Dacă e prima dată sau vrei un ghid de referință rapid fără să citești tot: urmează aceste comenzi în ordine. Conectează toate secțiunile din ghid.

```bash
# ── SETUP (o dată pe mașină nouă) ──────────────────────────────
git config --global user.name "Numele Tău"
git config --global user.email "email@exemplu.com"
git config --global core.editor "code --wait"
git config --global pull.rebase false

# ── INIȚIALIZARE PROIECT ───────────────────────────────────────
cd Desktop/proiect-meu
git init
# Creează .gitignore  (template în Parte 2)
# Creează .env.example (template în Parte 2)
git add .gitignore .env.example
git commit -m "chore: initial project setup with gitignore and env template"

# ── CONECTARE GITHUB ───────────────────────────────────────────
# GitHub.com → New Repository → Create (fără README)
git remote add origin git@github.com:username/proiect-meu.git
git branch -M main      # redenumești branch-ul default în "main"
git push -u origin main # -u setează upstream: de acum "git push" fără argumente

# ── VERCEL (o dată per proiect) ────────────────────────────────
# vercel.com → Add New Project → Import repo → Add env vars → Deploy

# ── WORKFLOW ZILNIC (repetă la fiecare sesiune) ────────────────
git pull                          # sincronizezi cu remote
# ... lucrezi în VS Code ...
git status                        # ce fișiere s-au schimbat
git diff                          # ce exact s-a schimbat
git add app/page.tsx              # adaugi fișierele relevante
git commit -m "feat: descriere clară"
git push                          # → Vercel deployează automat
```

**Rezultat:** proiect live pe `https://proiect-meu.vercel.app` cu auto-deploy la orice push viitor.

**Proiect existent (cod deja scris, fără Git):**
```bash
cd Desktop/proiect-meu
git init
# Creează .gitignore ÎNAINTE de git add (protejezi .env și node_modules)
git add -A
git commit -m "chore: initial commit"
# Continuă cu pașii de conectare GitHub de mai sus
```

---

## BLOC 1 — Git Setup & Mental Model

---

### Parte 0: Mental Model — Cele 4 Zone

Git nu e "Save As". E un sistem cu **4 zone distincte**, și dacă nu înțelegi asta, comenzile par magice.

```
[Fișiere pe disk]          [Git local]              [GitHub]

Working Tree  →  Staging  →  Local Repo  →  Remote Repo
(editezi)       (pregătești)  (commit)       (push)
                git add        git commit      git push
```

**Working Tree** = fișierele pe care le editezi în VS Code. Nimeni nu știe de ele în afară de tine.

**Staging Area (Index)** = "coș de cumpărături" — alegi ce intră în următorul commit. `git add fisier.ts` pune fișierul în coș.

**Local Repository** = snapshots permanente salvate pe calculatorul tău. `git commit -m "mesaj"` face o fotografie a tot ce e în Staging.

**Remote Repository (GitHub)** = copie în cloud a repo-ului tău local. `git push` trimite commit-urile locale la GitHub.

**Ce se întâmplă când tastezi `git status`:**
```
On branch main
Your branch is ahead of 'origin/main' by 5 commits.
  (use "git push" to publish your local commits)

Changes not staged for commit:
  modified:   app/page.tsx

Untracked files:
  components/NewWidget.tsx
```

- `ahead of 'origin/main' by 5` → ai 5 commit-uri locale care NU sunt pe GitHub
- `modified` → ai editat fișiere dar NU le-ai pus în Staging cu `git add`
- `Untracked` → fișiere noi pe care Git nu le urmărește deloc

**Greșeala clasică:** Crezi că `git commit` trimite codul pe GitHub. Nu — commit e doar o fotografie locală. Push e cel care trimite.

---

**Ce e `HEAD`:**

`HEAD` = "unde ești tu acum" în istoricul Git. Pointează la ultimul commit de pe branch-ul curent. `HEAD~1` = commit-ul dinaintea celui curent, `HEAD~2` = două commit-uri în urmă.

```
commit abc1234  ← HEAD (ești aici)
commit def5678  ← HEAD~1
commit ghi9012  ← HEAD~2
```

Apare în comenzi ca `git reset HEAD~1`, `git diff HEAD`, `git log HEAD..origin/main`.

---

**Setup inițial Git (o dată pe mașină nouă):**

Înainte de primul commit, Git trebuie să știe cine ești. Fără asta, `git commit` eșuează cu "Author identity unknown":

```bash
git config --global user.name "Numele Tău"
git config --global user.email "email@exemplu.com"

# Setează editorul default la VS Code (în loc de vim)
git config --global core.editor "code --wait"

# Comportament la git pull — evită eroarea "divergent branches" pe fresh install
git config --global pull.rebase false

# Verificare
git config --list
```

Fără `pull.rebase`, primul `git pull` pe o mașină nouă returnează:
```
fatal: Need to specify how to reconcile divergent branches.
```

Aceste setări se salvează în `~/.gitconfig` și se aplică la toate repo-urile de pe mașina ta.

---

### Parte 1: Workflow Zilnic

Acesta este ritmul de bază. Nu e calendar-based ("push zilnic") — e **event-driven**: push după fiecare sesiune de lucru sau feature complet, indiferent de oră.

**Pasul 1 — Sincronizează cu remote-ul ÎNAINTE să începi:**
```bash
git pull
```
Dacă lucrezi de pe mai multe mașini sau ai colaboratori, fă `git pull` la începutul fiecărei sesiuni. Altfel riști conflicte la push.

**Pasul 2 — Verifică ce s-a schimbat:**
```bash
git status
```
Citește output-ul. Înțelege ce e modified vs untracked vs staged.

**Pasul 3 — Revizuiește exact ce s-a modificat:**
```bash
git diff                # modificările nestaged (ce nu e încă în coș)
git diff --staged       # ce e deja în staging (după git add)
git diff HEAD           # TOATE modificările față de ultimul commit (staged + unstaged)
```
Acest pas previne commit-urile accidentale cu `console.log`, cod comentat, sau debugging code. Fă-l reflex înainte de orice `git add`.

**Pasul 4 — Adaugă fișierele relevante:**
```bash
# Adaugă fișiere specifice (preferabil — știi exact ce intră)
git add app/transactions/page.tsx
git add components/TransactionForm.tsx

# SAU adaugă tot (după ce ai verificat cu git diff că totul e intenționat)
git add -A
```

**Pasul 5 — Fă commit cu mesaj descriptiv:**
```bash
git commit -m "feat: add transaction form with Supabase insert

Co-Authored-By: Claude <noreply@anthropic.com>"
```

**Pasul 6 — Trimite pe GitHub:**
```bash
git push
```

**Pasul 7 — Confirmă:**
```bash
git status
# Trebuie să scrie: "Your branch is up to date with 'origin/main'."
```

**Workflow în Claude Code (cu comenzile custom):**
```
/commit   → face Pașii 2-5 automat
/push     → face Pasul 6 + verificare
```

**Când să push-uiești:**
- **Event**: la sfârșitul oricărei sesiuni de lucru cu rezultat concret
- **Event**: după fiecare feature complet sau bugfix
- **Obligatoriu**: înainte să închizi laptopul
- **Niciodată**: pe baza calendarului ("n-am push-uit azi") — produce push-uri goale sau haotice

**`git fetch` vs `git pull` — distincția care contează:**
```bash
git fetch origin          # descarcă modificările remote fără să le aplice
git status                # acum poți vedea: "behind 'origin/main' by 3 commits"
git merge origin/main     # aplici manual când ești pregătit

git pull                  # = git fetch + git merge origin/main automat (mai rapid, mai puțin control)
```
Folosește `git fetch` când vrei să *verifici* ce s-a schimbat înainte să *aplici*. Folosește `git pull` când ești sigur că nu ai conflicte locale.

---

### Parte 2: .gitignore și .env.example

**`.gitignore`** spune Git ce să ignore. **`.env.example`** documentează ce variabile sunt necesare. Amândouă merg în orice proiect serios.

---

**Template .gitignore pentru Next.js + Supabase:**
```gitignore
# Dependencies
node_modules/
.pnp
.pnp.js

# Build output
.next/
out/
build/
dist/

# Environment variables — CRITICAL
.env
.env.local
.env.development.local
.env.test.local
.env.production.local

# Supabase local dev
.supabase/

# Logs
*.log
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# OS files
.DS_Store
Thumbs.db
Desktop.ini

# IDE
.idea/
*.swp
*.swo

# TypeScript
*.tsbuildinfo
next-env.d.ts
```

**Template .gitignore pentru HTML static offline:**
```gitignore
# OS files
.DS_Store
Thumbs.db
Desktop.ini

# IDE
.idea/
*.swp
```

---

**`.env.example` — ce e și de ce îl commiți:**

Acesta e fișierul pe care îl uiți și care te costă ore când setup-ezi proiectul pe o mașină nouă sau când onboardezi pe cineva. Conține cheile cu valori placeholder — niciodată valori reale.

```bash
# .env.example — SE COMMITEAZĂ în git
# Copiază în .env.local și completează valorile reale

# Supabase
NEXT_PUBLIC_SUPABASE_URL=https://your-project-ref.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key-here

# Supabase Service Role (server-side only — niciodată NEXT_PUBLIC_)
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key-here

# Claude API
ANTHROPIC_API_KEY=sk-ant-your-key-here

# App config
NEXT_PUBLIC_APP_URL=http://localhost:3000
```

**Workflow cu .env.example:**
```bash
# Când clonezi un proiect pe mașină nouă:
cp .env.example .env.local
# Completezi valorile reale în .env.local
# .env.local NU se commitează (e în .gitignore)
```

**Verificare că .gitignore funcționează — înainte de primul push:**
```bash
git status
# Dacă vezi .env sau node_modules în listed files → OPREȘTE-TE
# Adaugă în .gitignore ÎNAINTE de git add
```

**Dacă ai commit-uit accidental .env:**
```bash
# Elimină din tracking (fișierul rămâne local):
git rm --cached .env
# PowerShell — fără risc de encoding greșit:
Add-Content .gitignore ".env"
git add .gitignore
git commit -m "chore: remove .env from tracking, add to gitignore"
git push
# IMPORTANT: rotează IMEDIAT toate cheile compromise (Supabase + Anthropic)
# Chiar dacă repo e privat — dacă a fost public chiar și 1 minut, cheile sunt compromise
```

**Dacă ai push-uit deja `.env` pe GitHub public:** rotează IMEDIAT toate cheile. GitHub scanează repo-urile public pentru pattern-uri de chei cunoscute. Istoria Git păstrează fișierele șterse — curățarea necesită `git filter-repo` (vezi Parte 14).

---

## BLOC 2 — Commit & Branch Strategy

---

### Parte 3: Mesaje de Commit care Lucrează

Un mesaj de commit bun îți spune CE s-a schimbat și DE CE — nu cum. Peste 3 luni, "fixed stuff" nu îți spune nimic.

**Format Conventional Commits (standard industrial):**
```
<tip>: <descriere scurtă în engleză> (max 72 caractere)

[corp opțional — de ce, nu cum]
```

**Tipuri oficiale:**
| Tip | Când îl folosești |
|-----|-------------------|
| `feat` | Feature nou care adaugă valoare utilizatorului |
| `fix` | Bug fix |
| `refactor` | Restructurare cod fără schimbare de comportament |
| `style` | Formatare, spații, fără schimbare logică |
| `docs` | Documentație, README, comentarii |
| `chore` | Setup, config, dependențe, fișiere suport |
| `ci` | CI/CD, scripts de build, deployment config |
| `perf` | Îmbunătățire de performanță |
| `test` | Adăugare sau modificare teste |
| `revert` | Revert la commit anterior |

**Exemple bune:**
```bash
git commit -m "feat: add expense categories with Supabase insert"
git commit -m "fix: prevent double submit on transaction form"
git commit -m "feat: implement auth flow with Supabase magic link"
git commit -m "chore: add .gitignore and .env.example for Next.js project"
git commit -m "ci: configure Vercel env vars for production"
git commit -m "perf: lazy load chart component to reduce initial bundle"
```

**Exemple proaste (evită):**
```bash
git commit -m "update"           # update ce?
git commit -m "fixed"            # fixat ce?
git commit -m "aaa"              # ...
git commit -m "work in progress" # nu commiți WIP pe main
git commit -m "deploy stuff"     # "deploy" nu e tip standard → chore: sau ci:
```

**Regulă practică:** Dacă mesajul necesită "și" (ex: "add form and fix bug and update style"), fă 3 commit-uri separate. Un commit = un lucru.

**Co-Authored-By pentru sesiunile Claude Code:**
```bash
git commit -m "feat: implement dashboard with Chart.js

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

### Parte 4: Branch Strategy pentru Vibe-Coding

Branching complet (Gitflow, trunk-based development) e overkill pentru proiecte solo sau IMM mic. Iată strategia simplă care funcționează:

**Strategia: Main + Feature Branches**

```
main          ●─────────●──────────●──────────● (production)
               \        /          \          /
feature/auth    ●──────●    feature/dashboard ●─●
```

**Regula de aur pentru `main`:**
- `main` = cod care funcționează. Tot ce e pe `main` e deployabil oricând.
- Nu lucra direct pe `main` la features mari sau riscante.

**Comenzi moderne — `git switch` (recomandate față de `git checkout`):**

Git 2.23+ a introdus `git switch` și `git restore` pentru a separa funcțiile confuze ale `git checkout`:

```bash
# Modern (recomandat)
git switch -c feature/auth-supabase   # creează și trece pe branch nou
git switch main                        # treci pe main
git restore fisier.tsx                 # anulează modificările unui fișier

# Classic (funcționează în continuare)
git checkout -b feature/auth-supabase
git checkout main
git checkout -- fisier.tsx
```

**Workflow complet cu branches:**
```bash
# 1. Creează branch nou
git switch -c feature/auth-supabase

# 2. Lucrezi, faci commit-uri pe branch
git add -A
git commit -m "feat: add login page with Supabase magic link"
git commit -m "feat: add session handling and redirect"

# 3. Push branch pe GitHub (Vercel va genera Preview URL automat)
git push -u origin feature/auth-supabase

# 4. Când e gata, mergi pe main și faci merge
git switch main
git pull                              # sincronizezi main cu remote ÎNAINTE de merge
git merge feature/auth-supabase

# 5. Push main → deploy în producție
git push

# 6. Șterge branch-ul (opțional, după merge)
git branch -d feature/auth-supabase
git push origin --delete feature/auth-supabase
```

**Când branching-ul devine util:**
- Lucrezi la ceva care durează 2+ zile și vrei să poți livra bugfix-uri pe main între timp
- Ai un deployment live și vrei URL de preview pentru testare înainte de producție
- Vrei să "abandoni" un experiment fără să strici ce funcționează

**Pentru proiecte solo simple (HTML offline, prototipuri):**
Lucrezi direct pe `main`. Branching e opțional — nu complica inutil.

**Vizualizare branch-uri:**
```bash
git log --oneline --graph --all
# Output vizual al tuturor branch-urilor și merge-urilor
```

---

### Parte 5: GitHub Setup + SSH + Clone

**Repo Public vs Privat:**

| Situație | Recomandare |
|----------|-------------|
| Tool gratuit distribuit (CashPulse, FollowUp, etc.) | Public |
| Proiect de portofoliu | Public |
| Cod de business cu logică proprietară | Privat |
| Proiecte cu date client (clinică, ERP) | **Obligatoriu Privat** |
| Orice proiect cu secrets în history | Privat |
| Default pentru proiecte comerciale | Privat |

**IMPORTANT:** Vercel și Netlify accesează repo-uri private fără probleme. Privat ≠ nedeployabil.

---

**SSH — setup o dată, push fără parolă pentru totdeauna:**

SSH e configurat o singură dată și funcționează permanent — varianta preferată față de HTTPS pentru lucru zilnic.

```bash
# 1. Generează cheie SSH (dacă nu ai deja)
ssh-keygen -t ed25519 -C "email@exemplu.com"
# Apasă Enter la toate întrebările (passphrase opțional — vezi mai jos)

# 2. Copiază cheia publică — Windows PowerShell:
Get-Content "$env:USERPROFILE\.ssh\id_ed25519.pub" | clip

# 3. Adaugă pe GitHub:
# GitHub.com → Settings → SSH and GPG Keys → New SSH Key → paste + Save

# 4. Testează conexiunea
ssh -T git@github.com
# Output așteptat: "Hi username! You've successfully authenticated..."

# 5. Schimbă remote-ul din HTTPS în SSH (pentru repo-uri existente)
git remote set-url origin git@github.com:username/repo-name.git

# 6. Verificare
git remote -v
# origin  git@github.com:username/repo-name.git (fetch)
# origin  git@github.com:username/repo-name.git (push)
```

**SSH passphrase + SSH Agent (Windows) — tastezi parola o dată, nu la fiecare push:**

Dacă ai setat passphrase la `ssh-keygen` (recomandat pentru securitate), fiecare push va cere parola — opusul a ce promite SSH. Soluția: SSH Agent ține cheia în memorie.

```powershell
# Activează OpenSSH Agent service (o dată, cu drepturi administrator)
Get-Service -Name ssh-agent | Set-Service -StartupType Automatic
Start-Service ssh-agent

# Adaugă cheia la agent (o dată per sesiune sau per boot)
ssh-add "$env:USERPROFILE\.ssh\id_ed25519"
# → Enter passphrase: (introduci o singură dată)
# → Identity added: ...

# De acum, git push funcționează fără parolă până la restart
```

Fără passphrase (ai apăsat Enter gol la generare) → SSH Agent nu e necesar.

---

**Setup repo nou pe GitHub:**
```bash
# 1. Pe GitHub.com: New Repository → Public/Private → Create (fără README inițial)

# 2. În terminal, în folderul proiectului:
git remote add origin git@github.com:username/repo-name.git
git branch -M main    # redenumești branch-ul default în "main" (convenție GitHub)
git push -u origin main
```

---

**git clone — cum aduci un proiect existent pe o mașină nouă:**

```bash
# Clonezi repo-ul (SSH — dacă ai configurat SSH pe mașina nouă)
git clone git@github.com:username/repo-name.git

# Sau HTTPS (mai simplu dacă SSH nu e configurat)
git clone https://github.com/username/repo-name.git

# Intri în folder
cd repo-name

# Setup variabile de mediu
cp .env.example .env.local
# Completezi valorile reale în .env.local

# Instalezi dependențele (Next.js)
npm install

# Pornești proiectul
npm run dev
```

`git clone` descarcă TOATĂ istoria repo-ului, nu doar fișierele curente. Branch-ul default (`main`) e activ automat.

---

**Verificare remote:**
```bash
git remote -v              # vede URL-ul curent
git remote get-url origin  # alternativă
```

---

## BLOC 3 — Deploy Pipeline

---

### Parte 6: Vercel Setup — Connect GitHub → Auto-Deploy

Vercel e platforma nativă pentru Next.js. Setup o dată, auto-deploy pentru totdeauna.

**Condiții prealabile:**
- Cont Vercel la vercel.com (free tier e suficient)
- Repo-ul proiectului pe GitHub
- Proiect Next.js cu `package.json` valid

**Setup pas cu pas:**

**Pasul 1 — Import proiect:**
1. Vercel Dashboard → "Add New Project" → "Import Git Repository"
2. Conectează contul GitHub dacă prima dată
3. Selectează repo-ul proiectului

**Pasul 2 — Configurare build:**
Vercel detectează automat Next.js. Nu schimba nimic din setările auto-detectate dacă nu știi exact ce faci:
- Framework Preset: `Next.js`
- Build Command: `next build`
- Output Directory: `.next`
- Install Command: `npm install`

**Pasul 3 — Variabile de mediu:**
Adaugă ÎNAINTE de primul deploy (Parte 7 — detalii complete).

**Pasul 4 — Deploy:**
Click "Deploy". Primul deploy durează 1-3 minute.

**Ce se întâmplă după:**
- Orice `git push` pe `main` → Vercel detectează automat → build → deploy nou
- Orice push pe alt branch → Vercel generează un URL de **Preview** separat
- URL de producție: `proiect-name.vercel.app` sau custom domain dacă ai setat

**Verificare că auto-deploy funcționează:**
```bash
# Fă o modificare mică, commit și push
git add app/page.tsx
git commit -m "chore: test auto-deploy"
git push
# Vercel Dashboard → Deployments → apare deployment nou în curs
```

---

**Cold Start — ce e și cum îl gestionezi:**

API routes pe Vercel Hobby plan sunt serverless functions. Dacă nu au primit trafic 10-30 minute, primul request după idle durează 3-5 secunde. Afectează demo-uri și aplicații cu utilizatori ocazionali.

```typescript
// Opțiunea 1 — Edge Runtime (zero cold start, ~50ms latency):
// app/api/generate/route.ts
export const runtime = 'edge'
// ATENȚIE: Edge Runtime NU suportă Supabase JS client v2.
// Folosește Edge Runtime DOAR pe routes care nu ating Supabase direct.

// Opțiunea 2 — Mărești timeout-ul (rămâi pe Node.js runtime):
export const maxDuration = 60  // secunde — metoda modernă Next.js App Router
```

Dacă folosești Supabase pe route, nu adăuga `export const runtime = 'edge'` — va eșua. Acceptă cold start și adaugă un loading state vizibil la prima cerere.

---

**Preview Deployments (bonus valoros):**
Vercel generează URL de preview pentru orice branch non-main — testezi înainte de producție:

```bash
git switch -c feature/new-dashboard
# lucrezi, commit-uri...
git push -u origin feature/new-dashboard
# Vercel generează: https://proiect-feature-new-dashboard.vercel.app
# Testezi → dacă e ok:
git switch main
git pull
git merge feature/new-dashboard
git push
```

---

### Parte 7: Variabile de Mediu pe Vercel

Variabilele din `.env.local` NU ajung pe Vercel automat — trebuie configurate manual.

**Categorii de variabile:**

| Prefix | Disponibil | Vizibil în browser | Exemple |
|--------|-----------|-------------------|---------|
| `NEXT_PUBLIC_` | Client + Server | **DA** — oricine poate vedea | `NEXT_PUBLIC_SUPABASE_URL` |
| fără prefix | Server only | **NU** | `ANTHROPIC_API_KEY`, `SUPABASE_SERVICE_ROLE_KEY` |

**Regula critică:**
- Chei API cu privilegii ridicate (service role, secret keys, ANTHROPIC_API_KEY) → **NICIODATĂ** `NEXT_PUBLIC_`
- Anon key Supabase e designată pentru public → `NEXT_PUBLIC_` e ok

**Unde adaugi pe Vercel:**
1. Vercel Dashboard → Proiectul tău → Settings → Environment Variables
2. Adaugă fiecare variabilă: Name + Value
3. Selectează mediile: Production ✓, Preview ✓, Development ✓
4. Save → **re-deploy necesar** (modificările la env vars nu se aplică retroactiv)

**Ce variabile pentru proiectele tale:**

```bash
# Orice proiect Supabase:
NEXT_PUBLIC_SUPABASE_URL        = https://xxxxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY   = eyJhbGci...
SUPABASE_SERVICE_ROLE_KEY       = eyJhbGci...   # dacă folosești server-side

# Proiecte cu Claude API:
ANTHROPIC_API_KEY               = sk-ant-...

# App config:
NEXT_PUBLIC_APP_URL             = https://proiect.vercel.app
```

**Validare la startup — eșuează devreme, nu la runtime:**
```typescript
// lib/env.ts
const requiredEnvVars = [
  'NEXT_PUBLIC_SUPABASE_URL',
  'NEXT_PUBLIC_SUPABASE_ANON_KEY',
  'ANTHROPIC_API_KEY',
]

for (const envVar of requiredEnvVars) {
  if (!process.env[envVar]) {
    throw new Error(`Missing required environment variable: ${envVar}`)
  }
}
```

**Simptom frecvent:** funcționează la `localhost:3000` dar pe Vercel returnează eroare.
**Cauza:** variabila există în `.env.local` local dar nu e setată pe Vercel.
**Fix:** Settings → Environment Variables pe Vercel → adaugă → re-deploy.

---

### Parte 8: Netlify pentru HTML Static Apps

Pentru aplicațiile offline (CashPulse, FollowUp Board, PurchaseCompare, Reorder Radar, InvoiceChaser, Daily Sales Flash, MenuMix Matrix) — HTML pur fără build step — Netlify e cel mai simplu.

**Metoda 1 — Drag & Drop (cel mai rapid, fără GitHub):**
1. netlify.com → New site → "Deploy manually"
2. Trage folderul proiectului direct în browser
3. Live în 10 secunde: `random-name.netlify.app`

Limitare: nu se auto-updatează la modificări viitoare.

**Metoda 2 — Connect GitHub (recomandat pentru proiecte active):**
1. Netlify Dashboard → Add New Site → Import from Git
2. Conectează GitHub → selectează repo
3. Configurare (pentru HTML pur):
   - Build command: **lasă gol**
   - Publish directory: `.` (sau subfolder dacă `index.html` nu e în rădăcină)
4. Deploy site

**Structura folder corectă:**
```
Desktop/cashpulse/
├── index.html       ← fișierul principal (Netlify îl caută automat)
├── landing.html     ← landing page opțional
└── .gitignore
```

---

**`_redirects` — DOAR pentru apps cu routing JavaScript (SPA/PWA):**

Dacă app-ul tău are routing client-side în JavaScript (navigare fără reload de pagină completă — ex: StudioFlow PWA cu hash routing), Netlify returnează 404 la refresh sau URL direct. Soluția:

```
# _redirects (fișier în rădăcina proiectului, lângă index.html)
/*    /index.html   200
```

**ATENȚIE:** Nu adăuga `_redirects` pe apps cu mai multe fișiere HTML distincte (ex: `index.html` + `landing.html`). Regula `/*` ar trimite și `/landing.html` spre `index.html`, rupând navigarea. Proiectele tale HTML cu `landing.html` separat **nu au nevoie de `_redirects`**.

---

**Custom URL pe Netlify (gratuit):**
Site Settings → Domain Management → Edit site name → `cashpulse.netlify.app`

**Netlify vs Vercel:**

| Criteriu | Netlify | Vercel |
|----------|---------|--------|
| HTML pur, fără build | ✓ Ideal | ✓ Merge, dar overkill |
| Next.js | ✓ Merge | ✓✓ Optimizat nativ |
| Drag & drop deploy | ✓ | ✗ |
| Auto-deploy din GitHub | ✓ | ✓ |
| Preview per branch | ✓ | ✓ |
| Free tier | Generos | Generos |

---

### Parte 9: Custom Domain pe Vercel

Ai un domeniu propriu (ex: `vibecafe.ro`) și vrei să-l conectezi.

**Pasul 1 — Adaugă domeniu pe Vercel:**
Settings → Domains → adaugă `vibecafe.ro` sau `app.vibecafe.ro`

**Pasul 2 — Configurează DNS la registrar:**

Vercel îți arată exact ce să adaugi. Două opțiuni:

**A Record (domeniu rădăcină `vibecafe.ro`):**
```
Type: A
Name: @
Value: 76.76.21.21   ← verifică valoarea exactă în Vercel Dashboard (poate fi actualizată)
TTL: 3600
```

**CNAME (subdomeniu `app.vibecafe.ro`):**
```
Type: CNAME
Name: app
Value: cname.vercel-dns.com
TTL: 3600
```

**Pasul 3 — Aștepți propagarea DNS:** 5-30 minute, rar până la 48h. Vercel afișează statusul verificării.

**SSL/HTTPS:** certificat Let's Encrypt generat automat după verificarea DNS. Zero configurare manuală.

**www redirect:** adaugă și `www.vibecafe.ro` → Vercel setează redirect automat.

---

## BLOC 4 — Troubleshooting & Recovery

---

### Parte 10: Merge Conflicts — Nu intra în panică

Merge conflicts apar când două branch-uri (sau local vs remote) au modificat același fișier pe aceeași linie. Git nu știe ce versiune să păstreze și cere să alegi tu.

**Cum arată un conflict:**
```
<<<<<<< HEAD
const title = "Dashboard Vânzări"
=======
const title = "Sales Dashboard"
>>>>>>> feature/translations
```

- `<<<<<<< HEAD` → versiunea ta (branch-ul curent)
- `=======` → separatorul
- `>>>>>>> feature/translations` → versiunea din branch-ul care se merge-uiește

**Pașii pentru rezolvare:**

**Pasul 1 — Identifică fișierele cu conflicte:**
```bash
git status
# Both modified: app/page.tsx
# Both modified: components/Header.tsx
```

**Pasul 2 — Deschide fișierul în VS Code:**
VS Code marchează vizual conflictele și oferă butoane: `Accept Current Change`, `Accept Incoming Change`, `Accept Both Changes`, `Compare Changes`.

**Pasul 3 — Editează manual la nevoie:**
Șterge marcajele `<<<<<<<`, `=======`, `>>>>>>>` și lasă codul corect final:
```typescript
const title = "Dashboard Vânzări"  // sau varianta corectă
```

**Pasul 4 — Marchează ca rezolvat și finalizează:**
```bash
git add app/page.tsx
git add components/Header.tsx
git commit -m "chore: resolve merge conflicts in dashboard"
```

---

**Conflict la `git pull` (cel mai frecvent scenariu):**
```bash
git pull
# Auto-merging app/page.tsx
# CONFLICT (content): Merge conflict in app/page.tsx
# Automatic merge failed; fix conflicts and then commit the result.
```

Urmezi Pașii 1-4 de mai sus.

---

**Conflict la `git merge feature/xyz`:**
Același proces. Dacă vrei să abandonezi merge-ul în mijlocul rezolvării:
```bash
git merge --abort   # anulează merge-ul, revii la starea dinainte
```

---

**Cum eviți conflictele:**
```bash
# La începutul oricărei sesiuni de lucru:
git pull

# Înainte de merge pe main — sincronizezi feature branch-ul cu main:
git switch feature/xyz
git fetch origin
git merge origin/main        # aduci modificările din main în feature branch
# rezolvi eventualele conflicte acum, în izolare
git switch main
git merge feature/xyz        # merge curat, fără surprize
```

---

**`git stash` — "parchează" modificările temporar:**

Scenariu real: ești la mijlocul implementării unui feature când apare un bug urgent pe `main`. Nu vrei să commiți cod neterminat, dar nici să pierzi modificările.

```bash
# Ascunde modificările curente (fără să faci commit)
git stash                    # salvează fișierele tracked modificate
git stash -u                 # include și fișierele untracked (noi, negit-add-uite)

# Treci pe main, rezolvi bug-ul
git switch main
git pull
# ... faci fix-ul ...
git add -A
git commit -m "fix: resolve urgent payment bug"
git push

# Revii la feature-ul tău și recuperezi modificările
git switch feature/dashboard
git stash pop

# Dacă ai mai multe stash-uri:
git stash list              # listează toate stash-urile
git stash pop stash@{1}     # aplică al doilea stash
git stash drop stash@{0}    # șterge un stash fără să-l aplici
```

**Important:** `git stash` fără `-u` nu salvează fișierele noi (untracked). Dacă ai creat fișiere noi pe care nu le-ai `git add`-at, folosește `git stash -u`.

---

**`git reflog` — fileul de siguranță. Nimic nu e cu adevărat pierdut în Git.**

`git reset --hard`, branch șters, commit pierdut? `git reflog` înregistrează ORICE stare prin care a trecut HEAD în ultimele 90 de zile — inclusiv operații aparent "ireversibile".

```bash
git reflog
# Output:
# abc1234 HEAD@{0}: reset: moving to HEAD~2     ← ai făcut reset --hard din greșeală
# def5678 HEAD@{1}: commit: feat: add dashboard  ← commit-ul pe care vrei să-l recuperezi
# ghi9012 HEAD@{2}: commit: fix: auth bug

# Recuperezi commit-ul "pierdut":
git reset --hard def5678
# sau creezi un branch nou din el:
git switch -c recovery/dashboard def5678
```

**Când ai nevoie de `git reflog`:**
- Ai făcut `git reset --hard` și ai pierdut modificări
- Ai șters un branch înainte să-l merge-uiești
- `git rebase` a mers greșit și nu găsești commit-urile vechi
- Orice moment în care crezi că "ai pierdut munca" în Git

Înainte de orice `git reset --hard` riscant: notează SHA-ul commit-ului curent cu `git log --oneline -3`. Dacă merge greșit, `git reflog` îl recuperează oricum.

---

### Parte 11: 8 Erori Comune la Deploy + Fix

**Eroarea 1 — Build Failed: Module not found**
```
Error: Cannot find module '@/components/Button'
```
Cauza: Diferență de case între Windows și Linux. Pe Windows, `button.tsx` și `Button.tsx` sunt "același fișier". Pe Vercel (Linux), nu.

Fix:
```bash
# Verifică exact cum se numește fișierul (din Git Bash sau terminal):
ls components/
# Asigură-te că import-ul din cod matches exact cu numele fișierului pe disk
```
**Regulă permanentă:** denumește fișierele consistent (PascalCase pentru componente React) și nu te baza pe case-insensitivity Windows.

---

**Eroarea 2 — Environment Variable undefined**
```
Error: supabaseUrl is required.
```
Cauza: Variabila există în `.env.local` local, dar nu pe Vercel.
Fix: Vercel → Settings → Environment Variables → adaugă → re-deploy.

---

**Eroarea 3 — TypeError: Cannot read properties of null**
Cauza: Cod care funcționează local cu date mock dar pe Vercel returnează `null`/`undefined`.
Fix:
```typescript
const data = result.data ?? []        // nu presupune array
if (!item) return null               // null check după .find()
```

---

**Eroarea 4 — 504 Gateway Timeout pe API Routes**
Cauza: Funcție serverless care durează >10 secunde (default timeout).
Fix — două abordări, una în fișierul route, una în `vercel.json`:
```typescript
// app/api/generate/route.ts — metoda modernă Next.js App Router
export const maxDuration = 60  // secunde
```
```json
// vercel.json — alternativă sau pentru mai mult control
{
  "functions": {
    "app/api/generate/route.ts": {
      "maxDuration": 60
    }
  }
}
```
Hobby plan: max 60s. Pro plan: max 300s.

---

**Eroarea 5 — Hydration Error în Next.js**
```
Error: Hydration failed because the initial UI does not match what was rendered on the server.
```
Cauza: Server renderează diferit față de client (date din `localStorage`, `Date.now()`, `Math.random()`).
Fix — alege varianta potrivită:
```typescript
// Varianta 1 — mounted flag (pentru orice conținut client-only)
const [mounted, setMounted] = useState(false)
useEffect(() => setMounted(true), [])
if (!mounted) return null

// Varianta 2 — dynamic import fără SSR (pentru componente întregi)
import dynamic from 'next/dynamic'
const Chart = dynamic(() => import('./Chart'), { ssr: false })
```

---

**Eroarea 6 — CORS Error la Supabase (auth)**
```
Access to fetch at 'https://xxx.supabase.co' blocked by CORS policy
```
Cauza: Domeniul de producție nu e înregistrat în Supabase.
Fix: Supabase Dashboard → Authentication → URL Configuration → adaugă URL-ul Vercel la **Site URL** și **Redirect URLs**.

---

**Eroarea 7 — "Failed to compile" — TypeScript errors**
Vercel tratează TypeScript errors ca erori de build (local pot fi warnings).
Fix:
```bash
npx tsc --noEmit   # rulează înainte de push, rezolvă toate erorile
```

---

**Eroarea 8 — Deploy reușit dar site-ul arată versiunea veche**
Cauza: Cache CDN.
Fix: Vercel → Deployments → deployment-ul nou → "..." → "Promote to Production".
Sau hard refresh în browser: `Ctrl+Shift+R`.

---

### Parte 12: Rollback — Cum Revii la Versiunea Anterioară

Ai push-uit ceva greșit și producția e broken.

**Metoda 1 — Rollback pe Vercel (instant, zero Git):**
1. Vercel Dashboard → proiectul tău → Deployments
2. Ultimul deployment care funcționa → "..." → "Promote to Production"
3. Gata — revert în secunde, fără să atingi codul

**Metoda 2 — Git Revert (safe, păstrează history):**
```bash
git log --oneline -10
# abc1234 feat: broke everything  ← vrei să anulezi asta
# def5678 feat: last working state

git revert abc1234    # creează commit NOU care anulează modificările
git push              # Vercel re-deployează automat cu codul revertat
```
`git revert` e safe — nu rescrie history, adaugă un "undo commit".

**Metoda 3 — Git Reset (dacă N-AI push-uit încă):**
```bash
git reset --soft HEAD~1    # anulează commit-ul, păstrează modificările în staging
git reset --hard HEAD~1    # anulează commit-ul ȘI modificările din Working Tree
                           # recuperabil prin git reflog ~90 zile (vezi Parte 10)
```

**Metoda 4 — Reset la commit specific (după push):**
```bash
git reset --hard def5678       # revii la acel commit exact
git push --force-with-lease    # rescrie GitHub SIGUR
                               # eșuează dacă remote are commit-uri noi nevăzute
# git push --force             # varianta nesigură — suprascrie indiferent
```

`--force-with-lease` e întotdeauna preferabil față de `--force` — te protejează de a suprascrie commit-urile unui coleg sau propriile commit-uri de pe altă mașină.

**Pe proiecte cu colegi:** discuți înainte de orice `--force*` — rescrie history-ul shared.

---

### Parte 13: Multiple Proiecte Workflow

Cu 15+ proiecte active, e ușor să pierzi track-ul care proiect e push-uit și care nu.

**Script PowerShell — audit toate proiectele de pe Desktop:**
```powershell
# Rulează din PowerShell în C:\Users\admin
$folders = Get-ChildItem -Directory "C:\Users\admin\Desktop" |
           Where-Object { Test-Path "$($_.FullName)\.git" }

foreach ($folder in $folders) {
    Push-Location $folder.FullName
    $status = git status --short 2>$null
    $ahead = git rev-list --count origin/main..HEAD 2>$null
    if ($status -or ($ahead -gt 0)) {
        Write-Host "`n[$($folder.Name)]" -ForegroundColor Yellow
        if ($ahead -gt 0) { Write-Host "  → $ahead commit(uri) nepush-uite" -ForegroundColor Red }
        if ($status)      { Write-Host "  → Modificări nesalvate" -ForegroundColor Cyan }
    }
    Pop-Location
}
Write-Host "`nAudit complet." -ForegroundColor Green
```

**Checklist per proiect la final de sesiune:**
```
□ git status → curat
□ git push → "up to date with origin/main"
□ Vercel/Netlify Dashboard → deployment verde
```

**Tracking în Claude Code:**
Comenzile `/end` și `/start` verifică deja branch + status la fiecare sesiune.

---

## BLOC 5 — Securitate & Quick Reference

---

### Parte 14: Securitate Git

**Greșeala #1 — Chei API hardcodate în cod:**
```typescript
// ❌ NICIODATĂ — pe GitHub pentru totdeauna, în orice branch, în orice commit
const supabase = createClient(
  "https://xxxxx.supabase.co",
  "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
)

// ✓ CORECT
const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
)
```

**Greșeala #2 — Service Role Key cu NEXT_PUBLIC_:**
```bash
# ❌ Service role key bypass-uiește RLS — vizibil în browser = oricine poate citi/șterge tot
NEXT_PUBLIC_SUPABASE_SERVICE_KEY=eyJhbGci...

# ✓ Fără prefix — rămâne server-side
SUPABASE_SERVICE_ROLE_KEY=eyJhbGci...
```

**Greșeala #3 — .gitignore absent sau incomplet:**
Verifică existența și conținutul `.gitignore` ÎNAINTE de primul `git add`.

---

**Cum verifici dacă un secret a ajuns în history:**
```bash
# Caută un fișier specific în tot history-ul
git log --all --full-history -- .env

# Caută un string specific în toate commit-urile
git log -p --all -S "sk-ant-"
git log -p --all -S "eyJhbGci"
```

---

**Ce faci dacă ai push-uit un secret pe repo public:**

**Pasul 1 (IMEDIAT — în secunde):** Revocă cheia compromisă:
- Anthropic: console.anthropic.com → API Keys → Delete
- Supabase: Dashboard → Settings → API → Regenerate

**Pasul 2:** Generează chei noi, actualizează `.env.local` și Vercel Environment Variables.

**Pasul 3:** Curăță history-ul cu `git filter-repo` (înlocuitorul oficial al lui `git filter-branch`):
```bash
# Instalează git-filter-repo
pip install git-filter-repo

# Notează URL-ul remote ÎNAINTE — filter-repo îl va elimina automat
git remote -v
# origin  git@github.com:username/repo-name.git

# Elimină fișierul din TOATĂ istoria
git filter-repo --path .env --invert-paths

# Re-adaugă remote-ul (pas obligatoriu — altfel push eșuează)
git remote add origin git@github.com:username/repo-name.git

# Force push cu history curat
git push --force --all
git push --force --tags
```

**Pasul 4:** Notifică utilizatorii dacă cheia expusă dădea acces la date sensibile.

---

**Pre-commit hook — blochează automat commit-urile cu secrete:**

**Varianta simplă (fără dependențe):**
```bash
# Creează fișierul: .git/hooks/pre-commit
#!/bin/sh
# Pattern precis — evită false positives
if git diff --cached | grep -E "(sk-ant-api03-[A-Za-z0-9]{40,}|SUPABASE_SERVICE_ROLE_KEY\s*=\s*ey)" > /dev/null; then
  echo "BLOCAT: Pattern de cheie API detectat în staged files."
  echo "Verifică cu: git diff --cached"
  exit 1
fi
```

**Varianta robustă — `gitleaks` (recomandat pentru proiecte serioase):**

```bash
# Instalare Windows (Chocolatey sau Scoop)
choco install gitleaks
# sau: scoop install gitleaks

# Scanează repo-ul pentru secrete în history
gitleaks detect --source . --verbose

# Ca pre-commit hook — adaugă în .git/hooks/pre-commit:
#!/bin/sh
gitleaks protect --staged --verbose
```

**Important:** Hook-urile din `.git/hooks/` nu se commitează în repo — există doar local. Dacă lucrezi în echipă și vrei hook-uri shared, folosește `husky` + `package.json`.

---

### Parte 15: Checklist Pre-Deploy

**Înainte de primul deploy al unui proiect (ordinea contează):**
```
□ git config user.name și user.email setate
□ pull.rebase false configurat global
□ .gitignore creat și include .env*, node_modules/, .next/
□ .env.example creat cu toate cheile (valori placeholder)
□ git status → .env și node_modules NU apar în listed files
□ Repo pe GitHub creat (public/privat conform decizie)
□ SSH configurat sau HTTPS funcțional
□ git remote add origin [URL] && git push -u origin main
□ npm run build → reușit local (pentru Next.js) — nu deploya ce nu compilează local
□ npx tsc --noEmit → zero TypeScript errors
□ Variabile de mediu adăugate pe Vercel/Netlify
□ URL Supabase adăugat în Authentication → URL Configuration pe Supabase
□ Deploy → verificat pe URL-ul de producție
```

**Înainte de orice push pe main (proiecte cu utilizatori reali):**
```
□ Feature testată local → funcționează end-to-end
□ No console.error în browser devtools
□ npx tsc --noEmit → zero errors
□ Variabile de mediu noi → adăugate pe Vercel
□ Schema DB modificată → migration aplicată pe Supabase
□ git status → exact fișierele pe care vrei să le commiți (nu mai mult)
□ git diff → ai citit ce se schimbă
```

**Verificare post-deploy:**
```
□ Vercel Dashboard → Deployment Status: Ready (nu Failed)
□ URL de producție → deschis în browser incognito (cookie fresh)
□ Feature modificată → testată pe producție
□ Console browser → fără erori noi
```

---

### Parte 16: Quick Reference Card v1.0

**Comenzi Git de zi cu zi:**
```bash
git status                     # ce fișiere s-au schimbat
git diff                       # modificările nestaged
git diff --staged              # ce e în staging (înainte de commit)
git diff HEAD                  # TOATE modificările față de ultimul commit
git add fisier.tsx             # adaugă fișier specific
git add -A                     # adaugă tot (după git diff verificat)
git commit -m "mesaj"          # salvează snapshot local
git push                       # trimite pe GitHub
git pull                       # ia modificări de pe GitHub
git fetch origin               # descarcă remote fără merge
git merge origin/main          # aplică modificările descărcate
git log --oneline -10          # ultimele 10 commit-uri
git log --oneline --graph --all # vizualizare cu branch-uri
git stash                      # ascunde modificări tracked temporar
git stash -u                   # ascunde inclusiv fișierele untracked
git stash pop                  # recuperează modificările ascunse
git stash list                 # vede toate stash-urile
```

**Clone & Remote:**
```bash
git clone git@github.com:user/repo.git   # descarcă repo pe mașina curentă
git remote -v                            # vede remote configurat
git remote add origin URL                # adaugă remote
git remote set-url origin URL           # schimbă URL remote
git push -u origin main                  # primul push + setează upstream
```

**Branch — comenzi moderne (Git 2.23+):**
```bash
git switch -c feature/xyz      # creează și trece pe branch nou
git switch main                # treci pe branch existent
git merge feature/xyz          # merge branch pe branch-ul curent
git branch -d feature/xyz      # șterge branch local (safe)
git branch -D feature/xyz      # șterge branch forțat
git push origin --delete xyz   # șterge branch de pe GitHub

# Classic (funcționează în continuare):
git checkout -b feature/xyz
git checkout main
```

**Recovery:**
```bash
git revert abc1234             # anulează commit specific (safe, adaugă commit nou)
git reset --soft HEAD~1        # anulează ultimul commit local (păstrează fișierele)
git reset --hard HEAD~1        # anulează commit + șterge modificările (recuperabil cu reflog)
git restore fisier.tsx         # anulează modificările unui fișier (ireversibil)
git merge --abort              # anulează un merge în curs
git reflog                     # vede ORICE stare anterioară a HEAD (90 zile)
git push --force-with-lease    # force push sigur (eșuează dacă remote are commit-uri noi)
```

**Diagnosticare:**
```bash
git log --oneline              # history commits
git log --oneline --graph --all # vizualizare completă cu branch-uri
git blame fisier.tsx           # cine a modificat ce linie
git diff HEAD~1                # ce s-a schimbat față de ultimul commit
git show abc1234               # detalii commit specific
git log -p --all -S "text"     # caută string în tot history-ul
git log --all --full-history -- fisier.txt  # history complet al unui fișier
```

**Merge conflicts:**
```bash
git status                     # identifică fișierele cu conflicte
# editezi fișierele, ștergi marcajele <<<<< ===== >>>>>
git add fisier.tsx             # marchează ca rezolvat
git commit                     # finalizează merge
git merge --abort              # sau abandonezi merge-ul
```

---

**Vercel:**
| Acțiune | Unde |
|---------|------|
| Import proiect | Dashboard → Add New → Import Git |
| Env vars | Project → Settings → Environment Variables |
| Rollback instant | Project → Deployments → "..." → Promote to Production |
| Custom domain | Project → Settings → Domains |
| Build logs | Project → Deployments → click deployment → View Build Logs |
| Preview URL | automat pe orice branch non-main |

**Netlify:**
| Acțiune | Unde |
|---------|------|
| Deploy manual | Drop folder pe netlify.com |
| Import GitHub | Sites → Add New → Import from Git |
| Custom URL | Site Settings → Domain Management → Edit site name |
| Deploy logs | Deploys → click deployment |

---

**Proiectele tale — stiva de deploy:**
| Tip | Tool | Trigger deploy |
|-----|------|----------------|
| Next.js (Vibe Budget, ERP, Clinică, etc.) | Vercel | `git push` pe main |
| HTML offline (CashPulse, FollowUp, etc.) | Netlify | `git push` pe main |

---

**Ordinea de setup pentru un proiect nou (de la zero la live):**
```
1.  git config user.name/email + pull.rebase false (dacă mașină nouă)
2.  mkdir proiect && cd proiect && git init
3.  Creează .gitignore
4.  Creează .env.example (cu chei placeholder)
5.  git status → verifică că .env și node_modules NU apar
6.  git add -A && git commit -m "chore: initial project setup"
7.  GitHub.com → New Repository → Create (fără README)
8.  git remote add origin git@github.com:user/repo.git
9.  git branch -M main && git push -u origin main
10. npm run build → verifici că compilează local (Next.js)
11. Vercel/Netlify → Import repo
12. Variabile de mediu configurate
13. Deploy → verificat live
```

---

**Regula de aur — rezumată:**
> **Push după fiecare sesiune. `.env.example` commitează, `.env.local` niciodată. Vercel conectat la GitHub.**
> Atât îți trebuie pentru 95% din cazuri.

---

*Stack de referință: Git 2.x · GitHub · Vercel (Next.js 14+) · Netlify (HTML static) · Supabase v2 · Windows 10 + Claude Code*
*Proiecte: Vibe Budget · ERP Financiar · CashPulse · FollowUp Board · PurchaseCompare · Reorder Radar · InvoiceChaser · Daily Sales Flash · MenuMix Matrix · Vibe Caffè · Clinică Medicală · StudioFlow*
*Actualizat: Mai 2026*
