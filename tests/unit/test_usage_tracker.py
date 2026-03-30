"""Tests for usage tracker module."""

from __future__ import annotations

import json
import tempfile
import os
from pathlib import Path

import pytest

from skill.engine.usage_tracker import UsageTracker, UsageSummary


class TestUsageTracker:
    """Test suite for UsageTracker class."""

    def test_initialization(self, tmp_path: Path):
        """Test UsageTracker initializes correctly."""
        tracker = UsageTracker(base_dir=tmp_path)
        assert tracker.base_dir == tmp_path

    def test_track_trigger_correct(self, tmp_path: Path):
        """Test tracking a correct trigger event."""
        tracker = UsageTracker(base_dir=tmp_path)
        tracker.track_trigger("test_skill", "auto", "auto")
        summary = tracker.get_usage_summary("test_skill", days=1)
        assert summary.total_triggers == 1
        assert summary.correct_triggers == 1

    def test_track_trigger_incorrect(self, tmp_path: Path):
        """Test tracking an incorrect trigger event."""
        tracker = UsageTracker(base_dir=tmp_path)
        tracker.track_trigger("test_skill", "auto", "manual")
        summary = tracker.get_usage_summary("test_skill", days=1)
        assert summary.total_triggers == 1
        assert summary.correct_triggers == 0

    def test_track_task_completed(self, tmp_path: Path):
        """Test tracking a completed task."""
        tracker = UsageTracker(base_dir=tmp_path)
        tracker.track_task("test_skill", "CREATE", completed=True, rounds=2)
        summary = tracker.get_usage_summary("test_skill", days=1)
        assert summary.total_tasks == 1
        assert summary.completed_tasks == 1

    def test_track_task_incomplete(self, tmp_path: Path):
        """Test tracking an incomplete task."""
        tracker = UsageTracker(base_dir=tmp_path)
        tracker.track_task("test_skill", "CREATE", completed=False, rounds=1)
        summary = tracker.get_usage_summary("test_skill", days=1)
        assert summary.total_tasks == 1
        assert summary.completed_tasks == 0

    def test_track_feedback(self, tmp_path: Path):
        """Test tracking feedback."""
        tracker = UsageTracker(base_dir=tmp_path)
        tracker.track_feedback("test_skill", rating=4, comment="Good")
        summary = tracker.get_usage_summary("test_skill", days=1)
        assert summary.total_feedback == 1
        assert summary.avg_feedback_rating == 4.0

    def test_multiple_feedback_ratings(self, tmp_path: Path):
        """Test averaging multiple feedback ratings."""
        tracker = UsageTracker(base_dir=tmp_path)
        tracker.track_feedback("test_skill", rating=5)
        tracker.track_feedback("test_skill", rating=3)
        summary = tracker.get_usage_summary("test_skill", days=1)
        assert summary.total_feedback == 2
        assert summary.avg_feedback_rating == 4.0

    def test_trigger_f1_calculation(self, tmp_path: Path):
        """Test trigger F1 is calculated correctly."""
        tracker = UsageTracker(base_dir=tmp_path)
        tracker.track_trigger("test_skill", "auto", "auto")
        tracker.track_trigger("test_skill", "auto", "auto")
        tracker.track_trigger("test_skill", "auto", "manual")
        summary = tracker.get_usage_summary("test_skill", days=1)
        assert summary.trigger_f1 == pytest.approx(2 / 3, rel=0.01)

    def test_task_completion_rate(self, tmp_path: Path):
        """Test task completion rate calculation."""
        tracker = UsageTracker(base_dir=tmp_path)
        tracker.track_task("test_skill", "CREATE", completed=True)
        tracker.track_task("test_skill", "CREATE", completed=False)
        tracker.track_task("test_skill", "CREATE", completed=True)
        summary = tracker.get_usage_summary("test_skill", days=1)
        assert summary.task_completion_rate == pytest.approx(2 / 3, rel=0.01)

    def test_empty_summary(self, tmp_path: Path):
        """Test summary for skill with no data."""
        tracker = UsageTracker(base_dir=tmp_path)
        summary = tracker.get_usage_summary("nonexistent", days=1)
        assert summary.total_triggers == 0
        assert summary.correct_triggers == 0
        assert summary.total_tasks == 0
        assert summary.completed_tasks == 0
        assert summary.total_feedback == 0
        assert summary.trigger_f1 == 0.0
        assert summary.task_completion_rate == 0.0

    def test_summary_to_dict(self, tmp_path: Path):
        """Test summary converts to dict correctly."""
        tracker = UsageTracker(base_dir=tmp_path)
        tracker.track_trigger("test_skill", "auto", "auto")
        summary = tracker.get_usage_summary("test_skill", days=1)
        data = summary.to_dict()
        assert data["trigger_f1"] == 1.0
        assert data["stats"]["triggers"]["total"] == 1
        assert data["stats"]["triggers"]["correct"] == 1


class TestUsageSummary:
    """Test suite for UsageSummary dataclass."""

    def test_usage_summary_creation(self):
        """Test UsageSummary stores all fields."""
        summary = UsageSummary(
            total_triggers=10,
            correct_triggers=8,
            total_tasks=5,
            completed_tasks=4,
            total_feedback=3,
            avg_feedback_rating=4.5,
        )
        assert summary.total_triggers == 10
        assert summary.correct_triggers == 8
        assert summary.trigger_f1 == 0.8
        assert summary.task_completion_rate == 0.8
        assert summary.avg_feedback_rating == 4.5

    def test_usage_summary_zero_division(self):
        """Test UsageSummary handles zero division."""
        summary = UsageSummary(
            total_triggers=0,
            correct_triggers=0,
            total_tasks=0,
            completed_tasks=0,
            total_feedback=0,
            avg_feedback_rating=0.0,
        )
        assert summary.trigger_f1 == 0.0
        assert summary.task_completion_rate == 0.0
        assert summary.avg_feedback_rating == 0.0
