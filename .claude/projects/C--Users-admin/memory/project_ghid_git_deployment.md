---
name: project-ghid-git-deployment
description: "Ghid Git & Deployment Workflow v1 pentru vibe-coding — locație, structură, status și conținut acoperit"
metadata: 
  node_type: memory
  type: project
  originSessionId: a3fd517a-f93d-4269-830f-cf60e6caed19
---

Ghid Git & Deployment Workflow v1 — DRAFT în curs de rafinare.

**Locație:** `C:\Users\admin\Desktop\Vibe-Coding\ghid-git-deployment-v1-DRAFT.md`

**Status:** FINAL v1.0 — publicat la `ghid-git-deployment-v1.md`. DRAFT șters.

**Why:** Utilizatorul are 62+ commit-uri nepush-uite pe 15+ proiecte — risc de pierdere date și întârzieri la lansare.

**Structură (17 secțiuni, 5 Bloc-uri):**

- **Walkthrough 20 comenzi** (nou): flow end-to-end de la zero la live
- **BLOC 1** — Git Setup & Mental Model (Parte 0-2): 4 zone, HEAD explicat, pull.rebase config, gitignore, .env.example
- **BLOC 2** — Commit & Branch Strategy (Parte 3-5): Conventional Commits, git switch/restore, SSH setup + ssh-agent Windows
- **BLOC 3** — Deploy Pipeline (Parte 6-9): Vercel auto-deploy + cold start warning, env vars, Netlify + _redirects fix, custom domain
- **BLOC 4** — Troubleshooting & Recovery (Parte 10-13): Merge conflicts, git stash, **git reflog** (nou), 8 erori comune, rollback cu force-with-lease, multi-project PowerShell audit
- **BLOC 5** — Securitate & Quick Reference (Parte 14-16): git filter-repo (cu remote add step fix), pre-commit hook + gitleaks, checklist pre-deploy, Quick Reference Card

**Stack acoperit:** Git + GitHub · Vercel (Next.js) · Netlify (HTML static) · Supabase env vars · Windows 10 + Claude Code

**How to apply:** Când utilizatorul lucrează cu Git, deploy sau debugging, referențiază secțiunile relevante din ghid.
