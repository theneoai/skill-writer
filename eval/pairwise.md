# Pairwise Skill Ranking

> **Purpose**: Bradley-Terry comparative ranking for evaluating multiple skills against each other.
> **Load**: When EVALUATE mode includes pairwise ranking request.
> **Main doc**: `claude/skill-framework.md §8`

---

## §1  When to Use Pairwise Ranking

Pairwise ranking answers the question: **"Which of these skills is best?"** when
absolute scores alone are insufficient (e.g. two skills both achieve GOLD, but you
need to pick one).

**Use cases**:
- Comparing multiple candidate skills for the same purpose
- Selecting the best skill after multiple OPTIMIZE cycles
- Benchmarking a new skill against existing production skills

**Input**: 2 to N skill files.
**Output**: Ranked list with Bradley-Terry β scores and confidence intervals.

---

## §2  Bradley-Terry Model

### Overview

The Bradley-Terry model assigns a strength parameter β_i to each skill i.
For a pair (i, j), the probability that skill i beats skill j is:

```
P(i beats j) = β_i / (β_i + β_j)
           = 1 / (1 + exp(β_j - β_i))    # logistic form
```

Higher β = stronger skill. After fitting, skills are ranked by β.

### Parameter Estimation

```python
def bradley_terry_estimate(wins: dict, max_iter: int = 100,
                           convergence_delta: float = 0.0001) -> dict:
    """
    wins[i][j] = number of times skill i beat skill j
    Returns: {skill_id: beta_score}
    """
    skills = list(set(wins.keys()))
    beta = {s: 1.0 for s in skills}       # initialize all to 1.0

    for iteration in range(max_iter):
        beta_prev = beta.copy()

        for i in skills:
            numerator = sum(wins[i].get(j, 0) for j in skills if j != i)
            denominator = sum(
                (wins[i].get(j, 0) + wins[j].get(i, 0)) / (beta[i] + beta[j])
                for j in skills if j != i
            )
            if denominator > 0:
                beta[i] = numerator / denominator

        # Normalize: set geometric mean = 1
        geo_mean = (product(beta.values())) ** (1 / len(beta))
        beta = {s: v / geo_mean for s, v in beta.items()}

        # Convergence check
        max_delta = max(abs(beta[s] - beta_prev[s]) for s in skills)
        if max_delta < convergence_delta:
            break

    return beta
```

**Convergence**: Typically < 50 iterations. Hard stop at `max_iter=100`.
Delta threshold: `0.0001` (on normalized β scale).

---

## §3  Comparison Protocol

### Setting Up Comparisons

For N skills, perform **N(N-1)/2** pairwise comparisons.

```
3 skills → 3 comparisons: (A,B), (A,C), (B,C)
4 skills → 6 comparisons
5 skills → 10 comparisons
```

For large N (> 6 skills), use random sampling: each skill participates in at least
`min(N-1, 5)` comparisons.

### Position Bias Elimination

LLMs exhibit position bias — the skill presented first tends to score higher.
**Mitigate by swapping order for every pair**:

```
Round 1: Compare (skill_A first, skill_B second) → record winner
Round 2: Compare (skill_B first, skill_A second) → record winner

wins[A][B] = round1_winner==A + round2_winner==A
wins[B][A] = round1_winner==B + round2_winner==B
```

This means each pair has 2 comparisons minimum. For high-stakes rankings, use 4
comparisons per pair (2 forward, 2 reverse) and average.

### Comparison Prompt Template

```
You are comparing two AI skill definitions. Evaluate which one is better overall
based on: (1) clarity and completeness, (2) trigger accuracy potential,
(3) security baseline, (4) practical usefulness.

SKILL A:
<skill_a_content>

SKILL B:
<skill_b_content>

Which skill is better? Answer ONLY with "A" or "B" and one sentence of reasoning.
```

**LLM role**: All three LLMs (LLM-1, LLM-2, LLM-3) run the comparison independently.
Winner = majority vote of 3. Ties: LLM-3 (Arbiter) decides.

---

## §4  Ranking Output

### Ranking Table

```
PAIRWISE RANKING RESULTS
========================
Skills compared: N
Total comparisons: N(N-1)/2 × 2 (position-swapped)

Rank | Skill Name      | Version | β Score | Win Rate | Tier
-----|-----------------|---------|---------|----------|-------
  1  | weather-query   | 2.1.0   | 3.42    | 85%      | GOLD
  2  | data-processor  | 1.3.0   | 1.87    | 67%      | GOLD
  3  | sql-query-skill | 1.0.0   | 0.91    | 45%      | SILVER
  4  | log-analyzer    | 1.1.0   | 0.38    | 30%      | BRONZE
```

**Win Rate**: % of pairwise comparisons this skill won.
**β Score**: Bradley-Terry strength parameter (higher = stronger).

### Confidence Intervals

```python
def compute_confidence_interval(beta: float, n_comparisons: int,
                                 confidence: float = 0.95) -> tuple:
    """
    Approximate CI using standard error of log-beta.
    """
    import math
    z = 1.96  # 95% CI
    se = 1 / math.sqrt(n_comparisons)
    log_beta = math.log(beta)
    return (math.exp(log_beta - z*se), math.exp(log_beta + z*se))
```

### Pairwise Matrix

```
           | weather | data-proc | sql-query | log-anal |
-----------|---------|-----------|-----------|----------|
weather    |    —    |   2W/0L   |   2W/0L   |  2W/0L   |
data-proc  |  0W/2L  |     —     |   2W/0L   |  1W/1L   |
sql-query  |  0W/2L  |  0W/2L   |     —     |  2W/0L   |
log-anal   |  0W/2L  |  1W/1L   |  0W/2L    |    —     |
```

---

## §5  Integration with EVALUATE Mode

When EVALUATE mode receives a pairwise ranking request:

```
1. Collect all skill files to compare
2. Run individual EVALUATE on each → get tier + total_score
3. If any skill is FAIL → exclude from pairwise (note in report)
4. Run pairwise comparisons (§3) for remaining skills
5. Fit Bradley-Terry model (§2)
6. Output: combined report with absolute scores + relative ranking

Combine scores:
  composite_rank_score = 0.6 × normalized_total_score + 0.4 × normalized_beta
```

---

## §6  Pairwise Log Entry

Each pairwise run appends to `.skill-audit/pairwise.jsonl`:

```json
{
  "timestamp": "<ISO-8601>",
  "skills_compared": ["skill-a", "skill-b", "skill-c"],
  "n_comparisons": 6,
  "position_swap": true,
  "convergence_iterations": 42,
  "convergence_delta": 0.00008,
  "rankings": [
    {"rank": 1, "skill": "skill-a", "beta": 3.42, "win_rate": 0.85},
    {"rank": 2, "skill": "skill-b", "beta": 1.87, "win_rate": 0.67}
  ],
  "bias_detected": false,
  "consensus": "UNANIMOUS"
}
```
