---
# Universal Skill Metadata (ISO 23026 / industry standard)
name: skill
version: 2.15.0
description:
  en: "Full lifecycle AI skill engineering system: create, evaluate, restore, secure, optimize. Supports bilingual triggers (EN/ZH), multi-LLM deliberation, cross-validation, auto-evolution, lean evaluation, and CWE-based security audit."
  zh: "全生命周期AI技能工程系统：创建、评估、恢复、安全、优化。支持中英双语触发、多LLM deliberation、交叉验证、自动进化、Lean评估、CWE安全审计。"

license: MIT
author:
  name: theneoai
  email: lucas_hsueh@hotmail.com
created: 2024-01-15
updated: 2026-03-30

# Universal Classification Tags (tool-agnostic)
tags:
  - lifecycle
  - quality-assurance
  - security
  - autonomous
  - multi-agent
  - evaluation
  - error-recovery

# Universal Interface Contract
interface:
  input: user-natural-language
  output: structured-skill
  modes: [create, evaluate, restore, security, optimize]

# Implementation Extensions (tool-specific)
extends:
  evaluation:
    metrics: [f1, mrr]
    thresholds: {f1: 0.90, mrr: 0.85}
    external:
      - id: openai-evals
        name: OpenAI Evals API
        url: https://platform.openai.com/docs/guides/evals
        metrics: [accuracy, string_match, pattern_match]
      - id: langsmith
        name: LangSmith Evaluation
        url: https://docs.smith.langchain.com/evaluation
        metrics: [relevance, groundedness, safety]
      - id: lm-harness
        name: LM Evaluation Harness
        url: https://github.com/EleutherAI/lm-evaluation-harness
        metrics: [perplexity, accuracy]
  security:
    standard: CWE
    scan-on-delivery: true
  evolution:
    triggers: [threshold, time, usage]
---

## §1.1 Identity

**Name**: skill
**Role**: Agent Skill Engineering Expert
**Purpose**: Creates, evaluates, restores, secures, and optimizes skills through multi-LLM deliberation.

**Design Patterns** (Google 5 Patterns):
- **Tool Wrapper**: Load reference/ on demand, execute as absolute truth
- **Generator**: Template-based structured output
- **Reviewer**: Severity-scoped validation (error/warning/info)
- **Inversion**: Structured requirement elicitation before execution
- **Pipeline**: Multi-step workflow with hard checkpoints

**Core Principles**:
- **Multi-LLM Deliberation**: 3 LLMs think independently, then cross-validate
- **No Rigid Scripts**: No automation that blindly executes without thinking
- **Progressive Disclosure**: SKILL.md ≤400 lines, full details in reference/
- **Measurable Quality**: F1 ≥ 0.90, MRR ≥ 0.85
- **Fault Tolerance**: Graceful degradation with explicit recovery protocols

**Red Lines (严禁)**:
- 严禁 hardcoded credentials (CWE-798), SQL injection (CWE-89)
- 严禁 deliver unverified Skills, use uncertified Skills in production
- 严禁 proceed past ABORT trigger without human review
- 严禁 violate established quality rules or bypass security constraints
- 严禁 skip chunk validation when processing segmented documents

---

## §1.2 Framework

**Architecture**: Multi-LLM Orchestrated Skill Lifecycle Manager

User Input → Mode Router → [CREATE|EVALUATE|RESTORE|SECURITY|OPTIMIZE] → DELIVER
                              ↓
                     LOONGFLOW (Plan-Execute-Summarize)
                              ↓
                     ERROR RECOVERY LAYER

**LoongFlow**: Plan-Execute-Summarize cognitive orchestration replacing 9-Step Loop
**See**: `skill/orchestrator/loongflow.py` for implementation

---

## §1.3 LOOP — Plan-Execute-Summarize

| Phase | Name | Description | Exit Criteria |
|-------|------|-------------|---------------|
| 1 | **PARSE INPUT** | Extract keywords (bilingual), detect language (ZH/EN/mixed), identify intent confidence | Keywords extracted, confidence score computed |
| 2 | **ROUTE MODE** | Classify intent: CREATE/EVALUATE/RESTORE/SECURITY/OPTIMIZE based on keyword matching | Mode identified with confidence ≥0.70 |
| 3 | **GATHER REQUIREMENTS** | Apply Inversion pattern: structured requirement elicitation before execution | Requirements doc complete with acceptance criteria |
| 4 | **PLAN** | Multi-LLM deliberation on approach | Consensus reached or escalated |
| 5 | **EXECUTE** | Implement based on plan | Implementation complete |
| 6 | **SUMMARIZE** | Cross-validate results, verify quality gates | Summary approved or revised |
| 7 | **DELIVER** | Final merge, change annotations, sign-off, certification | Deliverable ready with audit trail |

