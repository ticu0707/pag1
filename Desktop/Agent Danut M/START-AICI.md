# Cum îți construiești agentul (pornind de la acest șablon)

Ai un agent de social media complet, gata de adaptat. Pornește de la fișierele astea, nu de la zero.

## 1. Înțelege anatomia

- `CLAUDE.md`, contractul de pornire (recitește totul, pornește heartbeat-ul)
- `IDENTITY.md`, ce livrează agentul și la ce standard
- `USER.md`, despre tine, omul pentru care lucrează
- `SOUL.md`, ce face singur și ce întreabă întâi, plus securitate
- `TOOLS.md`, uneltele și conturile tale
- `MEMORY.md`, memoria pe termen lung
- `HEARTBEAT.md`, ce verifică la fiecare bătaie
- `briefs/`, aici pui brief-urile
- `output/{data}/`, aici scrie agentul
- `.claude/skills/`, skill-urile agentului (pipeline, voce, topic-radar, kie-image)

## 2. Personalizează (fișierele cu placeholdere [...])

1. `USER.md`, scrie despre tine și vocea ta
2. `IDENTITY.md`, destinatarul și standardul tău
3. `TOOLS.md`, conturile tale de social media
4. `.claude/skills/scriere-dm-ref/SKILL.md`, regulile vocii tale
5. `MEMORY.md`, preferințele și sursele tale

## 3. Pune cheile (în afara iCloud)

Secretele nu stau pe Desktop sau Documents (se sincronizează iCloud). Copiază folderul în afara lor:

```
cp -R sm-writer-template ~/agentul-meu
```

```
cd ~/agentul-meu
```

```
cp .env.example .env
```

Apoi editează `.env` cu cheile tale (Firecrawl, Kie AI, Zernio).

## 4. Pornește

Deschide Claude Code în folder și dă linia de bootstrap:

```
Citește CLAUDE.md și pornește.
```

Agentul recitește toate fișierele, pornește `/loop` la 30 de minute și raportează starea.
