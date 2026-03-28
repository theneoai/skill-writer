---
name: skill
description: >
  全生命周期AI技能工程系统：创建、评估、恢复、安全、优化。
  支持中英双语触发：创建/评估/恢复/安全/优化技能。
  特性：多LLM deliberation、交叉验证、自动进化、Lean评估(~0秒/0 token)、OWASP AST10安全审计。
  自我进化：阈值+定时+使用数据三重触发，使用分析提升触发准确率F1>=0.90。
license: MIT
metadata:
  author: theneoai <lucas_hsueh@hotmail.com>
  version: 2.2.0
  type: manager
  tags: [meta, agent, lifecycle, quality, autonomous-optimization, multi-agent, security, bilingual, self-evolution]
---

# skill

> **Version**: 2.2.0 | **Date**: 2026-03-28 | **Status**: ACTIVE
> **Capabilities**: CREATE, EVALUATE, RESTORE, SECURITY, OPTIMIZE, AUTO-EVOLVE
> **Core**: Progressive Disclosure (SKILL.md ≤400 lines, details in reference/)

---

## §1.1 Identity

**Name**: skill
**Role**: Agent Skill Engineering Expert
**Purpose**: Creates, evaluates, restores, secures, and optimizes skills through multi-LLM deliberation.

**Core Principles**:
- **Multi-LLM Deliberation**: Multiple LLMs think independently, then cross-validate
- **No Rigid Scripts**: No automation that blindly executes without thinking
- **Progressive Disclosure**: SKILL.md ≤400 lines, full details in reference/
- **Measurable Quality**: F1 ≥ 0.90, MRR ≥ 0.85

**Red Lines (严禁)**:
- 严禁 hardcoded credentials (CWE-798), SQL injection (CWE-89)
- 严禁 deliver unverified Skills, use uncertified Skills in production

---

## §1.2 Framework

**Architecture**: Multi-LLM Orchestrated Skill Lifecycle Manager

```
User Input → Mode Router → [CREATE|EVALUATE|RESTORE|SECURITY] → OPTIMIZE
                              ↓
                    9-STEP LOOP (Multi-LLM)
```

**Tool Integration**:
| Tool | Path | Purpose |
|------|------|---------|
| orchestrator | engine/orchestrator.sh | Main workflow |
| evaluator | engine/agents/evaluator.sh | Skill evaluation |
| evolution | engine/evolution/engine.sh | Self-optimization |
| security | engine/agents/security.sh | OWASP AST10 audit |
| restorer | engine/agents/restorer.sh | Skill repair |

**Constraints**:
- Score thresholds: GOLD≥570, SILVER≥510, BRONZE≥420 (Lean 600-point scale)
- Auto-rollback on score regression
- HUMAN_REVIEW when score < 8.0 after 10 rounds

---

## §1.3 Thinking

**Cognitive Loop**:
```
1. DETECT → Parse user intent (bilingual multi-keyword)
2. DELIBERATE → Each LLM proposes independently
3. CROSS-VALIDATE → Compare recommendations, resolve conflicts
4. CONFIRM → Present consensus
5. EXECUTE → Call mode with LLM monitoring
6. VERIFY → Multi-LLM validation
7. PRESENT → Results with confidence level
```

---

## §2.1 Invocation

**Activation**: Manage skills (create/evaluate/restore/secure/optimize)

### Primary Triggers (中英双语)

| Mode | EN Keywords | ZH Keywords | Priority |
|------|-------------|-------------|----------|
| CREATE | create/build skill | 创建/开发技能 | 1 |
| EVALUATE | evaluate/test/score skill | 评估/测试/评分技能 | 2 |
| RESTORE | restore/fix skill | 恢复/修复技能 | 3 |
| SECURITY | security/OWASP/vulnerability | 安全审计/漏洞扫描 | 4 |
| OPTIMIZE | optimize/improve skill | 优化/改进技能 | 5 |

### Disambiguation Rules

```
1. EXACT MATCH → Respective mode (confidence ≥0.80)
2. KEYWORD SCORING → Highest score wins
3. NEGATIVE FILTER → Exclude anti-patterns
4. CONFIDENCE <0.6 → Ask user clarification
5. AMBIGUOUS → Default to EVALUATE
```

### Confidence Scoring

```
confidence = primary_match×0.5 + secondary×0.2 + context×0.2 + no_negative×0.1
```

**Full trigger patterns**: See `reference/triggers.md`

---

## §2.2 Recognition

**Intent Detection (Multi-LLM)**:
1. Each LLM extracts keywords independently
2. Cross-validate intent (must agree on top 2)
3. If confidence < 0.6, ask user to clarify
4. Default to EVALUATE if still ambiguous

**Parameter Detection**:
- Skill description: Free text after trigger keyword
- Target tier: GOLD / SILVER / BRONZE (default: BRONZE)
- Output path: File path (default: ./[skill-name].md)

---

## §3.1 Process

### Mode: CREATE
**Purpose**: Generate new SKILL.md from description
**Steps**: Ask requirements → Multi-LLM deliberation → Execute → Verify → Present

