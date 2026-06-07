# Evals — Schema Tests, Contract Tests, A/B Baseline, Calibration

---

## Why Evals Are Non-Negotiable

A generated agent team is a hypothesis. Without evals, you have no signal on:
- Whether agents produce valid output (schema compliance)
- Whether team overhead is justified vs a single agent on the same task
- Whether cost is trending unexpectedly
- Whether a model update or brief change broke behavior silently

Evals are not optional polish. They are the line between prototype and production system.

---

## Tier 1: Schema Tests — Always, Free, < 5 Seconds

**What**: verify agent output contains all required sections and correct field values.
**When**: after ANY change to agent .md files, briefs, or model IDs.
**Cost**: zero — pattern matching only, no LLM invocation.

Run from project root:
```
# Mac/Linux:
python ~/.claude/skills/team-builder/scripts/validate_agents.py .claude/agents/
# Windows (PowerShell):
python $env:USERPROFILE\.claude\skills\team-builder\scripts\validate_agents.py .claude/agents/
```

```python
SCHEMA = {
    "researcher": {
        "required_sections": ["## Verdict:", "## Found:", "## Sources:"],
        "forbidden_sections": ["## Files Modified:"],  # researcher must NOT modify files
    },
    "executor": {
        "required_sections": ["## Summary:", "## Files Modified:", "## Tests Run:"],
        "forbidden_sections": [],
    },
    "validator": {
        "required_sections": ["## Verdict:", "## Issues:", "## Recommendation:"],
        "required_exact_values": {
            "## Verdict:": ["PASS", "FAIL", "PASS_WITH_WARNINGS"]
        },
    },
    "orchestrator": {
        "required_sections": ["## Summary:", "## Result:"],
        "forbidden_sections": [],
    },
}
```

**Schema keys map to actual agent names — adapt to your team:**

```python
# Generic role names in SCHEMA above are examples.
# Map your actual agent file names to their role schemas:

ROLE_MAP = {
    # actual agent name (stem of .md file) → role key in SCHEMA
    "[team-name]-researcher":  "researcher",
    "[team-name]-web-analyst": "researcher",   # multiple agents can share a role schema
    "[team-name]-worker":      "executor",
    "[team-name]-validator":   "validator",
    "[team-name]-orchestrator":"orchestrator",
}

def get_schema_for_agent(agent_name: str) -> dict | None:
    role = ROLE_MAP.get(agent_name)
    return SCHEMA.get(role) if role else None
```

**Failure taxonomy — maps to recovery action:**

| Error code | Symptom | Recovery |
|------------|---------|----------|
| `MISSING_SECTION` | Required section absent | Brief too vague → add explicit OUTPUT FORMAT |
| `WRONG_VALUE` | Section present, value not in allowed set | Add prescriptive constraint: "exactly PASS or FAIL, no other values" |
| `EMPTY_OUTPUT` | Agent returned nothing | maxTurns too low or task scope too large → split task |
| `PLACEHOLDER` | `[bracket]` found in output | Brief not filled in → replace all [brackets] |
| `YAML_PARSE` | Agent .md file unparseable | See YAML silent failures in tool-matrix.md |

---

## Tier 2: Brief Contract Tests — On Any Brief Change

**What**: invoke each agent 3× with the same test brief, verify schema valid all 3 times.
**When**: after ANY change to agent brief or system prompt.
**Cost**: 3× single agent cost (run in parallel → 1× latency).
**Pass threshold**: 3/3 schema valid. If 2/3: non-determinism issue. If 1/3: brief too vague.

> ⚠️ **Rate limit risk**: running 3 identical requests in parallel hits the same rate limit bucket.
> If on a shared account or hitting 429s, run sequentially with 5s gap between invocations.
> Parallel "1× latency" benefit only applies on accounts with sufficient RPM headroom.

```python
# Minimal test brief for any agent — adapt to your domain
TEST_BRIEF_TEMPLATE = """
Objective: [the simplest real task this agent is designed for]

Output format:
## [Required section 1]: [EXACT_VALUE or format spec]
## [Required section 2]: [structure]

Tool guidance: Use [allowlisted tools only].
Boundaries: [narrow scope — single file, single function, max 5 results]

Task ID: task_test_0001
Trace ID: trace_test_0001
"""
```

