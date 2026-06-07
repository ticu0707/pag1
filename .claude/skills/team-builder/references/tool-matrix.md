# Tool Matrix + YAML Spec + Naming Conventions

---

## Tool Restriction Matrix

> Principle: minimum privilege — each agent gets EXACTLY the tools it needs, no more.

| Role | Read | Grep/Glob | Write | Edit | Bash | Agent | WebSearch/Fetch |
|------|------|-----------|-------|------|------|-------|-----------------|
| Orchestrator | ✓ | ✓ | ✗ | ✗ | ✗ | ✓ | ✗ |
| Researcher | ✓ | ✓ | ✗ | ✗ | ✗ | ✗ | ✓ |
| Executor | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ | ✗* |
| Validator | ✓ | ✓ | ✗ | ✗ | ✓** | ✗ | ✗ |

> \* Executor may receive WebFetch if the task requires external documentation lookup — add explicitly in brief
> \*\* Validator uses Bash exclusively for running tests, not for modifications

---

## Model IDs (exact — pin these, never use aliases)

| Model | Exact ID | Context | Input $/1M | Output $/1M | Best for |
|-------|----------|---------|------------|-------------|----------|
| Claude Opus 4.8 | `claude-opus-4-8` | 1M | $5.00 | $25.00 | Orchestrators (complex), synthesis, strategic coordination |
| Claude Sonnet 4.6 | `claude-sonnet-4-6` | 1M | $3.00 | $15.00 | Orchestrators (default), workers, validators |
| Claude Haiku 4.5 | `claude-haiku-4-5` | 200K | $1.00 | $5.00 | Researchers, filtering, classification |

⚠️ **Never use**: `model: sonnet`, `model: opus`, `model: haiku`
These aliases resolve to whichever model is latest at the time — behavior can change without warning.

---

## Model Escalation Criteria — Orchestrators

**Default orchestrator**: `claude-sonnet-4-6`. Escalate to `claude-opus-4-8` when ANY criterion applies:

| Criterion | Threshold | Why escalate |
|-----------|-----------|--------------|
| Team size | 5+ agents requiring synthesis | Opus handles heterogeneous synthesis better at scale |
| Error cost | > $1,000 per error | Correctness > cost when stakes are this high |
| Domain breadth | 3+ fundamentally different domains (e.g., legal + code + design) | Cross-domain bridging requires deeper context |
| Reversibility | Irreversible actions in production | Deploys, financial transactions, emails sent |
| Context density | 100K+ tokens across agent outputs to synthesize | Sonnet may miss low-salience details at this scale |

**Cost impact of escalation**: Opus vs Sonnet orchestrator = +$0.05–$0.25 per task (pure overhead).
Justified when error-prevention value exceeds $0.25 per task — not justified for routine automation.

---

## YAML Frontmatter — Complete Field Reference

| Field | Required | Values | Priority |
|-------|----------|--------|----------|
| `name` | **YES** | lowercase, hyphens, unique in scope | — |
| `description` | **YES** | 2-3 sentences: trigger + exclusion | **CRITICAL** |
| `model` | no | **Exact ID** (see table above) | **CRITICAL for stability** |
| `tools` | no | allowlist string: `Read, Grep, Glob` | High |
| `disallowedTools` | no | denylist alternative | Medium |
| `maxTurns` | no | integer (NOT string: `"20"` fails silently) | **CRITICAL for cost** |
| `effort` | no | `low`, `medium`, `high`, `xhigh` (Opus 4.7/4.8), `max` (Opus 4.6+) | Medium |
| `permissionMode` | no | `default`, `acceptEdits`, `auto`, `bypassPermissions`, `plan` | High for executors |
| `isolation` | no | `worktree` | High for risky executors |
| `background` | no | `true` / `false` (boolean, NOT string) | High for parallel |
| `initialPrompt` | no | static context injected once before first user message | Medium |
| `color` | no | `red`, `blue`, `green`, `orange`, `purple` | Low |

