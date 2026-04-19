#!/usr/bin/env python3
"""
scripts/aggregate_benchmark.py — Aggregate grader/comparator outputs into benchmark.json.

Supports two input formats:
  - legacy "single" mode: grader JSON with `expectations[]` (agents/grader.md §single)
  - comparative mode:     comparator JSON with `alpha`/`beta` (agents/comparator.md)
    OR the full benchmark.json produced by run_benchmark.py (detected by `per_case` key)

Usage
-----
    # Legacy single-mode graders:
    python3 scripts/aggregate_benchmark.py \\
        --inputs eval/out/tc-*.json \\
        --json-out eval/out/benchmark.json \\
        --md-out  eval/out/benchmark.md

    # Comparative mode (comparator outputs):
    python3 scripts/aggregate_benchmark.py \\
        --inputs benchmarks/run/tc-*.json \\
        --mode comparative \\
        --skill my-skill.md \\
        --json-out benchmarks/run/benchmark.json \\
        --md-out  benchmarks/run/benchmark.md
"""
from __future__ import annotations

import argparse
import glob
import json
import math
import sys
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# Loaders
# ---------------------------------------------------------------------------

def load_files(paths: list[str]) -> list[dict]:
    files: list[str] = []
    for p in paths:
        files.extend(sorted(glob.glob(p)))
    out: list[dict] = []
    for f in files:
        try:
            out.append(json.loads(Path(f).read_text(encoding="utf-8")))
        except (OSError, json.JSONDecodeError) as e:
            print(f"  skip {f}: {e}", file=sys.stderr)
    return out


def detect_format(records: list[dict]) -> str:
    """Return 'comparative', 'benchmark_json', or 'single'."""
    if not records:
        return "single"
    first = records[0]
    if "per_case" in first:
        return "benchmark_json"
    if "alpha" in first and "beta" in first and "winner" in first:
        return "comparative"
    return "single"


# ---------------------------------------------------------------------------
# Aggregation helpers
# ---------------------------------------------------------------------------

