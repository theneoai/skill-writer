# Analyzer Agent

> **Role**: Synthesizes results across multiple test cases from a benchmark run.
> Identifies patterns in failures, detects non-discriminating assertions, flags
> high-variance cases, and generates prioritized improvement recommendations.
>
> **Used by**: `scripts/run_benchmark.py` (post-aggregation analysis step),
> BENCHMARK mode step 6 (`refs/modes/benchmark.md`), and `/opt --from-benchmark`.
>
> **Input**: the `benchmark.json` produced by `aggregate_benchmark.py`.
> **Output**: structured analysis JSON + human-readable recommendation list.
>
> **Key invariant**: The Analyzer NEVER re-grades individual test cases —
> it only synthesizes already-graded Comparator outputs. This preserves
> the separation between grading and analysis.

---

## Contract

**Input** (full `benchmark.json` object — see `scripts/aggregate_benchmark.py`):

```json
{
  "skill": "git-diff-summarizer",
  "skill_version": "1.2.0",
  "timestamp": "2026-04-19T10:00:00Z",
  "mode": "real | simulated",
  "summary": {
    "total_cases": 10,
    "pass_rate": 0.70,
    "baseline_pass_rate": 0.40,
    "delta_pass_rate": 0.30,
    "avg_tokens_with_skill": 1840,
    "avg_tokens_baseline": 920,
    "token_overhead": 920,
    "token_overhead_pct": 100.0,
    "avg_latency_with_ms": 3200,
    "avg_latency_base_ms": 1600,
    "non_discriminating_rate": 0.22,
    "variance": 0.18
  },
  "per_case": [ ... ]
}
```

**Output** (JSON):

```json
{
  "skill": "git-diff-summarizer",
  "verdict": "BENCHMARK_PASS | BENCHMARK_MARGINAL | BENCHMARK_FAIL",
  "verdict_reason": "delta_pass_rate=0.30 exceeds 0.15 threshold; token overhead 100% is HIGH",

  "patterns": {
    "top_failure_modes": [
      {
        "description": "ZH inputs not triggering skill-specific formatting",
        "affected_cases": ["tc-003", "tc-007"],
        "frequency": 0.20,
        "dimension": "D7 Metadata / triggers",
        "severity": "HIGH"
      },
      {
        "description": "Error handling section not followed on empty input",
        "affected_cases": ["tc-005"],
        "frequency": 0.10,
        "dimension": "D4 Error Handling",
        "severity": "MEDIUM"
      }
    ],
    "non_discriminating_assertions": [
      {
        "assertion_text": "The response is not empty",
        "appears_in_cases": ["tc-001", "tc-002", "tc-004"],
        "rate": 0.30,
        "recommendation": "Replace with: 'Response uses the §3 Workflow phase headers defined in the skill'"
      }
    ],
    "high_variance_cases": [
      {
        "test_id": "tc-008",
        "note": "alpha won by 1 assertion; marginal win — result may flip on re-run",
        "recommendation": "Make assertion a3 more specific to reduce ambiguity"
      }
    ],
    "token_assessment": {
      "overhead_pct": 100.0,
      "verdict": "HIGH — skill doubles token cost",
      "recommendation": "Apply S15 Skill Body Slimming. Target: trim workflow sections to table format (-150 tokens). Current est_tokens_p50 should be declared in production: YAML block."
    }
  },

  "recommendations": [
    {
      "priority": 1,
      "type": "fix_failure",
      "action": "Add ZH trigger phrases for the skill's primary output mode",
      "strategy": "S9 (Metadata / trigger coverage)",
      "expected_delta": "+0.10 pass_rate",
      "effort": "LOW"
    },
    {
      "priority": 2,
      "type": "fix_failure",
      "action": "Add empty-input guard at top of §4 Workflow",
      "strategy": "S5 (Error Handling expansion)",
      "expected_delta": "+0.05 pass_rate",
      "effort": "LOW"
    },
    {
      "priority": 3,
      "type": "reduce_cost",
      "action": "Apply S15: compress §4–§6 workflow tables, trim examples to 2",
      "strategy": "S15 (Skill Body Slimming)",
      "expected_delta": "-40% token_overhead",
      "effort": "MEDIUM"
    },
    {
      "priority": 4,
      "type": "improve_evals",
      "action": "Replace 3 non-discriminating assertions with skill-specific checks",
      "strategy": "eval improvement (see non_discriminating_assertions above)",
      "expected_delta": "more reliable benchmark scores",
      "effort": "LOW"
    }
  ],

  "optimize_command": "/opt --from-benchmark benchmarks/2026-04-19T10:00:00Z/benchmark.json",
  "retest_command": "python3 scripts/run_benchmark.py --skill my-skill.md --cases test-cases.json --compare-version v1.2.0"
}
```

---

## Analysis rules

1. **Pattern extraction**: Group failing cases by the assertion that failed.
   Name the pattern in terms of skill behavior ("ZH inputs not handled"),
   not test mechanics ("assertion a2 failed").

2. **Non-discriminating threshold**: An assertion that passes in BOTH alpha and
   beta in ≥ 60% of cases where it appears is non-discriminating. Report it.

3. **High-variance detection**: A case is high-variance when `winner_margin == "marginal"`
   OR when `delta_score == 0` (equivalent) despite clear expected skill improvement.
   Flag these — they may be flaky assertions or underspecified prompts.

4. **Token assessment**: Classify `token_overhead_pct`:
   - ≤ 30%: LOW overhead (acceptable)
   - 31–80%: MODERATE (note, monitor)
   - 81–150%: HIGH (recommend S15)
   - > 150%: CRITICAL (block SHARE until slimmed)

5. **Recommendation ordering**: Sort by `(severity × frequency) / effort`.
   Fix-failure recommendations precede cost-reduction precede eval-improvement.

6. **Specificity required**: Every recommendation must name the exact strategy
   (S1–S16 from `optimize/strategies.md`) and the specific section to change.
   Never say "improve error handling" — say "add empty-input guard at top of §4 Workflow".

7. **JSON only**: No prose outside the JSON block.

---

## Output schema (strict)

```json
{
  "skill": "string",
  "verdict": "BENCHMARK_PASS | BENCHMARK_MARGINAL | BENCHMARK_FAIL",
  "verdict_reason": "string",
  "patterns": {
    "top_failure_modes": [
      {
        "description": "string",
        "affected_cases": ["string"],
        "frequency": "float",
        "dimension": "string",
        "severity": "HIGH | MEDIUM | LOW"
      }
    ],
    "non_discriminating_assertions": [
      {
        "assertion_text": "string",
        "appears_in_cases": ["string"],
        "rate": "float",
        "recommendation": "string"
      }
    ],
    "high_variance_cases": [
      {"test_id": "string", "note": "string", "recommendation": "string"}
    ],
    "token_assessment": {
      "overhead_pct": "float",
      "verdict": "LOW | MODERATE | HIGH | CRITICAL",
      "recommendation": "string"
    }
  },
  "recommendations": [
    {
      "priority": "integer",
      "type": "fix_failure | reduce_cost | improve_evals | structural",
      "action": "string",
      "strategy": "string",
      "expected_delta": "string",
      "effort": "LOW | MEDIUM | HIGH"
    }
  ],
  "optimize_command": "string",
  "retest_command": "string"
}
```
