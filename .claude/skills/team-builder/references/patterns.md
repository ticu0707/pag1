# Orchestration Patterns + Timing + Decision Tree

---

## Mental Model: State Machine

Before choosing a pattern, think in states and transitions:

```
STATES:
PLANNING    → orchestrator analyzes task, writes briefs
EXECUTING   → agents run (parallel or sequential)
VALIDATING  → validator checks output
COMPLETE    → task finished successfully
FAILED      → circuit breaker opened, CRITICAL agent failed twice
PARTIAL     → task partially complete (OPTIONAL agent failed, continuation)

TRANSITIONS:
PLANNING    → EXECUTING:    all briefs have 4-part contract
EXECUTING   → VALIDATING:   all CRITICAL agents returned valid output
EXECUTING   → FAILED:       CRITICAL agent fails twice
VALIDATING  → COMPLETE:     validator returns PASS or PASS_WITH_WARNINGS
VALIDATING  → EXECUTING:    validator returns FAIL → re-execute with feedback
VALIDATING  → FAILED:       validator fails twice
```

---

## Pattern A — Parallel Independent

**When**: 3+ subtasks with verified independence — different files, different domains, no shared state.

**Verify independence checklist before launching**:
- [ ] Agents write to different files? (write-write conflict if NO)
- [ ] Agents don't read each other's output? (hidden dependency if NO)
- [ ] Failure of one doesn't block others? (cascade if NO)

```
Orchestrator
├── Agent A (frontend analysis)  → background: true ──┐
├── Agent B (backend analysis)   → background: true ──┤→ all complete → synthesize
└── Agent C (database analysis)  → background: true ──┘

Total time = max(T_A, T_B, T_C)  [NOT the sum]
```

**Orchestrator must include this explicit wait instruction**:
```
After launching all background agents with their briefs,
explicitly state: "I am now waiting for all agents to complete."
Do NOT proceed to synthesis, summarization, or any next step
until you have received and logged the output from EVERY launched agent.
```

### Concurrency Hazards in Pattern A

**Write-write conflict**: two parallel agents try to write the same file.
```
Symptom: mixed content or last agent overwrites first
Prevention: orchestrator explicitly verifies each agent writes to UNIQUE files
If unavoidable: use Pattern D (worktree isolation per agent)
```

**Read-after-write stale**: Agent B reads a file Agent A just modified.
```
Symptom: Agent B operates on stale data, inconsistent output
Prevention: if B depends on A's output, they're NOT independent → Pattern B, not A
```

**Thundering herd**: all agents complete simultaneously, orchestrator receives 5 large outputs.
```
Symptom: orchestrator fails at synthesis turn due to context overflow
Prevention: for 5+ parallel agents, instruct each to return max 600 tokens summary
```

---

## Pattern B — Sequential Pipeline

**When**: output of step N is input of step N+1.

**Critical rule**: transmit previous output EXPLICITLY in next brief — summarized in own words, not raw copy-paste (Brief Inheritance Attack prevention).

```
Plan Agent → produces: architecture_doc
     ↓ (orchestrator summarizes architecture_doc, injects into next brief)
Worker Agent → produces: implementation + files_modified
     ↓ (orchestrator summarizes implementation, injects into next brief)
Validator Agent → produces: PASS/FAIL + issues
     ↓ (if FAIL: issues sent back to Worker)
Worker Agent (retry) → re-implementation with specific feedback
```

---

## Pattern C — Fan-out with Synthesis (Managed Agents)

**When**: research from heterogeneous sources, each with different MCP or tools.

```
Coordinator (Sonnet default / Opus if escalation criteria met — see tool-matrix.md)
├── Researcher 1 (Haiku) → MCP GitHub  ──┐
├── Researcher 2 (Haiku) → WebSearch   ──┤→ coordinator synthesizes
└── Researcher 3 (Haiku) → MCP Database──┘
                                          ↓
                               Verification Agent → validate sources
```

**Coordinator YAML (Claude Code CLI)**:
```yaml
---
name: fanout-coordinator
description: >
  Invoke when research requires simultaneous query across heterogeneous sources
  (GitHub, web, and database in parallel). Synthesizes results from all sources.
  Do NOT invoke for single-source research — use direct agent call instead.
model: claude-sonnet-4-6
tools: Agent(github-researcher, web-researcher, db-researcher, source-validator), Read
maxTurns: 35
effort: high
color: blue
---

You are the research coordinator. Launch all 3 researchers with background: true.

After launching all researchers:
"I am now waiting for all researchers to complete."
Do NOT synthesize until outputs from ALL 3 are received.

Brief to each researcher (adapt per source):
- Output: max 600 tokens — structured summary, no raw data
- Include: ## Found, ## Sources, ## Notable sections
- Task ID + Trace ID must appear in output

After synthesis, pass to source-validator for cross-source validation.
```