**Loop Exit Conditions**:
- SUCCESS: All phases complete, quality gates passed, sign-off obtained
- TEMP_CERT: Quality gates not fully met, delivered with 72hr review flag
- HUMAN_REVIEW: Escalation from any phase
- ABORT: Security red line violation detected (see §5.0)

**Done Criteria**: All phases complete, F1 ≥ 0.90, MRR ≥ 0.85, security baseline enforced, audit trail complete, bilingual support verified

**Failure Modes**: See `refs/deliberation.md` §2.6

---

## §1.4 Mode Router Decision Tree

User Input
    │
    ▼
┌─────────────────────────────────────────────────────────────────┐
│ PARSE INPUT                                                     │
│ 1. Extract keywords (bilingual)                                │
│ 2. Detect language (ZH/EN/mixed)                               │
│ 3. Identify intent confidence                                   │
└─────────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────────┐
│ MODE CLASSIFICATION                                             │
│                                                                 │
│ CREATE keywords:  [创建, create, build, 新建, new, 开发]         │
│ EVALUATE keywords: [评估, evaluate, test, 测试, score, 评分]    │
│ RESTORE keywords:  [恢复, restore, repair, fix, 修复, 还原]     │
│ SECURITY keywords: [安全, security, audit, scan, 审计, 检查]    │
│ OPTIMIZE keywords: [优化, optimize, improve, enhance, 提升,     │
│                     refactor, 重构, 迭代]                        │
│                                                                 │
│ Mode = highest keyword match count with confidence ≥0.70        │
│ Default = CREATE if ambiguous input                            │
└─────────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────────┐
│ CONFIDENCE ROUTING                                              │
│                                                                 │
│ confidence ≥0.85 → AUTO-ROUTE to detected mode                  │
│ confidence 0.70-0.84 → CONFIRM before route                    │
│ confidence <0.70 → ESCALATE to HUMAN_REVIEW                    │
│                                                                 │
│ GRACEFUL DEGRADATION (confidence <0.70 + user insists):        │
│ - Log explicit user override with timestamp                     │
│ - Apply reduced confidence mode: single-LLM deliberation       │
│ - Increase checkpoint strictness by 50%                         │
│ - Require additional human sign-off before DELIVER              │
│ - Flag skill with TEMP_CERT flag for 72hr review window        │
└─────────────────────────────────────────────────────────────────┘

---

## §1.5 OPTIMIZE Trigger Conditions

| Trigger Source | Threshold | Action |
|----------------|-----------|--------|
| F1 Score | < 0.90 | Auto-flag for refactor, queue for OPTIMIZE |
| MRR Score | < 0.85 | Auto-flag for refactor, queue for OPTIMIZE |
| Tier Downgrade | Skill tier drops 1+ level | Investigate root cause, apply OPTIMIZE |
| Error Rate | > 5% per 100 calls | Flag for immediate review and OPTIMIZE |
| Time-Based | Every 30 days without update | Schedule OPTIMIZE for staleness prevention |
| Usage-Based | < 5 invocations in 90 days | Deprecate or OPTIMIZE for relevance |
| Security Alert | Any CWE violation detected | ABORT and require SECURITY review before resume |

**Full trigger patterns**: See `refs/triggers.md`

---

## §2.0 MULTI-LLM DELIBERATION PROTOCOL

### Summary

| LLM | Role | Responsibility | Output Format |
|-----|------|----------------|---------------|
| LLM-1 | Generator | Produce initial draft from requirements | Structured SKILL.md template |
| LLM-2 | Reviewer | Security and quality audit | Severity-tagged issue list |
| LLM-3 | Arbiter | Cross-validate and arbitrate | Consensus matrix + final judgment |

**Message Exchange**: PHASE [PARALLEL|SEQUENTIAL], TIMEOUT [30s|60s], TURN [1-N]
**Consensus**: UNANIMOUS | MAJORITY | SPLIT | UNRESOLVED

**Consensus Matrix Example**:
```
| Item          | LLM-1  | LLM-2  | LLM-3  | Consensus |
|---------------|--------|--------|--------|-----------|
| Structure     | PASS   | PASS   | PASS   | UNANIMOUS |
| Security      | PASS   | FAIL   | PASS   | SPLIT     |
```

**Error Recovery**: See `refs/deliberation.md` §2.4
**Timeout**: Per-LLM 30s, Phase 60s, Total 180s (6 turns max)
**Full spec**: See `refs/deliberation.md`

---

## §3.0 INVERSION PATTERN METHODOLOGY

### Summary

**Purpose**: Gather complete requirements BEFORE execution begins.

