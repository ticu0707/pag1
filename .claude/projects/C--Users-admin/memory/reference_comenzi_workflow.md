---
name: Comenzi workflow slash — /start /end /commit /push
description: Comenzile custom de workflow create pentru utilizator, locație și scop
type: reference
---

Utilizatorul are 4 comenzi slash custom în `~/.claude/commands/`:

| Comandă | Fișier | Scop |
|---|---|---|
| `/start` | `~/.claude/commands/start.md` | Checklist început sesiune: branch, git status, fetch, todo-uri rămase |
| `/end` | `~/.claude/commands/end.md` | Checklist sfârșit sesiune: commit, push, rezumat, todo viitor, salvare memorie |
| `/commit` | `~/.claude/commands/commit.md` | Commit local: status, diff, add, message în engleză, Co-Authored-By Claude |
| `/push` | `~/.claude/commands/push.md` | Push pe GitHub: verifică commit-uri locale nepush-uite, push, confirmă |

Workflow tipic: `/start` → lucru → `/commit` → `/push` → `/end`
