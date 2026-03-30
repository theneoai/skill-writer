"""LLM-based summarization for skill improvement."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Callable


SYSTEM_PROMPT = """You are an expert AI skill architect specializing in synthesizing analysis findings into actionable improvement plans.

Your task is to take analysis results and create a clear, prioritized summary that can be used to improve a SKILL.md file."""


@dataclass
class SummaryResult:
    priority_issues: list[dict[str, Any]]
    key_findings: list[str]
    improvement_plan: list[dict[str, Any]]
    expected_impact: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "priority_issues": self.priority_issues,
            "key_findings": self.key_findings,
            "improvement_plan": self.improvement_plan,
            "expected_impact": self.expected_impact,
        }


class Summarizer:
    def __init__(
        self,
        llm_caller: Callable[[str, str, str], str] | None = None,
        model: str = "kimi-code",
    ) -> None:
        self.system_prompt = SYSTEM_PROMPT
        self.llm_caller = llm_caller
        self.model = model

    def summarize(self, analysis: str, skill_name: str) -> SummaryResult | None:
        prompt = f"""Summarize the following analysis for skill '{skill_name}' into a prioritized improvement plan:

{analysis}

Provide a JSON summary with:
1. priority_issues: Array of {{issue, section, severity}} sorted by severity
2. key_findings: Array of main insights from the analysis
3. improvement_plan: Array of {{action, section, rationale}} in priority order
4. expected_impact: Description of how improvements will affect scores"""

        response = self._call_llm(prompt)
        if response is None:
            return None

        try:
            data = json.loads(response)
            return SummaryResult(
                priority_issues=data.get("priority_issues", []),
                key_findings=data.get("key_findings", []),
                improvement_plan=data.get("improvement_plan", []),
                expected_impact=data.get("expected_impact", ""),
            )
        except (json.JSONDecodeError, KeyError):
            return None

    def summarize_for_human(self, analysis: str, skill_name: str) -> str | None:
        prompt = f"""Create a human-readable summary of the analysis for skill '{skill_name}'.

Analysis:
{analysis}

Provide a concise summary covering:
1. Current state assessment
2. Top 3 priority improvements
3. Expected outcome"""

        return self._call_llm(prompt)

    def extract_key_insights(self, analysis: str) -> list[str] | None:
        prompt = f"""Extract the 3-5 most critical insights from this analysis:

{analysis}

Format as a JSON array of strings, each being one key insight."""

        response = self._call_llm(prompt)
        if response is None:
            return None

        try:
            data = json.loads(response)
            if isinstance(data, list):
                return data
            return []
        except json.JSONDecodeError:
            return None

    def _call_llm(self, user_prompt: str) -> str | None:
        if self.llm_caller is None:
            return None
        try:
            response = self.llm_caller(self.system_prompt, user_prompt, self.model)
            if not response or response.startswith("ERROR:"):
                return None
            return response
        except Exception:
            return None
