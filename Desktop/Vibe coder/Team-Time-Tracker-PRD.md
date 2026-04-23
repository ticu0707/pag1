# Team Time Tracker — PRD v1.0

## 1. Scopul aplicatiei

O platforma universala de time tracking pentru echipe mixte (angajati + freelanceri + colaboratori), aplicabila in orice domeniu de activitate. Sistemul monitorizeaza automat timpul petrecut in orice aplicatie activa pe calculatorul fiecarui membru, centralizeaza datele pe un server propriu al firmei, si ofera managerului un dashboard web cu vizibilitate completa asupra activitatii echipei, distributiei timpului pe proiecte si generarii de rapoarte pentru facturare.

---

## 2. Utilizatorii tinta si problemele lor

### 2.1 Managerul
**Problema:** Nu are vizibilitate centralizata asupra timpului real lucrat de fiecare membru pe fiecare proiect. Nu poate face facturare precisa catre clienti, nu poate identifica suprasolicitarea sau subutilizarea resurselor, nu poate compara estimarile cu realitatea.

**Ce face dupa ce foloseste aplicatia:** Deschide dashboardul, vede cine lucreaza acum si pe ce proiect, verifica orele cumulate pe proiecte pentru facturare lunara, descarca rapoarte individuale pentru freelanceri.

### 2.2 Angajatul
**Problema:** Nu are o evidenta clara a propriului timp pe proiecte. Nu stie cat a lucrat efectiv intr-o saptamana sau luna.

**Ce face dupa ce foloseste aplicatia:** Vede propriul sumar zilnic/saptamanal, isi urmareste evolutia personala.

### 2.3 Freelancerul / Colaboratorul
**Problema:** Nu are un raport de ore gata de atasat la factura. Trebuie sa reconstituie manual ce a lucrat.

**Ce face dupa ce foloseste aplicatia:** Descarca propriul raport de ore per proiect, il ataseaza direct la factura catre firma.

---

## 3. Contextul de utilizare

Aplicatia este generica si poate fi folosita in orice domeniu:
- **Studio de arhitectura:** AutoCAD, Revit, Rhino, browsere, Excel
- **Echipa AI / vibe coding:** VS Code, Cursor, Windsurf, browser
- **Agentie digitala:** Figma, browser, Slack, tool-uri de management
- **Orice alta echipa** care lucreaza pe calculator cu aplicatii desktop sau web

Sistemul nu este legat de nicio aplicatie specifica. Trackeaza orice aplicatie activa pe ecran.

---

## 4. Functionalitati esentiale (v1)

### 4.1 Agent local (ruleaza pe calculatorul fiecarui membru)
- Detecteaza automat aplicatia activa in prim-plan (foreground app)
- Inregistreaza timpul per aplicatie, grupat pe categorii configurabile (ex: "design", "modelare 3D", "comunicare", "browser", "office")
- Trimite datele periodic (la fiecare 5 minute) catre serverul central
- La inceputul sesiunii de lucru, userul declara manual proiectul activ
- Userul poate schimba proiectul activ oricand din tray icon / widget minimal
- Detecteaza inactivitatea (fara input mouse/tastatura > 10 min) si pauzeaza automat tracking-ul
- La sfarsitul zilei genereaza un sumar local: timp total, timp per aplicatie, timp per proiect

### 4.2 Server central (self-hosted)
- Primeste si stocheaza datele de la toti agentii
- Baza de date PostgreSQL
- API REST securizat (autentificare cu token per utilizator)
- Accesibil pe reteaua interna a firmei sau prin VPN
- Rulabil prin Docker (instalare simpla pe orice server Linux)

### 4.3 Dashboard web — Manager
- **Vedere in timp real:** cine lucreaza acum, pe ce proiect, de cat timp
- **Radar lunar:** toti membrii echipei pe un singur ecran — ore totale, proiecte active, zile lucrate
- **Per proiect:** ore cumulate total, ore per membru, comparatie cu bugetul de ore estimat
- **Per membru:** distributia timpului pe aplicatii, evolutie saptamanala
- **Alerte:** proiect care depaseste bugetul de ore estimat, inactivitate neobisnuita
- **Rapoarte descarcabile:** PDF/Excel per proiect, per membru, per perioada
- **Configurare rapoarte automate:** managerul seteaza frecventa (zilnic / saptamanal / lunar) si destinatarii

### 4.4 Dashboard web — Membru (angajat / freelancer)
- Vedere proprie: ore azi, ore saptamana, ore luna
- Distributia timpului pe aplicatii si proiecte
- Raport propriu descarcabil (pentru freelanceri: gata de atasat la factura)
- Nu vede datele altor membri

