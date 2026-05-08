---
name: MenuMix Matrix
description: Lead magnet HoReCa — matrix menu engineering Star/Potențial/Muncitor/Candidat; 2 HTML offline files; commit local, nepushed
type: project
originSessionId: 729aceaa-93b2-4c82-a0ff-7aa135935542
---
Lead magnet offline pentru restaurante/baruri/cafenele care aplică menu engineering (matricea Kasavana-Smith).

**Why:** Proprietari și manageri HoReCa nu știu ce preparate aduc profit vs. consumă resurse. Aplicația clasifică preparatele în 4 categorii bazate pe popularitate și marjă.

**How to apply:** Implementare completă. Înainte de deploy: configurare EmailJS în index.html.

## Fișiere
- `Desktop/menu-mix-matrix/index.html` — landing page (Google Fonts + EmailJS CDN)
- `Desktop/menu-mix-matrix/app.html` — aplicație 100% offline (zero CDN)

## Status
- Implementare completă (L1-L6 landing + A1-A9 app)
- Commit local: `06d0ab1`
- **23 commits nepushed** față de origin/main (inclusiv toate proiectele anterioare)
- Push: intenționat amânat

## De făcut înainte de deploy
1. Configurare EmailJS în `index.html`: înlocuiește `YOUR_SERVICE_ID`, `YOUR_TEMPLATE_ID`, `YOUR_PUBLIC_KEY`
2. Testare browser: formular landing → descărcare app.html
3. Testare app: 8+ preparate → matrice SVG + acțiuni + print A4 + F5 restore + reset modal
4. Deploy landing page pe Netlify sau GitHub Pages

## Arhitectură
- Clasificare: medii dinamice (avgMargin, avgPopularity) din datele introduse
- SVG matrix: normalizare min-max pe axe, linie prag la 300px vizual
- sessionStorage autosave la fiecare input
- Custom modal reset (fără `confirm()` nativ)
- GDPR checkbox obligatoriu pe landing
- Mobile warning overlay < 768px pe ambele fișiere
