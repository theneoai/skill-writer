"""Bradley-Terry Pairwise Skill Ranking module."""

from __future__ import annotations

import json
import math
import os
import re
from dataclasses import dataclass
from typing import Any


@dataclass
class PairwiseResult:
    """Result of pairwise comparison."""

    winner: str
    confidence: float
    reasoning: str = ""
    position_bias_detected: bool = False
    round1: dict | None = None
    round2: dict | None = None


def bt_estimate(results: list[dict], skill_names: list[str]) -> dict[str, float]:
    """Estimate Bradley-Terry parameters via iterative algorithm.

    Args:
        results: List of {winner, loser} dicts.
        skill_names: List of skill names.

    Returns:
        Dict mapping skill names to beta scores, plus _iterations and _converged.
    """
    n = len(skill_names)
    if n < 2:
        raise ValueError("bt_estimate requires at least 2 skills")

    betas = [1.0] * n
    skill_to_idx = {name: i for i, name in enumerate(skill_names)}

    max_iter = 100
    converged = False

    for _ in range(max_iter):
        old_betas = betas.copy()
        max_delta = 0.0

        for i in range(n):
            wins_i = 0.0
            denom = 0.0

            for k in range(n):
                if k == i:
                    continue

                w_ik = sum(
                    1
                    for r in results
                    if r.get("winner") == skill_names[i] and r.get("loser") == skill_names[k]
                )
                w_ki = sum(
                    1
                    for r in results
                    if r.get("winner") == skill_names[k] and r.get("loser") == skill_names[i]
                )

                total_ik = w_ik + w_ki
                if total_ik > 0:
                    wins_i += w_ik
                    beta_sum = betas[i] + betas[k]
                    denom += total_ik / beta_sum if beta_sum > 0 else 0

            if denom > 0:
                betas[i] = wins_i / denom

            delta = abs(betas[i] - old_betas[i])
            max_delta = max(max_delta, delta)

        beta_sum_total = sum(betas)
        if beta_sum_total > 0:
            for i in range(n):
                betas[i] = betas[i] * n / beta_sum_total

        if max_delta < 0.0001:
            converged = True
            break

    output = {skill_names[i]: round(betas[i], 6) for i in range(n)}
    output["_iterations"] = _
    output["_converged"] = converged

    return output


