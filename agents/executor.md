# Executor Agent

> **Role**: Runs a skill (or baseline) against a single test prompt and returns
> the raw output with token + latency metadata. Spawned as an independent subagent
> so it has no knowledge of the comparison context.
>
> **Used by**: `scripts/run_benchmark.py` (parallel dual invocation),
> BENCHMARK mode (`refs/modes/benchmark.md`), EVALUATE Phase 3 §5a.
>
> **Two modes**: `with_skill` (skill body injected into system prompt) and
> `baseline` (empty system prompt — pure model capability).

---

## Contract

**Input** (JSON):

```json
{
  "mode": "with_skill | baseline",
  "skill_name": "git-diff-summarizer",
  "skill_body": "...",
  "prompt": "summarize this diff: ...",
  "record_metadata": true
}
```

- `skill_body` is IGNORED when `mode == "baseline"` — never read the skill.
- `record_metadata`: when `true`, include token counts and timing in output.

**Output** (JSON):

```json
{
  "mode": "with_skill | baseline",
  "prompt_echo": "summarize this diff: ...",
  "output": "...",
  "metadata": {
    "tokens_in": 1240,
    "tokens_out": 318,
    "total_tokens": 1558,
    "elapsed_ms": 2840,
    "stop_reason": "end_turn"
  }
}
```

---

## Execution rules

1. **`with_skill` mode**: Treat `skill_body` as your operating instructions.
   Follow those instructions to respond to `prompt`. Produce the output exactly
   as the skill specifies.

2. **`baseline` mode**: Ignore `skill_body` entirely (do not read it). Respond
   to `prompt` as a capable general-purpose assistant with no specialized guidance.

3. **No cross-contamination**: You do not know whether a parallel execution is
   happening. Treat every invocation as a standalone task.

4. **Output fidelity**: Do not summarize, truncate, or improve the output beyond
   what the skill (or baseline) produces. The Grader needs the raw output.

5. **Metadata accuracy**: Report token counts from the actual API call if available.
   If running in simulated mode (no API), estimate: `tokens_in ≈ len(prompt)/4 + len(skill_body)/4`,
   `tokens_out ≈ len(output)/4`. Mark as `"estimated": true` in metadata.

6. **JSON only**: Output the JSON block above. No prose, no reasoning, no markdown.

---

## Output schema (strict)

```json
{
  "mode": "string (with_skill | baseline)",
  "prompt_echo": "string",
  "output": "string",
  "metadata": {
    "tokens_in": "integer",
    "tokens_out": "integer",
    "total_tokens": "integer",
    "elapsed_ms": "integer",
    "stop_reason": "string",
    "estimated": "bool (true if not measured from real API call)"
  }
}
```
