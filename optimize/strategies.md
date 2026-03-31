# Optimization Strategies

> **Purpose**: 7-dimension strategy catalog for the 9-step OPTIMIZE loop.
> **Load**: When §9 (OPTIMIZE Mode) of `claude/skill-framework.md` is accessed.
> **Main doc**: `claude/skill-framework.md §9`

---

## §1  7-Dimension Scoring Reference

The OPTIMIZE loop always targets the **lowest-scoring dimension first**.

| Dim | Name | Weight | What It Covers | Strategy |
|-----|------|--------|---------------|----------|
| D1 | System Design | 20% | Identity, role hierarchy, design patterns, Red Lines | S2 |
| D2 | Domain Knowledge | 20% | Template accuracy, API/schema specificity | S3 |
| D3 | Workflow Definition | 20% | Phase sequence, exit criteria, loop gates | S4 |
| D4 | Error Handling | 15% | Recovery paths, escalation triggers, timeouts | S5 |
| D5 | Examples | 15% | Count, bilingual, output shown, realistic | S1+S3 |
| D6 | Metadata | 10% | YAML completeness, versioning, tags, dates | S6 |
| D7 | Long-Context | 10% | Section cross-refs, chunking, reference integrity | S7 |

**Tie-break**: When two dimensions score equally, prioritize by weight (higher weight first).

---

## §2  The 9-Step Loop

```
Round N (repeat up to 20 rounds, or until convergence):

  Step 1  READ       Score all 7 dimensions. Record to score_history[N].
  Step 2  ANALYZE    LLM-1 and LLM-2 each propose 3 targeted fixes for lowest dim.
  Step 3  CURATE     Every 10 rounds: consolidate learning, prune context (§3).
  Step 4  PLAN       LLM-3 selects best fix; records decision in dim_history[N].
  Step 5  IMPLEMENT  Apply one atomic change. Single dimension focus. No rewrites.
  Step 6  VERIFY     Re-score. IF regressed → rollback. IF no improvement → try fix #2.
  Step 7  HUMAN_REVIEW  Trigger if total_score < 560 (FAIL×0.8) after round 10.
  Step 8  LOG        Record: round, dimension, delta, confidence, strategy_used.
  Step 9  COMMIT     Git commit every 10 rounds with tag [optimize-round-N score=XXX].

  After every round → check convergence (claude/refs/convergence.md)
    IF converged → STOP → certify at current tier
```

**Rollback rule (Step 6)**: If re-score shows regression > 5 pts → discard change,
restore previous version, try the second-best fix from LLM-2's list.
If all 3 proposed fixes regress → switch strategy to next-lowest dimension.

---

## §3  Curation Protocol (Every 10 Rounds)

**Purpose**: Prevent context window bloat; refocus on highest-leverage improvements.

```
CURATE:
  1. Summarize: "Rounds 1–10 improved D3 by +38pts, D1 by +12pts, D5 unchanged."
  2. Rank strategies by delta produced: [S4: +38, S2: +12, S1: +0]
  3. Prune: discard individual round details; keep only summary + score_history list
  4. Re-prioritize: next 10 rounds → lead with highest-delta strategy
  5. Reset: clear LLM context for rounds 1–10; load only summary + current skill
  6. Log: {"curation_round": N, "context_reduced_pct": 40, "top_strategy": "S4"}
```

---

## §4  Strategy Catalog

### S1 — Expand Trigger Keywords

**Target dimension**: D5 (Examples), D3 (Workflow) when trigger accuracy < 0.90
**Estimated delta**: +15 to +30 pts

**Steps**:
1. List all current primary/secondary EN and ZH keywords per mode.
2. Find failing benchmark cases — which words appeared in failures?
3. Add 3+ new primary keywords per failing mode.
4. Add ZH equivalents for every EN primary that lacks one.
5. Add 3–5 secondary/context triggers per mode.
6. Add negative patterns for the top 2 misroute pairs.
7. Verify confidence formula weights still sum correctly.

**Example**:
```
Before: CREATE keywords: [create, build, new]
After:  CREATE keywords: [create, build, new, generate, scaffold, develop, make, add]
        ZH: [创建, 新建, 生成, 开发, 构建, 制作, 添加]
```

