# Convergence Detection

> **Purpose**: Three-signal convergence algorithm used to stop optimization loops early.
> **Load**: When §9 (OPTIMIZE Loop) of `claude/skill-framework.md` is accessed.
> **Main doc**: `claude/skill-framework.md §9`

---

## §1  Why Convergence Detection

The 9-step optimization loop (§9 of skill-framework.md) runs up to 20 rounds.
Without convergence detection, it wastes compute on loops where:
- Scores have stabilized (volatility check)
- All easy gains are exhausted (plateau check)
- The strategy is actively making things worse (trend check — DIVERGING)

The loop checks all three signals after every round. **Any convergence signal
triggers early stopping.**

---

## §2  Signal 1 — Volatility Check

**Purpose**: Detect when scores have stabilized (low variance across recent rounds).

**Algorithm**:
```python
def volatility_check(score_history: list[float], window: int = 10) -> bool:
    """
    Returns True (CONVERGED) if the standard deviation of the last `window`
    scores is below the threshold.
    """
    if len(score_history) < window:
        return False  # not enough data yet

    recent = score_history[-window:]
    mean = sum(recent) / len(recent)
    variance = sum((x - mean) ** 2 for x in recent) / len(recent)
    stddev = variance ** 0.5

    # Threshold: 2.0 score points (on 1000-point scale)
    return stddev < 2.0
```

**Interpretation**:
- `stddev < 2.0` → scores are essentially flat → no more gains from current strategy
- Action: **STOP loop**, declare convergence signal = `"volatility"`

---

## §3  Signal 2 — Plateau Check

**Purpose**: Detect when incremental improvements have become negligible.

**Algorithm**:
```python
def plateau_check(score_history: list[float], window: int = 10) -> bool:
    """
    Returns True (CONVERGED) if:
    - More than 70% of round-to-round deltas are below 0.5 pts
    - AND total delta over the window is ≤ 0 (not improving overall)
    """
    if len(score_history) < window:
        return False

    recent = score_history[-window:]
    deltas = [abs(recent[i] - recent[i-1]) for i in range(1, len(recent))]

    small_delta_pct = sum(1 for d in deltas if d < 0.5) / len(deltas)
    total_delta = recent[-1] - recent[0]

    return small_delta_pct > 0.70 and total_delta <= 0
```

**Interpretation**:
- Most rounds produce < 0.5-point gain AND overall trend is flat or negative
- Action: **STOP loop**, declare convergence signal = `"plateau"`

---

## §4  Signal 3 — Trend Check

**Purpose**: Detect whether the optimization trajectory is improving, stable, or diverging.

**Algorithm**:
```python
def trend_check(score_history: list[float]) -> str:
    """
    Returns "IMPROVING", "STABLE", or "DIVERGING".
    Compares the mean of the first half vs the mean of the second half.
    """
    if len(score_history) < 4:
        return "IMPROVING"  # too early to judge

    mid = len(score_history) // 2
    first_half_mean = sum(score_history[:mid]) / mid
    second_half_mean = sum(score_history[mid:]) / (len(score_history) - mid)

    delta = second_half_mean - first_half_mean

    if delta > 5.0:    # ≥5 pts improvement → IMPROVING
        return "IMPROVING"
    elif delta < -5.0: # ≥5 pts degradation → DIVERGING
        return "DIVERGING"
    else:              # within ±5 pts → STABLE
        return "STABLE"
```

**Interpretation and actions**:

| Result | Meaning | Action |
|--------|---------|--------|
| IMPROVING | Current strategy is working | Continue loop |
| STABLE | No clear improvement | Switch to different strategy or stop |
| DIVERGING | Strategy is making things worse | **HALT immediately** → HUMAN_REVIEW |

---

## §5  Combined Convergence Decision

All three signals are checked after every optimization round:

```python
def should_stop(score_history: list[float], current_round: int) -> tuple[bool, str]:
    """
    Returns (stop: bool, reason: str).
    """
    # Hard stop
    if current_round >= 20:
        return True, "max_rounds"

    # Volatility: stop if stable
    if volatility_check(score_history):
        return True, "volatility"

    # Plateau: stop if exhausted
    if plateau_check(score_history):
        return True, "plateau"

    # Trend: stop if diverging
    trend = trend_check(score_history)
    if trend == "STABLE" and current_round >= 5:
        return True, "trend_stable"
    if trend == "DIVERGING":
        return True, "trend_diverging"

    return False, "continue"
```

---

## §6  Post-Convergence Actions

| Signal | Action |
|--------|--------|
| `volatility` | Declare final score; certify at current tier; update audit |
| `plateau` | Try one final alternative strategy; if no improvement → certify |
| `trend_stable` | Certify at current tier; log "plateau reached at round N" |
| `trend_diverging` | **HALT**, roll back to best-score snapshot, escalate HUMAN_REVIEW |
| `max_rounds` | If score ≥ 700 → certify BRONZE; else → HUMAN_REVIEW |

---

## §7  Score History Format

The optimization loop maintains a score history list:

```json
{
  "skill_name": "<name>",
  "optimization_run_id": "<uuid>",
  "score_history": [684, 706, 718, 724, 729, 731, 732, 731, 732, 732],
  "dimension_history": [
    {"round": 1, "lowest_dim": "Workflow Definition", "score": 684, "delta": null},
    {"round": 2, "lowest_dim": "Workflow Definition", "score": 706, "delta": +22},
    {"round": 3, "lowest_dim": "Error Handling",      "score": 718, "delta": +12}
  ],
  "convergence_check": [
    {"round": 9,  "volatility": false, "plateau": false, "trend": "STABLE"},
    {"round": 10", "volatility": true,  "plateau": false, "trend": "STABLE",
     "decision": "STOP", "reason": "volatility"}
  ],
  "final_score": 732,
  "final_tier": "BRONZE",
  "converged_at_round": 10,
  "convergence_signal": "volatility"
}
```

---

## §8  Curation at Round 10

Every 10 rounds, the optimization loop performs a curation step to prevent context bloat:

```
CURATE (round 10, 20):
  1. Summarize all dimension changes so far: which improved, by how much
  2. Identify the top 2 strategies that produced the most delta
  3. Prune: discard individual round details, keep only summary + score_history
  4. Re-prioritize: next 10 rounds focus on top-performing strategy first
  5. Log: {"curation_round": 10, "strategies_pruned": [...], "context_reduced_by": "~40%"}
```

This prevents the LLM context window from filling up with stale round-by-round details
and keeps attention focused on the highest-leverage remaining improvements.
