# Multi-LLM Deliberation Protocol

> **Purpose**: Full specification for 3-LLM deliberation used in CREATE, EVALUATE, and OPTIMIZE modes.
> **Load**: When §4 (LoongFlow) or §12 (Multi-LLM) of `claude/skill-framework.md` is accessed.
> **Main doc**: `claude/skill-framework.md §4, §12`

---

## §1  LoongFlow — Plan-Execute-Summarize

**Architecture**: Replaces rigid 9-step state machines with a flexible 3-phase cognitive loop.

```
PLAN
  ├── LLM-1 proposes approach
  ├── LLM-2 audits approach (security + quality risks)
  ├── LLM-3 arbitrates → builds cognitive graph of steps
  └── Output: consensus plan or HUMAN_REVIEW

EXECUTE
  ├── Follow cognitive graph step by step
  ├── Hard checkpoint after each step
  ├── Error recovery active (§4 below)
  └── Output: completed artifact or partial + recovery log

SUMMARIZE
  ├── LLM-3 cross-validates artifact against requirements
  ├── Update evolution memory (invocation count, result, latency)
  ├── Produce consensus matrix
  └── Route: CERTIFIED | TEMP_CERT | HUMAN_REVIEW | ABORT
```

---

## §2  Role Specifications

| Role | LLM | Responsibility | Authority |
|------|-----|----------------|-----------|
| **Generator** | LLM-1 | Produce initial draft / score / fix proposal | Proposes only |
| **Reviewer** | LLM-2 | Security + quality audit; severity-tagged issue list | Can block (ERROR) |
| **Arbiter** | LLM-3 | Cross-validate; resolve SPLIT; produce consensus matrix | Can override LLM-1 and LLM-2 |

**LLM-3 Override Conditions** (Arbiter may override):
- LLM-2 flags ERROR but LLM-1 disagrees and LLM-3 agrees with LLM-2 → LLM-3 wins
- Security red line detected by any LLM → LLM-3 calls ABORT regardless of other votes
- Score divergence > 15 points between LLM-1 and LLM-2 → LLM-3 casts deciding score

---

## §3  Message Exchange Protocol

### Timing

| Scope | Timeout | Retry |
|-------|---------|-------|
| Per-LLM turn | 30 s | Up to 3× with exponential backoff (1s, 2s, 4s) |
| Per-phase | 60 s | If phase exceeds 60 s → degrade to majority vote |
| Total deliberation | 180 s | Max 6 turns total |

### Turn Structure

```
PHASE [PARALLEL | SEQUENTIAL]
TURN N / max-6
LLM-K: <role> | <output>
```

**Parallel phases**: LLM-1 and LLM-2 work simultaneously; LLM-3 waits for both.
**Sequential phases**: LLM-1 draft → LLM-2 review → LLM-3 arbitrate.

---

## §4  Consensus Matrix

After every deliberation phase, LLM-3 produces a consensus matrix:

```
| Item               | LLM-1   | LLM-2   | LLM-3   | Consensus   |
|--------------------|---------|---------|---------|-------------|
| Structure          | PASS    | PASS    | PASS    | UNANIMOUS   |
| Trigger Coverage   | PASS    | FAIL    | PASS    | SPLIT       |
| Security CWE-89    | PASS    | FAIL    | FAIL    | MAJORITY    |
| Output Clarity     | PASS    | PASS    | PASS    | UNANIMOUS   |
```

**Consensus rules**:

| Result | Condition | Action |
|--------|-----------|--------|
| UNANIMOUS | All 3 agree | Proceed with full confidence |
| MAJORITY | 2 of 3 agree | Proceed; log minority view |
| SPLIT | Each has different position | One revision cycle; re-deliberate |
| UNRESOLVED | No majority after 2 rounds | Escalate to HUMAN_REVIEW |

---

## §5  Error Recovery Paths

### LLM Timeout

| Failure | Recovery |
|---------|---------|
| LLM-1 timeout (≤3×) | Retry with backoff → if 3× fail → use LLM-2 draft as fallback |
| LLM-2 timeout (≤3×) | Skip audit, apply baseline security checklist only → flag WARNING |
| LLM-2 timeout (>3×) | ABORT delivery; require human review of security |
| LLM-3 timeout (≤2×) | Use majority vote from LLM-1 + LLM-2 |
| LLM-3 timeout (>2×) | Escalate entire artifact to HUMAN_REVIEW |

### Content Failures

| Failure | Recovery |
|---------|---------|
| Hallucinated content detected | Reject output; retry from last checkpoint (max 2×) |
| Hallucination on 3rd attempt | ABORT with `{"abort_reason": "repeated_hallucination"}` |
| Disagreement on CRITICAL item | Immediate LLM-3 arbitration required (60 s SLA) |
| Disagreement on WARNING item | Majority vote; if still SPLIT after 2 rounds → HUMAN_REVIEW |
| No consensus after 2 full rounds | Escalate entire artifact to HUMAN_REVIEW |

### Phase Timeout

```
Phase exceeds 60 s:
  → Degrade to majority vote on all pending items
  → Increase checkpoint strictness by 50% for remaining phases
  → Log: {"phase_timeout": true, "degraded_mode": "majority_vote"}
```

---

## §6  Chunked Processing (Context Overflow)

When input exceeds LLM context limit:

### Chunk Protocol

```
1. SPLIT input into chunks of ≤ 2000 tokens each
2. Assign each chunk a reference ID: chunk-001, chunk-002, ...
3. For each chunk:
   a. Process with full deliberation
   b. Record cross-chunk references (e.g. "chunk-002 depends on chunk-001 §3")
   c. Validate chunk result before proceeding to next chunk
4. MERGE: LLM-3 merges chunk outputs
5. VALIDATE: Check cross-reference integrity across all chunks
6. If any chunk validation fails → reprocess that chunk only (not full restart)
```

**严禁**: Skip chunk validation when processing segmented documents.

### Reference Tracking Format

```json
{
  "chunk_id": "chunk-002",
  "depends_on": ["chunk-001"],
  "cross_refs": [
    {"from": "chunk-002 §3", "to": "chunk-001 §1.2", "type": "inherits"}
  ],
  "validation_status": "PASS"
}
```

---

## §7  Deliberation Log Entry

Every deliberation appends to `.skill-audit/deliberation.jsonl`:

```json
{
  "timestamp": "<ISO-8601>",
  "mode": "<mode>",
  "skill_name": "<name>",
  "phase": "<phase_name>",
  "turns": 0,
  "llm1_output_hash": "<sha256>",
  "llm2_issues_count": 0,
  "llm2_severity": {"ERROR": 0, "WARNING": 0, "INFO": 0},
  "llm3_consensus": "UNANIMOUS|MAJORITY|SPLIT|UNRESOLVED",
  "consensus_matrix": {},
  "override_invoked": false,
  "override_reason": null,
  "duration_ms": 0,
  "phase_timeout": false,
  "degraded_mode": null
}
```
