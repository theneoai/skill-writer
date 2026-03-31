# EVALUATE Mode Documentation

> **Purpose**: EVALUATE mode provides a rigorous, standardized 4-phase quality assessment system for AI skills. It assigns a 1000-point score across structural, textual, runtime, and certification dimensions, enabling objective comparison and tiered certification.
> **Version**: 2.0.0
> **Last Updated**: 2026-03-31

---

## Table of Contents

1. [Overview](#overview)
2. [4-Phase Pipeline](#4-phase-pipeline)
3. [Phase 1: Parse & Validate](#phase-1-parse--validate)
4. [Phase 2: Text Quality](#phase-2-text-quality)
5. [Phase 3: Runtime Testing](#phase-3-runtime-testing)
6. [Phase 4: Certification](#phase-4-certification)
7. [Certification Tiers](#certification-tiers)
8. [Variance Analysis](#variance-analysis)
9. [Usage Examples](#usage-examples)
10. [Output Format](#output-format)
11. [Integration](#integration)

---

## Overview

EVALUATE mode is the quality assurance engine of the skill-writer. It performs comprehensive assessment of skill files against standardized criteria, producing an objective 1000-point score and certification tier.

### Key Features

- **1000-point scoring system** across 4 phases
- **6 sub-dimensions** for deep text quality analysis
- **Automated runtime testing** with benchmark scenarios
- **Variance tracking** for score stability
- **5-tier certification** (PLATINUM, GOLD, SILVER, BRONZE, FAIL)
- **Machine-readable output** for CI/CD integration

### Assessment Philosophy

```
┌─────────────────────────────────────────────────────────────────┐
│                    EVALUATION PRINCIPLES                        │
├─────────────────────────────────────────────────────────────────┤
│ • Objective: Same skill → Same score (± variance tolerance)    │
│ • Comprehensive: No quality dimension left unassessed           │
│ • Transparent: Every point is traceable to specific criteria    │
│ • Actionable: Results include specific improvement guidance     │
│ • Fast: Full evaluation completes in < 30 seconds              │
└─────────────────────────────────────────────────────────────────┘
```

---

## 4-Phase Pipeline

The evaluation pipeline processes skills through four sequential phases. Each phase has hard gates—failure at any gate terminates evaluation with a FAIL tier.

```
┌─────────────────────────────────────────────────────────────────┐
│                         SKILL INPUT                             │
│                    (Markdown file path)                         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ PHASE 1: PARSE & VALIDATE (100 pts)                             │
│ ├─ YAML frontmatter syntax check                                │
│ ├─ Required section presence (§1, §2, §3...)                    │
│ ├─ Markdown structure validation                                │
│ └─ External reference resolution                                │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ PHASE 2: TEXT QUALITY (300 pts)                                 │
│ ├─ System Design (50 pts)                                       │
│ ├─ Domain Knowledge (50 pts)                                    │
│ ├─ Workflow Definition (50 pts)                                 │
│ ├─ Error Handling (50 pts)                                      │
│ ├─ Examples (50 pts)                                            │
│ └─ Metadata (50 pts)                                            │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ PHASE 3: RUNTIME TESTING (400 pts)                              │
│ ├─ Benchmark scenario execution                                 │
│ ├─ Performance measurement                                      │
│ ├─ Edge case handling                                           │
│ └─ Security validation                                          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ PHASE 4: CERTIFICATION (200 pts)                                │
│ ├─ Human review checkpoint                                      │
│ ├─ Final quality gates                                          │
│ ├─ Variance analysis                                            │
│ └─ Tier assignment                                              │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      EVALUATION OUTPUT                          │
│              (Score, Tier, Report, Recommendations)             │
└─────────────────────────────────────────────────────────────────┘
```

### Phase Gates Summary

| Phase | Max Points | Gate Condition | Failure Action |
|-------|-----------|----------------|----------------|
| Parse & Validate | 100 | YAML valid + all required sections present | FAIL tier, abort |
| Text Quality | 300 | All 6 sub-dimensions scored | Continue with penalty |
| Runtime Testing | 400 | All benchmarks execute without crash | FAIL tier if crash |
| Certification | 200 | Variance < threshold + human sign-off | Degrade tier |

---

## Phase 1: Parse & Validate

**Maximum Points**: 100  
**Purpose**: Ensure the skill file is structurally sound and machine-readable.

### 1.1 YAML Frontmatter Validation (30 pts)

Validates the YAML metadata block at the start of the skill file.

| Check | Points | Description |
|-------|--------|-------------|
| Valid YAML syntax | 10 | Parses without errors |
| Required fields present | 10 | `name`, `version`, `description` |
| Type compliance | 10 | Fields match expected types |

**Required Fields:**
```yaml
name: string           # Skill identifier
version: string        # Semantic version (e.g., "1.0.0")
description: string    # Human-readable purpose
type: enum             # api-integration | data-pipeline | workflow-automation | base
```

**Scoring:**
- 30/30: All checks pass
- 20/30: One check fails
- 10/30: Two checks fail
- 0/30: YAML unparseable → **ABORT**

### 1.2 Section Presence Validation (40 pts)

Verifies all required sections exist with proper headers.

| Section | Points | Purpose |
|---------|--------|---------|
| §1 Identity | 10 | Name, role, purpose, red lines |
| §2+ Modes | 10 | At least one mode definition |
| §N Security | 10 | Security baseline section |
| §N Examples | 10 | Minimum 2 usage examples |

**Scoring:**
- 40/40: All sections present
- 30/40: One section missing
- 20/40: Two sections missing
- 0/40: Three+ sections missing → **ABORT**

### 1.3 Markdown Structure Validation (20 pts)

Checks for well-formed Markdown.

| Check | Points | Description |
|-------|--------|-------------|
| Valid header hierarchy | 5 | No skipped levels (## → ####) |
| Closed code blocks | 5 | All ``` have matching close |
| Valid table syntax | 5 | Tables are parseable |
| Link integrity | 5 | No broken internal links |

### 1.4 External Reference Resolution (10 pts)

Validates that referenced files exist.

| Check | Points | Description |
|-------|--------|-------------|
| Template references | 5 | Referenced templates exist |
| Security patterns | 5 | CWE patterns file accessible |

---

## Phase 2: Text Quality

**Maximum Points**: 300  
**Purpose**: Deep analysis of skill content quality across 6 sub-dimensions.

Each sub-dimension is scored 0-50 points based on specific criteria.

### 2.1 System Design (50 pts)

Evaluates architectural clarity and design pattern usage.

| Criterion | Weight | Description |
|-----------|--------|-------------|
| Clear boundaries | 15% | Components have well-defined interfaces |
| Single responsibility | 15% | Each component does one thing |
| Design patterns | 10% | Appropriate patterns (Factory, Strategy, etc.) |
| Scalability notes | 10% | Addresses performance at scale |

**Scoring Rubric:**
- 45-50: Excellent design, clear architecture, proper patterns
- 35-44: Good design, minor boundary issues
- 25-34: Adequate design, some responsibilities unclear
- 15-24: Poor design, mixed responsibilities
- 0-14: No discernible architecture

### 2.2 Domain Knowledge (50 pts)

Assesses depth of domain expertise demonstrated.

| Criterion | Weight | Description |
|-----------|--------|-------------|
| Terminology accuracy | 20% | Correct domain terms used |
| Best practices | 15% | Industry standards referenced |
| Edge cases covered | 15% | Domain-specific edge cases addressed |

**Scoring Rubric:**
- 45-50: Expert-level knowledge, comprehensive coverage
- 35-44: Solid knowledge, minor gaps
- 25-34: Basic knowledge, some inaccuracies
- 15-24: Limited knowledge, notable gaps
- 0-14: Incorrect or missing domain knowledge

### 2.3 Workflow Definition (50 pts)

Evaluates clarity and completeness of workflow descriptions.

| Criterion | Weight | Description |
|-----------|--------|-------------|
| Step sequence | 20% | Clear, ordered steps |
| Decision points | 15% | Branches and conditions documented |
| State transitions | 15% | How state changes between steps |

**Scoring Rubric:**
- 45-50: Crystal clear workflow, all paths documented
- 35-44: Good workflow, minor path gaps
- 25-34: Adequate workflow, some ambiguity
- 15-24: Unclear workflow, missing steps
- 0-14: No coherent workflow defined

### 2.4 Error Handling (50 pts)

Assesses robustness of error handling strategy.

| Criterion | Weight | Description |
|-----------|--------|-------------|
| Error categories | 20% | Input, runtime, external errors covered |
| Recovery strategies | 15% | How to recover from each error |
| User messages | 15% | Clear, actionable error messages |

**Scoring Rubric:**
- 45-50: Comprehensive handling, all cases covered
- 35-44: Good coverage, minor gaps
- 25-34: Basic handling, some cases missing
- 15-24: Limited handling, major gaps
- 0-14: No error handling described

### 2.5 Examples (50 pts)

Evaluates quality and completeness of usage examples.

| Criterion | Weight | Description |
|-----------|--------|-------------|
| Quantity | 15% | Minimum 2, bonus for 4+ |
| Coverage | 20% | Examples cover happy path + edge cases |
| Clarity | 15% | Easy to understand and follow |

**Scoring Rubric:**
- 45-50: Excellent examples, comprehensive coverage
- 35-44: Good examples, minor gaps
- 25-34: Adequate examples (2+), basic coverage
- 15-24: Poor examples, unclear or insufficient
- 0-14: No examples or single example → **-25 penalty**

### 2.6 Metadata (50 pts)

Assesses completeness and accuracy of metadata.

| Criterion | Weight | Description |
|-----------|--------|-------------|
| Versioning | 15% | Semantic versioning, changelog |
| Authorship | 10% | Author, license, created/updated dates |
| Tags | 10% | Relevant, comprehensive tags |
| Interface spec | 15% | Clear input/output definitions |

**Scoring Rubric:**
- 45-50: Complete metadata, all fields accurate
- 35-44: Good metadata, minor omissions
- 25-34: Adequate metadata, some fields missing
- 15-24: Poor metadata, major omissions
- 0-14: Minimal or incorrect metadata

### Text Quality Scoring Formula

```
Text Quality Score = Σ(sub_dimension_scores)

Where each sub-dimension (0-50):
  - 45-50: Exceptional
  - 35-44: Good
  - 25-34: Adequate
  - 15-24: Poor
  - 0-14: Critical deficiency
```

---

## Phase 3: Runtime Testing

**Maximum Points**: 400  
**Purpose**: Execute the skill against benchmark scenarios to measure actual performance.

### 3.1 Benchmark Execution (200 pts)

Runs standardized test scenarios against the skill.

| Test Suite | Points | Description |
|------------|--------|-------------|
| Happy path | 50 | Standard successful execution |
| Edge cases | 50 | Boundary conditions and unusual inputs |
| Error injection | 50 | Invalid inputs, failures, timeouts |
| Performance | 50 | Response time, resource usage |

**Scoring per Suite:**
- 45-50: All tests pass, excellent performance
- 35-44: Most tests pass, minor issues
- 25-34: Some tests pass, notable issues
- 15-24: Few tests pass, major issues
- 0-14: Critical failures or crashes → **ABORT**

### 3.2 Security Validation (100 pts)

Validates security controls during execution.

| Check | Points | Description |
|-------|--------|-------------|
| Input sanitization | 30 | Malicious input handled safely |
| Secret handling | 30 | No secrets in logs/output |
| Privilege check | 20 | Runs with minimal permissions |
| CWE compliance | 20 | No triggered CWE patterns |

### 3.3 Conformance Testing (100 pts)

Verifies adherence to skill-writer specification.

| Check | Points | Description |
|-------|--------|-------------|
| Mode structure | 30 | Follows §N mode format |
| Trigger keywords | 30 | Valid EN+ZH trigger lists |
| Red lines | 20 | Red lines are specific and testable |
| Quality gates | 20 | Measurable thresholds defined |

---

## Phase 4: Certification

**Maximum Points**: 200  
**Purpose**: Final quality gates, variance analysis, and tier assignment.

### 4.1 Human Review Checkpoint (50 pts)

Optional human-in-the-loop validation.

| Component | Points | Description |
|-----------|--------|-------------|
| Review completion | 30 | Human has reviewed and signed off |
| Issue resolution | 20 | All flagged issues addressed |

**Note:** Human review is optional for automated evaluation. If skipped, points are allocated based on automated checks passing.

### 4.2 Final Quality Gates (80 pts)

Hard thresholds that must be met.

| Gate | Threshold | Points |
|------|-----------|--------|
| Minimum score | ≥ 700 | 20 |
| No critical failures | Zero P0 issues | 20 |
| Documentation complete | All sections filled | 20 |
| Test coverage | ≥ 80% | 20 |

### 4.3 Variance Analysis (50 pts)

Measures score stability across multiple evaluation runs.

See [Variance Analysis](#variance-analysis) section for detailed formula.

| Variance Level | Points | Description |
|----------------|--------|-------------|
| Low (< 5%) | 50 | Highly consistent |
| Medium (5-10%) | 30 | Acceptable variation |
| High (10-20%) | 10 | Concerning variation |
| Critical (> 20%) | 0 | Unstable, requires investigation |

### 4.4 Tier Assignment (20 pts)

Final certification tier based on total score.

| Tier | Score Range | Points |
|------|-------------|--------|
| PLATINUM | ≥ 950 | 20 |
| GOLD | 900-949 | 15 |
| SILVER | 800-899 | 10 |
| BRONZE | 700-799 | 5 |
| FAIL | < 700 | 0 |

---

## Certification Tiers

EVALUATE mode assigns one of five certification tiers based on the final 1000-point score.

### Tier Definitions

```
┌─────────────────────────────────────────────────────────────────┐
│                        TIER THRESHOLDS                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   PLATINUM  ████████████████████████████████████████  ≥ 950    │
│             Exceptional quality, production-ready,              │
│             zero critical issues, exemplary documentation       │
│                                                                 │
│   GOLD      ██████████████████████████████████        ≥ 900    │
│             High quality, production-ready, minor               │
│             improvements possible                               │
│                                                                 │
│   SILVER    ████████████████████████████              ≥ 800    │
│             Good quality, suitable for production with          │
│             monitoring, some areas need attention               │
│                                                                 │
│   BRONZE    ████████████████████                      ≥ 700    │
│             Acceptable quality, requires review before          │
│             production use, notable improvements needed         │
│                                                                 │
│   FAIL      ██████████                                < 700    │
│             Does not meet minimum quality standards,            │
│             requires significant rework                         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Tier Characteristics

| Tier | Score | Production Ready | Confidence | Action Required |
|------|-------|------------------|------------|-----------------|
| **PLATINUM** | ≥ 950 | Yes | Very High | None - exemplary skill |
| **GOLD** | 900-949 | Yes | High | Optional minor improvements |
| **SILVER** | 800-899 | With monitoring | Medium | Address flagged issues |
| **BRONZE** | 700-799 | Review required | Low | Significant improvements needed |
| **FAIL** | < 700 | No | Very Low | Major rework required |

### Tier Badges

Skills receive visual tier badges in their metadata:

```yaml
---
name: example-skill
version: "1.0.0"
certification:
  tier: PLATINUM
  score: 967
  evaluated_at: "2026-03-31T10:30:00Z"
  variance: 0.02
---
```

---

## Variance Analysis

Variance measures the stability of evaluation scores across multiple runs. High variance indicates non-deterministic behavior or flaky assessments.

### Variance Formula

```
Variance = σ / μ

Where:
  σ = standard deviation of scores across N runs
  μ = mean score across N runs
  N = minimum 3 evaluation runs (default: 5)

Standard Deviation (σ):
  σ = √(Σ(xi - μ)² / N)

Coefficient of Variation (CV):
  CV = (σ / μ) × 100%
```

### Interpretation

| Variance (CV) | Classification | Action |
|---------------|----------------|--------|
| **< 5%** | Low | Excellent stability, score is reliable |
| **5-10%** | Medium | Acceptable, monitor for trends |
| **10-20%** | High | Concerning, investigate root cause |
| **> 20%** | Critical | Unstable, evaluation is unreliable |

### Variance Investigation

When variance exceeds 10%, investigate:

1. **Non-deterministic components**: Does the skill use randomness?
2. **External dependencies**: Are API calls or file I/O involved?
3. **Timing issues**: Are there race conditions or timeouts?
4. **Resource contention**: Is the evaluation environment consistent?
5. **Scoring inconsistencies**: Are rubrics applied uniformly?

### Variance Report Example

```
VARIANCE ANALYSIS REPORT
========================
Skill: api-integration-skill v1.2.0
Runs: 5

Scores: [945, 938, 942, 951, 939]
Mean (μ): 943.0
Std Dev (σ): 5.1
Variance (CV): 0.54% ✓ LOW

Interpretation:
- Score is highly stable across runs
- Certification tier is reliable: GOLD
- No investigation required
```

---

## Usage Examples

### Example 1: Basic Evaluation

Evaluate a single skill file:

```bash
# CLI usage
skill-writer evaluate --file skills/my-skill.md

# Programmatic usage
from skill_framework import evaluate

result = evaluate("skills/my-skill.md")
print(f"Score: {result.score}/1000")
print(f"Tier: {result.tier}")
```

**Output:**
```json
{
  "skill": "my-skill",
  "version": "1.0.0",
  "score": 867,
  "tier": "SILVER",
  "phases": {
    "parse_validate": 95,
    "text_quality": 275,
    "runtime_testing": 350,
    "certification": 147
  },
  "variance": 0.03,
  "recommendations": [
    "Add more comprehensive error handling examples",
    "Include performance benchmarks in quality gates",
    "Expand domain terminology coverage"
  ]
}
```

### Example 2: Batch Evaluation

Evaluate multiple skills:

```bash
skill-writer evaluate --batch skills/*.md --output report.json
```

**Output:**
```json
{
  "evaluated_at": "2026-03-31T10:30:00Z",
  "total_skills": 12,
  "tier_distribution": {
    "PLATINUM": 2,
    "GOLD": 5,
    "SILVER": 3,
    "BRONZE": 1,
    "FAIL": 1
  },
  "average_score": 842,
  "skills": [
    {"name": "skill-a", "score": 967, "tier": "PLATINUM"},
    {"name": "skill-b", "score": 923, "tier": "GOLD"},
    ...
  ]
}
```

### Example 3: CI/CD Integration

Use in a GitHub Actions workflow:

```yaml
name: Skill Evaluation

on: [push, pull_request]

jobs:
  evaluate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Evaluate Skills
        run: |
          skill-writer evaluate \
            --batch skills/*.md \
            --min-tier SILVER \
            --output evaluation.json
      
      - name: Check Tier Threshold
        run: |
          if grep -q '"tier": "FAIL"' evaluation.json; then
            echo "FAIL tier detected. Blocking merge."
            exit 1
          fi
      
      - name: Upload Report
        uses: actions/upload-artifact@v3
        with:
          name: evaluation-report
          path: evaluation.json
```

### Example 4: Evaluation with Custom Thresholds

Override default thresholds:

```bash
skill-writer evaluate \
  --file skills/my-skill.md \
  --min-score 850 \
  --max-variance 0.08 \
  --runs 7
```

### Example 5: Detailed Report Generation

Generate a comprehensive HTML report:

```bash
skill-writer evaluate \
  --file skills/my-skill.md \
  --format html \
  --output report.html \
  --include-recommendations \
  --include-diff
```

---

## Output Format

EVALUATE mode produces structured output in multiple formats.

### JSON Output Schema

```json
{
  "evaluation_version": "2.0.0",
  "evaluated_at": "2026-03-31T10:30:00Z",
  "skill": {
    "name": "string",
    "version": "string",
    "file_path": "string",
    "file_hash": "sha256:..."
  },
  "summary": {
    "total_score": 867,
    "max_score": 1000,
    "tier": "SILVER",
    "passed": true,
    "variance": {
      "coefficient": 0.03,
      "classification": "LOW",
      "runs": 5
    }
  },
  "phases": {
    "parse_validate": {
      "score": 95,
      "max": 100,
      "passed": true,
      "checks": {
        "yaml_frontmatter": {"score": 30, "max": 30, "passed": true},
        "section_presence": {"score": 35, "max": 40, "passed": true, "missing": ["§4 Examples"]},
        "markdown_structure": {"score": 20, "max": 20, "passed": true},
        "external_refs": {"score": 10, "max": 10, "passed": true}
      }
    },
    "text_quality": {
      "score": 275,
      "max": 300,
      "passed": true,
      "dimensions": {
        "system_design": {"score": 45, "max": 50, "feedback": "Good architecture, minor boundary clarification needed"},
        "domain_knowledge": {"score": 48, "max": 50, "feedback": "Excellent domain coverage"},
        "workflow_definition": {"score": 42, "max": 50, "feedback": "Clear workflow, add more decision branches"},
        "error_handling": {"score": 38, "max": 50, "feedback": "Basic coverage, expand error categories"},
        "examples": {"score": 50, "max": 50, "feedback": "Comprehensive examples"},
        "metadata": {"score": 52, "max": 50, "feedback": "Complete metadata"}
      }
    },
    "runtime_testing": {
      "score": 350,
      "max": 400,
      "passed": true,
      "benchmarks": {
        "happy_path": {"score": 50, "max": 50, "tests_passed": 10, "tests_total": 10},
        "edge_cases": {"score": 45, "max": 50, "tests_passed": 9, "tests_total": 10, "failed": ["test_null_input"]},
        "error_injection": {"score": 50, "max": 50, "tests_passed": 8, "tests_total": 8},
        "performance": {"score": 45, "max": 50, "avg_response_ms": 145, "threshold_ms": 200}
      },
      "security": {"score": 100, "max": 100, "passed": true},
      "conformance": {"score": 60, "max": 100, "passed": true, "issues": ["Trigger keywords missing Chinese translations"]}
    },
    "certification": {
      "score": 147,
      "max": 200,
      "passed": true,
      "human_review": {"completed": false, "score": 20, "max": 50},
      "quality_gates": {"score": 80, "max": 80, "passed": true},
      "variance": {"score": 50, "max": 50, "classification": "LOW"},
      "tier": {"assigned": "SILVER", "score": 20, "max": 20}
    }
  },
  "recommendations": [
    {
      "priority": "HIGH",
      "category": "Error Handling",
      "message": "Expand error handling to cover network timeouts and API rate limits",
      "impact": "+15 points potential"
    },
    {
      "priority": "MEDIUM",
      "category": "Examples",
      "message": "Add example for error recovery workflow",
      "impact": "+5 points potential"
    },
    {
      "priority": "LOW",
      "category": "Metadata",
      "message": "Add 'updated' timestamp to track modifications",
      "impact": "+2 points potential"
    }
  ],
  "improvement_potential": 22,
  "next_tier": {
    "target": "GOLD",
    "threshold": 900,
    "gap": 33,
    "recommendations_to_implement": 2
  }
}
```

### Markdown Report Format

```markdown
# Evaluation Report: my-skill v1.0.0

**Evaluated**: 2026-03-31T10:30:00Z  
**Score**: 867 / 1000  
**Tier**: 🥈 SILVER  
**Variance**: 0.03 (LOW)  

---

## Phase Breakdown

| Phase | Score | Max | % |
|-------|-------|-----|---|
| Parse & Validate | 95 | 100 | 95% |
| Text Quality | 275 | 300 | 92% |
| Runtime Testing | 350 | 400 | 88% |
| Certification | 147 | 200 | 74% |

---

## Recommendations

### HIGH Priority
1. **Error Handling** (+15 points)
   - Expand error handling to cover network timeouts and API rate limits

### MEDIUM Priority
2. **Examples** (+5 points)
   - Add example for error recovery workflow

---

## Next Tier: GOLD (900 points)

Gap: 33 points  
Implement 2 HIGH priority recommendations to reach GOLD tier.
```

---

## Integration

### As a Library

```python
from skill_framework.evaluate import evaluate_skill, EvaluationConfig

config = EvaluationConfig(
    min_tier="SILVER",
    max_variance=0.05,
    runs=5,
    include_recommendations=True
)

result = evaluate_skill("path/to/skill.md", config)

if result.tier == "FAIL":
    print("Skill failed evaluation")
    for issue in result.critical_issues:
        print(f"  - {issue}")
else:
    print(f"Certified: {result.tier} ({result.score}/1000)")
```

### As a CLI Tool

```bash
# Basic evaluation
skill-writer evaluate -f skill.md

# With options
skill-writer evaluate \
  -f skill.md \
  --format json \
  --output result.json \
  --verbose

# Batch mode
skill-writer evaluate -b "skills/*.md" --min-tier GOLD
```

### Webhook Integration

```python
# Trigger evaluation via webhook
curl -X POST https://api.skill-writer.dev/evaluate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "skill_url": "https://raw.githubusercontent.com/user/repo/main/skill.md",
    "callback_url": "https://my-app.com/webhooks/evaluation",
    "config": {
      "min_tier": "SILVER",
      "runs": 3
    }
  }'
```

---

## References

- **Framework Specification**: `../skill-writer.md`
- **CREATE Mode**: `../create/README.md`
- **OPTIMIZE Mode**: `../optimize/README.md`
- **Security Patterns**: `../shared/security/cwe-patterns.yaml`
- **Scoring Rubrics**: `rubrics.yaml`
- **Phase Definitions**: `phases.yaml`
- **Certification Rules**: `certification.yaml`

---

**End of EVALUATE Mode Documentation**
