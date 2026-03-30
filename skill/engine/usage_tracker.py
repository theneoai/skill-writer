"""Usage tracking for skill evolution."""

from __future__ import annotations

import json
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass
class UsageSummary:
    total_triggers: int
    correct_triggers: int
    total_tasks: int
    completed_tasks: int
    total_feedback: int
    avg_feedback_rating: float

    @property
    def trigger_f1(self) -> float:
        if self.total_triggers == 0:
            return 0.0
        return self.correct_triggers / self.total_triggers

    @property
    def task_completion_rate(self) -> float:
        if self.total_tasks == 0:
            return 0.0
        return self.completed_tasks / self.total_tasks

    def to_dict(self) -> dict[str, Any]:
        return {
            "trigger_f1": self.trigger_f1,
            "task_completion_rate": self.task_completion_rate,
            "avg_feedback_rating": self.avg_feedback_rating,
            "stats": {
                "triggers": {"total": self.total_triggers, "correct": self.correct_triggers},
                "tasks": {"total": self.total_tasks, "completed": self.completed_tasks},
                "feedback": {"count": self.total_feedback},
            },
        }


class UsageTracker:
    def __init__(self, base_dir: Path | None = None) -> None:
        self.base_dir = base_dir or Path.home() / ".skill" / "evolution" / "usage"

    def _get_usage_file(self, skill_name: str) -> Path:
        date_str = datetime.now().strftime("%Y%m%d")
        self.base_dir.mkdir(parents=True, exist_ok=True)
        return self.base_dir / f"usage_{skill_name}_{date_str}.jsonl"

    def track_trigger(self, skill_name: str, expected_mode: str, actual_mode: str) -> None:
        correct = expected_mode == actual_mode
        event = {
            "timestamp": time.time(),
            "skill": skill_name,
            "event_type": "trigger",
            "expected_mode": expected_mode,
            "actual_mode": actual_mode,
            "correct": correct,
        }
        usage_file = self._get_usage_file(skill_name)
        with open(usage_file, "a") as f:
            f.write(json.dumps(event) + "\n")

    def track_task(
        self,
        skill_name: str,
        task_type: str,
        completed: bool,
        rounds: int = 1,
    ) -> None:
        event = {
            "timestamp": time.time(),
            "skill": skill_name,
            "event_type": "task",
            "task_type": task_type,
            "completed": completed,
            "rounds": rounds,
        }
        usage_file = self._get_usage_file(skill_name)
        with open(usage_file, "a") as f:
            f.write(json.dumps(event) + "\n")

    def track_feedback(self, skill_name: str, rating: int, comment: str = "") -> None:
        event = {
            "timestamp": time.time(),
            "skill": skill_name,
            "event_type": "feedback",
            "rating": rating,
            "comment": comment,
        }
        usage_file = self._get_usage_file(skill_name)
        with open(usage_file, "a") as f:
            f.write(json.dumps(event) + "\n")

    def get_usage_summary(self, skill_name: str, days: int = 7) -> UsageSummary:
        total_triggers = 0
        correct_triggers = 0
        total_tasks = 0
        completed_tasks = 0
        total_feedback = 0
        feedback_sum = 0.0

        for i in range(days):
            date_str = datetime.now().strftime("%Y%m%d")
            usage_file = self.base_dir / f"usage_{skill_name}_{date_str}.jsonl"
            if not usage_file.exists():
                continue

            with open(usage_file) as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    event = json.loads(line)
                    event_type = event.get("event_type")
                    if event_type == "trigger":
                        total_triggers += 1
                        if event.get("correct"):
                            correct_triggers += 1
                    elif event_type == "task":
                        total_tasks += 1
                        if event.get("completed"):
                            completed_tasks += 1
                    elif event_type == "feedback":
                        total_feedback += 1
                        feedback_sum += event.get("rating", 0)

        avg_rating = feedback_sum / total_feedback if total_feedback > 0 else 0.0

        return UsageSummary(
            total_triggers=total_triggers,
            correct_triggers=correct_triggers,
            total_tasks=total_tasks,
            completed_tasks=completed_tasks,
            total_feedback=total_feedback,
            avg_feedback_rating=avg_rating,
        )