def _stdev(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0
    mean = sum(values) / len(values)
    return math.sqrt(sum((v - mean) ** 2 for v in values) / len(values))


# ---------------------------------------------------------------------------
# Comparative aggregation (comparator.md output)
# ---------------------------------------------------------------------------

def aggregate_comparative(records: list[dict], skill: str) -> dict:
    per_case: list[dict] = []
    all_nd_rates: list[float] = []
    all_delta_scores: list[int] = []
    total_tokens_alpha: list[int] = []
    total_tokens_beta: list[int] = []
    total_latency_alpha: list[int] = []
    total_latency_beta: list[int] = []

    alpha_wins = beta_wins = equivalent = 0
    alpha_assertions_passed = alpha_assertions_total = 0
    beta_assertions_passed = beta_assertions_total = 0

    all_nd_assertions: dict[str, list[str]] = {}  # assertion_text -> [test_ids]

    for r in records:
        test_id = r.get("test_id", "unknown")
        winner = r.get("winner", "equivalent")
        delta = r.get("delta_score", 0)
        nd_rate = r.get("non_discriminating_rate", 0.0)

        all_delta_scores.append(int(delta))
        all_nd_rates.append(float(nd_rate))

        if winner == "alpha":
            alpha_wins += 1
        elif winner == "beta":
            beta_wins += 1
        else:
            equivalent += 1

        alpha_score = r.get("alpha", {}).get("score", 0)
        beta_score = r.get("beta", {}).get("score", 0)
        alpha_total = len(r.get("alpha", {}).get("assertions", []))
        beta_total = len(r.get("beta", {}).get("assertions", []))

        alpha_assertions_passed += alpha_score
        alpha_assertions_total += alpha_total
        beta_assertions_passed += beta_score
        beta_assertions_total += beta_total

        # Token metadata (may be present from run_benchmark.py pairing)
        td = r.get("token_data", {})
        for key, lst in [("alpha", total_tokens_alpha), ("beta", total_tokens_beta)]:
            entry = td.get(key, {})
            t = entry.get("tokens_in", 0) + entry.get("tokens_out", 0)
            if t:
                lst.append(t)
        for key, lst in [("alpha", total_latency_alpha), ("beta", total_latency_beta)]:
            entry = td.get(key, {})
            ms = entry.get("elapsed_ms", 0)
            if ms:
                lst.append(ms)

        # Collect non-discriminating assertions across cases
        for pa in r.get("per_assertion_discriminating", []):
            if pa.get("both_passed"):
                # find assertion text from alpha assertions
                for a in r.get("alpha", {}).get("assertions", []):
                    if a.get("id") == pa.get("id"):
                        txt = a.get("evidence", pa.get("id"))
                        # use the id as key since we don't have original text here
                        key_txt = f"assertion:{pa.get('id')}"
                        all_nd_assertions.setdefault(key_txt, []).append(test_id)

        per_case.append({
            "test_id": test_id,
            "winner": winner,
            "winner_margin": r.get("winner_margin", "n/a"),
            "delta_score": delta,
            "alpha_score": alpha_score,
            "beta_score": beta_score,
            "alpha_verdict": r.get("alpha", {}).get("verdict", "unknown"),
            "beta_verdict": r.get("beta", {}).get("verdict", "unknown"),
            "non_discriminating_rate": nd_rate,
            "non_discriminating_count": r.get("non_discriminating_count", 0),
            "notes": r.get("notes", ""),
        })

    n = len(records)
    alpha_pass_rate = round(alpha_assertions_passed / alpha_assertions_total, 3) if alpha_assertions_total else 0.0
    beta_pass_rate = round(beta_assertions_passed / beta_assertions_total, 3) if beta_assertions_total else 0.0
    delta_pass_rate = round(alpha_pass_rate - beta_pass_rate, 3)
    avg_nd_rate = round(sum(all_nd_rates) / n, 3) if n else 0.0
    variance = round(_stdev([float(d) for d in all_delta_scores]), 3)

    avg_tokens_alpha = round(sum(total_tokens_alpha) / len(total_tokens_alpha), 1) if total_tokens_alpha else None
    avg_tokens_beta = round(sum(total_tokens_beta) / len(total_tokens_beta), 1) if total_tokens_beta else None
    token_overhead: Any = None
    token_overhead_pct: Any = None
    if avg_tokens_alpha is not None and avg_tokens_beta and avg_tokens_beta > 0:
        token_overhead = round(avg_tokens_alpha - avg_tokens_beta, 1)
        token_overhead_pct = round((avg_tokens_alpha - avg_tokens_beta) / avg_tokens_beta * 100, 1)

    avg_latency_alpha = round(sum(total_latency_alpha) / len(total_latency_alpha), 1) if total_latency_alpha else None
    avg_latency_beta = round(sum(total_latency_beta) / len(total_latency_beta), 1) if total_latency_beta else None

    # Verdict
    nd_blocked = avg_nd_rate >= 0.50
    if nd_blocked:
        verdict = "BENCHMARK_INCONCLUSIVE"
        verdict_reason = f"non_discriminating_rate={avg_nd_rate:.0%} ≥ 50% — evals not measuring skill impact"
    elif delta_pass_rate >= 0.15 and alpha_pass_rate >= 0.70:
        verdict = "BENCHMARK_PASS"
        verdict_reason = f"delta_pass_rate={delta_pass_rate:.2f} ≥ 0.15 and pass_rate={alpha_pass_rate:.2f} ≥ 0.70"
    elif delta_pass_rate >= 0.05 or alpha_pass_rate >= 0.50:
        verdict = "BENCHMARK_MARGINAL"
        verdict_reason = f"delta_pass_rate={delta_pass_rate:.2f}, pass_rate={alpha_pass_rate:.2f} — marginal improvement"
    else:
        verdict = "BENCHMARK_FAIL"
        verdict_reason = f"delta_pass_rate={delta_pass_rate:.2f} < 0.05 and pass_rate={alpha_pass_rate:.2f} < 0.50"

    nd_assertions_list = [
        {"assertion_id": k, "appears_in_cases": v, "rate": round(len(v) / n, 3)}
        for k, v in all_nd_assertions.items()
        if len(v) / n >= 0.30
    ]

    summary: dict[str, Any] = {
        "total_cases": n,
        "pass_rate": alpha_pass_rate,
        "baseline_pass_rate": beta_pass_rate,
        "delta_pass_rate": delta_pass_rate,
        "alpha_wins": alpha_wins,
        "beta_wins": beta_wins,
        "equivalent": equivalent,
        "non_discriminating_rate": avg_nd_rate,
        "variance": variance,
    }
    if avg_tokens_alpha is not None:
        summary["avg_tokens_with_skill"] = avg_tokens_alpha
        summary["avg_tokens_baseline"] = avg_tokens_beta
        summary["token_overhead"] = token_overhead
        summary["token_overhead_pct"] = token_overhead_pct
    if avg_latency_alpha is not None:
        summary["avg_latency_with_ms"] = avg_latency_alpha
        summary["avg_latency_base_ms"] = avg_latency_beta

    return {
        "skill": skill,
        "format": "comparative",
        "verdict": verdict,
        "verdict_reason": verdict_reason,
        "summary": summary,
        "per_case": per_case,
        "non_discriminating_assertions": nd_assertions_list,
    }


# ---------------------------------------------------------------------------
# Legacy single-mode aggregation (grader.md §single)
# ---------------------------------------------------------------------------

def aggregate_single(graders: list[dict]) -> dict:
    assertion_rows: list[dict] = []
    per_case: list[dict] = []
    for g in graders:
        case_pass = case_total = 0
        for e in g.get("expectations", []):
            case_total += 1
            case_pass += 1 if e.get("passed") else 0
            assertion_rows.append({
                "test_id": g.get("test_id"),
                "assertion": e.get("text"),
                "passed": bool(e.get("passed")),
                "evidence": e.get("evidence", ""),
            })
        per_case.append({
            "test_id": g.get("test_id"),
            "verdict": g.get("verdict"),
            "triggered": bool(g.get("triggered")),
            "assertions_passed": case_pass,
            "assertions_total": case_total,
            "notes": g.get("notes", ""),
        })
    total = len(assertion_rows)
    passed = sum(1 for r in assertion_rows if r["passed"])
    pass_rate = round(passed / total, 3) if total else 0.0
    verdicts = {"pass": 0, "partial": 0, "fail": 0}
    for c in per_case:
        v = c.get("verdict")
        if v in verdicts:
            verdicts[v] += 1
    return {
        "format": "single",
        "n_cases": len(per_case),
        "n_assertions": total,
        "assertions_passed": passed,
        "pass_rate": pass_rate,
        "case_verdicts": verdicts,
        "cases": per_case,
        "assertions": assertion_rows,
    }


# ---------------------------------------------------------------------------
# Passthrough for pre-aggregated benchmark.json
# ---------------------------------------------------------------------------

def aggregate_benchmark_json(records: list[dict]) -> dict:
    if len(records) == 1:
        return records[0]
    # Merge multiple benchmark.json files — just report count
    print(f"  warning: {len(records)} benchmark.json files found; using first", file=sys.stderr)
    return records[0]


# ---------------------------------------------------------------------------
# Markdown rendering
# ---------------------------------------------------------------------------

def to_md_comparative(report: dict) -> str:
    s = report.get("summary", {})
    lines = [
        f"# Benchmark Report — {report.get('skill', 'unknown')}",
        "",
        f"**Verdict**: `{report.get('verdict')}`  ",
        f"**Reason**: {report.get('verdict_reason')}",
        "",
        "## Summary",
        "",
        f"| Metric | Value |",
        f"|--------|-------|",
        f"| Cases | {s.get('total_cases')} |",
        f"| pass_rate (with-skill) | {s.get('pass_rate', 0):.2%} |",
        f"| baseline_pass_rate | {s.get('baseline_pass_rate', 0):.2%} |",
        f"| delta_pass_rate | {s.get('delta_pass_rate', 0):+.2%} |",
        f"| alpha_wins / beta_wins / equiv | {s.get('alpha_wins')} / {s.get('beta_wins')} / {s.get('equivalent')} |",
        f"| non_discriminating_rate | {s.get('non_discriminating_rate', 0):.2%} |",
        f"| variance (δ-score stdev) | {s.get('variance', 0):.3f} |",
    ]
    if s.get("token_overhead_pct") is not None:
        lines += [
            f"| token_overhead_pct | {s.get('token_overhead_pct'):.1f}% |",
            f"| avg_tokens (skill / base) | {s.get('avg_tokens_with_skill')} / {s.get('avg_tokens_baseline')} |",
        ]
    lines += [
        "",
        "## Per-Case Results",
        "",
        "| Test ID | Winner | Margin | Δ Score | α | β | ND Rate | Notes |",
        "|---------|--------|--------|---------|---|---|---------|-------|",
    ]
    for c in report.get("per_case", []):
        lines.append(
            f"| {c['test_id']} | {c['winner']} | {c['winner_margin']} | "
            f"{c['delta_score']:+d} | {c['alpha_score']} | {c['beta_score']} | "
            f"{c['non_discriminating_rate']:.0%} | {str(c.get('notes', ''))[:50]} |"
        )
    nd = report.get("non_discriminating_assertions", [])
    if nd:
        lines += ["", "## Non-Discriminating Assertions (≥ 30% of cases)", ""]
        for item in nd:
            lines.append(f"- `{item['assertion_id']}` — appears in {item['appears_in_cases']} ({item['rate']:.0%})")
    return "\n".join(lines) + "\n"


def to_md_single(report: dict) -> str:
    lines = ["# Benchmark Summary", ""]
    lines.append(f"- Cases: **{report['n_cases']}**")
    lines.append(f"- Assertions: **{report['assertions_passed']} / {report['n_assertions']}** "
                 f"(pass rate {report['pass_rate']:.2%})")
    v = report["case_verdicts"]
    lines.append(f"- Verdicts: pass={v['pass']}  partial={v['partial']}  fail={v['fail']}")
    lines.append("")
    lines.append("## Cases")
    lines.append("")
    lines.append("| Test ID | Verdict | Triggered | Assertions | Notes |")
    lines.append("|---------|---------|-----------|------------|-------|")
    for c in report["cases"]:
        lines.append(
            f"| {c['test_id']} | {c['verdict']} | {c['triggered']} | "
            f"{c['assertions_passed']}/{c['assertions_total']} | {c['notes'][:60]} |"
        )
    return "\n".join(lines) + "\n"


def to_md(report: dict) -> str:
    fmt = report.get("format", "single")
    if fmt == "comparative":
        return to_md_comparative(report)
    return to_md_single(report)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    p = argparse.ArgumentParser(
        description="Aggregate grader/comparator outputs into benchmark.json + benchmark.md"
    )
    p.add_argument("--inputs", nargs="+", required=True,
                   help="Input JSON files (glob patterns accepted)")
    p.add_argument("--mode", choices=["auto", "single", "comparative"], default="auto",
                   help="Input format. 'auto' detects from file content (default)")
    p.add_argument("--skill", default="",
                   help="Skill name for comparative output header")
    p.add_argument("--json-out", default=None)
    p.add_argument("--md-out", default=None)
    args = p.parse_args()

    records = load_files(args.inputs)
    if not records:
        print("no input files matched", file=sys.stderr)
        return 1

    # Determine format
    fmt = args.mode
    if fmt == "auto":
        fmt = detect_format(records)

    if fmt == "benchmark_json":
        report = aggregate_benchmark_json(records)
    elif fmt == "comparative":
        report = aggregate_comparative(records, skill=args.skill)
    else:
        report = aggregate_single(records)

    if args.json_out:
        Path(args.json_out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.json_out).write_text(json.dumps(report, indent=2), encoding="utf-8")
        print(f"wrote {args.json_out}")
    if args.md_out:
        Path(args.md_out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.md_out).write_text(to_md(report), encoding="utf-8")
        print(f"wrote {args.md_out}")

    # Summary line
    fmt_label = report.get("format", "single")
    if fmt_label == "comparative":
        s = report.get("summary", {})
        print(f"  cases={s.get('total_cases')}  "
              f"delta_pass_rate={s.get('delta_pass_rate', 0):+.2%}  "
              f"verdict={report.get('verdict')}  "
              f"nd_rate={s.get('non_discriminating_rate', 0):.0%}")
    else:
        print(f"  cases={report['n_cases']}  "
              f"pass_rate={report['pass_rate']:.2%}  "
              f"verdicts={report.get('case_verdicts', {})}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
