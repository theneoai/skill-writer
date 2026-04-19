#!/usr/bin/env python3
"""
scripts/run_benchmark.py — Real parallel A/B benchmark runner.

Spawns two Claude API calls concurrently per test case:
  - Agent A (with-skill):  system prompt = skill body; user prompt = test case
  - Agent B (baseline):    system prompt = empty;       user prompt = test case

Passes both outputs to the Comparator agent (agents/comparator.md) for blind
A/B evaluation, then runs the Analyzer agent (agents/analyzer.md) across all
results to produce actionable recommendations.

This is the direct analogue of Anthropic skill-creator's parallel
Executor + Grader + Comparator + Analyzer pipeline.

Usage
-----
    export ANTHROPIC_API_KEY=...

    # Basic run (JSON test-cases file)
    python3 scripts/run_benchmark.py \\
        --skill path/to/skill.md \\
        --cases path/to/test-cases.json \\
        --out benchmarks/

    # Compare two skill versions
    python3 scripts/run_benchmark.py \\
        --skill-a path/to/skill-v2.md \\
        --skill-b path/to/skill-v1.md \\
        --cases path/to/test-cases.json \\
        --mode compare \\
        --out benchmarks/

    # Dry-run (simulated, no API calls)
    python3 scripts/run_benchmark.py \\
        --skill path/to/skill.md \\
        --cases path/to/test-cases.json \\
        --dry-run

Test-cases JSON format
----------------------
[
  {
    "test_id": "tc-001",
    "prompt": "write a commit message for this diff: ...",
    "assertions": [
      {"id": "a1", "text": "Uses conventional commit type prefix"},
      {"id": "a2", "text": "Subject line ≤ 72 characters"}
    ],
    "type": "should-trigger"
  }
]

Output
------
benchmarks/<ISO-timestamp>/
    benchmark.json      full results with delta metrics
    benchmark.md        human-readable summary

Exit codes: 0 = success, 1 = error, 2 = BENCHMARK_FAIL verdict
"""
from __future__ import annotations

import argparse
import json
import math
import os
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

try:
    import anthropic  # type: ignore
except ImportError:
    anthropic = None

MODEL_DEFAULT = "claude-sonnet-4-6"
MAX_WORKERS = 4          # parallel API calls per batch
TIMEOUT_S = 120          # per-call timeout in seconds

# Tier targets for token overhead
TOKEN_OVERHEAD_TIERS = [
    (30,  "LOW",      "acceptable"),
    (80,  "MODERATE", "note and monitor"),
    (150, "HIGH",     "apply S15 Skill Body Slimming"),
    (float("inf"), "CRITICAL", "block SHARE — must slim before publishing"),
]


# ─── Frontmatter parsing ─────────────────────────────────────────────────────

def parse_frontmatter(path: Path) -> dict:
    """Extract YAML frontmatter fields (name, description) from a skill file."""
    text = path.read_text(encoding="utf-8")
    candidates: list[str] = []
    cursor = 0
    while True:
        m = re.match(r"^---\n(.*?)\n---\n", text[cursor:], re.DOTALL)
        if not m:
            break
        candidates.append(m.group(1))
        cursor += m.end()
    for block in candidates:
        name_m = re.search(r"^name:\s*(.+)$", block, re.MULTILINE)
        desc_m = re.search(r"^description:\s*['\"]?(.+?)['\"]?\s*$", block, re.MULTILINE)
        if name_m and desc_m:
            return {"name": name_m.group(1).strip(), "description": desc_m.group(1).strip()}
    return {}


def read_skill_body(path: Path) -> str:
    """Return full file content (used as system prompt for with-skill agent)."""
    return path.read_text(encoding="utf-8")


def load_agent_prompt(agent_name: str) -> str:
    """Load agent prompt from agents/<name>.md relative to this script."""
    here = Path(__file__).parent.parent
    p = here / "agents" / f"{agent_name}.md"
    if not p.exists():
        return ""
    return p.read_text(encoding="utf-8")


# ─── API execution ───────────────────────────────────────────────────────────

