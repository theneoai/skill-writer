"""Tests for learner module."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

from skill.engine.learner import (
    get_improvement_hints,
    learn_from_usage,
)


class TestGetImprovementHints:
    """Test suite for get_improvement_hints."""

    def test_returns_hint_when_trigger_f1_low(self):
        """Test returns hint when trigger F1 is below threshold."""
        patterns = {
            "skill": "test_skill",
            "metrics": {"trigger_f1": 0.75, "task_completion_rate": 0.90},
            "patterns": {
                "weak_triggers": ["expected->actual"],
                "strong_triggers": [],
                "failed_task_types": [],
                "successful_task_types": [],
            },
        }
        with tempfile.NamedTemporaryFile(
            mode="w", suffix="_patterns.json", delete=False
        ) as f:
            json.dump(patterns, f)
            patterns_file = f.name
        try:
            result = get_improvement_hints(patterns_file)
            assert result["hint_count"] > 0
            assert any("Trigger confusion" in h for h in result["hints"])
        finally:
            Path(patterns_file).unlink()

    def test_returns_hint_when_task_rate_low(self):
        """Test returns hint when task completion rate is low."""
        patterns = {
            "skill": "test_skill",
            "metrics": {"trigger_f1": 0.95, "task_completion_rate": 0.70},
            "patterns": {
                "weak_triggers": [],
                "strong_triggers": [],
                "failed_task_types": ["task_type_a"],
                "successful_task_types": [],
            },
        }
        with tempfile.NamedTemporaryFile(
            mode="w", suffix="_patterns.json", delete=False
        ) as f:
            json.dump(patterns, f)
            patterns_file = f.name
        try:
            result = get_improvement_hints(patterns_file)
            assert result["hint_count"] > 0
            assert any("Task completion" in h for h in result["hints"])
        finally:
            Path(patterns_file).unlink()

    def test_returns_no_issues_hint_when_metrics_good(self):
        """Test returns no issues hint when metrics are good."""
        patterns = {
            "skill": "good_skill",
            "metrics": {"trigger_f1": 0.95, "task_completion_rate": 0.90},
            "patterns": {
                "weak_triggers": [],
                "strong_triggers": [],
                "failed_task_types": [],
                "successful_task_types": [],
            },
        }
        with tempfile.NamedTemporaryFile(
            mode="w", suffix="_patterns.json", delete=False
        ) as f:
            json.dump(patterns, f)
            patterns_file = f.name
        try:
            result = get_improvement_hints(patterns_file)
            assert result["skill"] == "good_skill"
        finally:
            Path(patterns_file).unlink()