**Estimated F1 gain**: +0.03–0.06 per 3 new primary keywords.

---

### S2 — Strengthen System Design

**Target dimension**: D1 (System Design)
**Estimated delta**: +10 to +25 pts

**Steps**:
1. Check Identity section: name, role, purpose all present?
2. Check design patterns named (Tool Wrapper, Generator, Reviewer, Inversion, Pipeline)?
3. Check Red Lines section: ≥ 3 specific, measurable prohibitions?
4. If any Red Line is vague ("don't do bad things") → replace with CWE or measurable threshold.
5. Add LoongFlow reference if not present.
6. Verify role hierarchy is explicit (who can override whom).

**Red Line quality check**:
```
BAD:  "严禁 unsafe operations"
GOOD: "严禁 hardcoded credentials (CWE-798) — use env var AUTH_TOKEN"
```

---

### S3 — Deepen Domain Knowledge

**Target dimension**: D2 (Domain Knowledge), D5 (Examples)
**Estimated delta**: +15 to +35 pts

**Steps by skill type**:

**api-integration**:
- List all endpoint paths with HTTP methods and purpose.
- Name the specific auth env var (e.g. `OPENWEATHER_API_KEY`).
- List response fields that will be extracted.
- Add realistic field values in examples.

**data-pipeline**:
- Define input schema with field names and types.
- Define output schema with field names and types.
- Specify null handling strategy explicitly.
- Add quarantine threshold (e.g. ≤ 5%).

**workflow-automation**:
- Fill in the workflow steps table completely (all N steps).
- Add rollback action for each mutating step.
- Mark destructive steps explicitly.
- Add estimated duration per step.

**base**:
- Add domain-specific vocabulary to trigger keywords.
- Replace generic "output" descriptions with typed field lists.

---

### S4 — Tighten Workflow Definition

**Target dimension**: D3 (Workflow Definition)
**Estimated delta**: +20 to +40 pts

**Steps**:
1. For each mode section, check: does it have a Phase/Step table?
2. Add exit criteria per phase if missing:
   ```
   BAD:  "3. Execute the task"
   GOOD: "3. EXECUTE | action: call API | exit: HTTP 2xx received"
   ```
3. Add hard checkpoint markers at destructive or irreversible steps.
4. Define loop exit conditions explicitly (SUCCESS, FAIL, HUMAN_REVIEW).
5. Add parallel step annotations where steps can run concurrently.
6. Verify that every "IF error" path leads somewhere (recovery or escalation).

**Phase table template** (copy per mode):
```markdown
| # | Phase | Description | Exit Criteria |
|---|-------|-------------|---------------|
| 1 | PARSE | ... | ... |
| 2 | PLAN  | ... | ... |
| 3 | EXECUTE | ... | ... |
| 4 | VERIFY | ... | ... |
| 5 | DELIVER | ... | ... |
```

---

### S5 — Harden Error Handling

**Target dimension**: D4 (Error Handling)
**Estimated delta**: +15 to +30 pts

**Steps**:
1. List all failure modes relevant to the skill type.
2. For each failure: specify trigger condition, recovery action, escalation path.
3. Set explicit timeout values (e.g. "API timeout: 10 s → retry once → surface error").
4. Add retry logic with max retries and backoff (exponential: 1s, 2s, 4s).
5. Add error output contract per mode.
6. For workflow skills: define rollback sequence for each step.

**Error catalog by type**:

| Error Type | Recovery Pattern |
|-----------|----------------|
| HTTP 4xx | Parse error → human-readable message |
| HTTP 429 | Read `Retry-After` header → wait → retry (max 3) |
| HTTP 5xx | Backoff retry (1s, 2s, 4s) → HUMAN_REVIEW after 3 fails |
| Timeout | Retry once → if fails again → surface error |
| Validation fail | Quarantine record → continue with remaining |
| Security violation | ABORT immediately → log → notify |
| LLM timeout | Degrade to majority vote or baseline check |

---

### S6 — Complete Metadata

**Target dimension**: D6 (Metadata)
**Estimated delta**: +8 to +15 pts

**Steps**:
1. Verify YAML frontmatter has: `name`, `version`, `description`, `description_i18n` (EN+ZH),
   `license`, `author`, `created`, `updated`, `type`, `tags`, `interface`.
