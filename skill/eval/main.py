"""Main evaluation module for skill assessment."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional


@dataclass
class EvalArgs:
    """Parsed evaluation arguments."""

    skill_path: str
    eval_mode: str = "fast"
    corpus_path: str = ""
    output_dir: str = "./eval_results"
    ci_mode: bool = False
    use_agent: str = "auto"
    lang: str = "auto"


def parse_args(args: Optional[list[str]] = None) -> EvalArgs:
    """Parse command line arguments.

    Args:
        args: Command line arguments (defaults to sys.argv[1:])

    Returns:
        Parsed arguments object

    Raises:
        SystemExit: If --skill is not provided
    """
    if args is None:
        args = sys.argv[1:]

    parser = argparse.ArgumentParser(prog="eval")
    parser.add_argument("--skill", required=True, help="Path to SKILL.md file")
    parser.add_argument("--fast", action="store_true", help="Fast evaluation")
    parser.add_argument("--full", action="store_true", help="Full evaluation")
    parser.add_argument("--corpus", help="Custom corpus path")
    parser.add_argument("--output", default="./eval_results", help="Output directory")
    parser.add_argument("--ci", action="store_true", help="CI mode")
    parser.add_argument("--agent", action="store_true", help="Force agent evaluation")
    parser.add_argument("--no-agent", action="store_true", help="Skip agent evaluation")
    parser.add_argument("--lang", default="auto", help="Language (zh|en)")

    parsed = parser.parse_args(args)

    if parsed.fast:
        eval_mode = "fast"
    elif parsed.full:
        eval_mode = "full"
    elif parsed.corpus:
        eval_mode = "custom"
    else:
        eval_mode = "fast"

    if parsed.no_agent:
        use_agent = "skip"
    elif parsed.agent:
        use_agent = "force"
    else:
        use_agent = "auto"

    return EvalArgs(
        skill_path=parsed.skill,
        eval_mode=eval_mode,
        corpus_path=parsed.corpus or "",
        output_dir=parsed.output,
        ci_mode=parsed.ci,
        use_agent=use_agent,
        lang=parsed.lang,
    )


def determine_tier(grand_total: float, variance: float, security_violation: int) -> tuple[str, int]:
    """Determine certification tier based on score and variance.

    Args:
        grand_total: Total score across all phases
        variance: Difference between normalized text and runtime scores
        security_violation: 1 if security issue detected, 0 otherwise

    Returns:
        Tuple of (tier_name, tier_score)
    """
    if security_violation == 1:
        return "REJECTED", 0

    if grand_total >= 950 and variance < 20:
        return "PLATINUM", 30
    if grand_total >= 900 and variance < 50:
        return "GOLD", 25
    if grand_total >= 800 and variance < 80:
        return "SILVER", 20
    if grand_total >= 700 and variance < 150:
        return "BRONZE", 15

    return "NOT_CERTIFIED", 0


def calculate_variance_score(variance: float) -> int:
    """Calculate variance score based on normalized variance.

    Args:
        variance: The variance value (already normalized to per-1000 scale)

    Returns:
        Variance score (0-40)
    """
    if variance < 30:
        return 40
    if variance < 50:
        return 30
    if variance < 70:
        return 20
    if variance < 100:
        return 10
    if variance < 150:
        return 5
    return 0


def run_phase1(skill_path: str, output_dir: str) -> tuple[int, dict]:
    """Run Phase 1: Parse & Validate (100pts).

    Args:
        skill_path: Path to SKILL.md file
        output_dir: Directory for output files

    Returns:
        Tuple of (total_score, details_dict)
    """
    PARSE_YAML_FRONT = 30
    PARSE_THREE_SECTIONS = 30
    PARSE_TRIGGER_LIST = 25
    PARSE_NO_PLACEHOLDERS = 15

    yaml_front = 0
    sections = 0
    trigger_list = 0
    no_placeholder = 0
    security_violation = 0

    with open(skill_path) as f:
        content = f.read()

    if (
        re.search(r"^---", content, re.MULTILINE)
        and re.search(r"^name:", content, re.MULTILINE)
        and re.search(r"^description:", content, re.MULTILINE)
        and re.search(r"^license:", content, re.MULTILINE)
    ):
        yaml_front = PARSE_YAML_FRONT

    s11 = len(re.findall(r"§1\.1|1\.1 Identity|## § 1· Identity", content))
    s12 = len(re.findall(r"§1\.2|1\.2 Framework|## § 2· Framework", content))
    s13 = len(re.findall(r"§1\.3|1\.3 Thinking|## § 3· Thinking", content))

    if s11 > 0:
        sections += 10
    if s12 > 0:
        sections += 10
    if s13 > 0:
        sections += 10

    create_cnt = len(re.findall(r"\*\*CREATE\*\*|CREATE Mode|CREATE.*trigger", content))
    eval_cnt = len(re.findall(r"\*\*EVALUATE\*\*|EVALUATE Mode|EVALUATE.*trigger", content))
    restore_cnt = len(re.findall(r"\*\*RESTORE\*\*|RESTORE Mode|RESTORE.*trigger", content))
    tune_cnt = len(re.findall(r"\*\*TUNE\*\*|TUNE Mode|TUNE.*trigger|OPTIMIZE.*trigger", content))

    if create_cnt >= 1:
        trigger_list += 7
    if eval_cnt >= 1:
        trigger_list += 6
    if restore_cnt >= 1:
        trigger_list += 6
    if tune_cnt >= 1:
        trigger_list += 6

    placeholder_cnt = len(re.findall(r"\[TODO\]|\[FIXME\]|TBD|placeholder|undefined", content))

    if placeholder_cnt == 0:
        no_placeholder = PARSE_NO_PLACEHOLDERS
    elif placeholder_cnt <= 2:
        no_placeholder = 10
    elif placeholder_cnt <= 5:
        no_placeholder = 5

    if re.search(r"sk-[a-zA-Z0-9]{20,}|api[-_]?key.*=.*[\"'][a-zA-Z0-9]", content):
        security_violation = 1

    score = yaml_front + sections + trigger_list + no_placeholder

    details = {
        "yaml_frontmatter": yaml_front,
        "three_sections": sections,
        "trigger_list": trigger_list,
        "no_placeholders": no_placeholder,
        "security_violation": security_violation,
    }

    os.makedirs(output_dir, exist_ok=True)
    with open(os.path.join(output_dir, "phase1.json"), "w") as f:
        json.dump(
            {
                "phase": "parse_validate",
                "score": score,
                "max": 100,
                "details": details,
                "security_violation": security_violation,
            },
            f,
            indent=4,
        )

    return score, details


def generate_summary(
    output_dir: str,
    total: int,
    p1: int,
    p2: int,
    p3: int,
    p4: int,
    tier: str,
    f1_score: float = 0.5,
    mode_accuracy: float = 0.5,
) -> None:
    """Generate summary.json and summary.html reports.

    Args:
        output_dir: Output directory path
        total: Total score
        p1: Phase 1 score
        p2: Phase 2 score
        p3: Phase 3 score
        p4: Phase 4 score
        tier: Certification tier
        f1_score: F1 score metric
        mode_accuracy: Mode accuracy metric
    """
    timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

    summary_data = {
        "framework": "unified-skill-eval",
        "version": "2.0",
        "timestamp": timestamp,
        "total_score": total,
        "max_score": 1000,
        "tier": tier,
        "phases": {
            "parse_validate": p1,
            "text_score": p2,
            "runtime_score": p3,
            "certification": p4,
        },
    }

    with open(os.path.join(output_dir, "summary.json"), "w") as f:
        json.dump(summary_data, f, indent=2)