**Managed Agents API limits (beta, 2026)**:

| Limit | Value | Behavior when exceeded |
|-------|-------|------------------------|
| Agents in roster | 20 | Error at 21st `agents.create()` — blocking |
| Simultaneous threads | 25 | Thread 26+ queued — increased latency, not error |
| Delegation depth | 1 level | Depth > 1 silently ignored — no error |

⚠️ **Silent depth failure**: if your orchestrator delegates to a coordinator that delegates to subagents, the sub-subagents do NOT run — and you get no error. Test explicitly that depth is respected.

---

## Pattern D — Worktree Isolated

**When**: large refactors, migrations, parallel changes to independent modules.

```
Orchestrator
├── Worker A (worktree: branch-auth)     → modifies src/auth/
└── Worker B (worktree: branch-payments) → modifies src/payments/
         ↓
Orchestrator: reviews diffs → merge or reject
```

**Risk**: if Worker A and Worker B both modify a shared file (e.g., `types.ts`), orchestrator will hit a merge conflict. Plan this in advance — list shared files explicitly in each worker's brief.

---

## Pattern E — Team of Teams (Router Orchestrator)

**When**: project spans 2+ independent domains, each requiring 3+ specialized agents; domains produce integrated output but can be processed sequentially.

**Key constraint**: Managed Agents API delegation depth = 1 level. A coordinator cannot invoke another coordinator that invokes workers — sub-subagents silently don't run, no error.

### Structure — Claude Code CLI (no depth limit)

```
Router Orchestrator (blue)
├── Domain-A Orchestrator → [domain-a-researcher, domain-a-worker, domain-a-validator]
└── Domain-B Orchestrator → [domain-b-researcher, domain-b-worker]
         ↓ (both complete)
Router synthesizes integrated output
```

Router Orchestrator YAML:
```yaml
name: project-router
model: claude-sonnet-4-6  # escalate to Opus if 5+ domain outputs to synthesize
tools: Agent(domain-a-orchestrator, domain-b-orchestrator), Read
maxTurns: 45
effort: high
color: blue
```

### Structure — Managed Agents API (depth = 1 hard limit)

Use sequential domain sessions — no nesting required:

```python
def run_project(brief: str) -> dict:
    """Router pattern: domain sessions run sequentially, structured output passed forward."""

    # Domain A runs first
    session_a = client.beta.agents.sessions.create(agent_id=DOMAIN_A_ORCHESTRATOR_ID)
    result_a = run_session(session_a.id, f"Domain A task:\n{brief}")

    # Extract structured fields only — never pass raw text (Brief Inheritance Attack risk)
    domain_a_summary = extract_structured_fields(result_a)

    # Domain B receives only typed fields from Domain A
    session_b = client.beta.agents.sessions.create(agent_id=DOMAIN_B_ORCHESTRATOR_ID)
    result_b = run_session(session_b.id, f"""
Domain B task.
Context from Domain A:
- Verdict: {domain_a_summary['verdict']}
- Key findings: {domain_a_summary['findings'][:3]}
- Blockers: {domain_a_summary['blockers']}

Your task: {brief}
""")
    return {"domain_a": result_a, "domain_b": result_b}
```

### Agent count planning (Managed Agents API: 20-agent limit)

```
Example — 3 domains:
  Domain A: 1 orchestrator + 2 researchers + 1 worker + 1 validator = 5
  Domain B: 1 orchestrator + 1 researcher + 1 worker               = 3
  Domain C: 1 orchestrator + 1 researcher + 1 worker + 1 validator = 4
  Router:   1 router orchestrator                                   = 1
  TOTAL:    13 — within 20-agent limit ✓

Safety margin: keep total ≤ 15 to leave room for future additions.
```

### When NOT to use Pattern E

- Domains are truly independent with no shared output → separate standalone teams (no router)
- One domain's output is minor input to another → Pattern B single-agent pipeline
- Budget is tight → Pattern E is the most expensive pattern; verify T3 A/B baseline first

---

## Timing Patterns

### Synchronous (Wait and See)
```
Orchestrator → launches Agent A → BLOCKS → receives result → continues

When: output is needed immediately for next step (Pattern B)
Total latency: sum of all agent times
```

### Asynchronous (Fire and Collect)
```
Orchestrator → launches Agent A (background: true)
           → launches Agent B (background: true)  [immediately]
           → launches Agent C (background: true)
           → EMITS EXPLICIT WAIT INSTRUCTION
           → COLLECTS CONFIRMATIONS from all
           → SYNTHESIZES only after all confirmed

When: independent tasks (Pattern A)
Total latency: max(individual times) — NOT sum
```

