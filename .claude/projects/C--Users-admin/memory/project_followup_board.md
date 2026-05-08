---
name: FollowUp Board
description: Lead magnet gratuit — tool offline urmărire lead-uri pentru IMM români, single HTML + landing page, implementare completă, testat F1-F20, rămâne local
type: project
originSessionId: 430c8236-11f6-4625-a787-9714d5465dfb
---
Aplicație lead magnet gratuită pentru owner-i de IMM români (2-5 angajați).

**Fișiere:**
- `C:/Users/admin/Desktop/followup-board/followup-board.html` — app offline, ~1650 linii, 18 module, zero dependențe
- `C:/Users/admin/Desktop/followup-board/landing.html` — landing page Netlify-ready, Tailwind CDN

**Status:** COMPLET. Testat F1-F20 — toate funcționale. Rămâne local (nu se face push/deploy).

**Ultimul commit:** `a4d1c49` — Polish keyboard hint bar

**Why:** Induce autoritate față de lead rece, funcționează 100% offline, fără instalare, fără cont. Schema LocalStorage `followupboard_v4`.

**Arhitectură:**
- CSS custom properties (NU Tailwind) — consistent cu CashPulse + Reorder Radar
- Vanilla JS ES6+, global state, global named functions, render() pattern
- 18 module separate cu `// ═══ MODULE X ═══` comentarii bloc
- Event delegation pe `#main`

**Module cheie:**
- M07 Urgency Engine: red/yellow/gray pe baza nextDate
- M11 Morning Briefing: overlay 4s auto-dismiss + progress bar
- M13 Won/Lost: CSS confetti (22 pieces, @keyframes), insight banner la 3+ aceeași cauză
- M14 Templates: 5 texte în română, Clipboard API
- M15 Backup: export JSON (MERGE la import), CSV cu BOM UTF-8, reminder la sesiune 7
- M16 Retention: ICS cu RRULE:FREQ=DAILY, favicon Canvas API cu badge roșu

**Fix-uri aplicate (post-lansare):**
- AND-filter logic + demo lead edit guard
- Format date românesc DD/MM/YYYY — hybrid inputs (text vizibil + picker ascuns + buton 📅)
- CSV export date în DD/MM/YYYY (fix Excel `########`)
- Keyboard shortcuts: inFormField guard, N din search bar, Esc blur

**How to apply:** Proiect închis. Dacă se reia — push GitHub + deploy Netlify (drag & drop ambele fișiere).
