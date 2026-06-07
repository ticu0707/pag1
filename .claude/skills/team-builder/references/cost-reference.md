# Cost Reference — Pricing, Ranges, Caching, Batch API

---

## Model Pricing (Anthropic, 2026)

| Model | Input $/1M | Output $/1M | Cache Read $/1M | Context max |
|-------|------------|-------------|-----------------|-------------|
| Claude Opus 4.8 | $5.00 | $25.00 | $0.50 | 1M tokens |
| Claude Sonnet 4.6 | $3.00 | $15.00 | $0.30 | 1M tokens |
| Claude Haiku 4.5 | $1.00 | $5.00 | $0.10 | 200K tokens |

---

## Cost Ranges Per Agent

| Agent | Model | Simple task | Medium task | Complex task |
|-------|-------|-------------|-------------|--------------|
| Researcher | Haiku | $0.005–$0.015 | $0.015–$0.06 | $0.06–$0.15 |
| Worker | Sonnet | $0.04–$0.12 | $0.12–$0.40 | $0.40–$1.20 |
| Validator | Sonnet | $0.02–$0.06 | $0.06–$0.20 | $0.20–$0.50 |
| Orchestrator (Sonnet, **default**) | Sonnet | $0.02–$0.09 | $0.09–$0.27 | $0.27–$0.90 |
| Orchestrator (Opus, escalated) | Opus | $0.04–$0.15 | $0.15–$0.45 | $0.45–$1.50 |

> Escalate orchestrator to Opus only when criteria apply (see `references/tool-matrix.md` → Model Escalation Criteria).
> Opus vs Sonnet orchestrator = +$0.02–$0.60 per task depending on complexity.

**Warning**: actual cost varies 10-100× from any point estimate. Always use ranges.

---

## Cost Ranges Per Team Configuration

| Configuration | Simple | Medium | Complex |
|---------------|--------|--------|---------|
| 1 Orchestrator + 1 Worker | $0.08–$0.27 | $0.27–$0.85 | $0.85–$2.70 |
| Standard (Orch + 2 Researcher + 1 Worker + 1 Validator) | $0.12–$0.40 | $0.40–$1.30 | $1.30–$4.00 |
| Research-heavy (Orch + 5 Researcher + 1 Worker + 1 Validator) | $0.18–$0.55 | $0.55–$1.80 | $1.80–$5.50 |

**Practical rule**: P50 cost > $1.00 → re-evaluate if all agents are necessary. P50 > $3.00 → restructure fundamentally.

---

## Orchestration Overhead (independent of task)

An orchestrator (Sonnet default; Opus when escalated — see tool-matrix.md) coordinating 3 agents consumes at minimum:
- 3K–8K tokens for task analysis and decomposition
- 1K–3K tokens per brief written (× number of agents)
- 2K–6K tokens for final synthesis

**Total overhead**: 7K–25K extra tokens regardless of task.
- Sonnet orchestrator overhead: **$0.02–$0.10 per task** before any agents run
- Opus orchestrator overhead: **$0.05–$0.25 per task** before any agents run

If the task can be solved by a Sonnet in 10K tokens ($0.06 total), a 3-agent team can cost 3-5× more **without producing better output**.

---

## Prompt Caching — Up to 65% Savings

> Ignored frequently. Can reduce cost by up to 90% for repeatedly-invoked agents with long prefixes.

```
How it works:
- Any prefix > 1024 tokens is eligible for caching
- Cache TTL: 5 minutes
- Cache read cost: ~10% of normal input price
- Prefix = system prompt + any static context at message start

Most valuable for:
├── Long system prompts (> 1024 tokens) invoked many times per day
│   → first invocation: normal cost; subsequent: -90% on prefix
│
├── Codebase context (repo summary) added to each brief
│   → same summary for 10 agents → cache hit for all
│
└── Standard templates (brief template, output schema)
    → fixed format → cacheable

NOT cacheable:
- Content that changes per invocation (task-specific data)
- Prefixes < 1024 tokens (below minimum threshold)
- Context that expires in < 5 minutes

Estimated savings for 5-agent team invoked 100×/day:
- Without caching: 100 × $0.40 = $40/day
- With caching on system prompts (~70% of input): ~$14/day
- Savings: ~$26/day (~65% reduction)
```

**To enable caching**: structure your system prompt so the static portion comes first (> 1024 tokens), followed by the dynamic/task-specific portion. The SDK handles the rest automatically.

---

## Batch API — 50% Cost Reduction for Non-Real-Time Tasks

