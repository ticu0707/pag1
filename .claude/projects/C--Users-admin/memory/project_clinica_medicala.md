---
name: Aplicatie Clinica Medicala — IVR Chatbot Programari
description: Proiect nou: bot vocal IVR pentru programari la clinica medicala, cu panou admin multi-rol
type: project
---

Aplicație de programări medicale prin apel vocal automat (IVR), cu panou de administrare web.

**Why:** Proiect real (clinică existentă) + scop de învățare. Prima digitalizare a clinicii — nu există niciun sistem acum.

**How to apply:** Construim pas cu pas, explicând fiecare decizie. Prioritate: să funcționeze corect și să fie scalabil.

## Decizii stabilite

| Aspect | Decizie |
|---|---|
| Tip interacțiune | Apel vocal automat IVR |
| Date colectate | Nume, telefon, specialitate, medic preferat, dată/oră |
| Mărime clinică | Mică acum (2-3 specialități, câțiva medici), arhitectură scalabilă |
| Sistem existent | Zero — primul sistem digital al clinicii |
| După programare | Confirmare vocală + SMS pacient + apare în panou admin |
| Panou admin | Multi-user cu roluri: recepționer / medic / administrator |
| Interacțiune bot | Hibrid: meniuri DTMF + înțelegere vocală AI (Claude API) |
| Budget | De stabilit — vrea să vadă opțiunile mai întâi |
| Hosting | Vercel (admin panel) + Supabase (DB + auth) + Railway (backend IVR) |
| Scop | Real + învățat |

## Stack tehnologic

- **Twilio** — telefonie IVR + SMS (~€20-40/lună după volum)
- **Claude API** — înțelegere vocală AI (~€5-15/lună)
- **Supabase** — PostgreSQL + autentificare cu roluri (gratuit free tier)
- **Next.js** — frontend panou admin (utilizatorul știe deja Next.js)
- **Vercel** — hosting frontend (gratuit)
- **Railway** — hosting backend IVR Node.js (~€5-10/lună)
- **Cost total estimat:** ~€25-55/lună

## Arhitectură

```
Pacient sună → Twilio (număr virtual)
             → Backend Node.js pe Railway (logică IVR + webhooks)
             → Claude API (înțelegere răspunsuri vocale libere)
             → Supabase (salvare programare)
             → Twilio SMS (confirmare pacient)
             → Next.js Admin Panel pe Vercel (recepționer/medic/admin văd programările)
```

## Module de construit (în ordine)

1. **Fundația** — Supabase: bază de date + autentificare cu roluri
2. **Admin Panel** — Next.js: dashboard cu roluri (recepționer / medic / admin)
3. **Botul vocal** — Twilio IVR + Claude API: logica apelului

## Status

Planificare completă. Modulul 1 (Supabase) în curs de început.

## Următorii pași (to-do sesiunea viitoare)

1. Răspunde la 3 întrebări de clarificare:
   - Cont Supabase existent sau de creat de la zero?
   - Câte specialități și care sunt (ex: cardiologie, pediatrie)?
   - Câți medici? Un medic poate avea mai multe specialități?
2. Creare/configurare proiect Supabase
3. Definire schema BD și creare tabele: `specialties`, `doctors`, `appointments`, `profiles`
