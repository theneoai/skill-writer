from __future__ import annotations

from typing import Any, Literal

from skill.agents.evolution_memory import EvolutionMemory
from skill.agents.trajectory import TrajectoryCollector


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
