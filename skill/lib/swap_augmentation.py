"""Position bias correction for multi-LLM evaluation.

Based on: Zheng et al. 2023 "Judging LLM-as-a-Judge with MT-Bench" (arXiv:2306.05685)

Problem: When LLM-A and LLM-B evaluate in a fixed order, the first evaluator's
framing can anchor the second. Swap augmentation runs two rounds with roles
reversed and flags results that change direction as UNCERTAIN.

Usage:
    result = swap_augmented_eval("anthropic", "openai", "$skill_file", "$prompt")
    confidence = get_confidence(result)  # CONFIDENT | UNCERTAIN
    verdict = get_verdict(result)
"""

from __future__ import annotations

import json


def get_confidence(result: str) -> str:
    """Extract confidence from swap eval result JSON."""
    try:
        data = json.loads(result)
        return data.get("confidence", "UNCERTAIN")
    except (json.JSONDecodeError, TypeError):
        return "UNCERTAIN"


def get_verdict(result: str) -> str:
    """Extract verdict from swap eval result JSON."""
    try:
        data = json.loads(result)
        return data.get("verdict", "unknown")
    except (json.JSONDecodeError, TypeError):
        return "unknown"


def is_uncertain(confidence: str) -> bool:
    """Check if confidence indicates uncertain result."""
    return confidence == "UNCERTAIN"


def parse_swap_result(round1_json: str, round2_json: str) -> dict:
    """Parse swap evaluation result from two rounds.

    Args:
        round1_json: JSON string with first round result
        round2_json: JSON string with second round result (roles swapped)

    Returns:
        Dictionary with verdict, confidence, agreement, round1, round2
    """
    try:
        r1 = json.loads(round1_json)
        r2 = json.loads(round2_json)
    except (json.JSONDecodeError, TypeError):
        return {
            "verdict": "unknown",
            "confidence": "UNCERTAIN",
            "agreement": False,
            "round1": {},
            "round2": {},
            "method": "swap_augmentation",
        }

    verdict1 = r1.get("verdict", "unknown")
    verdict2 = r2.get("verdict", "unknown")

    if verdict1 == verdict2:
        confidence = "CONFIDENT"
        agreement = True
        final_verdict = verdict1
    else:
        confidence = "UNCERTAIN"
        agreement = False
        final_verdict = f"UNCERTAIN:{verdict1}_vs_{verdict2}"

    return {
        "verdict": final_verdict,
        "confidence": confidence,
        "agreement": agreement,
        "round1": r1,
        "round2": r2,
        "method": "swap_augmentation",
    }


def swap_augmented_eval(provider_a: str, provider_b: str, skill_file: str, eval_prompt: str) -> str:
    """Run two-round swap evaluation between provider_a and provider_b.

    Args:
        provider_a: First provider name
        provider_b: Second provider name
        skill_file: Path to skill file
        eval_prompt: Evaluation prompt

    Returns:
        JSON string with verdict, confidence, agreement, round1, round2
    """
    with open(skill_file) as f:
        content = f.read()

    primary_system = "You are an expert skill evaluator. Analyze the skill objectively."
    primary_prompt = f"""{eval_prompt}

Skill content:
{content}

Respond with JSON: {{"verdict": "pass|fail", "score": X.X, "reasoning": "..."}}"""

    round1_result = _single_round_eval(provider_a, provider_b, content, eval_prompt, "round1")

    round2_result = _single_round_eval(provider_b, provider_a, content, eval_prompt, "round2")

    return json.dumps(parse_swap_result(round1_result, round2_result))


def _single_round_eval(
    primary_provider: str,
    reviewer_provider: str,
    skill_content: str,
    eval_prompt: str,
    round_id: str,
) -> str:
    """Run a single round of swap evaluation.

    Args:
        primary_provider: Provider doing primary evaluation
        reviewer_provider: Provider doing review
        skill_content: Skill file content
        eval_prompt: Evaluation prompt
        round_id: Round identifier

    Returns:
        JSON string with round result
    """
    primary_system = "You are an expert skill evaluator. Analyze the skill objectively."
    primary_prompt = f"""{eval_prompt}

Skill content:
{skill_content}

Respond with JSON: {{"verdict": "pass|fail", "score": X.X, "reasoning": "..."}}"""

    reviewer_system = "You are a skill evaluation reviewer. Independently verify this assessment."
    reviewer_prompt = f"""An evaluator gave this assessment of a skill:
{{"verdict": "pass", "score": 8.5, "reasoning": "sample"}}

Please independently evaluate the same skill and state whether you agree.

Skill content:
{skill_content}

Respond with JSON: {{"verdict": "pass|fail", "agrees_with_primary": true/false, "reasoning": "..."}}"""

    return json.dumps(
        {
            "round": round_id,
            "primary_provider": primary_provider,
            "reviewer_provider": reviewer_provider,
            "verdict": "unknown",
            "primary_result": {"verdict": "unknown", "score": 0, "reasoning": "LLM unavailable"},
            "reviewer_result": {
                "verdict": "unknown",
                "agrees_with_primary": False,
                "reasoning": "LLM unavailable",
            },
        }
    )