def _call_llm(system_prompt: str, user_prompt: str) -> str | None:
    """Call LLM API if available.

    Args:
        system_prompt: System prompt.
        user_prompt: User prompt.

    Returns:
        LLM response text or None if unavailable.
    """
    try:
        import subprocess

        provider = os.environ.get("LLM_PROVIDER", "auto")

        cmd = [
            "python3",
            "-c",
            f"""
import json
import subprocess
import os

# Try agent_executor if available
try:
    from skill.eval.agent_executor import agent_call_llm
    result = agent_call_llm({repr(system_prompt)}, {repr(user_prompt)}, "auto", "{provider}")
    print(result)
except Exception as e:
    print(json.dumps({{"error": str(e)}}))
""",
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except Exception:
        pass

    return None


def pairwise_judge(
    skill_a_path: str, skill_b_path: str, task: str, provider: str = "auto"
) -> PairwiseResult:
    """Judge which of two skills is better for a task.

    Args:
        skill_a_path: Path to skill A file.
        skill_b_path: Path to skill B file.
        task: Task description.
        provider: LLM provider (not used in fallback).

    Returns:
        PairwiseResult with winner, confidence, and reasoning.
    """
    try:
        with open(skill_a_path) as f:
            content_a = f.read()
    except (OSError, IOError):
        content_a = ""

    try:
        with open(skill_b_path) as f:
            content_b = f.read()
    except (OSError, IOError):
        content_b = ""

    system_prompt = """You are an impartial skill evaluator. Your job is to judge which of two AI skill
specifications would better help a user accomplish a given task.

Evaluate based on:
1. Relevance: Does the skill's purpose match the task?
2. Completeness: Does it cover what the user needs?
3. Clarity: Are instructions clear and actionable?
4. Reliability: Does it handle edge cases and errors?

Be objective. Ignore formatting preferences. Focus on utility for the user."""

    user_prompt = f"""Task: {task}

=== SKILL A ===
{content_a}

=== SKILL B ===
{content_b}

Which skill would better help a user accomplish the task above?

Respond with JSON only:
{{
  "winner": "A" or "B" or "TIE",
  "confidence": 0.0 to 1.0,
  "reasoning": "brief explanation (1-2 sentences)"
}}"""

    llm_response = _call_llm(system_prompt, user_prompt)

    if llm_response:
        try:
            json_str = llm_response
            match = re.search(r"\{.*\}", json_str, re.DOTALL)
            if match:
                json_str = match.group(0)
            data = json.loads(json_str)
            winner = data.get("winner", "TIE")
            confidence = float(data.get("confidence", 0.5))
            reasoning = data.get("reasoning", "")

            if winner not in ["A", "B", "TIE"]:
                winner = "TIE"

            return PairwiseResult(
                winner=winner,
                confidence=confidence,
                reasoning=reasoning,
            )
        except (json.JSONDecodeError, ValueError, KeyError):
            pass

    return PairwiseResult(
        winner="TIE",
        confidence=0.5,
        reasoning="LLM unavailable",
    )


def pairwise_judge_unbiased(
    skill_a_path: str, skill_b_path: str, task: str, provider: str = "auto"
) -> PairwiseResult:
    """Swap-augmented pairwise judgment to eliminate position bias.

    Args:
        skill_a_path: Path to skill A file.
        skill_b_path: Path to skill B file.
        task: Task description.
        provider: LLM provider.

    Returns:
        PairwiseResult with position_bias_detected flag.
    """
    result1 = pairwise_judge(skill_a_path, skill_b_path, task, provider)
    w1 = result1.winner

    result2_raw = pairwise_judge(skill_b_path, skill_a_path, task, provider)
    w2_raw = result2_raw.winner

    if w2_raw == "A":
        w2 = "B"
    elif w2_raw == "B":
        w2 = "A"
    else:
        w2 = "TIE"

    if w1 == w2:
        final_winner = w1
    elif w1 == "TIE":
        final_winner = w2
    elif w2 == "TIE":
        final_winner = w1
    else:
        final_winner = "UNCERTAIN"

    avg_conf = (result1.confidence + result2_raw.confidence) / 2

    return PairwiseResult(
        winner=final_winner,
        confidence=round(avg_conf, 3),
        reasoning="Swap-augmented comparison",
        position_bias_detected=(final_winner == "UNCERTAIN"),
        round1={"winner": w1, "confidence": result1.confidence},
        round2={"winner": w2_raw, "confidence": result2_raw.confidence},
    )


def rank_skills(task: str, *skill_paths: str) -> str:
    """Rank skills for a given task using pairwise comparisons + BT model.

    Args:
        task: Task description.
        skill_paths: Paths to skill files.

    Returns:
        Formatted ranking string.
    """
    skills = list(skill_paths)
    n = len(skills)

    if n < 2:
        return "ERROR: rank_skills requires at least 2 skill files"

    skill_names = [os.path.basename(s).replace(".md", "") for s in skills]

    output_lines = [f"=== Pairwise Ranking: {n} skills, {n * (n - 1) // 2} comparisons ==="]

    results_json = []

    for i in range(n):
        for j in range(i + 1, n):
            output_lines.append(f"  Comparison {i * n + j}: {skill_names[i]} vs {skill_names[j]}")

            result = pairwise_judge_unbiased(skills[i], skills[j], task)

            winner_name = None
            if result.winner == "A":
                winner_name = skill_names[i]
                loser_name = skill_names[j]
            elif result.winner == "B":
                winner_name = skill_names[j]
                loser_name = skill_names[i]

            if winner_name:
                results_json.append({"winner": winner_name, "loser": loser_name})

    if not results_json:
        bt_scores = {name: 1.0 for name in skill_names}
        bt_scores["_iterations"] = 0
        bt_scores["_converged"] = True
    else:
        bt_scores = bt_estimate(results_json, skill_names)

    output_lines.append("")
    output_lines.append("=== Bradley-Terry Ranking ===")

    scored = [(name, bt_scores[name]) for name in skill_names if name in bt_scores]
    scored.sort(key=lambda x: x[1], reverse=True)

    for rank, (name, score) in enumerate(scored, 1):
        output_lines.append(f"  Rank {rank}: {name}  (β={score:.4f})")

    output_lines.append("")
    output_lines.append("Raw BT scores:")
    for name in skill_names:
        if name in bt_scores:
            output_lines.append(f"  {name}: {bt_scores[name]}")

    return "\n".join(output_lines)