**Failure investigation — in order of probability:**

1. Schema fails all 3/3 → rewrite OUTPUT FORMAT section with exact heading names and value constraints
2. Schema fails 1-2/3 → add: "Return EXACTLY these values: PASS or FAIL — no other text in this field"
3. Schema valid but content wrong → add BOUNDARIES section with explicit "Do NOT" negative lists
4. turns_used = maxTurns on fail → task scope too large; split brief or increase maxTurns by 50%

---

## Tier 3: Single-Agent Baseline (A/B) — Once, Before First Production Use

**What**: run the same task on a single capable agent and compare quality + cost.
**When**: before first production deployment. Required to justify team overhead.
**The one question**: does the team produce materially better output than a single Sonnet?

```
SINGLE AGENT RUN:
  Model: claude-sonnet-4-6, maxTurns: 25
  Task: same real task you'd use the team for
  → Record: cost, turns, schema valid, quality score (1-5), edge cases found

TEAM RUN:
  Same task through the full team
  → Record: same metrics

COMPARISON TABLE:
| Metric            | Single Agent | Team   | Delta    |
|-------------------|-------------|--------|----------|
| Total cost        | $X          | $Y     | +N%      |
| Total latency     | Xs          | Ys     | +N%      |
| Quality score     | N/5         | N/5    | +/-      |
| Schema valid      | Y/N         | Y/N    |          |
| Issues found      | N           | N      | +/-      |

DECISION RULE:
  Quality delta < 0.5 AND cost delta > 50% → team not justified → redesign
  Quality delta ≥ 1.0 OR critical issues found by team but NOT single agent → team justified
  Record decision and rationale in a comment at top of orchestrator.md
```

---

## Tier 4: Calibration — After First 20 Real Tasks

**Why**: planning ranges from cost-reference.md have 10-100× variance. After 20 real runs you can tighten to 2-3× (p50 to p95).

**How to collect**: structured logging must be active (see production-hardening.md → Observability). After 20 runs, compute from logs:

```python
# Fill this after first 20 real runs — use actual log data, not estimates
BASELINE = {
    "[team-name]": {
        "schema_validity_rate": 0.0,   # count(schema_valid) / count(total_runs)
        "p50_cost_usd": 0.0,           # median cost per task
        "p95_cost_usd": 0.0,           # 95th percentile — use as budget ceiling
        "p50_turns_orchestrator": 0,   # median turns used by orchestrator
        "p95_turns_orchestrator": 0,
        "sample_size": 0,
        "last_updated": "YYYY-MM-DD",
        "model_ids": [],               # exact model IDs in use when baseline was collected
    }
}

ALERT_THRESHOLDS = {
    "schema_validity_min": 0.95,    # alert if drops > 5% below baseline
    "cost_p50_max_drift": 0.30,     # alert if p50 grows > 30% above baseline
    "turns_p50_max_drift": 0.25,    # alert if p50 turns grow > 25%
}
```

**Alert actions:**

| Alert | Threshold | Immediate action |
|-------|-----------|-----------------|
| Schema validity drop | < 95% of baseline | Run Tier 2 Contract Tests → find regression |
| Cost drift up | > 30% above p50 | Check: model update? brief change? task scope creep? |
| Turn drift up | > 25% above p50 | Check: maxTurns headroom exhausted? retry loops? |
| Schema validity 0% | Catastrophic | STOP all production use → debug from checkpoint logs |

---

## Testing Cadence by Change Type

| Change type | T1 Schema | T2 Contract | T3 A/B | T4 Calibration |
|-------------|-----------|-------------|--------|----------------|
| Any .md file edit | ✓ required | — | — | — |
| Brief / system prompt change | ✓ required | ✓ required | — | — |
| Model ID update | ✓ required | ✓ required | ✓ recommended | Reset baseline |
| New agent added | ✓ required | ✓ for new agent | — | — |
| Structural schema change | ✓ required | ✓ required | — | Reset baseline |
| First production deployment | ✓ required | ✓ required | ✓ required | Start collecting |
| Weekly cadence | ✓ | — | — | Update if ≥ 20 new runs |

---

## Chaos Testing — Resilience Verification