def call_claude(
    client,
    model: str,
    system: str,
    user: str,
    dry_run: bool = False,
) -> dict:
    """Single Claude API call. Returns {output, tokens_in, tokens_out, elapsed_ms}."""
    if dry_run or client is None:
        # Simulated mode: produce plausible placeholder output
        sim_out = f"[SIMULATED] Response to: {user[:80]}..."
        tok_in = max(10, len((system + user).split()) * 1)
        tok_out = max(5, len(sim_out.split()))
        return {
            "output": sim_out,
            "tokens_in": tok_in,
            "tokens_out": tok_out,
            "total_tokens": tok_in + tok_out,
            "elapsed_ms": 0,
            "stop_reason": "simulated",
            "estimated": True,
        }

    t0 = time.monotonic()
    try:
        resp = client.messages.create(
            model=model,
            max_tokens=2048,
            system=system if system else anthropic.NOT_GIVEN,
            messages=[{"role": "user", "content": user}],
        )
    except Exception as exc:
        raise RuntimeError(f"API call failed: {exc}") from exc

    elapsed = int((time.monotonic() - t0) * 1000)
    content = resp.content[0].text if resp.content else ""
    usage = resp.usage
    return {
        "output": content,
        "tokens_in": usage.input_tokens,
        "tokens_out": usage.output_tokens,
        "total_tokens": usage.input_tokens + usage.output_tokens,
        "elapsed_ms": elapsed,
        "stop_reason": resp.stop_reason,
        "estimated": False,
    }


def run_pair(
    client,
    model: str,
    skill_body: str,
    case: dict,
    mode: str = "ab",  # "ab" = with-skill vs baseline; "compare" = skill_a vs skill_b
    skill_b_body: str = "",
    dry_run: bool = False,
) -> dict:
    """Run both agents for one test case concurrently. Returns raw pair result."""
    prompt = case["prompt"]
    system_a = skill_body
    system_b = skill_b_body if mode == "compare" else ""

    with ThreadPoolExecutor(max_workers=2) as pool:
        fut_a = pool.submit(call_claude, client, model, system_a, prompt, dry_run)
        fut_b = pool.submit(call_claude, client, model, system_b, prompt, dry_run)
        result_a = fut_a.result(timeout=TIMEOUT_S)
        result_b = fut_b.result(timeout=TIMEOUT_S)

    return {
        "test_id": case["test_id"],
        "prompt": prompt,
        "assertions": case.get("assertions", []),
        "type": case.get("type", "behavioral"),
        "alpha": result_a,   # with-skill (or skill-a in compare mode)
        "beta":  result_b,   # baseline   (or skill-b in compare mode)
    }


# ─── Comparator invocation ────────────────────────────────────────────────────

def grade_pair(client, model: str, pair: dict, comparator_prompt: str, dry_run: bool) -> dict:
    """Invoke Comparator agent for one pair. Returns comparator JSON."""
    payload = {
        "test_id": pair["test_id"],
        "prompt": pair["prompt"],
        "assertions": pair["assertions"],
        "alpha_output": pair["alpha"]["output"],
        "beta_output":  pair["beta"]["output"],
        "token_data": {
            "alpha": {k: pair["alpha"][k] for k in ("tokens_in", "tokens_out", "elapsed_ms")},
            "beta":  {k: pair["beta"][k]  for k in ("tokens_in", "tokens_out", "elapsed_ms")},
        },
    }
    user_msg = f"Grade this A/B test case:\n\n```json\n{json.dumps(payload, indent=2)}\n```"

    if dry_run or client is None:
        # Synthetic comparator result
        n = len(pair["assertions"])
        return {
            "test_id": pair["test_id"],
            "alpha": {"verdict": "pass", "score": n,
                      "assertions": [{"id": a["id"], "passed": True, "evidence": "[sim]"} for a in pair["assertions"]]},
            "beta":  {"verdict": "fail", "score": 0,
                      "assertions": [{"id": a["id"], "passed": False, "evidence": "[sim]"} for a in pair["assertions"]]},
            "winner": "alpha",
            "winner_margin": "clear",
            "delta_score": n,
            "per_assertion_discriminating": [{"id": a["id"], "discriminating": True, "both_passed": False} for a in pair["assertions"]],
            "non_discriminating_count": 0,
            "non_discriminating_rate": 0.0,
            "notes": "[simulated]",
        }

    result = call_claude(client, model, comparator_prompt, user_msg, dry_run=False)
    raw = result["output"].strip()
    # Extract JSON block if wrapped in markdown
    m = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", raw, re.DOTALL)
    if m:
        raw = m.group(1)
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"test_id": pair["test_id"], "error": "comparator JSON parse failed", "raw": raw[:200]}


