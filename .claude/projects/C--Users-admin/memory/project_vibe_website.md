---
name: Proiect Vibe Caffè Website
description: Proiect curs Next.js — Hero + Features + Menu + Footer + sistem rezervări complet cu Supabase + admin panel + deploy Vercel
type: project
---

## Stare curentă proiect

- **Repo local:** `C:\Users\admin\vibe-website` (branch `starter`)
- **Repo GitHub:** `https://github.com/ticu0707/vibe-website.git`
- **Live Vercel:** `https://vibe-website-ticu.vercel.app`
- **Server local:** `cd C:\Users\admin\vibe-website && npm run dev` → http://localhost:3000
- **Stack:** Next.js 16, React 19, TypeScript 5, Tailwind CSS 4, Lenis, OpenAI SDK, Supabase

---

## Supabase

- **Proiect:** `vibe-caffe` — Central EU (Frankfurt)
- **Reference ID:** `azgyjdnfyctenttfteef`
- **URL:** `https://azgyjdnfyctenttfteef.supabase.co`
- **Cheile:** salvate în `.env.local` și pe Vercel (env vars)
- **Tabel:** `rezervari` cu RLS activ (public CRUD)

### Schema tabel `rezervari`:
| Câmp | Tip | Detalii |
|------|-----|---------|
| id | BIGSERIAL | PK, auto-increment |
| nume | TEXT | NOT NULL |
| email | TEXT | NOT NULL |
| telefon | TEXT | NOT NULL |
| numar_persoane | INTEGER | NOT NULL, DEFAULT 2 |
| data | DATE | NOT NULL |
| ora | TIME | NOT NULL |
| status | TEXT | DEFAULT 'în așteptare' |
| created_at | TIMESTAMPTZ | DEFAULT NOW() |

---

## Fișiere create / modificate

| Fișier | Status | Descriere |
|--------|--------|-----------|
| `components/HeroStarter.tsx` | Modificat | Hero complet + scroll smooth |
| `components/FeaturesStarter.tsx` | Creat | Bento Grid 3 carduri |
| `components/MenuStarter.tsx` | Creat | 4 tab-uri, 24 produse |
| `components/FooterStarter.tsx` | Neatins | Footer minimal |
| `app/page.tsx` | Actualizat | 4 componente |
| `lib/supabase.ts` | Creat | Client Supabase |
| `lib/rezervari.ts` | Creat | CRUD: save, read, updateStatus, delete |
| `app/rezervari/page.tsx` | Creat | Formular rezervări 3 pași |
| `app/api/rezervari/route.ts` | Creat | POST / PATCH / DELETE |
| `app/api/admin/rezervari/route.ts` | Creat | GET toate rezervările |
| `app/admin/page.tsx` | Creat | Admin panel cu filtre + acțiuni |
| `supabase/migrations/20260324_create_rezervari.sql` | Creat | Migrare DB |

---

## Pagini live

| Pagină | URL |
|--------|-----|
| Homepage | `/` |
| Rezervări | `/rezervari` |
| Admin | `/admin` |

---

## Următorii pași planificați (în ordinea cursului)

1. **Navigation.tsx** — navbar sticky cu logo + linkuri + scroll behavior ← *next*
2. **About.tsx** — secțiune despre noi
3. **Footer.tsx** — footer complet cu wave SVG (înlocuiește FooterStarter)
4. **ChatWidget.tsx** — Barista Bot cu OpenAI
5. **Pagina /locatie** — butonul "Vizitează-ne" din Hero duce aici
6. **Pagina /pickup** — butonul "Comandă Pickup" din Hero duce aici

---

**Why:** Proiect de curs vibe-coding — utilizatorul învață Next.js + Tailwind + Supabase construind un site real pentru o cafenea fictivă.
**How to apply:** La reluarea sesiunii → `npm run dev` în `C:\Users\admin\vibe-website`. Sistemul de rezervări e complet și live pe Vercel. Se continuă cu **Navigation.tsx**.
