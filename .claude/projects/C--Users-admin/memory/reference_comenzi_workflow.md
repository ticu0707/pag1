---
name: comenzi-workflow-slash-start-end-commit-push
description: "Comenzile custom de workflow create pentru utilizator, locație și scop"
metadata: 
  node_type: memory
  type: reference
  originSessionId: a3fd517a-f93d-4269-830f-cf60e6caed19
---

Utilizatorul are 6 comenzi slash custom în `~/.claude/commands/`:

| Comandă | Fișier | Scop |
|---|---|---|
| `/prep` | `~/.claude/commands/prep.md` | Generează Context Block complet pentru sesiune: citește memoria proiectului, selectează priming, produce "Mesajul 1 perfect" gata de trimis |
| `/start` | `~/.claude/commands/start.md` | Checklist început sesiune: branch, git status, fetch, todo-uri rămase |
| `/end` | `~/.claude/commands/end.md` | Checklist sfârșit sesiune: commit, push, rezumat, todo viitor, salvare memorie |
| `/commit` | `~/.claude/commands/commit.md` | Commit local: status, diff, add, message în engleză, Co-Authored-By Claude |
| `/push` | `~/.claude/commands/push.md` | Push pe GitHub: verifică commit-uri locale nepush-uite, push, confirmă |
| `/chat` | `~/.claude/commands/chat.md` | Manager conversații: listează, caută, redenumește, reia sau auto-numește |

Workflow tipic: `/prep [proiect]` → `/start` → lucru → `/commit` → `/push` → `/end`

**Notă despre /prep:** Implementează Template 7 + Priming + arcul de sesiune din ghidul de prompt engineering v4.0. Citește automat memoria proiectului, pune 2 întrebări rapide, generează Context Block complet gata de trimis. Acceptă argument opțional: `/prep vibe-budget`.