# ─── Aggregation ─────────────────────────────────────────────────────────────

def aggregate_results(pairs: list[dict], graded: list[dict], mode: str) -> dict:
    """Compute summary statistics from graded pairs."""
    total = len(graded)
    if total == 0:
        return {}

    alpha_passes = sum(1 for g in graded if g.get("winner") in ("alpha", "equivalent"))
    beta_passes  = sum(1 for g in graded if g.get("winner") in ("beta",  "equivalent"))
    # For A/B mode: alpha = with-skill
    pass_rate      = alpha_passes / total
    baseline_rate  = beta_passes  / total
    delta          = pass_rate - baseline_rate

    # Token stats
    tok_with = [p["alpha"]["total_tokens"] for p in pairs]
    tok_base = [p["beta"]["total_tokens"]  for p in pairs]
    lat_with = [p["alpha"]["elapsed_ms"]   for p in pairs]
    lat_base = [p["beta"]["elapsed_ms"]    for p in pairs]

    avg_tok_with = sum(tok_with) / len(tok_with) if tok_with else 0
    avg_tok_base = sum(tok_base) / len(tok_base) if tok_base else 0
    avg_lat_with = sum(lat_with) / len(lat_with) if lat_with else 0
    avg_lat_base = sum(lat_base) / len(lat_base) if lat_base else 0
    overhead_pct = ((avg_tok_with - avg_tok_base) / avg_tok_base * 100) if avg_tok_base > 0 else 0

    # Non-discriminating rate
    nd_counts = [g.get("non_discriminating_count", 0) for g in graded]
    total_assertions = sum(len(g.get("alpha", {}).get("assertions", [])) for g in graded)
    nd_total = sum(nd_counts)
    nd_rate = nd_total / total_assertions if total_assertions > 0 else 0.0

    # Variance (stdev of per-case delta scores)
    deltas = [g.get("delta_score", 0) for g in graded]
    mean_d = sum(deltas) / len(deltas) if deltas else 0
    variance = math.sqrt(sum((d - mean_d) ** 2 for d in deltas) / len(deltas)) if len(deltas) > 1 else 0.0

    return {
        "total_cases": total,
        "pass_rate": round(pass_rate, 3),
        "baseline_pass_rate": round(baseline_rate, 3),
        "delta_pass_rate": round(delta, 3),
        "avg_tokens_with_skill": round(avg_tok_with),
        "avg_tokens_baseline": round(avg_tok_base),
        "token_overhead": round(avg_tok_with - avg_tok_base),
        "token_overhead_pct": round(overhead_pct, 1),
        "avg_latency_with_ms": round(avg_lat_with),
        "avg_latency_base_ms": round(avg_lat_base),
        "latency_overhead_ms": round(avg_lat_with - avg_lat_base),
        "non_discriminating_rate": round(nd_rate, 3),
        "variance": round(variance, 3),
    }


def compute_verdict(summary: dict) -> tuple[str, str]:
    """BENCHMARK_PASS / MARGINAL / FAIL based on summary."""
    delta = summary.get("delta_pass_rate", 0)
    rate  = summary.get("pass_rate", 0)
    nd    = summary.get("non_discriminating_rate", 0)

    if nd >= 0.50:
        return "BENCHMARK_INCONCLUSIVE", f"non_discriminating_rate={nd:.0%} ≥ 50% — evals not measuring skill impact"
    if delta >= 0.15 and rate >= 0.70:
        return "BENCHMARK_PASS", f"delta={delta:+.0%} ≥ 15%, pass_rate={rate:.0%} ≥ 70%"
    if delta >= 0.05 or rate >= 0.50:
        return "BENCHMARK_MARGINAL", f"delta={delta:+.0%} or pass_rate={rate:.0%} is marginal"
    return "BENCHMARK_FAIL", f"delta={delta:+.0%} < 5% and pass_rate={rate:.0%} < 50% — skill provides no reliable benefit"


