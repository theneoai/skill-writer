from __future__ import annotations

from typing import TYPE_CHECKING, Any

from skill.agents.evolution_memory import EvolutionMemory
from skill.agents.trajectory import TrajectoryCollector

if TYPE_CHECKING:
    from typing import Literal


class AgentAction:
    def __init__(self, action_type: str, content: str, confidence: float = 0.5):
        self.action_type = action_type
        self.content = content
        self.confidence = confidence


class YoutuAgent:
    def __init__(self, memory: EvolutionMemory, exploration_rate: float = 0.1) -> None:
        self.memory = memory
        self.exploration_rate = exploration_rate
        self.collector = TrajectoryCollector()
        self._q_table: dict[tuple[str, str], float] = {}
        self._alpha = 0.1

    def decide_mode(self, context: dict[str, Any]) -> Literal["practice", "rl"]:
        successful = self.memory.get_successful_trajectories(context.get("task_type", ""))
        if len(successful) >= 3:
            return "practice"
        return "rl"

    def practice(self, _task: str, context: dict[str, Any]) -> AgentAction:
        trajectories = self.memory.get_successful_trajectories(context.get("task_type", ""))
        if not trajectories:
            return AgentAction("practice", "no_successful_trajectories", 0.0)

        avg_confidence = min(0.5 + (len(trajectories) * 0.1), 0.95)
        return AgentAction(
            "practice", f"learned_from_{len(trajectories)}_trajectories", avg_confidence
        )

    def rl_step(self, state: dict[str, Any], reward: float) -> AgentAction:
        attempts = state.get("attempts", 0)

        if reward > 0.8:
            return AgentAction("rl", "exploit_high_reward", 0.9)
        if reward > 0.5:
            return AgentAction("rl", "exploit_medium_reward", 0.7)
        return AgentAction("rl", "explore_new_strategy", 0.5 + (self.exploration_rate * attempts))

    def update_q(self, task_type: str, action: str, reward: float) -> None:
        key = (task_type, action)
        current = self._q_table.get(key, 0.0)
        self._q_table[key] = current + self._alpha * (reward - current)
