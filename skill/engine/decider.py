"""Evolution decision engine."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


GOLD_THRESHOLD = 570
SILVER_THRESHOLD = 510
BRONZE_THRESHOLD = 420

CHECK_INTERVAL_HOURS = 24
LAST_CHECK_FILE = Path.home() / ".skill" / "evolution" / "usage" / ".last_evolution_check"


@dataclass
class EvolutionDecision:
    decision: str
    reason: str
    score: float = 0.0
    trigger_f1: float | None = None
    task_rate: float | None = None

    def to_dict(self) -> dict[str, Any]:
        result = {
            "decision": self.decision,
            "reason": self.reason,
            "score": self.score,
        }
        if self.trigger_f1 is not None:
            result["trigger_f1"] = self.trigger_f1
        if self.task_rate is not None:
            result["task_rate"] = self.task_rate
        return result


class EvolutionDecider:
    def __init__(
        self,
        gold_threshold: float = GOLD_THRESHOLD,
        silver_threshold: float = SILVER_THRESHOLD,
        bronze_threshold: float = BRONZE_THRESHOLD,
    ) -> None:
        self.gold_threshold = gold_threshold
        self.silver_threshold = silver_threshold
        self.bronze_threshold = bronze_threshold

    def should_evolve_score(self, current_score: float, force: bool = False) -> EvolutionDecision:
        if force:
            return EvolutionDecision(decision="evolve", reason="forced", score=current_score)

        if current_score < self.gold_threshold:
            reason = f"score_below_gold_{current_score}"
            return EvolutionDecision(
                decision="evolve",
                reason=reason,
                score=current_score,
            )

        return EvolutionDecision(
            decision="skip",
            reason="metrics_ok",
            score=current_score,
        )

    def should_check_scheduled(self) -> bool:
        if not LAST_CHECK_FILE.exists():
            return True

        last_check = LAST_CHECK_FILE.read_text().strip()
        try:
            last_check_epoch = time.mktime(time.strptime(last_check, "%Y-%m-%dT%H:%M:%SZ"))
        except ValueError:
            return True

        now_epoch = time.time()
        hours_elapsed = (now_epoch - last_check_epoch) / 3600
        return hours_elapsed >= CHECK_INTERVAL_HOURS

    def update_last_check(self) -> None:
        LAST_CHECK_FILE.parent.mkdir(parents=True, exist_ok=True)
        LAST_CHECK_FILE.write_text(time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))

    def should_evolve_usage_metrics(
        self,
        trigger_f1: float,
        task_rate: float,
        current_score: float,
    ) -> EvolutionDecision:
        if trigger_f1 < 0.85 or task_rate < 0.80:
            return EvolutionDecision(
                decision="evolve",
                reason="usage_metrics_low",
                score=current_score,
                trigger_f1=trigger_f1,
                task_rate=task_rate,
            )

        return EvolutionDecision(
            decision="skip",
            reason="metrics_ok",
            score=current_score,
            trigger_f1=trigger_f1,
            task_rate=task_rate,
        )

    def get_recommendations(
        self,
        trigger_f1: float,
        task_rate: float,
        avg_feedback: float,
    ) -> list[str]:
        recommendations = []

        if trigger_f1 < 0.90:
            recommendations.append(f"Improve trigger accuracy (current: {trigger_f1:.2f})")

        if task_rate < 0.85:
            recommendations.append(f"Improve task completion rate (current: {task_rate:.2f})")

        if avg_feedback < 3.5 and avg_feedback > 0:
            recommendations.append(f"Address user feedback issues (avg: {avg_feedback:.2f})")

        if not recommendations:
            recommendations.append("All metrics look good, minor refinements only")

        return recommendations

    def should_evolve(
        self,
        skill_file: str | Path,
        force: bool = False,
        current_score: float | None = None,
        trigger_f1: float | None = None,
        task_rate: float | None = None,
        avg_feedback: float | None = None,
    ) -> EvolutionDecision:
        skill_name = Path(skill_file).stem

        if force:
            return EvolutionDecision(decision="evolve", reason="forced", score=current_score or 0)

        if current_score is not None and current_score < self.gold_threshold:
            reason = f"score_below_gold_{current_score}"
            return EvolutionDecision(decision="evolve", reason=reason, score=current_score)

        if self.should_check_scheduled():
            return EvolutionDecision(
                decision="evolve",
                reason="scheduled",
                score=current_score or 0,
            )

        if trigger_f1 is not None and task_rate is not None:
            if trigger_f1 < 0.85 or task_rate < 0.80:
                return EvolutionDecision(
                    decision="evolve",
                    reason="usage_metrics_low",
                    score=current_score or 0,
                    trigger_f1=trigger_f1,
                    task_rate=task_rate,
                )

        return EvolutionDecision(
            decision="skip",
            reason="metrics_ok",
            score=current_score or 0,
            trigger_f1=trigger_f1,
            task_rate=task_rate,
        )