**What**: deliberately induce failure conditions to verify circuit breaker, graceful degradation, and security response.
**When**: before first production deployment + after any change to orchestrator circuit breaker logic.
**Cost**: 3–10× a normal team run. Run once; repeat only when orchestrator logic changes.

| Scenario | How to inject | Expected behavior | Pass criteria |
|----------|--------------|-------------------|---------------|
| CRITICAL agent schema fail (×2) | Brief with wrong output format constraint | Pipeline stops cleanly | PARTIAL_RESULT with FAILED_[agent] marker |
| OPTIONAL agent empty output | Return empty string from agent | Pipeline continues with warning | `[WARNING: [agent] unavailable]` in output |
| maxTurns exhaustion | Task requiring 3× more turns than limit | Agent stops, missing sections | Circuit breaker activates (not crash) |
| Thundering herd (5 agents × 2K tokens) | Brief producing verbose output | Orchestrator synthesizes without overflow | Valid synthesis output, no "Found nothing" |
| Prompt injection in researcher output | Include "Ignore previous instructions" in researcher's mock output | Orchestrator blocks forwarding | SECURITY ALERT logged |
| Rate limit (429) | Launch 8+ parallel agents simultaneously | Retry or RATE_LIMITED status | No unhandled exception, task resumes or reports cleanly |

**Minimal chaos test (Python)**:
```python
def test_circuit_breaker_activates(orchestrator_id: str) -> None:
    """Verify PARTIAL_RESULT returned when CRITICAL agent schema fails."""
    # Brief that forces agent to produce wrong output format
    chaos_brief = """
Objective: test circuit breaker
Output format:
## WrongSection:    ← intentionally wrong
## AlsoWrong:
"""
    result = run_team(chaos_brief, task_id="task_chaos_001")

    assert "PARTIAL_RESULT" in result["output"] or "FAILED_" in result["output"], \
        f"Circuit breaker did not activate. Got status: {result['status']}"
    assert result["status"] != "COMPLETED", \
        "Team reported COMPLETED despite schema failure"
    print("PASS: circuit breaker activates on schema failure")
```

**Chaos testing cadence**:
- Before first production deployment: run full chaos matrix
- After modifying circuit breaker logic in orchestrator: re-run full matrix
- After adding a new CRITICAL agent: test that its failure activates circuit breaker
- After a production incident: add the scenario that would have caught it

---

## CI/CD Integration — Automate Tier 1 Schema Tests

Tier 1 Schema Tests (static, no LLM, < 5 seconds) should run in CI/CD on every PR touching `.claude/agents/`.

**GitHub Actions**:
```yaml
# .github/workflows/agent-schema-check.yml
name: Agent Schema Validation
on:
  pull_request:
    paths:
      - '.claude/agents/**'
jobs:
  validate-agents:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Validate agent schemas
        run: |
          python ~/.claude/skills/team-builder/scripts/validate_agents.py .claude/agents/
          # Exit code 1 on any FAIL — blocks PR automatically
```

> Windows runner: replace `~/.claude/...` with `$env:USERPROFILE\.claude\...` in a PowerShell step.

**What CI/CD catches vs what it doesn't**:

| Caught by CI/CD (Tier 1) | NOT caught by CI/CD |
|--------------------------|---------------------|
| YAML parse errors | Semantic correctness |
| Missing required sections | Schema validity on real tasks (need Tier 2) |
| Wrong exact values in fields | Cost drift (need Tier 4 production logs) |
| `effort` not a valid string | Behavior changes from model updates |
| `maxTurns` as string instead of integer | Orchestrator logic regressions |

CI/CD enforces structural correctness; Tier 2 Contract Tests enforce behavioral contract.

---

## Common Eval Mistakes

- **Schema validity = correctness**: schema tests check structure, not semantics. An agent can return all required sections with wrong content and still pass Tier 1.
- **Single run as proof**: one successful run proves nothing for non-deterministic systems. Minimum 3 for contract tests, 20 for calibration.
- **Calibrating on test tasks**: calibration must use real production tasks at real complexity. Synthetic test briefs are too short and produce artificially low cost estimates.
- **Resetting baseline without reason**: baseline should only reset intentionally (model update, schema change). Accidental reset hides regressions.
- **Skipping A/B baseline**: without a comparison point you cannot quantify the overhead-to-quality tradeoff.