### 4.5 Gestionare proiecte si echipa (manager)
- Creeaza si editeaza proiecte (nume, client, buget ore estimat, data limita)
- Atribuie membri la proiecte
- Seteaza categorii de aplicatii (ex: AutoCAD → "modelare", Chrome → "browser")
- Adauga / dezactiveaza membri din sistem
- Seteaza roluri: Manager / Angajat / Freelancer

---

## 5. Mecanismul de tracking — detalii tehnice

| Eveniment | Ce se intampla |
|-----------|----------------|
| User porneste calculatorul | Agentul porneste automat (startup) |
| User declara proiectul activ | Selecteaza din lista proiectelor atribuite lui |
| Aplicatie in foreground | Agentul inregistreaza numele aplicatiei + timestamp |
| Schimbare aplicatie | Inchide intervalul precedent, deschide unul nou |
| Inactivitate > 10 min | Tracking pauza automat, se reia la primul input |
| User schimba proiectul | Intervalul curent se inchide, se deschide pe noul proiect |
| La fiecare 5 min | Agentul trimite batch de date la server |
| Sfarsit de zi (ora configurabila) | Agentul genereaza sumar local, trimite final la server |

---

## 6. Structura roluri si acces

| Functionalitate | Manager | Angajat | Freelancer |
|-----------------|---------|---------|------------|
| Vede datele tuturor membrilor | Da | Nu | Nu |
| Vede propriile date | Da | Da | Da |
| Descarca raport propriu | Da | Da | Da |
| Descarca rapoarte ale echipei | Da | Nu | Nu |
| Creeaza / editeaza proiecte | Da | Nu | Nu |
| Atribuie membri la proiecte | Da | Nu | Nu |
| Configureaza rapoarte automate | Da | Nu | Nu |
| Seteaza categorii aplicatii | Da | Nu | Nu |

---

## 7. Rapoarte si export

### Tipuri de rapoarte disponibile
1. **Raport zilnic per membru** — ore totale, timp per aplicatie, timp per proiect
2. **Raport saptamanal per proiect** — ore totale per proiect, contributia fiecarui membru
3. **Raport lunar echipa (Radar)** — toti membrii pe un singur ecran, ore totale, proiecte active
4. **Raport facturare freelancer** — ore per proiect intr-o perioada, gata de atasat la factura
5. **Raport buget proiect** — ore estimate vs. ore reale, progres, proiectie finalizare

### Formate export
- PDF (pentru clienti si facturare)
- Excel/CSV (pentru procesare ulterioara)
- Vizibil in dashboard (grafice interactive)

### Rapoarte automate
- Managerul configureaza: frecventa (zilnic / saptamanal / lunar), tipul raportului, destinatarii (email)
- Rapoartele se genereaza automat si sunt disponibile pentru descarcare din dashboard

---

## 8. In afara scopului (v1)

- Integrare cu tool-uri externe (Toggl, Clockify, Jira, Asana)
- Tracking pe mobile / tablet
- Capturi de ecran pentru verificarea activitatii
- Estimare automata timp de finalizare proiect (v2)
- Facturare automata catre clienti (v2)
- SSO / integrare Active Directory (v2)
- Aplicatie mobila pentru declararea proiectului (v2)

---

## 9. Stack tehnologic recomandat

| Componenta | Tehnologie | Motivatie |
|------------|------------|-----------|
| Agent local | Python 3.9+ | Cross-platform, usor de instalat, biblioteca bogata |
| Detectie aplicatie activa | `pygetwindow` / `psutil` + OS APIs | Cross-platform (Windows/macOS/Linux) |
| Comunicare agent → server | REST API cu token JWT | Simplu, securizat, stateless |
| Backend server | FastAPI (Python) | Rapid, documentatie automata, async |
| Baza de date | PostgreSQL | Multi-user, robust, self-hosted |
| Dashboard web | Next.js + Tailwind CSS | Modern, responsive, usor de customizat |
| Grafice dashboard | Chart.js sau Recharts | Interactive, browser-native |
| Deployment server | Docker + Docker Compose | Instalare simpla, portabil |
| Autentificare | JWT + refresh tokens | Standard industry |

---

## 10. Arhitectura sistemului

