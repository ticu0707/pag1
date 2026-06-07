---
name: team-builder
description: >
  Invoke when user needs to design and generate a complete multi-agent AI team.
  Follows 10-step workflow: qualification → decomposition → surface selection →
  agent design → descriptions → briefings → production hardening → file generation →
  dry-run gates → anti-patterns check → convenience skill → evals setup.
  Produces: .claude/agents/*.md files, cost estimate, production checklist,
  optionally Python Managed Agents API code + convenience skill + evals test plan.
  Do NOT invoke for single-agent design, editing existing agents, or creating skills without a team.
---

## References

Load only when the step explicitly says to:

- **Agent role templates + Haiku warning**: `references/agent-roles.md`
- **Tool matrix + YAML spec + naming conventions + model escalation**: `references/tool-matrix.md`
- **5 orchestration patterns (incl. Pattern E team-of-teams) + timing + decision tree + when-to-redesign diagnostic**: `references/patterns.md`
- **Fault tolerance + observability + secrets management + structured output + security + non-determinism**: `references/production-hardening.md`
- **Cost ranges + prompt caching + Batch API + calibration methodology**: `references/cost-reference.md`
- **Output templates + convenience skill example + Day-2 summary**: `references/skill-output.md`
- **Evals methodology — schema tests, contract tests, A/B baseline, calibration**: `references/evals.md`

---

## Step 1: QUALIFY — Does the task need a team?

Ask the user:
> "Describe the task the agent team must solve. Be specific: what input does it receive,
> what output do you want, how often does it run?"

After receiving the answer, apply these 6 criteria (YES/NO per criterion):

```
□ Can you name 3 agents with completely different responsibilities in 30 seconds?
□ Does the task have 3+ distinct subtasks?
□ Do the subtasks require different tools?
□ Is the estimated total context > 30K tokens?
□ Are any subtasks parallelizable (independent inputs/outputs)?
□ Is error cost high enough to justify a validator?
```

**If 4+ criteria = NO:**
Respond: "Based on the task, a single agent with generous context can handle this.
A team would add 40-60s latency and 30-80% extra cost without better output.
Would you like a team anyway (state the reason), or shall I design a single agent?"

**If task justifies a team:** Continue to Step 2.

---

## Step 2: DECOMPOSE — What subtasks exist?

Complete this table jointly with the user:

```
| Agent | Does CONCRETELY (one action verb) | DIFFERENT tools from others | Output for whom |
|-------|----------------------------------|----------------------------|-----------------|
| A     | ?                                | ?                          | ?               |
| B     | ?                                | ?                          | ?               |
| C     | ?                                | ?                          | ?               |
```

Then map dependencies:
> "Which of these can run in parallel (independent)? Which depend on another's output?
> Mark with →: A → B means B needs A's output.
> Diamond dependency: C ← A, B means C needs BOTH A and B to complete first.
> C cannot start until both are done — note explicit wait instruction required in orchestrator."

Choose orchestration pattern (read `references/patterns.md` for full details + concurrency hazards):

| Condition | Pattern |
|-----------|---------|
| 3+ independent subtasks, different files/scopes | **A — Parallel** |
| Clear output → input dependencies | **B — Sequential Pipeline** |
| Heterogeneous sources + synthesis (MCP, different APIs) | **C — Fan-out** |
| Risky parallel changes to independent modules | **D — Worktree** |

Announce: "I'll use Pattern [X] because [reason]."

---

## Step 2.5: CHOOSE SURFACE — Claude Code or Managed Agents API?

| | Claude Code CLI | Managed Agents API |
|--|-----------------|-------------------|
| **How invoked** | Interactively in terminal | Python/TypeScript server code |
| **Files generated** | `.claude/agents/*.md` | `agents.create()` + `sessions.create()` |
| **Agent state** | Stateless per invocation | Persistent agent IDs (create once, reuse) |
| **Platform support** | Universal | NOT on Bedrock / Vertex AI / Foundry |
| **Best for** | Developer workflows, interactive use | Automated pipelines, user-facing products |

Ask:
> "How will this team be used?
> (A) Interactively in terminal / Claude Code CLI — you invoke manually
> (B) From a server-side application (Python/TypeScript backend, API, cron job)
> (C) Both contexts"

- **(A)** → Generate `.claude/agents/[team-name]-[role].md` files only
- **(B)** → Generate Managed Agents API code (Python or TypeScript — ask user's preferred language)
  - ⚠️ NOT available on Amazon Bedrock, Google Vertex AI, or Microsoft Foundry → use (A) on those platforms
- **(C)** → Generate both variants

---

## Step 3: DESIGN AGENTS — One agent per subtask

Read `references/agent-roles.md` for the 4 canonical role templates.
Read `references/tool-matrix.md` for the full tool restriction matrix and model IDs.

For each agent, determine:

**Model** (always pin to exact ID — never use aliases `sonnet`, `opus`, `haiku`):
- **Orchestrator default**: `claude-sonnet-4-6` → escalate to `claude-opus-4-8` only if: 5+ agents to synthesize, error cost > $1,000, 3+ heterogeneous domains, or irreversible production actions. See `references/tool-matrix.md` for full escalation criteria.
- Code implementation / execution / medium reasoning → `claude-sonnet-4-6`
- Search / filtering / classification / high volume → `claude-haiku-4-5`
  ⚠️ **Haiku hard limit**: if estimated input > 150K tokens → use `claude-sonnet-4-6` instead (silent truncation, no error)

**Tools** (minimum required per role — see tool matrix):
- Researcher: `Read, Grep, Glob, WebSearch, WebFetch` (NO Write/Edit/Bash)
- Executor: `Read, Grep, Glob, Edit, Write, Bash`
- Validator: `Read, Grep, Glob, Bash` (NO Write/Edit)
- Orchestrator: `Agent([agents...]), Read`

**maxTurns** (conservative defaults):
```
Researcher: 10-15    Worker simple: 15-20    Worker complex: 20-25
Validator:  8-12     Orchestrator:  25-35
```

**Other fields**:
- `isolation: worktree` — executor with Edit/Write/Bash on existing files + regression risk
- `permissionMode: acceptEdits` — executors | `plan` — safe-planners | `default` — others
- `background: true` — parallel agents (Pattern A)
- Criticality: **CRITICAL** (absence blocks task) or **OPTIONAL** (absence degrades quality)

Present design summary and ask for confirmation before proceeding:

```
"Proposed team design:
| Agent | Model | Tools | maxTurns | Criticality | isolation | background |
|-------|-------|-------|----------|-------------|-----------|------------|
| ...   | ...   | ...   | ...      | ...         | ...       | ...        |

Any modifications before I write descriptions?"
```

---

## Step 4: WRITE DESCRIPTIONS — The routing field

For each agent, apply this anatomy:

```
"Invoke when [specific trigger condition].
[Input type if relevant: 'when given a file path', 'when analyzing TypeScript'].
Do NOT invoke for [at least one exclusion].
[Position in workflow: 'Called by orchestrator after X completes.' if sequential]"
```

Mental test: "Seeing only this description, would I always know when to invoke and when NOT to invoke?"
If NO → rewrite with more specific trigger or additional exclusion cases.

**Naming**: `[team-name]-[role]` kebab-case, max 30 chars.
Valid: `research-lead`, `auth-reviewer`, `data-worker`
Invalid: `general`, `helper`, `research_lead` (underscore)

---

## Step 5: WRITE BRIEFINGS — 4-Part Contract

For each agent, write the brief the orchestrator will send:

```markdown
**Objective**: [what must be achieved — specific and verifiable]

**Output format**:
## [Required section 1]
[exact structure]

## [Required section 2]
[exact structure]

**Tool guidance**: Use [allowlisted tools]. Do NOT use [excluded tools].

**Boundaries**:
- Operate ONLY within [exact scope]
- Do NOT modify [what must not be touched]
- If [ambiguous situation]: [exact action to take]
- Max [N] results/iterations
- Stop immediately if [condition] and report it
```

Verification gate: "If an agent receives ONLY this brief (zero prior context), can it produce the desired output?
If NO → identify what information is missing and add it."

---

## Step 6: PRODUCTION HARDENING

Read `references/production-hardening.md` for full fault tolerance, security, and non-determinism details.

Apply these critical checks — all must be DA before generating files:

**Fault Tolerance:**
- [ ] Circuit breaker in orchestrator (max 2 retry → FAILED, CRITICAL stops | OPTIONAL continues)?
- [ ] Every agent classified CRITICAL or OPTIONAL?
- [ ] Checkpoint compression in orchestrator (max 400 tokens per agent)?
- [ ] Side-effect operations idempotent or protected with task_id?
- [ ] Non-rollbackable operations identified → validation BEFORE execution?
- [ ] Orchestrators using `background: true` have explicit wait instruction?

**Observability:**
- [ ] Orchestrator logs: `## [LOG] Agent: [name] | Status: [X] | Turns: [X/max] | Cost: ~$[est]`?
- [ ] Briefs contain `Task ID` and `Trace ID`?

**Cost** (read `references/cost-reference.md`):
- [ ] Cost range calculated and acceptable?
- [ ] System prompts > 1024 tokens structured with stable prefix for caching?
- [ ] Haiku researchers won't receive > 150K tokens input?
- [ ] For Opus 4.7/4.8 via Managed Agents API: `task_budget` set to prevent runaway loops?

**Secrets & Environment:**
- [ ] No API keys, tokens, or passwords in task briefs or checkpoint logs?
- [ ] Secrets referenced in system prompts only as `$ENV_VAR_NAME` — agent reads from environment at runtime?
- [ ] `create_team()` validates all required env vars at startup (fail fast before sessions start)?

**Structured Output (when downstream code parses agent output):**
- [ ] All programmatically-parsed fields use exact value constraints (not free-form text)?
- [ ] Output section names in briefs match exactly the sections in Tier 1 SCHEMA dict?
- [ ] For Managed Agents API validators: consider `output_config.format.json_schema` for machine-parsed fields?

**Security:**
- [ ] Agents processing external content (web, files) have tools WITHOUT Write/Edit/Bash?
- [ ] Each system prompt includes ABSOLUTE SECURITY RULE (see `references/production-hardening.md`)?
- [ ] Orchestrator has summarization instruction (no copy-paste of external content into next brief)?
- [ ] High-security teams (external content + executor with Bash): consider upgrading to Structured Handoff Schema — orchestrator extracts typed fields only, raw text discarded (see `references/production-hardening.md` → Structured Handoff Schema)?

---

## Step 7: GENERATE FILES

Read `references/skill-output.md` for the orchestrator template and output format spec.

Produce ALL of the following:

**1. Agent files** — one `.claude/agents/[team-name]-[role].md` per agent
- Complete YAML frontmatter + full production-ready system prompt
- ZERO placeholder text — every `[bracket]` replaced with real content
- Orchestrator must include: circuit breaker + checkpoint logging + background wait instruction + security summarization rule

**2. Brief template** — markdown, ready to copy-paste when invoking the team manually

**3. Cost estimate**:
```
Configuration: [list agents + their models]
Cost per task:
  Simple:  $[min]–$[max]
  Medium:  $[min]–$[max]
  Complex: $[min]–$[max]
Cost per 100 tasks (no caching): $[range]
Cost per 100 tasks (with prompt caching ~65% reduction): $[range]
```

**4. Production checklist** — 35 binary items (DA/NU) based on decisions from Steps 1-6

**5. Installation instructions**:
```
## Installation

### Global — available in all projects (recommended for personal use):
- Mac/Linux: Copy to ~/.claude/agents/
- Windows:   Copy to C:\Users\[username]\.claude\agents\

### Per-project — version-controlled in git (recommended for teams):
Copy to [project-root]/.claude/agents/
git add .claude/agents/ && git commit -m "add [team-name] agent team"
```

**6. Managed Agents API code** (if surface B or C chosen in Step 2.5)
Ask: "Python or TypeScript?" then follow the matching pattern from `references/skill-output.md`.

---

## Step 7.5: DRY-RUN VALIDATION GATES

Before delivering files, pass all 3 gates. If any gate fails — fix the issue, do NOT deliver.

**Gate 1: Schema validation** — run from your project root:
```
# Mac/Linux:
python ~/.claude/skills/team-builder/scripts/validate_agents.py .claude/agents/
# Windows (PowerShell):
python $env:USERPROFILE\.claude\skills\team-builder\scripts\validate_agents.py .claude/agents/
```
Required: ALL files PASS. Any FAIL = fix before proceeding.

**Gate 2: Brief self-sufficiency check**
For each agent brief: "If I received ONLY this brief with zero prior context, could I produce the required output?"
Required: YES for every agent. If NO — identify what is missing and add it.

**Gate 3: Orchestrator logic trace**
Mentally trace the full execution step-by-step:
- Every output section from each agent is explicitly consumed in the next step
- Circuit breaker covers every CRITICAL agent path
- Explicit wait instruction present before synthesis (if Pattern A)
- No undefined handoffs ("assume agent returns X" without a verified output schema)

Only after all 3 gates pass → proceed to Step 8.

---

## Step 8: PRODUCTION READINESS CHECK

Before delivering, verify all 15 items:

- [ ] 1. Team justified (Step 2 table filled with 3 distinct roles)?
- [ ] 2. All descriptions have trigger + "Do NOT invoke for" exclusion?
- [ ] 3. All briefs have all 4 contract parts (Objective + Format + Tools + Boundaries)?
- [ ] 4. `maxTurns` set on ALL agents (integer, not string)?
- [ ] 5. Circuit breaker in orchestrator (not just maxTurns)?
- [ ] 6. Tool over-granting checked (each agent has minimum required)?
- [ ] 7. Parallelism used where beneficial and correct pattern chosen?
- [ ] 8. Model pinned to exact ID, not alias (`claude-sonnet-4-6` not `sonnet`)?
- [ ] 9. Context overflow evaluated (5 agents × 30 turns ≈ 20-40K tokens at orchestrator)?
- [ ] 10. Brief poisoning mitigated (summarize, don't copy-paste external content)?
- [ ] 11. `background: true` agents have explicit wait instruction before synthesis?
- [ ] 12. Convenience skill (if generated) has complete Step 1 brief collection + Step 2 cost confirm?
- [ ] 13. All 3 Dry-Run Gates passed (Gate 1 schema validator, Gate 2 brief self-sufficiency, Gate 3 orchestrator trace)?
- [ ] 14. Evals setup offered in Step 10 (T1 Schema + T2 Contract + T3 A/B baseline)?
- [ ] 15. Cost estimate presented as range, with note that Tier 4 calibration tightens to p50/p95 after 20 runs?
- [ ] 16. No secrets/credentials in agent files or briefs — `$ENV_VAR_NAME` references only?
- [ ] 17. Structured output fields (if code parses them) use exact value constraints, not free-form text?
- [ ] 18. `effort` field set on all agents (low/medium/high/xhigh appropriate to role and model)?

If any item = NO: fix before delivery.

---

## Step 9: GENERATE CONVENIENCE SKILL (optional)

Ask:
> "Would you like me to generate a convenience skill `.claude/skills/[team-name].md`?
> This creates a `/[team-name]` command that collects the brief interactively before launching the team.
> ⚠️ The skill will be available starting with your NEXT Claude Code session — skills are loaded once
> at session start from `~/.claude/skills/` or `.claude/skills/`. To invoke the team NOW without
> waiting for next session: use the brief template from Step 7 output #2 directly with the orchestrator."

If YES: generate `.claude/skills/[team-name].md` following the Convenience Skill Template in `references/skill-output.md`.

Rules for the convenience skill:
- Step 1: collect all information needed for the orchestrator brief
- Step 2: present cost estimate → ask confirmation → launch orchestrator with Agent tool
- Step 3: present results + offer follow-up
- Zero placeholder text — every field completed with real content for this specific team
- Frontmatter: `name` + `description` ONLY (no `tools`, `model`, `maxTurns` — those are agent fields)

Add installation instructions for the skill file:
```
## Convenience Skill Installation

### Global:
- Mac/Linux: Copy to ~/.claude/skills/
- Windows:   Copy to C:\Users\[username]\.claude\skills\

### Per-project:
Copy to [project-root]/.claude/skills/
```

---

## Step 10: EVALS SETUP

Read `references/evals.md` for the complete 4-tier methodology.

Present to user:
> "Before first production use, recommend setting up evals:
>
> **Immediate (free, < 5 seconds):**
> `python scripts/validate_agents.py .claude/agents/` — run after any .md file change.
>
> **Before first production deployment:**
> - Tier 2: invoke each agent 3× with a test brief → schema valid all 3 times?
> - Tier 3 A/B: run same task on single `claude-sonnet-4-6` vs full team.
>   Decision rule: quality delta < 0.5 AND cost delta > 50% → team not justified → redesign.
>
> **After first 20 real runs:**
> - Tier 4: compute p50/p95 from logs → tighten cost estimate from ±10× to ±3×.
>
> Should I generate a `.claude/[team-name]-evals.md` test plan with test briefs specific to this team?"

If YES: generate a test plan with:
- `SCHEMA` dict per agent (required/forbidden sections from their output format)
- `TEST_BRIEF_TEMPLATE` filled for each agent
- `BASELINE` dict prefilled with team name, agent list, zeros to fill after 20 runs
- `ALERT_THRESHOLDS` dict (defaults from `references/evals.md`)

---

## Output Specification

This skill MUST produce all of:
1. `.claude/agents/[team-name]-*.md` files — complete, no placeholders, all roles
2. Brief template for manual team invocation
3. Cost estimate range (simple / medium / complex) — as range, not point estimate
4. Production checklist — DA/NU per item (Step 6 checks + Step 8 checks, ~30 items total)
5. Installation instructions (global + per-project, both platforms)
6. Python Managed Agents API code (if surface B or C chosen)
7. `.claude/skills/[team-name].md` convenience skill (if confirmed in Step 9)
8. `.claude/[team-name]-evals.md` test plan (if confirmed in Step 10)

---

## Anti-patterns

- **Proposing without qualifying**: Never propose team design before Step 1 is complete
- **Skipping Step 2.5**: Always determine deployment surface — it dictates what files to generate
- **Placeholder text in output**: Every `[bracket]` must be replaced with actual content
- **Describing instead of generating**: Output is files, not descriptions of what files would contain
- **Alias model IDs**: Never use `sonnet`, `opus`, `haiku` — always exact IDs like `claude-sonnet-4-6`
- **Opus for all orchestrators**: Default orchestrator is `claude-sonnet-4-6` — escalate to Opus only when escalation criteria apply (see `references/tool-matrix.md`)
- **Skipping production hardening**: Step 6 is mandatory, not optional
- **Delivering without dry-run gates**: Never skip Step 7.5 — Gate 1 (schema validator), Gate 2 (brief self-sufficiency), Gate 3 (orchestrator trace) must all pass
- **Skipping A/B baseline**: Without Tier 3 comparison, you cannot know if team overhead is justified — always offer Step 10 evals setup
- **Point estimates for cost**: Present ranges, not single numbers; note that Tier 4 calibration tightens to p50/p95 after 20 real runs
- **Announcing skill availability in current session**: Always inform user the convenience skill is available in NEXT session
- **Orchestrator context overflow mid-execution**: With 5+ agents returning 600 tokens each, the orchestrator accumulates 3K+ tokens of checkpoints per run. Symptoms appear silently at turn 25–30: agents skipped, "found nothing" despite output, loop repetition, lost agent tracking. Prevention: checkpoint compression (max 400 tokens/agent) + maxTurns ceiling + split large tasks into sequential phases
- **Credentials in agent briefs**: Never put API keys, tokens, or passwords in task briefs — they end up in checkpoint logs and structured output. Use environment variables or secrets management; reference them in the system prompt only as `$ENV_VAR_NAME` with a note that the agent should read the actual value from the environment
- **Free-form output for machine-parsed fields**: If code parses agent output (verdict, status flags), prescribe exact values in brief ("exactly PASS or FAIL — no other text"). Free-form text causes regex fragility and silent parser failures
- **Team-of-teams via agent nesting**: Managed Agents API supports only 1 level of delegation — nested sub-subagents silently don't run, no error. Use Pattern E (Router Orchestrator) instead of nesting
- **Skipping `effort` field**: Not setting `effort` means every agent runs at default (`high`). Haiku researchers at `low` cost ~50% less — significant at scale. Opus orchestrators at `xhigh` produce meaningfully better synthesis than `high`
- **Launching v2 without shadow testing**: Breaking changes to a live team without shadow mode (20 parallel shadow runs comparing v1 vs v2) risk silent regression in production
