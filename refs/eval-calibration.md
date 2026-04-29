# Evaluation Calibration Protocol

> **Purpose**: Detect and correct systematic bias in LLM-as-Judge evaluation used by LEAN,
> EVALUATE Phase 3, and A/B BENCHMARK — producing calibrated, uncertainty-aware scores.
> **Load**: When S18 (multi-run statistical eval), S20 (TEE decomposition), or EVALUATE Phase 4
> Behavioral Verifier of `claude/skill-writer.md` is accessed.
> **Main doc**: `claude/skill-writer.md §8 (EVALUATE), §9 (OPTIMIZE)`
> **Research basis**:
>   - Bose et al. 2026, *"Hidden Measurement Error in LLM Evaluation Pipelines"*
>     (arXiv:2604.11581, April 2026). Introduces Total Evaluation Error (TEE) decomposition.
>   - Huang et al. 2025, *"LLM-as-Judge Bias in Communication Systems"*
>     (arXiv:2510.12462, October 2025). Regression-based calibration, 1.2% max error.
>   - Zhang et al. 2025, *"Evaluating Scoring Bias in LLM-as-a-Judge"*
>     (arXiv:2506.22316, June 2025). Agreeableness bias identified as dominant failure.
>   - LM-Polygraph UQ Benchmark (MIT TACL 2025). Calibrated confidence scores for LLM eval.
> **v3.6.0**: New companion file for S20 strategy and EVALUATE Phase 4 calibration advisory.

---

## §1  Why Calibration Matters

The LEAN 500-pt and EVALUATE 1000-pt pipelines rely on LLM judges for Phases 2 and 3.
Without calibration, two systematic biases inflate apparent skill quality:

### 1.1  Agreeableness Bias (dominant failure mode)

An LLM judge that always finds skills "mostly good" exhibits:
- **True Positive Rate (TPR) > 96%**: Almost all genuinely good skills score high ✓
- **True Negative Rate (TNR) < 25%**: Most genuinely bad skills also score high ✗

**Effect**: A FAIL-tier skill may be scored BRONZE (700–800/1000) by an
agreeableness-biased judge. Your EVALUATE report shows "BRONZE" — the skill is actually
unusable. This is the most common form of "phantom GOLD" (see anti-patterns G1–G2).

**Detection signal**: If LEAN Phase 3 scores are consistently 380–400/400 (near ceiling)
across multiple independent runs, agreeableness bias is likely.

### 1.2  Total Evaluation Error (TEE)

TEE decomposes evaluation variance into two components:

```
TEE = Systematic Bias (reducible) + Random Variance (partially irreducible)

Systematic Bias:
  - Prompt framing: judge scores differently based on how the question is phrased
  - Position bias: judge favors the first or last option in comparisons
  - Agreeableness bias: judge rates all outputs high regardless of quality
  - Self-consistency bias: generator inflates scores for its own outputs

Random Variance:
  - Temperature sampling: different outputs from same prompt on re-run
  - Context-window truncation: long skills scored differently when truncated
  - Model version drift: API weights may change between invocations
```

**Evidence (arXiv:2604.11581)**: Minor prompt perturbations shifted MMLU rankings
by up to 8 positions. Removing just 10 of 60K Chatbot Arena preferences flipped the
top model. Point estimates without uncertainty bounds are unreliable near tier boundaries.

---

## §2  Calibration Protocol

### §2.1  Step 1 — Agreeableness Bias Detection

**When to run**: Before certifying any skill at GOLD (≥900) or PLATINUM (≥950) tier.

```
AGREEABLENESS CHECK:
  1. Create 3 "known-FAIL" calibration skills:
     - A skill with only §1 Identity (missing all other required sections)
     - A skill with placeholder tokens: {{SKILL_NAME}}, {{TODO}}
     - A skill with no trigger phrases and no examples

  2. Run LEAN on each calibration skill.
     Expected result: all three should score < 350/500 (FAIL tier).

  3. Evaluate agreeableness:
     IF any calibration skill scores ≥ 400/500:
       → Agreeableness bias CONFIRMED
       → Apply calibration discount (§2.2)
       → Flag in evaluation report: "agreeableness_bias: true"

     IF all calibration skills score < 350:
       → Bias within normal range
       → Proceed with standard certification
```