2. Check `version` follows semver: `N.N.N`.
3. Check `tags` has ≥ 3 relevant tags.
4. Check `description_i18n.zh` is a real Chinese translation, not just `"todo"`.
5. Update `updated` date to today.
6. Check `interface.modes` matches actual modes in the skill body.
7. Add `extends` block if skill references rubrics/security:
   ```yaml
   extends:
     evaluation:
       metrics: [f1, mrr]
       thresholds: {f1: 0.90, mrr: 0.85}
     security:
       standard: CWE
       scan-on-delivery: true
   ```

---

### S7 — Fix Long-Context Integrity

**Target dimension**: D7 (Long-Context)
**Estimated delta**: +10 to +20 pts

**Steps**:
1. Scan all `§N` section references in the skill — do they point to real sections?
2. Scan all `claude/refs/`, `claude/eval/`, `claude/templates/` references — do files exist?
3. Add cross-references where a section mentions another without linking.
4. If skill > 400 lines: add a Progressive Disclosure table at the top listing sections
   and which ones are loaded on demand.
5. If any section is a stub (< 3 lines), either fill it or mark as "See: `<ref-file>`".
6. Check chunk integrity: if the skill was processed in chunks, verify all sections merged
   correctly and cross-references are consistent.

**Progressive Disclosure table template**:
```markdown
| Section | Loaded When | Size |
|---------|------------|------|
| §1 Identity | Always | Full |
| §2 Mode Router | Always | Full |
| §3 CREATE | On CREATE trigger | Full |
| §N Details | On demand | Lazy |
| claude/refs/deliberation.md | §4 accessed | External |
```

---

### S8 — Full Structural Rebuild

**When to use**: Overall score < 560 after 2 cycles, OR multiple dimensions all < 50%.
Targeted fixes are less efficient than a clean rebuild.

**Steps**:
1. Extract salvageable content: identity description, domain knowledge, any good examples.
2. Select fresh template from `claude/templates/` matching the skill type.
3. Run CREATE mode (§5 of skill-framework.md) with extracted content as pre-filled answers.
4. Port salvaged content into new template draft.
5. Run LEAN eval immediately. If LEAN PASS → full EVALUATE.
6. Version: if original never delivered → keep v1.0.0. If delivered → bump minor: v1.1.0.

**Exit gate**: New skill passes EVALUATE at BRONZE or higher.

---

### S9 — Targeted Metric Boost (Within 0.03 of Threshold)

**When to use**: A single metric barely fails (within 0.03 of threshold). Surgical fix only.

**F1 boost** (F1 between 0.87–0.89):
- Add 2 primary triggers per mode with false negatives (use benchmark failure log).
- Remove 1–2 ambiguous triggers causing false positives.
- Expected gain: +0.01–0.02 F1.

**MRR boost** (MRR between 0.82–0.84):
- Ensure the single most common trigger phrase is the **first** listed primary keyword per mode.
- Reduce number of modes if one mode is essentially never used.
- Expected gain: +0.02–0.04 MRR.

**Trigger accuracy boost** (accuracy 0.87–0.89):
- Add clarification prompts for the 2 most-confused mode pairs.
- Add negative patterns for the most common misroutes.

---

## §5  Strategy Selection Matrix

```
Lowest-scoring dimension → apply strategy
  D1 System Design     → S2
  D2 Domain Knowledge  → S3
  D3 Workflow          → S4
  D4 Error Handling    → S5
  D5 Examples          → S1 (trigger) or S3 (content)
  D6 Metadata          → S6
  D7 Long-Context      → S7
  All < 50%            → S8 (rebuild)
  Single metric fails  → S9 (targeted boost)
```

**Cycle budget**:

| Cycle | Allowed Strategies | Outcome if Still Failing |
|-------|--------------------|--------------------------|
| 1 | S1–S7, S9 | Proceed to Cycle 2 |
| 2 | S1–S7, S9 | Proceed to Cycle 3 |
| 3 | S8 (rebuild) or S9 | If still FAIL → HUMAN_REVIEW |

After 3 cycles at FAIL, or after round 20, stop and escalate.
Log to audit trail: `{"outcome": "HUMAN_REVIEW", "optimize_cycles": 3}`.
