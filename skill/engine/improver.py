"""LLM-based skill improvement."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable


SYSTEM_PROMPT = """You are an expert SKILL.md editor. Your task is to improve existing SKILL.md files based on improvement suggestions.

Follow the agentskills.io v2.1.0 specification strictly. When modifying a SKILL.md:
1. Preserve existing content unless explicitly told to replace
2. Add missing sections with high-quality content
3. Improve unclear or incomplete sections
4. Add better examples and edge case handling
5. Maintain consistent formatting and style

Output format: Return a JSON object with the improved SKILL.md content as the 'content' field."""


@dataclass
class ImprovementResult:
    content: str

    def to_dict(self) -> dict[str, Any]:
        return {"content": self.content}


class Improver:
    def __init__(
        self,
        llm_caller: Callable[[str, str, str], str] | None = None,
        model: str = "kimi-code",
        evaluator: Callable[[Path, str], dict[str, Any]] | None = None,
    ) -> None:
        self.system_prompt = SYSTEM_PROMPT
        self.llm_caller = llm_caller
        self.model = model
        self.evaluator = evaluator

    def generate(self, summary: str, skill_file: Path) -> ImprovementResult | None:
        if not skill_file.exists():
            return None

        current_content = skill_file.read_text()
        skill_name = skill_file.stem

        prompt = f"""Improve the following SKILL.md file for '{skill_name}' based on this improvement plan:

{summary}

Current SKILL.md content:
{current_content}

Analyze the improvement plan and current content, then produce an improved version.
Return a JSON object: {{"content": "<improved SKILL.md content here>"}}"""

        response = self._call_llm(prompt)
        if response is None:
            return None

        return self._parse_response(response)

    def generate_targeted(
        self,
        skill_file: Path,
        target_section: str,
        improvement_guide: str,
    ) -> ImprovementResult | None:
        if not skill_file.exists():
            return None

        current_content = skill_file.read_text()
        skill_name = skill_file.stem

        prompt = f"""Improve only section §{target_section} of this SKILL.md for '{skill_name}'.

Improvement guide:
{improvement_guide}

Current SKILL.md content:
{current_content}

Return a JSON object: {{"content": "<improved SKILL.md content here>"}}"""

        response = self._call_llm(prompt)
        if response is None:
            return None

        return self._parse_response(response)

    def validate_improvement(
        self,
        original_file: Path,
        improved_file: Path,
    ) -> dict[str, Any] | None:
        if self.evaluator is None:
            return None

        original_result = self.evaluator(original_file, "fast")
        improved_result = self.evaluator(improved_file, "fast")

        original_score = original_result.get("total_score", 0)
        improved_score = improved_result.get("total_score", 0)
        delta = improved_score - original_score

        return {
            "original_score": original_score,
            "improved_score": improved_score,
            "delta": delta,
            "improved_file": str(improved_file),
        }

    def apply_with_validation(
        self,
        skill_file: Path,
        improvements: str,
    ) -> dict[str, Any] | None:
        improved_content = self._extract_content(improvements)
        if not improved_content:
            return None

        temp_file = skill_file.parent / f".improved_{skill_file.name}"
        try:
            temp_file.write_text(improved_content)

            validation = self.validate_improvement(skill_file, temp_file)
            if validation is None:
                return None

            delta = validation["delta"]

            if delta > 0:
                temp_file.rename(skill_file)
                validation["applied"] = True
            else:
                temp_file.unlink()
                validation["applied"] = False

            return validation
        except Exception:
            if temp_file.exists():
                temp_file.unlink()
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

    def _parse_response(self, response: str) -> ImprovementResult | None:
        try:
            data = json.loads(response)
            content = data.get("content", "")
            if not content:
                return None
            return ImprovementResult(content=content)
        except json.JSONDecodeError:
            return None

    def _extract_content(self, improvements: str) -> str | None:
        try:
            data = json.loads(improvements)
            return data.get("content")
        except json.JSONDecodeError:
            return None