### §2.2  Calibration Discount Calculation

When agreeableness bias is confirmed:

```python
# Regression-based calibration (after arXiv:2510.12462)
# Uses a small calibration set of known-outcome skills

def calibrated_score(raw_score: int, calibration_skills: list[dict]) -> dict:
    """
    raw_score: the uncalibrated LEAN or EVALUATE score
    calibration_skills: list of {expected_outcome: 'PASS'|'FAIL', actual_score: int}

    Returns: {calibrated_score, confidence_interval, discount_factor, agreeableness_flag}
    """
    # Count false positives: FAIL skills that scored ≥ threshold
    threshold = 350  # LEAN PASS threshold (500-pt scale)
    fail_skills = [s for s in calibration_skills if s['expected_outcome'] == 'FAIL']
    false_positives = [s for s in fail_skills if s['actual_score'] >= threshold]

    false_positive_rate = len(false_positives) / len(fail_skills) if fail_skills else 0.0

    # Apply discount
    discount_factor = false_positive_rate * 0.15  # scale factor from arXiv:2510.12462
    calibrated = int(raw_score * (1.0 - discount_factor))

    return {
        "raw_score": raw_score,
        "calibrated_score": calibrated,
        "discount_factor": round(discount_factor, 3),
        "agreeableness_bias_rate": round(false_positive_rate, 3),
        "calibration_sample_size": len(fail_skills)
    }
```

**Example**:
```
Calibration set: 5 known-FAIL skills
False positives (scored ≥ 350): 3/5 → false_positive_rate = 0.60
Discount factor: 0.60 × 0.15 = 0.09 (9%)
Raw EVALUATE score: 920 → Calibrated score: 920 × 0.91 = 837
Tier: raw = GOLD; calibrated = SILVER → USE CALIBRATED TIER
```

### §2.3  Dimension Confidence Intervals (TEE)

For each of the 7 LEAN dimensions, compute a confidence interval from N independent runs:

```
DIMENSION CI PROTOCOL (run after S18 multi-run eval with --tee flag):

For each dimension D in {D1..D7}:
  scores_D = [run1_D, run2_D, ..., runN_D]
  mean_D = avg(scores_D)
  stddev_D = std(scores_D)
  cv_D = stddev_D / mean_D   # coefficient of variation
  ci_D = (mean_D - 1.96 × stddev_D, mean_D + 1.96 × stddev_D)  # 95% CI

Classify each dimension:
  cv < 0.03  → STABLE   (reliable signal; use mean as score)
  0.03–0.07  → MODERATE (use mean; note uncertainty in report)
  > 0.07     → NOISY    (dimension improvement needed before certification)
```

**Typical dimension stability** (empirically observed):

| Dimension | Typical CV | Why |
|-----------|-----------|-----|
| D6 Security | 0.01–0.02 | Pattern-based; deterministic |
| D7 Metadata | 0.01–0.03 | YAML structure; mostly deterministic |
| D1 System Design | 0.02–0.04 | Structured section check |
| D4 Error Handling | 0.03–0.06 | Some judgment on recovery path quality |
| D5 Examples | 0.03–0.06 | Realism judgment varies |
| D2 Domain Knowledge | 0.04–0.08 | Subjective depth assessment |
| D3 Workflow | 0.05–0.10 | Most affected by prompt framing |

---

## §3  Calibrated Certification Flow

Replace the standard EVALUATE Phase 4 certification with the calibrated version
when targeting GOLD or PLATINUM:

```
CALIBRATED CERTIFICATION (for GOLD / PLATINUM target):

1. Run S18 (3–5 independent EVALUATE passes) → scores: [s1, s2, ..., sN]
2. Compute: median_score, score_ci = (min, max), per-dimension CV
3. Run §2.1 agreeableness check (3 known-FAIL calibration skills)
4. IF agreeableness_bias confirmed:
     → Apply §2.2 discount to median_score → calibrated_score
     → Use calibrated_score for tier assignment
   ELSE:
     → Use median_score directly
5. Flag borderline cases: if calibrated_score within 30 pts of a tier boundary:
     → Run 1 additional S18 pass
     → Use conservative tier (lower one) if ambiguous
6. Record calibration metadata in skill YAML:
     evaluation_calibration:
       runs: N
       raw_median: X
       agreeableness_bias: true/false
       discount_factor: 0.0–0.15
       calibrated_score: Y
       cv_max_dimension: "D3 workflow"
       cv_max_value: 0.08
       certified_tier: SILVER  # use calibrated tier here
```

---

## §4  Calibration Output Format

When S20 (TEE decomposition) runs, append to `multi-eval-report.json`:

```json
"calibration": {
  "agreeableness_bias_detected": false,
  "false_positive_rate": 0.0,
  "discount_factor": 0.0,
  "raw_median_score": 847,
  "calibrated_score": 847,
  "tier_raw": "SILVER",
  "tier_calibrated": "SILVER",
  "tier_changed": false,
  "dimension_cv": {
    "systemDesign": 0.022,
    "domainKnowledge": 0.058,
    "workflow": 0.082,
    "errorHandling": 0.034,
    "examples": 0.041,
    "security": 0.011,
    "metadata": 0.019
  },
  "noisy_dimensions": ["workflow"],
  "stable_dimensions": ["security", "metadata", "systemDesign"],
  "tee_verdict": "MODERATE_VARIANCE",
  "recommendation": "Workflow (D3) CV=0.082 is noisy. Apply S4 (workflow definition) before re-certifying. All other dimensions are stable."
}
```

---

## §5  When to Apply Calibration

| Situation | Action |
|-----------|--------|
| Targeting GOLD (≥900) or PLATINUM (≥950) | Always run §2.1 agreeableness check |
| Phase 3 scores near ceiling (>95% of max) on all runs | Agreeableness bias likely; run §2.1 |
| Any dimension CV > 0.07 after S18 | Apply §2.3 CI; fix noisy dim before certifying |
| A/B benchmark delta near 0.15 threshold | Run S20; confirm delta is above noise floor |
| Score changes > 30 pts between two S18 runs | TEE variance is high; fix D3 before certifying |
| Certifying for production / team use | Always run full calibration (§2.1 + §2.3) |
| Quick development iteration | Skip calibration; use raw LEAN score |

---

## §6  Common Calibration Pitfalls

### P1 — Using calibration without enough samples

**Wrong**: "I ran calibration on 1 known-FAIL skill."
**Right**: Use at least 3 known-FAIL skills for the false-positive rate estimate.
With N=1, the estimate is 0 or 1 (binary) — too noisy for useful calibration.

### P2 — Applying discount to every skill indiscriminately

**Wrong**: "I always apply a 9% discount."
**Right**: Compute the discount from fresh calibration skills each time.
Agreeableness bias varies by model version, prompt phrasing, and skill domain.

### P3 — Treating calibration as a content fix

**Wrong**: "My skill has agreeableness bias — I'll calibrate it down and publish."
**Right**: Calibration reveals inflation; it does NOT improve the skill. 
Fix the content (S1–S19), re-evaluate, then re-calibrate for certification.

### P4 — Ignoring borderline tiers

**Wrong**: "Calibrated score is 901 → GOLD. Done."
**Right**: 901 is within 9 pts of the GOLD boundary (900). Run 1 more S18 pass.
If the new pass shows 887 → conservative tier = SILVER. Use SILVER.