def token_overhead_label(pct: float) -> str:
    for threshold, label, _ in TOKEN_OVERHEAD_TIERS:
        if pct <= threshold:
            return label
    return "CRITICAL"


# ─── Analyzer invocation ──────────────────────────────────────────────────────

def run_analyzer(client, model: str, benchmark: dict, analyzer_prompt: str, dry_run: bool) -> dict:
    """Invoke Analyzer agent with the full benchmark.json."""
    if dry_run or client is None or not analyzer_prompt:
        return {"note": "analyzer skipped (dry-run or no prompt)", "recommendations": []}

    user_msg = f"Analyze this benchmark result:\n\n```json\n{json.dumps(benchmark, indent=2)}\n```"
    result = call_claude(client, model, analyzer_prompt, user_msg, dry_run=False)
    raw = result["output"].strip()
    m = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", raw, re.DOTALL)
    if m:
        raw = m.group(1)
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"error": "analyzer JSON parse failed", "raw": raw[:400]}


# ─── Report generation ────────────────────────────────────────────────────────

def build_benchmark_json(
    skill_meta: dict,
    skill_version: str,
    run_mode: str,
    model: str,
    dry_run: bool,
    summary: dict,
    verdict: str,
    verdict_reason: str,
    pairs: list[dict],
    graded: list[dict],
    analysis: dict,
) -> dict:
    per_case = []
    for pair, grade in zip(pairs, graded):
        per_case.append({
            "test_id": pair["test_id"],
            "prompt": pair["prompt"][:200],
            "type": pair.get("type", "behavioral"),
            "assertions": pair["assertions"],
            "alpha": {
                "verdict": grade.get("alpha", {}).get("verdict", "unknown"),
                "score":   grade.get("alpha", {}).get("score", 0),
                "tokens_in":  pair["alpha"]["tokens_in"],
                "tokens_out": pair["alpha"]["tokens_out"],
                "elapsed_ms": pair["alpha"]["elapsed_ms"],
                "estimated":  pair["alpha"].get("estimated", False),
            },
            "beta": {
                "verdict": grade.get("beta", {}).get("verdict", "unknown"),
                "score":   grade.get("beta", {}).get("score", 0),
                "tokens_in":  pair["beta"]["tokens_in"],
                "tokens_out": pair["beta"]["tokens_out"],
                "elapsed_ms": pair["beta"]["elapsed_ms"],
                "estimated":  pair["beta"].get("estimated", False),
            },
            "winner":        grade.get("winner", "unknown"),
            "winner_margin": grade.get("winner_margin", "n/a"),
            "delta_score":   grade.get("delta_score", 0),
            "non_discriminating_count": grade.get("non_discriminating_count", 0),
            "non_discriminating_rate":  grade.get("non_discriminating_rate", 0.0),
        })

    return {
        "skill":           skill_meta.get("name", "unknown"),
        "skill_version":   skill_version,
        "benchmark_version": "3.5.0",
        "timestamp":       datetime.now(timezone.utc).isoformat(),
        "mode":            "simulated" if dry_run else "real",
        "run_mode":        run_mode,
        "model":           model,
        "summary":         summary,
        "verdict":         verdict,
        "verdict_reason":  verdict_reason,
        "token_overhead_label": token_overhead_label(summary.get("token_overhead_pct", 0)),
        "per_case":        per_case,
        "analysis":        analysis,
    }