> **`thinking` is NOT a YAML field.** Use `effort: xhigh` in YAML (Opus 4.7/4.8) for deep reasoning.
> `thinking: {type: "adaptive"}` is a Python Managed Agents API parameter only — `output_config` dict.

> **`permissionMode: bypassPermissions` — when valid, when dangerous**:
> Grants the agent full access — bypasses ALL permission prompts with no user confirmation.
> **Valid**: CI/CD pipelines with no human present, fully automated scripts with pre-approved and narrow scope.
> **Dangerous**: any session that processes external content, any agent with `WebFetch` or `WebSearch`.
> If a `bypassPermissions` agent is compromised via prompt injection, it executes arbitrary system commands without any safety prompt.
> Rule: `bypassPermissions` + any external content (web, files, API responses) = unacceptable risk.
> Safe combination: `bypassPermissions` + `isolation: worktree` + no web tools + fully internal data only.

> **`tools` (allowlist) vs `disallowedTools` (denylist)**:
> Use `tools` for all production agents — unknown tools are blocked by default.
> Use `disallowedTools` only when you cannot enumerate all needed tools (e.g., MCP server with many dynamic tools).
> Never use both on the same agent — behavior is undefined.

---

## YAML Syntax Edge Cases — 6 Silent Failures

These produce unexpected behavior without any error:

**1. `tools:` — string and array both accepted**
```yaml
tools: Read, Grep, Glob        # string inline — RECOMMENDED
tools: [Read, Grep, Glob]      # array inline — accepted
```

**2. `description:` — `>` vs `|`**
```yaml
description: >     # folded: newlines become spaces (sentences flow together)
  Invoke when X.
  Do NOT invoke for Y.    # → "Invoke when X. Do NOT invoke for Y."

description: |     # literal: newlines preserved (use for lists)
  Invoke when:
  - condition A
```

**3. `maxTurns:` must be integer, NOT string**
```yaml
maxTurns: 20     # ✓ integer — works
maxTurns: "20"   # ✗ string — silently ignored or causes parse error
```

**4. Typos in field names are silently ignored**
```yaml
permisionMode: acceptEdits   # ✗ missing 's' — completely ignored, no error
permissionMode: acceptEdits  # ✓ correct
```

**5. `model:` — no leading/trailing spaces**
```yaml
model: claude-sonnet-4-6    # ✓
model:  claude-sonnet-4-6   # ✗ double space — may cause parse error
```

**6. `background:` must be boolean, NOT string**
```yaml
background: true    # ✓ boolean
background: "true"  # ✗ string — may be misinterpreted
```

---

## Naming Conventions

**Agents** — format: `[team-name]-[role]`, kebab-case, max 30 characters:
```
✓ research-lead          → orchestrator of the research team
✓ auth-reviewer          → domain-specific reviewer
✓ data-worker            → executor for data tasks
✓ safe-planner           → planning agent with plan permission mode

✗ general                → too vague (Claude never knows when to invoke)
✗ helper                 → too vague
✗ agent                  → reserved word, causes confusion
✗ research_lead          → underscore instead of hyphen
✗ myVeryLongAgentName    → over 30 chars, camelCase
```

**Skills** — format: `[domain]-[action]` or `[action]`, kebab-case:
```
✓ team-builder           → meta-skill for building teams
✓ nextjs-audit           → Next.js-specific audit
✓ commit                 → simple process
✓ deep-researcher        → in-depth research

✗ /help, /clear          → conflicts with built-in CLI commands
✗ skill_creator          → underscore instead of hyphen
```

**Teams** — consistent prefix across all agent files:
```
research team:
  research-lead.md
  research-web-analyst.md
  research-code-analyst.md
  research-validator.md
```

---

## MCP Server Tools in Agent YAML

MCP (Model Context Protocol) tools are configured at the session/environment level, not in agent YAML `tools` field.

### Claude Code CLI agents

