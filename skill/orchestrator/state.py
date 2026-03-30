from __future__ import annotations
from typing import Any


_orchestrator_state: OrchestratorState | None = None


class OrchestratorState:
    def __init__(self) -> None:
        self.initial_prompt: str = ""
        self.target_skill_file: str = ""
        self.target_tier: str = "BRONZE"
        self.max_iterations: int = 20
        self.current_section: int = 0
        self.evaluation_count: int = 0
        self.last_score: int = 0
        self.iteration_count: int = 0
        self.creator_sourced: int = 0
        self.evaluator_sourced: int = 0
        self.dry_run: int = 0
        self.verbose: int = 0

    def set_prompt(self, prompt: str) -> None:
        self.initial_prompt = prompt

    def set_target_file(self, path: str) -> None:
        self.target_skill_file = path

    def set_tier(self, tier: str) -> None:
        self.target_tier = tier

    def inc_iteration(self) -> None:
        self.iteration_count += 1

    def inc_evaluation(self) -> None:
        self.evaluation_count += 1

    def inc_section(self) -> None:
        self.current_section += 1

    def set_last_score(self, score: int) -> None:
        self.last_score = score

    def get_context(self) -> dict[str, Any]:
        return {
            "user_prompt": self.initial_prompt,
            "current_section": self.current_section,
            "target_tier": self.target_tier,
            "iteration": self.iteration_count,
            "eval_count": self.evaluation_count,
        }

    def dump(self) -> str:
        return "\n".join(
            [
                "=== State ===",
                f"PROMPT: {self.initial_prompt}",
                f"TARGET: {self.target_skill_file}",
                f"TIER: {self.target_tier}",
                f"SECTION: {self.current_section}",
                f"EVAL_COUNT: {self.evaluation_count}",
                f"LAST_SCORE: {self.last_score}",
                f"ITERATION: {self.iteration_count}",
                "===========",
            ]
        )


def get_orchestrator_state() -> OrchestratorState:
    global _orchestrator_state
    if _orchestrator_state is None:
        _orchestrator_state = OrchestratorState()
    return _orchestrator_state