def to_markdown(bm: dict) -> str:
    s = bm["summary"]
    lines = [
        "# Benchmark Report",
        "",
        f"**Skill**: {bm['skill']} v{bm['skill_version']}  ",
        f"**Date**: {bm['timestamp'][:10]}  ",
        f"**Mode**: {bm['mode']} ({bm['run_mode']})  ",
        f"**Model**: {bm['model']}",
        "",
        f"## Verdict: {bm['verdict']}",
        f"> {bm['verdict_reason']}",
        "",
        "## Summary",
        "",
        "| Metric | With-Skill | Baseline | Delta |",
        "|--------|-----------|---------|-------|",
        f"| Pass Rate | {s['pass_rate']:.0%} | {s['baseline_pass_rate']:.0%} | {s['delta_pass_rate']:+.0%} |",
        f"| Avg Tokens | {s['avg_tokens_with_skill']:,} | {s['avg_tokens_baseline']:,} | +{s['token_overhead']:,} ({s['token_overhead_pct']:+.0f}%) |",
        f"| Avg Latency (ms) | {s['avg_latency_with_ms']:,} | {s['avg_latency_base_ms']:,} | +{s['latency_overhead_ms']:,} |",
        f"| Non-discriminating rate | {s['non_discriminating_rate']:.0%} | — | — |",
        "",
        "## Per-Case Results",
        "",
        "| Test ID | Winner | Delta Score | Alpha Verdict | Beta Verdict | ND Rate |",
        "|---------|--------|------------|--------------|-------------|---------|",
    ]
    for c in bm["per_case"]:
        lines.append(
            f"| {c['test_id']} | {c['winner']} | {c['delta_score']:+d} "
            f"| {c['alpha']['verdict']} | {c['beta']['verdict']} "
            f"| {c['non_discriminating_rate']:.0%} |"
        )
    lines.append("")

    # Recommendations from analysis
    recs = bm.get("analysis", {}).get("recommendations", [])
    if recs:
        lines += ["## Recommendations", ""]
        for r in recs:
            lines.append(f"{r['priority']}. **[{r['type'].upper()}]** {r['action']}")
            lines.append(f"   Strategy: {r['strategy']} | Expected: {r['expected_delta']} | Effort: {r['effort']}")
            lines.append("")

    opt_cmd = bm.get("analysis", {}).get("optimize_command", "")
    if opt_cmd:
        lines += ["## Next Steps", "", f"```bash", f"{opt_cmd}", "```", ""]

    return "\n".join(lines)


# ─── Main ─────────────────────────────────────────────────────────────────────

