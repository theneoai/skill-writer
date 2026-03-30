"""Tests for trigger analyzer module."""

from __future__ import annotations

import json

import pytest


class TestComputeMetrics:
    """Test suite for _compute_metrics."""

    def test_empty_data_returns_zeros(self):
        """Test that empty data returns zero scores."""
        from skill.eval.trigger_analyzer import _compute_metrics

        result = _compute_metrics("[]")
        assert result["f1_score"] == 0.0
        assert result["mrr_score"] == 0.0
        assert result["trigger_accuracy"] == 0.0

    def test_perfect_match(self):
        """Test perfect match returns F1 of 1.0."""
        from skill.eval.trigger_analyzer import _compute_metrics

        data = json.dumps(
            [
                {
                    "expected_trigger": "CREATE",
                    "predicted_triggers": ["CREATE"],
                    "rank": 1,
                }
            ]
        )
        result = _compute_metrics(data)
        assert result["f1_score"] == 1.0
        assert result["trigger_accuracy"] == 1.0

    def test_partial_match(self):
        """Test partial match returns correct F1."""
        from skill.eval.trigger_analyzer import _compute_metrics

        data = json.dumps(
            [
                {
                    "expected_trigger": "CREATE",
                    "predicted_triggers": ["EVALUATE"],
                    "rank": 0,
                }
            ]
        )
        result = _compute_metrics(data)
        assert result["f1_score"] == 0.0
        assert result["trigger_accuracy"] == 0.0

    def test_mrr_calculation(self):
        """Test MRR is calculated correctly."""
        from skill.eval.trigger_analyzer import _compute_metrics

        data = json.dumps(
            [
                {
                    "expected_trigger": "CREATE",
                    "predicted_triggers": ["CREATE"],
                    "rank": 1,
                },
                {
                    "expected_trigger": "EVALUATE",
                    "predicted_triggers": ["EVALUATE"],
                    "rank": 2,
                },
            ]
        )
        result = _compute_metrics(data)
        expected_mrr = (1 / 1 + 1 / 2) / 2
        assert result["mrr_score"] == expected_mrr


class TestThresholdChecks:
    """Test suite for threshold checks."""

    def test_f1_threshold_met(self):
        """Test F1 threshold check when met."""
        from skill.eval.trigger_analyzer import check_thresholds

        result = check_thresholds(f1_score=0.95, mrr_score=0.90, trigger_accuracy=0.99)
        assert result["f1"] is True

    def test_f1_threshold_not_met(self):
        """Test F1 threshold check when not met."""
        from skill.eval.trigger_analyzer import check_thresholds

        result = check_thresholds(f1_score=0.85, mrr_score=0.90, trigger_accuracy=0.99)
        assert result["f1"] is False

    def test_all_thresholds_met(self):
        """Test all thresholds met returns full pass."""
        from skill.eval.trigger_analyzer import check_thresholds

        result = check_thresholds(f1_score=0.95, mrr_score=0.90, trigger_accuracy=0.99)
        assert result["all_pass"] is True