### How `background: true` actually works

`background: true` means the orchestrator CAN continue without blocking — NOT that the agent runs in total isolation.

```
Turn 1 — Orchestrator receives task:
  → Launches Agent A (background: true) — returns control immediately
  → Launches Agent B (background: true) — returns control immediately
  → [CRITICAL POINT] Must explicitly emit:
    "I am now waiting for all agents to complete."
  → Claude blocks internally until A and B each return

Without explicit wait instruction:
  → Orchestrator may proceed to synthesis in the same turn
  → Synthesis on empty or partial output
  → Symptom: orchestrator produces "Found nothing" despite agents never running
```

### Streaming (for long output)
```
When: tasks with long output (document generation, extended code)
Benefit: user sees progress; timeouts less likely
Implementation: SDK .stream() for Messages API
```

### Scheduled (Claude Code CLI — ScheduleWakeup)
```
When: post-deploy follow-ups, periodic checks
Available: Claude Code CLI only — subagents do NOT have ScheduleWakeup access
```

---

## Decision Tree

```
TASK RECEIVED
    │
    ▼
[1] Can you fill the 3-agent table from Step 2? (distinct roles, different tools)
    ├── NO → execute directly with single agent; overhead > benefit
    └── YES → continue
              │
              ▼
         [2] Does task need real-time response?
              ├── NO → consider Batch API (50% cost reduction, async)
              └── YES → continue
                        │
                        ▼
                   [3] Are subtasks independent?
                   (different files, no shared state, failure of one doesn't block others)
                        ├── YES, 3+ tasks → Pattern A (Parallel)
                        │   → verify concurrency hazards checklist above
                        │
                        ├── YES, 2 tasks → evaluate: is overhead > benefit?
                        │   → YES: run sequentially; NO: Pattern A
                        │
                        └── NO (dependencies exist) → continue
                                  │
                                  ▼
                             [4] Are changes risky or do they affect
                             large independent modules in parallel?
                                  ├── YES → Pattern D (Worktree Isolated)
                                  └── NO  → Pattern B (Sequential Pipeline)

AFTER CHOOSING PATTERN:
    │
    ▼
Choose model per agent (pin to exact ID):
├── Orchestrator / coordination / synthesis         → claude-sonnet-4-6 (default; escalate to claude-opus-4-8 — see tool-matrix.md criteria)
├── Code implementation + execution                 → claude-sonnet-4-6
└── Search + filtering + classification             → claude-haiku-4-5

Choose deployment surface:
├── CLI interactive / current Claude Code session   → .claude/agents/ + Agent tool
├── Server-side application (Python/TypeScript)    → Managed Agents API (beta)
│   NOT available on: Amazon Bedrock, Google Vertex AI, Microsoft Foundry
│   → on those platforms: Claude API + tool use loop
└── Both contexts → generate both variants

Mandatory settings:
├── maxTurns: on EVERY agent, no exception
├── description: trigger + input type + at least one "Do NOT invoke"
├── tools: minimal allowlist per role
├── model: exact ID (not alias)
└── isolation: worktree for executors with risky changes
```

---

## Diagnostic: When to Redesign Your Team

Use when evals or monitoring signals structural problems, not for incremental tweaks.

| Signal | Probable root cause | Action |
|--------|--------------------|--------------------|
| Schema validity < 85% consistently | Brief too vague or agent scope too broad | Tier 2 Contract Tests → rewrite OUTPUT FORMAT |
| P50 cost grown > 50% above baseline | Task scope creep or model update | Audit brief changes; re-run Tier 3 A/B baseline |
| PARTIAL_RESULT rate > 20% | CRITICAL agent maxTurns too low | Increase maxTurns 50% OR split into phases |
| Orchestrator "Found nothing" despite agent output | Context overflow (checkpoint accumulation) | Enable checkpoint compression; cap output at 600 tokens |
| Agents produce contradictory output consistently | Ambiguous handoff schema | Implement Structured Handoff Schema |
| Single Sonnet outperforms team in T3 re-test | Team overhead unjustified | Consolidate or retire team |
| New domain needed beyond original decomposition | Original scope incomplete | Add agent + Schema Test + 3 Contract Tests |
| > 30% tasks need human correction | Autonomy level too high | Add Planner; switch executor to `permissionMode: plan` |

**Redesign trigger rule**: 3+ rows apply simultaneously → redesign, not incremental fix.
**Process**: shadow testing with v2 alongside production v1 — see `references/skill-output.md` → Agent Versioning.