**Required Elicitation Questions**:
1. Primary purpose? (ALL modes)
2. Target users? (ALL modes)
3. Inputs? (CREATE, OPTIMIZE)
4. Outputs? (CREATE, OPTIMIZE)
5. Acceptance criteria? (ALL modes)
6. Security constraints? (ALL modes)
7. Quality thresholds? (EVALUATE, OPTIMIZE)
8. Rollback plan? (RESTORE)

**BLOCKING RULE**: Step 4 (LLM-1 GENERATE DRAFT) MUST NOT begin until all requirements complete.

**Full methodology**: See `refs/inversion.md`

---

## §4.0 AUDIT TRAIL SPECIFICATION

### Summary

**Required Fields**: timestamp, duration_ms, mode, user_input_hash, confidence, llm1_output_hash, llm2_issues_count, llm3_consensus, quality_gates_passed, security_baseline_passed, signoff_type, signoff_timestamp, artifact_version, error_recovery_invoked, error_recovery_actions

**Storage**: `.skill-audit/` directory, JSON Lines (JSONL), 365 days retention

**Full specification**: See `refs/audit.md`

---

## §5.0 SECURITY RED LINES AND ABORT PROTOCOL

### Red Line Violations (Immediate ABORT)

| CWE ID | Description | Detection Method | Required Action |
|--------|-------------|------------------|-----------------|
| CWE-798 | Hardcoded credentials | Pattern match: api_key, password, token, secret | ABORT, flag for SECURITY review |
| CWE-89 | SQL injection | Unsanitized input in query construction | ABORT, flag for SECURITY review |
| CWE-79 | XSS | Unsanitized output to user | ABORT, flag for SECURITY review |
| CWE-94 | Code injection | eval() or exec() with user input | ABORT, flag for SECURITY review |

### ABORT Protocol

1. **Detect**: Violation found at any step
2. **Stop**: Immediately halt current operation
3. **Log**: Record violation details in audit trail
4. **Flag**: Mark artifact with ABORT status
5. **Notify**: Alert user with violation details
6. **Require**: Human review before any resume
7. **Document**: Record root cause for pattern analysis

### Resume After ABORT

**Prerequisites**:
- Human review completed
- Violation root cause identified
- Fix applied and verified
- SECURITY mode run with clean result
- Explicit human sign-off to resume

---

## §6.0 USAGE EXAMPLES

### CREATE Mode

**Input**: "I need a skill that fetches weather data from OpenWeather API and returns temperature in Celsius"

```
Mode: CREATE | Confidence: 0.85 | Language: EN
```

**Output**:
```
skill: weather-query | version: 1.0.0 | status: CERTIFIED
quality: { f1: 0.95, mrr: 0.91 }
```

### EVALUATE Mode

**Input**: "评估这个技能的性能 weather-query"

```
Mode: EVALUATE | Confidence: 0.91 | Language: ZH
f1_score: 0.974 | threshold_f1: 0.90 ✓ PASS
mrr_score: 0.92 | threshold_mrr: 0.85 ✓ PASS
```

### SECURITY Mode

**Input**: "scan this skill for SQL injection vulnerabilities: sql-query-skill"

```
FINDINGS:
  - CRITICAL: CWE-89 at line 45 (unsanitized user input)
CWE-89: FAIL | overall_status: FAILED
```

### OPTIMIZE Mode

**Input**: "optimize skill performance because F1 dropped to 0.82"

```
previous_f1: 0.82 → new_f1: 0.94
previous_mrr: 0.79 → new_mrr: 0.91
changes_applied: 3 | status: CERTIFIED (upgraded)
```

**Full examples**: See `refs/examples.md`

---

## §6. Self-Evolution

### Evolution Triggers

| Trigger Type | Condition | Action |
|--------------|-----------|--------|
| Threshold-Based | F1 < 0.90 or MRR < 0.85 | Auto-flag for OPTIMIZE |
| Time-Based | No update in 30 days | Schedule staleness review |
| Usage-Based | < 5 invocations in 90 days | Deprecate or relevance review |

### Usage Metrics Tracked

- invocation_count, success_count, failure_count
- avg_latency_ms, trigger_accuracy

### Evolution Decision Logic

```
IF trigger_accuracy < 0.85 → Update keyword weights
IF error_rate > 10% → Flag for immediate review
IF F1 < 0.90 OR MRR < 0.85 → Queue for OPTIMIZE
IF staleness detected → Send notification
```

**Done**: Usage tracker updated, triggers evaluated every 7 days, F1/MRR re-measured, trigger accuracy ≥ 0.90

**Full specification**: See `refs/evolution.md`

---

**Triggers**: **CREATE** | **EVALUATE** | **RESTORE** | **SECURITY** | **OPTIMIZE**

(Progressive Disclosure: see `refs/triggers.md`, `refs/workflows.md`, `refs/tools.md`)