```
[Calculator Membru 1]          [Calculator Membru 2]          [Calculator Membru N]
  Agent Python (local)           Agent Python (local)           Agent Python (local)
  - detecteaza app activa        - detecteaza app activa        - detecteaza app activa
  - tray icon: selectie proiect  - tray icon: selectie proiect  - tray icon: selectie proiect
  - trimite date la 5 min        - trimite date la 5 min        - trimite date la 5 min
        |                               |                               |
        |_______________ REST API (JWT) _|_______________________________|
                                        |
                              [Server Firma / VPS]
                              Docker Compose:
                              - FastAPI backend
                              - PostgreSQL database
                              - Next.js frontend (dashboard)
                              - Nginx reverse proxy
                                        |
                              [Browser Manager]         [Browser Angajat/Freelancer]
                              Dashboard complet         Dashboard personal
                              - radar echipa            - date proprii
                              - rapoarte                - export facturare
                              - configurare
```

---

## 11. Structura proiectului (cod)

```
team-time-tracker/
├── agent/                          # Agentul local (ruleaza pe fiecare calculator)
│   ├── main.py                     # Entry point agent
│   ├── tracker.py                  # Detectie aplicatie activa + inactivitate
│   ├── uploader.py                 # Trimitere date la server (REST)
│   ├── tray.py                     # Tray icon + selectie proiect
│   ├── config.py                   # Configurare (server URL, token, user)
│   └── install/
│       ├── install_windows.ps1     # Instalare + autostart Windows
│       └── install_macos.sh        # Instalare + autostart macOS
│
├── backend/                        # Server FastAPI
│   ├── main.py                     # App FastAPI
│   ├── routers/
│   │   ├── auth.py                 # Login, JWT
│   │   ├── sessions.py             # Ingestie date de la agenti
│   │   ├── projects.py             # CRUD proiecte
│   │   ├── users.py                # CRUD utilizatori
│   │   └── reports.py              # Generare rapoarte
│   ├── models/                     # Modele SQLAlchemy
│   ├── schemas/                    # Scheme Pydantic
│   └── db.py                       # Conexiune PostgreSQL
│
├── frontend/                       # Dashboard Next.js
│   ├── pages/
│   │   ├── login.tsx
│   │   ├── dashboard/
│   │   │   ├── manager.tsx         # Dashboard manager
│   │   │   └── member.tsx          # Dashboard membru
│   │   ├── projects/               # Management proiecte
│   │   └── reports/                # Rapoarte + export
│   └── components/
│       ├── RadarEchipa.tsx         # Radar lunar activitate
│       ├── ChartTimeline.tsx       # Evolutie saptamanala
│       └── ReportExport.tsx        # Generare + descarcare rapoarte
│
├── docker-compose.yml              # Deployment complet
└── README.md                       # Instructiuni instalare server
```

---

## 12. Module — ordine de constructie

**Regula:** Fiecare modul se construieste complet si se testeaza inainte de a trece la urmatorul.

| # | Modul | Ce face | Test |
|---|-------|---------|------|
| 1 | **DB Schema + Modele** | Tabele PostgreSQL: users, projects, app_sessions, daily_summaries | Insert manual, verific in DB |
| 2 | **Auth backend** | Login, JWT, roluri (manager/angajat/freelancer) | Login cu Postman, token valid |
| 3 | **Agent local — tracker** | Detectie app activa, inactivitate, sumar zilnic | Rulat local, verific log-uri |
| 4 | **Agent local — uploader** | Trimitere date la server prin REST | Date ajung in DB |
| 5 | **Agent local — tray icon** | Selectie proiect, start/stop manual, indicator activ | Schimb proiect din tray, verific DB |
| 6 | **API rapoarte** | Endpoint-uri pentru dashboard si export | Date corecte in Postman |
| 7 | **Dashboard manager** | Radar echipa, per proiect, per membru, alerte | Manager vede echipa in timp real |
| 8 | **Dashboard membru** | Date personale, export raport propriu | Freelancer descarca raport facturare |
| 9 | **Rapoarte automate** | Generare periodica PDF/Excel, descarcare din app | Raport generat la interval configurat |
| 10 | **Instalare one-script** | `install_windows.ps1` / `install_macos.sh` + Docker Compose | Instalare curata pe masina noua |

---

## 13. Criterii de succes

- Agentul porneste automat la login si nu necesita nicio actiune din partea userului in afara de selectia proiectului
- Managerul vede in dashboard cine lucreaza acum si pe ce proiect, in timp real
- La sfarsitul lunii, managerul genereaza si descarca rapoartele de facturare in sub 2 minute
- Un freelancer poate descarca propriul raport de ore, gata de atasat la factura, fara ajutorul managerului
- Instalarea agentului pe un calculator nou dureaza sub 10 minute cu scriptul de instalare
- Serverul ruleaza stabil pe un VPS de baza (2 CPU, 4GB RAM) pentru o echipa de pana la 50 de persoane