The `tools` YAML field accepts built-in tool names only. MCP tools are inherited from session config:
1. User global: `~/.claude/settings.json` (Windows: `%USERPROFILE%\.claude\settings.json`)
2. Project: `.claude/settings.json`

The agent does NOT declare MCP tools in YAML — they're available automatically if configured in settings.

### Managed Agents API — pass MCP tools in `agents.create()`

```python
agent = client.beta.agents.create(
    name="github-researcher",
    model="claude-haiku-4-5",
    instructions="...",
    tools=[
        {"type": "web_search"},
        # MCP tool declaration — format depends on your MCP server:
        {"type": "mcp", "server": "github", "tool_name": "search_repositories"},
        {"type": "mcp", "server": "github", "tool_name": "get_file_contents"},
    ],
)
```

### Pattern C (Fan-out) with heterogeneous MCPs

Each researcher gets different MCP tools; the coordinator uses `agent_invocation` only:

```python
# github-researcher — GitHub MCP only
github_tools = [{"type": "mcp", "server": "github", "tool_name": "search_repositories"}]

# database-researcher — Postgres MCP only
db_tools = [{"type": "mcp", "server": "postgres", "tool_name": "query"}]

# web-researcher — built-in web tools only
web_tools = [{"type": "web_search"}, {"type": "web_fetch"}]
```

```yaml
# Coordinator YAML (Claude Code CLI) — no MCP, only agent invocation
name: fanout-coordinator
tools: Agent(github-researcher, database-researcher, web-researcher), Read
```

---

## Color Conventions

Colors are semantic conventions — affect Claude Code UI display only, no impact on behavior.

| Color | Role | Purpose |
|-------|------|---------|
| `blue` | Orchestrator / Router | Authority — coordinates the team |
| `green` | Researcher / Explorer | Discovery — read-only |
| `orange` | Executor / Worker | Action — writes files |
| `red` | Validator / Critic | Verification — finds problems |
| `purple` | Planner / Analyzer | Strategy — no production writes |

Follow this convention consistently across teams for visual navigation in Claude Code's UI.

---

## `initialPrompt` — When and How to Use

`initialPrompt` injects static text **once**, before the first user message, without polluting the system prompt.

**When to use:**
- Large static context (codebase summary, schema reference, product brief) shared across many invocations
- Context that is the same every run but too large to repeat in each task brief
- When you want the stable prefix to be **cacheable** (> 1024 tokens = eligible for prompt caching → ~90% cost reduction on subsequent calls)

**When NOT to use:**
- Dynamic content that changes per task → put in the brief instead
- Short context (< 1024 tokens) → caching benefit negligible, use system prompt directly
- Security-sensitive instructions → keep those in the system prompt, not initialPrompt (loaded first, more resilient)

**Example:**
```yaml
---
name: codebase-worker
model: claude-sonnet-4-6
tools: Read, Grep, Glob, Edit
maxTurns: 20
initialPrompt: |
  ## Codebase Context
  Repository: acme-monorepo
  Stack: Next.js 14, Supabase v2, TypeScript strict
  Key directories: src/app/ (routes), src/lib/ (shared), .claude/agents/ (team files)
  Critical constraints: no direct DB writes outside src/lib/db/, all writes behind RLS
---
```

This codebase context is sent once per session and cached after the first call.

---

## Tool Availability in Subagents

Tools NOT available for subagents (agents invoked by orchestrator):
- `Agent` — cannot spawn other agents (exception: orchestrator with explicit `tools: Agent(...)`)
- `AskUserQuestion` — no direct interaction with user
- `EnterPlanMode` / `ExitPlanMode`
- `ScheduleWakeup`

---

## Agent File Storage Locations (priority descending)

1. Managed settings org-wide
2. `--agents` CLI flag (current session only)
3. `.claude/agents/` — **recommended for production**, version-controlled in git
4. `~/.claude/agents/` — user global (all projects)
5. Plugin `agents/` directory
