---
name: reference_skill_skill_creator
description: Skill /skill-creator — meta-skill pentru crearea și pachetizarea altor skill-uri Claude Code; include scripturi Python și referințe de design
metadata: 
  node_type: memory
  type: reference
  originSessionId: 5684968a-3935-49fa-9aef-87d81766bca3
---

# Skill: /skill-creator

**Locație globală:** `C:\Users\admin\.claude\skills\skill-creator\`

**Scop:** Meta-skill — ghidează crearea de skill-uri noi de la zero. Acoperă întreg ciclul: înțelegere → planificare → inițializare → editare → pachetizare → iterare.

## Structura instalată

```
skill-creator/
├── SKILL.md                        ← instrucțiuni principale
├── references/
│   ├── output-patterns.md          ← Template Pattern + Examples Pattern
│   └── workflows.md                ← Sequential + Conditional Workflows
└── scripts/
    ├── init_skill.py               ← creează directorul skill din template
    ← package_skill.py             ← pachetizează skill-ul în .skill (zip)
    └── quick_validate.py           ← validare rapidă structură skill
```

## Cum se folosește

**Pasul 1 — Init:**
```bash
python .claude/skills/skill-creator/scripts/init_skill.py <skill-name> --path .claude/skills
```

**Pasul 2 — Editare:** Completezi TODO-urile din SKILL.md generat.

**Pasul 3 — Pachetizare:**
```bash
python .claude/skills/skill-creator/scripts/package_skill.py .claude/skills/<skill-name>
```
→ Produce `<skill-name>.skill` (zip cu extensie .skill) pentru distribuție.

**Pasul 4 — Validare:**
```bash
python .claude/skills/skill-creator/scripts/quick_validate.py .claude/skills/<skill-name>
```

## Principii cheie

- **Concis is Key** — contextul e o resursă partajată; nu adaugă ce Claude știe deja
- **Progressive Disclosure** — SKILL.md body < 500 linii; detalii în `references/`
- **Degrees of Freedom** — high (text) / medium (pseudocode) / low (script fix) în funcție de fragilitate
- **Nu include** README.md, INSTALLATION_GUIDE.md sau alte fișiere auxiliare

## Anatomia unui skill complet

```
skill-name/
├── SKILL.md             ← frontmatter (name + description) + instrucțiuni
├── scripts/             ← cod executabil (Python/Bash)
├── references/          ← documentație de context (încărcată la nevoie)
└── assets/              ← template-uri, imagini, fonturi (nu se încarcă în context)
```

**Why:** Fiecare element are un rol diferit față de context window — assets nu se încarcă niciodată; references se încarcă doar când sunt relevante.

**How to apply:** Când userul cere să creăm un skill nou, folosim `/skill-creator` și urmăm cei 6 pași. `init_skill.py` generează structura; noi editam; `package_skill.py` distribuie.
