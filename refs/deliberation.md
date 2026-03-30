# Multi-LLM Deliberation Protocol Reference

> **Purpose**: Complete deliberation protocol specification
> **Load**: When §2.0 Multi-LLM Deliberation is accessed
> **Full doc**: SKILL.md §2.0

---

## §2.1 Protocol Overview

The Multi-LLM Deliberation Protocol defines how three independent LLM instances collaborate to produce high-quality skill artifacts. Each LLM operates as a specialized role with distinct responsibilities. The protocol uses a **hierarchical** structure where LLM-3 (Arbiter) sits at the top tier to review and override LLM-1 and LLM-2 outputs when consensus cannot be reached, ensuring final decisions respect security constraints and quality rules.

### §2.2 LLM Role Definitions

| LLM | Role | Responsibility | Output Format |
|-----|------|----------------|---------------|
| LLM-1 | Generator | Produce initial draft from requirements | Structured SKILL.md template |
| LLM-2 | Reviewer | Security and quality audit | Severity-tagged issue list |
| LLM-3 | Arbiter | Cross-validate and arbitrate | Consensus matrix + final judgment |

### §2.3 Message Exchange Format


```
PHASE: [PARALLEL|SEQUENTIAL]
TIMEOUT: [30s|60s]
TURN: [1-N]

MSG-LLM1: [content]
MSG-LLM2: [content]
MSG-LLM3: [content]

CONSENSUS: [UNANIMOUS|MAJORITY|SPLIT|UNRESOLVED]
ARBITRATION_NEEDED: [true|false]
```

**Message Types**:
- `CONTRIBUTION`: LLM provides its independent output
- `REVIEW`: LLM comments on another LLM's output
- `CHALLENGE`: LLM disputes a claim or suggestion
- `ARBITRATION`: LLM-3 resolves a dispute
- `FINAL`: Consensus reached, artifact approved

---

## §2.4 DELIBERATION ERROR RECOVERY

| Error Condition | Recovery Action | Escalation Path |
|-----------------|-----------------|-----------------|
| LLM-1 timeout | Retry with exponential backoff (1s, 2s, 4s) | 3 failures → HUMAN_REVIEW |
| LLM-2 timeout | Skip audit, apply baseline checklist only | 3 failures → ABORT delivery |
| LLM-3 timeout | Use majority vote from LLM-1 and LLM-2 | 2 failures → HUMAN_REVIEW |
| Disagreement on CRITICAL | Immediate arbitration required | LLM-3 must resolve within 60s |
| Disagreement on WARNING | Majority vote decides | 2 rounds unresolved → HUMAN_REVIEW |
| No consensus after 2 rounds | Escalate entire artifact to HUMAN_REVIEW | Log all inputs for audit |
| Hallucinated content detected | Reject output, retry from last checkpoint | 2 hallucinations → ABORT |

**Consensus Matrix Format**:

```
DECISION_MATRIX:
  | Item          | LLM-1  | LLM-2  | LLM-3  | Consensus |
  |---------------|--------|--------|--------|-----------|
  | Structure     | PASS   | PASS   | PASS   | UNANIMOUS |
  | Security      | PASS   | FAIL   | PASS   | SPLIT     |
  | Completeness  | PASS   | WARN   | PASS   | MAJORITY  |

RESOLUTION: [Accept LLM-2 security finding, refactor, retry Step 5]
```

### §2.5 Timeout Handling

- **Per-LLM Timeout**: 30 seconds for single turn
- **Phase Timeout**: 60 seconds for parallel LLMs
- **Total Deliberation Timeout**: 180 seconds (6 turns maximum)
- **Graceful Degradation**: If any LLM exceeds timeout, apply single-LLM deliberation mode with increased validation

---

## §2.6 Failure Modes (Anti-Patterns)

- **Hardcoded Credentials** (CWE-798): API keys or passwords in skill output → ABORT
- **SQL Injection** (CWE-89): Unsanitized user input in queries → ABORT
- **Hallucinated Function Calls**: LLM generates non-existent tool names → Reject and retry
- **Incomplete Requirements**: Proceeding to Step 4 without full requirements → Block and gather more info
- **Single Point of Failure**: No fallback when LLM-1 or LLM-2 fails → Requires degraded mode activation
- **Context Window Overflow**: Input exceeds LLM context limit → Split/chunk large documents into smaller segments, process each chunk with reference tracking to maintain cross-reference integrity across chunks
- **Mode Routing Ambiguity**: Multiple modes with equal keyword match count → Default to CREATE, request clarification
- **Circular Deliberation**: LLM-1 output fed back to LLM-1 for "review" → Strict role separation enforced
- **Premature Delivery**: Skipping quality gates for "urgent" requests → TEMP_CERT only, 72hr review mandatory
- **Golden Path Dependency**: Assuming past success predicts future quality → Each delivery re-evaluated independently
- **Constraint Violation**: Ignoring defined security rules or quality constraints → All constraints must pass verification before delivery
- **Rule**: Hardcoded credentials (CWE-798) and SQL injection (CWE-89) are absolute rules that cannot be bypassed
- **Constraint**: Parallel LLM execution must respect timeout constraints
- **Rule**: All deliberation outputs must be validated against established quality rules before delivery
