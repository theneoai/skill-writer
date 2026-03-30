"""GEPA (Generalized Policy Evaluation) trajectory-level scoring."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


class Trajectory(Protocol):
    """Protocol for execution trajectories."""

    steps: list[dict]
    final_state: dict


@dataclass
class GEPAResult:
    """Result of GEPA trajectory evaluation."""

    trajectory_score: float
    step_scores: list[float]
    convergence_indicator: float


class GEPAScorer:
    """GEPA (Generalized Policy Evaluation) scorer for trajectory-level rewards.

    Evaluates complete execution trajectories and computes trajectory-level
    reward scores with convergence indicators.

    Args:
        model: Optional model identifier for scoring.
        gamma: Discount factor in [0, 1] for discounted cumulative reward.
            When ``gamma=1.0`` (default) the score equals the plain sum of
            step rewards (no discounting).  Values below 1 down-weight later
            steps, which is useful when early decisions matter more.
    """

    def __init__(self, model: str | None = None, gamma: float = 1.0) -> None:
        if not 0.0 <= gamma <= 1.0:
            raise ValueError(f"gamma must be in [0, 1], got {gamma}")
        self.model = model
        self.gamma = gamma

    def score_trajectory(self, trajectory: Trajectory) -> GEPAResult:
        """Score a complete execution trajectory.

        Args:
            trajectory: The execution trajectory to evaluate.

        Returns:
            GEPAResult with trajectory score, step scores, and convergence.
        """
        steps = trajectory.steps if hasattr(trajectory, "steps") else trajectory["steps"]
        step_scores = [step.get("reward", 0.0) for step in steps]
        trajectory_score = self.aggregate_step_rewards(step_scores)
        convergence_indicator = self._compute_convergence(step_scores)

        return GEPAResult(
            trajectory_score=trajectory_score,
            step_scores=step_scores,
            convergence_indicator=convergence_indicator,
        )

    def aggregate_step_rewards(self, rewards: list[float]) -> float:
        """Aggregate step rewards into a trajectory-level score.

        Uses discounted cumulative reward (DCR) when ``self.gamma < 1``:

        .. math::
            G = \\sum_{t=0}^{T-1} \\gamma^t \\cdot r_t

        When ``gamma == 1`` this reduces to a plain sum, preserving backward
        compatibility with the original implementation.

        Args:
            rewards: List of step-level reward values.

        Returns:
            Aggregated trajectory score.
        """
        if self.gamma == 1.0:
            return sum(rewards)

        total = 0.0
        discount = 1.0
        for r in rewards:
            total += discount * r
            discount *= self.gamma
        return total

    def _compute_convergence(self, step_scores: list[float]) -> float:
        """Compute convergence indicator based on step score variance."""
        if not step_scores:
            return 0.0

        if len(step_scores) == 1:
            return 1.0

        mean = sum(step_scores) / len(step_scores)
        if (
            not (-1e10 < mean < 1e10)
            or mean == float("nan")
            or mean == float("inf")
            or mean == float("-inf")
        ):
            return 0.0

        variance = sum((s - mean) ** 2 for s in step_scores) / len(step_scores)
        if variance != variance or variance == float("inf") or variance == float("-inf"):
            return 0.0

        max_variance = mean * (1 - mean) if 0.0 < mean < 1.0 else 0.0

        if max_variance == 0:
            return 0.0 if (mean == 0.0 or mean == 1.0) else 1.0

        return max(0.0, 1.0 - variance / max_variance)