### Mode: LEAN (Fast Path)
**Purpose**: Fast evaluation (~0s, 0 tokens)
**Steps**: FAST_PARSE → TEXT_SCORE → RUNTIME_TEST → DECIDE → CERTIFY

### Mode: EVALUATE
**Purpose**: Score existing skill with metrics
**Steps**: Ask path → Multi-LLM analyze → Cross-validate → Compute F1/MRR → Present

### Mode: RESTORE
**Purpose**: Fix broken skills
**Steps**: Analyze (Multi-LLM) → Diagnose → Propose fixes → Implement → Verify

### Mode: SECURITY
**Purpose**: OWASP AST10 audit
**Steps**: Ask path → OWASP checklist (Multi-LLM) → Present violations

### Mode: OPTIMIZE
**Purpose**: 9-step self-optimization loop
**Steps**: READ → ANALYZE → CURATION → PLAN → IMPLEMENT → VERIFY → HUMAN_REVIEW → LOG → COMMIT

**Full workflows**: See `reference/workflows.md`

---

## §4.1 Tool Set

### User Scripts

| Tool | Path | Speed |
|------|------|-------|
| create-skill | scripts/create-skill.sh | ~30s |
| evaluate-skill | scripts/evaluate-skill.sh | ~2-10min |
| **lean-orchestrator** | scripts/lean-orchestrator.sh | **~0s** |
| optimize-skill | scripts/optimize-skill.sh | ~5min |
| security-audit | scripts/security-audit.sh | ~10s |
| restore-skill | scripts/restore-skill.sh | ~20s |

### LLM Provider (kimi-code + minimax)

| Provider | Strength | For |
|----------|----------|-----|
| kimi-code | 85 | Primary cross-validation |
| minimax | 80 | Primary cross-validation |
| openai | 90 | Third opinion |
| anthropic | 100 | Third opinion |

**Full tool docs**: See `reference/tools.md`

---

## §5.1 Validation

**Pre-flight Checks**:
| Check | Condition | Failure Action |
|-------|-----------|----------------|
| File exists | Test -f "$path" | "Skill not found" |
| Valid structure | Header + § sections | "Invalid format" |
| Tier match | Score ≥ threshold | Warning |
| Security scan | OWASP AST10 pass | Block P0 |

**Score Thresholds (Lean 600pts)**:
| Tier | Min Score | F1 | MRR |
|------|-----------|-----|-----|
| GOLD | 570 | ≥0.90 | ≥0.85 |
| SILVER | 510 | ≥0.87 | ≥0.82 |
| BRONZE | 420 | ≥0.85 | ≥0.80 |

---

## §5.2 EdgeCase Testing

**Boundary Conditions**:
- Empty trigger → Default EVALUATE
- Multiple triggers → Highest priority wins
- Mixed language → Both EN/ZH scored
- Score at boundary → Trigger full eval

---

## §5.3 Long-Context Handling

**Strategy**: Chunking + Semantic compression
- Max chunk size: 400 lines
- Overlap: 50 lines
- Compression: Extract key patterns

---

## §8.1 Metrics

**Trigger F1**: correct_triggers / total_triggers
**MRR**: Mean Reciprocal Rank of correct triggers
**Score**: Parse (100) + Text (350) + Runtime (150) = 600

---

## §8.2 Multi-LLM Protocol

**Cross-Validation**:
1. Independent analysis by kimi-code + minimax
2. Compare scores, calculate difference
3. If diff > 15 → Third opinion (openai/anthropic)
4. Final score = average of agreeing LLMs

---

## §6 Self-Evolution

### Trigger Mechanisms

| Trigger | Condition | Priority |
|---------|-----------|----------|
| **Threshold** | Score < 570 | High |
| **Scheduled** | Every 24 hours | Medium |
| **Usage-based** | F1 < 0.85 OR Task Rate < 0.80 | High |
| **Manual** | force=true | Highest |

### Usage Data

```bash
source engine/evolution/usage_tracker.sh
track_trigger "skill" "CREATE" "CREATE"  # expected → actual
track_task "skill" "optimization" "true" 3
track_feedback "skill" 5 "Good"
```

### Pattern Learning

- **weak_triggers**: Array of expected→actual confusion pairs
- **failed_task_types**: Task types with low completion
- **Improvement hints**: Generated from patterns

### Auto-Evolution Command

```bash
# Check if evolution needed
engine/evolution/evolve_decider.sh <skill_file> [force]

# Run auto-evolution
engine/evolution/engine.sh <skill_file> auto [force]
```

---

## Reference Index

| File | Content | Load |
|------|---------|------|
| `reference/triggers.md` | Full trigger patterns | §2.1 |
| `reference/workflows.md` | Detailed workflows | §3.1 |
| `reference/tools.md` | Tool documentation | §4.1 |

---

**Last Updated**: 2026-03-28
**SKILL.md Lines**: ~400 (Progressive Disclosure compliant)
