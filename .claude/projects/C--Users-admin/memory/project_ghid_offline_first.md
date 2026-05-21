---
name: project-ghid-offline-first
description: "Ghid Offline-First Architecture v1.1 — locație, structură, status și conținut acoperit"
metadata:
  node_type: memory
  type: project
  originSessionId: a3fd517a-f93d-4269-830f-cf60e6caed19
---

Ghid Offline-First Architecture v1.1 — FINAL, salvat.

**Locație:** `C:\Users\admin\Desktop\Vibe-Coding\ghid-offline-first-architecture-v1.md`

**Status:** FINAL v1.1 — 3 runde de review expert aplicate (23 + 15 fix-uri total).

**Why:** Jumătate din portofoliu (CashPulse, FollowUp Board, PurchaseCompare, Reorder Radar, InvoiceChaser, Daily Sales Flash, MenuMix Matrix, StudioFlow) rulează offline-first. Bug-uri recurente: date pierdute la refresh, JSON corupt, 5MB exceeded silențios, tab care blochează upgrade IndexedDB.

**Structură (17 secțiuni, 5 Bloc-uri):**

- **Walkthrough 15 pași** (3 grupe progresive): de la HTML static cu localStorage la PWA completă
- **BLOC 1** (Parte 0-3): localStorage + sessionStorage + Decision Matrix + BroadcastChannel + namespacing
- **BLOC 2** (Parte 4-6): IndexedDB nativ (onblocked + setupVersionChangeHandler obligatoriu) + Dexie.js (ALL stores rule, liveQuery, Promise.all, paginare)
- **BLOC 3** (Parte 7-9): SW Lifecycle (scope + skipWaiting coordonat) + 5 strategii (cache coherence) + Workbox (@ducanh2912/next-pwa)
- **BLOC 4** (Parte 10-12): manifest.json (icoane separate) + beforeinstallprompt + iOS Safari limitări consolidate + Offline UX (isReallyOnline, beforeunload/visibilitychange) + Background Sync (retry limits)
- **BLOC 5** (Parte 13-16): File System Access API (dispatchEvent fallback) + Securitate (CSP clarificat) + Debug + Quick Reference

**Concepte-cheie acoperite:**
- `setupVersionChangeHandler(db)` — apelat în `onsuccess` (nu doar definit)
- `initPersistentStorage()` — consistență naming (fix B2 din round 3)
- `liveQuery` Dexie 3+ pentru UI reactiv
- `BroadcastChannel` vs `storage` event
- `beforeinstallprompt` + iOS "Add to Home Screen" fallback
- iOS Safari limitări PWA consolidate (tabel complet)
- `beforeunload` + `visibilitychange` pentru draft save
- localStorage key namespacing: `PREFIX + key`
- `Promise.all` pentru reads paralele IndexedDB
- Cursor iteration + paginare pentru volume mari

**Stack acoperit:** HTML/JS Vanilla · Next.js 14 App Router · Chrome/Edge · Netlify · Vercel · Windows 10

**How to apply:** Când utilizatorul lucrează cu localStorage, IndexedDB, Service Workers sau PWA, referențiază secțiunile relevante. StudioFlow → BLOC 2 (Dexie) + Parte 10 (PWA + iOS). HTML static → BLOC 1 + Parte 7 (SW scope).