```
When to use:
- Tasks that don't need immediate response (< 24h acceptable)
- Bulk processing: hundreds of files, documents, items
- Research, analysis, content generation at volume

How it works:
- Submit a batch of requests in one API call
- Anthropic processes asynchronously, returns all results
- Cost: 50% vs standard API

Python implementation:
batch = client.messages.batches.create(
    requests=[
        {"custom_id": "task-001", "params": {...}},
        {"custom_id": "task-002", "params": {...}},
    ]
)
# poll for results or webhook when ready

DO NOT use Batch API for:
- Agents requiring interactivity (Sequential Pattern B with feedback)
- Tasks with latency SLA < 5 minutes
- Pipelines where step N depends on step N-1 in real-time
```

---

## Calibration Methodology — From 10-100× Variance to 2-3×

Planning ranges in this file have 10-100× variance — useful for go/no-go decisions, not for budgeting.
After first 20 real runs, tighten to p50/p95 from structured logs.

**Step 1: Enable structured logging** (see `production-hardening.md` → Structured JSON Logging).
Required fields: `cost_usd`, `turns_used`, `output_schema_valid`, `task_id`.

**Step 2: Collect 20 real production runs.**
Must be real tasks at real complexity — synthetic test briefs produce artificially low estimates.
20 is the minimum for statistical stability (p95 from < 20 runs is unreliable).

**Step 3: Compute calibrated ranges.**

```python
import statistics

def calibrate(cost_samples: list[float]) -> dict:
    sorted_samples = sorted(cost_samples)
    p95_index = int(len(sorted_samples) * 0.95)
    return {
        "p50": statistics.median(sorted_samples),           # planning estimate
        "p95": sorted_samples[p95_index],                   # budget ceiling
        "sample_size": len(sorted_samples),
        "variance_ratio": sorted_samples[-1] / sorted_samples[0],  # target: < 3×
    }
```

**Step 4: Update BASELINE in evals file.**
Replace `p50_cost_usd: 0.0` and `p95_cost_usd: 0.0` with computed values.
Use **p95 as budget ceiling**, not p50 and not the pre-calibration range.

**Before calibration**: `$X–$Y (pre-calibration estimate, ±10×)`
**After calibration**: `$[p50] median, $[p95] ceiling (calibrated, N=[sample_size] runs)`

**Re-run calibration when**:
- Any model ID changed
- Brief or system prompt structurally changed
- 6+ months since last calibration
- Observed cost drifts > 30% above current p50

---

## Production Cost Controls

**1. `maxTurns`** — most effective control, always set conservatively

**2. `effort` in YAML**:

| Level | Approx. cost vs `high` | Recommended for |
|-------|------------------------|-----------------|
| `low` | ~0.4–0.6× | Haiku: filtering, classification, simple extraction |
| `medium` | ~0.7–0.85× | Validators, simple summarization |
| `high` (default) | 1× | Standard workers, orchestrators |
| `xhigh` (Opus 4.7/4.8) | ~1.3–1.8× | Complex coding, agentic synthesis |
| `max` (Opus 4.6+) | ~2–3× | Correctness > cost; irreversible actions |

Recommended defaults per role:
- Haiku researcher: `effort: low` (filtering) or `medium` (deep analysis)
- Sonnet worker: `effort: high` (default — omit field to use default)
- Sonnet validator: `effort: medium` (sufficient for verification)
- Opus orchestrator: `effort: xhigh` (primary reason to use Opus)

> Multipliers are approximate — calibrate with Tier 4 after 20 real runs.

**3. `task_budget` (Opus 4.7/4.8 beta — beta header: `task-budgets-2026-03-13`)**:

Unlike `max_tokens` (enforced ceiling the model is NOT aware of), `task_budget` is a soft ceiling the model IS aware of — it sees a running countdown and self-moderates.

| Team size | Recommended `task_budget` |
|-----------|--------------------------|
| 3-agent, simple tasks | 30,000 tokens |
| 5-agent, medium tasks | 60,000 tokens |
| 8-agent, complex tasks | 120,000 tokens |

```python
session = client.beta.agents.sessions.create(
    agent_id=ORCHESTRATOR_ID,
    output_config={"task_budget": {"type": "tokens", "total": 60000}},
    extra_headers={"anthropic-beta": "task-budgets-2026-03-13"},
)
```

Without `task_budget`, a stuck retry loop can consume 500K+ tokens before hitting `max_tokens`.
Always set for Opus 4.7/4.8 orchestrators on automated pipelines.

**4. Model selection heuristic**:
```
Haiku if: repetitive task, high volume, error is recoverable
Sonnet if: medium reasoning required, standard implementation
Opus if: strategic coordination, high-impact decision, complex synthesis
```

**5. Simple in-prompt cost alerting**:
```
Add to orchestrator:
"After each agent, estimate cost:
- Haiku researcher: ~$0.002 × turns_used
- Sonnet worker: ~$0.01 × turns_used
- Opus orchestrator: ~$0.015 × turns_used
If cumulative estimated cost > $[threshold]: stop pipeline and report COST_LIMIT_REACHED"
```
