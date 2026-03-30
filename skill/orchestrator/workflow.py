from __future__ import annotations

from pathlib import Path
from typing import Any

from skill.orchestrator.state import get_orchestrator_state


class WorkflowOrchestrator:
    def __init__(self) -> None:
        self.state = get_orchestrator_state()
        self.evaluator_feedback: str = ""

    def init_workflow(
        self, user_prompt: str, output_file: str, parent_skill: str | None = None
    ) -> None:
        self.state.set_prompt(user_prompt)
        self.state.set_target_file(output_file)

        Path(output_file).parent.mkdir(parents=True, exist_ok=True)

        if parent_skill:
            pass

        print(f"Workflow initialized: {output_file}")
        print(f"Target tier: {self.state.target_tier}")

    def run_creator(self, evaluator_feedback: str = "") -> str | None:
        return ""

    def run_evaluator(self) -> dict[str, Any] | None:
        return None

    def append_content(self, new_content: str) -> bool:
        if not new_content or new_content == "{}":
            return False

        if self.state.dry_run == 1:
            print(f"[DRY RUN] Would append content to {self.state.target_skill_file}")
            return True

        with open(self.state.target_skill_file, "a") as f:
            f.write(f"\n{new_content}")
        return True

    def get_next_action(self, score: int, tier: str) -> str:
        from skill.orchestrator.actions import get_actions_orchestrator

        actions = get_actions_orchestrator()
        return actions.get_next_action(score, tier)

    def check_evolution_trigger(self) -> bool:
        from skill.orchestrator.actions import get_actions_orchestrator

        actions = get_actions_orchestrator()
        return actions.check_evolution_trigger()

    def trigger_evolution(self) -> None:
        print("Evolution triggered")

    def run_workflow(self) -> dict[str, Any]:
        if self.state.dry_run == 1:
            print("DRY RUN MODE - No changes will be made")

        while True:
            self.state.inc_iteration()
            print(
                f"\n=== Iteration {self.state.iteration_count} (Section {self.state.current_section}) ==="
            )

            new_content = self.run_creator(self.evaluator_feedback)

            if new_content:
                self.append_content(new_content)

            eval_result = self.run_evaluator()

            if eval_result:
                score = eval_result.get("score", 0)
                tier = eval_result.get("tier", "UNKNOWN")
                suggestions = eval_result.get("suggestions", "")

                self.state.inc_evaluation()
                self.state.set_last_score(score)

                print(f"  Score: {score} ({tier})")

                action = self.get_next_action(score, tier)

                if action == "done":
                    print("  Completion reached")
                    break
                if action == "continue":
                    self.state.inc_section()
                    self.evaluator_feedback = ""
                    continue
                if action == "improve":
                    self.evaluator_feedback = suggestions
                    if self.check_evolution_trigger():
                        print("  Evolution triggered")
                        self.trigger_evolution()
                    continue

            else:
                self.evaluator_feedback = "Please fix the format and content issues."

            if self.state.iteration_count >= self.state.max_iterations:
                print("Max iterations reached")
                break

        return self.final_evaluate()

    def final_evaluate(self) -> dict[str, Any]:
        result = {
            "final_score": 0,
            "final_tier": "UNKNOWN",
            "iterations": self.state.iteration_count,
        }

        print("\n=== Final Result ===")
        print(f"Score: {result['final_score']}")
        print(f"Tier: {result['final_tier']}")

        return result