def main() -> int:
    p = argparse.ArgumentParser(description="Run parallel A/B benchmark for a skill.")
    p.add_argument("--skill",   help="Path to skill .md file (A/B mode)")
    p.add_argument("--skill-a", help="Path to skill A .md file (compare mode)")
    p.add_argument("--skill-b", help="Path to skill B .md file (compare mode)")
    p.add_argument("--cases",   required=True, help="Path to test-cases JSON file")
    p.add_argument("--out",     default="benchmarks", help="Output directory")
    p.add_argument("--mode",    choices=["ab", "compare"], default="ab",
                   help="ab: skill vs baseline; compare: skill-a vs skill-b")
    p.add_argument("--model",   default=MODEL_DEFAULT)
    p.add_argument("--workers", type=int, default=MAX_WORKERS)
    p.add_argument("--skill-version", default="unknown")
    p.add_argument("--dry-run", action="store_true", help="Simulate API calls (no key needed)")
    args = p.parse_args()

    # Validate inputs
    if args.mode == "ab" and not args.skill:
        p.error("--skill required for ab mode")
    if args.mode == "compare" and (not args.skill_a or not args.skill_b):
        p.error("--skill-a and --skill-b required for compare mode")

    # Load skill(s)
    skill_path = Path(args.skill) if args.skill else Path(args.skill_a)
    skill_body   = read_skill_body(skill_path)
    skill_b_body = read_skill_body(Path(args.skill_b)) if args.mode == "compare" else ""
    skill_meta   = parse_frontmatter(skill_path)
    skill_version = args.skill_version or skill_meta.get("version", "unknown")

    # Load test cases
    cases = json.loads(Path(args.cases).read_text(encoding="utf-8"))
    print(f"Loaded {len(cases)} test cases from {args.cases}")

    # Load agent prompts
    comparator_prompt = load_agent_prompt("comparator")
    analyzer_prompt   = load_agent_prompt("analyzer")

    # Init client
    client = None
    if not args.dry_run:
        api_key = os.environ.get("ANTHROPIC_API_KEY", "")
        if not api_key:
            print("WARNING: ANTHROPIC_API_KEY not set — falling back to dry-run mode",
                  file=sys.stderr)
            args.dry_run = True
        elif anthropic is None:
            print("ERROR: anthropic package not installed. Run: pip install anthropic",
                  file=sys.stderr)
            return 1
        else:
            client = anthropic.Anthropic(api_key=api_key)

    mode_label = "simulated" if args.dry_run else "real"
    print(f"Running {len(cases)} cases in {mode_label} {args.mode} mode "
          f"(model={args.model}, workers={args.workers})")

    # Run all pairs
    pairs: list[dict] = []
    errors: list[str] = []

    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {
            pool.submit(run_pair, client, args.model, skill_body, case,
                        args.mode, skill_b_body, args.dry_run): case
            for case in cases
        }
        for fut in as_completed(futures):
            case = futures[fut]
            try:
                pairs.append(fut.result(timeout=TIMEOUT_S + 10))
                print(f"  ✓ {case['test_id']}")
            except Exception as exc:
                errors.append(f"{case['test_id']}: {exc}")
                print(f"  ✗ {case['test_id']}: {exc}", file=sys.stderr)

    if not pairs:
        print("No pairs completed. Exiting.", file=sys.stderr)
        return 1

    # Sort by test_id for deterministic output
    pairs.sort(key=lambda x: x["test_id"])

    # Grade all pairs
    print(f"\nGrading {len(pairs)} pairs with Comparator agent...")
    graded: list[dict] = []
    for pair in pairs:
        g = grade_pair(client, args.model, pair, comparator_prompt, args.dry_run)
        graded.append(g)
        winner = g.get("winner", "?")
        print(f"  {pair['test_id']}: winner={winner}, nd_rate={g.get('non_discriminating_rate', 0):.0%}")

    # Aggregate
    summary = aggregate_results(pairs, graded, args.mode)
    verdict, verdict_reason = compute_verdict(summary)

    # Analyzer
    print(f"\nRunning Analyzer agent...")
    bm_partial = {"skill": skill_meta.get("name", "?"), "summary": summary, "per_case": []}
    analysis = run_analyzer(client, args.model, bm_partial, analyzer_prompt, args.dry_run)

    # Build final benchmark.json
    bm = build_benchmark_json(
        skill_meta, skill_version, args.mode, args.model, args.dry_run,
        summary, verdict, verdict_reason, pairs, graded, analysis,
    )

    # Write outputs
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%SZ")
    out_dir = Path(args.out) / ts
    out_dir.mkdir(parents=True, exist_ok=True)

    json_path = out_dir / "benchmark.json"
    md_path   = out_dir / "benchmark.md"
    json_path.write_text(json.dumps(bm, indent=2), encoding="utf-8")
    md_path.write_text(to_markdown(bm), encoding="utf-8")

    print(f"\n{'='*60}")
    print(f"Verdict: {verdict}")
    print(f"Reason:  {verdict_reason}")
    print(f"Pass rate:     {summary['pass_rate']:.0%}  (baseline: {summary['baseline_pass_rate']:.0%})")
    print(f"Delta:         {summary['delta_pass_rate']:+.0%}")
    print(f"Token overhead:{summary['token_overhead_pct']:+.0f}%  ({token_overhead_label(summary['token_overhead_pct'])})")
    print(f"ND rate:       {summary['non_discriminating_rate']:.0%}")
    if errors:
        print(f"Errors: {len(errors)} cases failed — see stderr")
    print(f"\nOutputs: {json_path}  {md_path}")

    # Recommendations summary
    recs = analysis.get("recommendations", [])
    if recs:
        print("\nTop recommendations:")
        for r in recs[:3]:
            print(f"  {r['priority']}. [{r['effort']}] {r['action']}")

    return 2 if verdict == "BENCHMARK_FAIL" else 0


if __name__ == "__main__":
    sys.exit(main())
