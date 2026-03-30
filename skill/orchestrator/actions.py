from __future__ import annotations

import sys

from skill.orchestrator.state import get_orchestrator_state


EVOLUTION_THRESHOLD_NEW = 10
EVOLUTION_THRESHOLD_GROWING = 50
EVOLUTION_THRESHOLD_STABLE = 100


_actions_orchestrator: ActionsOrchestrator | None = None


class ActionsOrchestrator:
    def __init__(self) -> None:
        self.state = get_orchestrator_state()
        self.verbose = self.state.verbose

    def get_next_action(self, score: int, tier: str) -> str:
        if tier == "PLATINUM":
            return "done"
        if tier == "GOLD" and score >= 900:
            return "done"
        if tier == "SILVER" and score >= 800:
            return "done"
        if tier == "BRONZE" and score >= 700:
            return "done"
        if self.state.iteration_count >= self.state.max_iterations:
            return "done"
        if score > self.state.last_score:
            return "continue"
        return "improve"

    def check_evolution_trigger(self) -> bool:
        eval_count = self.state.evaluation_count

        if eval_count < 10:
            threshold = EVOLUTION_THRESHOLD_NEW
        elif eval_count < 50:
            threshold = EVOLUTION_THRESHOLD_GROWING
        else:
            threshold = EVOLUTION_THRESHOLD_STABLE

        return eval_count > 0 and eval_count % threshold == 0

    def trigger_evolution(self) -> None:
        print("Evolution skipped: engine busy")

    def log_usage(self, skill_name: str, score: int, tier: str, iterations: int) -> None:
        pass

    def log_verbose(self, message: str) -> None:
        if self.verbose == 1:
            print(f"[VERBOSE] {message}", file=sys.stderr)


def get_actions_orchestrator() -> ActionsOrchestrator:
    global _actions_orchestrator
    if _actions_orchestrator is None:
        _actions_orchestrator = ActionsOrchestrator()
    return _actions_orchestrator
