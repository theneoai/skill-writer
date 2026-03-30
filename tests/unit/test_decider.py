"""Tests for evolution decider module."""

from __future__ import annotations

import pytest

from skill.engine.decider import (
    EvolutionDecision,
    EvolutionDecider,
    GOLD_THRESHOLD,
    SILVER_THRESHOLD,
    BRONZE_THRESHOLD,
)


class TestEvolutionDecision:
    """Test suite for EvolutionDecision dataclass."""

    def test_decision_creation_evolve(self):
        """Test creating an evolve decision."""
        decision = EvolutionDecision(
            decision="evolve",
            reason="score_below_gold",
            score=550,
        )
        assert decision.decision == "evolve"
        assert decision.reason == "score_below_gold"
        assert decision.score == 550

    def test_decision_creation_skip(self):
        """Test creating a skip decision."""
        decision = EvolutionDecision(
            decision="skip",
            reason="metrics_ok",
            score=580,
            trigger_f1=0.9,
            task_rate=0.85,
        )
        assert decision.decision == "skip"
        assert decision.trigger_f1 == 0.9
        assert decision.task_rate == 0.85

    def test_decision_to_dict(self):
        """Test decision converts to dict."""
        decision = EvolutionDecision(
            decision="evolve",
            reason="forced",
            score=0,
        )
        data = decision.to_dict()
        assert data["decision"] == "evolve"
        assert data["reason"] == "forced"


class TestEvolutionDecider:
    """Test suite for EvolutionDecider class."""

    def test_thresholds_defined(self):
        """Test threshold constants are defined."""
        assert GOLD_THRESHOLD == 570
        assert SILVER_THRESHOLD == 510
        assert BRONZE_THRESHOLD == 420

    def test_should_evolve_below_gold(self):
        """Test evolve decision when score below gold threshold."""
        decider = EvolutionDecider()
        result = decider.should_evolve_score(550)
        assert result.decision == "evolve"
        assert "score_below_gold" in result.reason

    def test_should_evolve_above_gold(self):
        """Test skip decision when score above gold threshold."""
        decider = EvolutionDecider()
        result = decider.should_evolve_score(580)
        assert result.decision == "skip"

    def test_should_evolve_at_gold_boundary(self):
        """Test decision at gold threshold boundary."""
        decider = EvolutionDecider()
        result = decider.should_evolve_score(570)
        assert result.decision == "skip"

    def test_should_evolve_below_silver(self):
        """Test decision below silver threshold."""
        decider = EvolutionDecider()
        result = decider.should_evolve_score(500)
        assert result.decision == "evolve"

    def test_should_evolve_force(self):
        """Test forced evolution."""
        decider = EvolutionDecider()
        result = decider.should_evolve_score(600, force=True)
        assert result.decision == "evolve"
        assert result.reason == "forced"

    def test_should_evolve_low_usage_metrics(self):
        """Test evolve due to low usage metrics."""
        decider = EvolutionDecider()
        result = decider.should_evolve_usage_metrics(
            trigger_f1=0.80,
            task_rate=0.70,
            current_score=580,
        )
        assert result.decision == "evolve"
        assert "usage_metrics_low" in result.reason

    def test_should_skip_good_usage_metrics(self):
        """Test skip when usage metrics are good."""
        decider = EvolutionDecider()
        result = decider.should_evolve_usage_metrics(
            trigger_f1=0.90,
            task_rate=0.85,
            current_score=580,
        )
        assert result.decision == "skip"
        assert result.reason == "metrics_ok"

    def test_should_evolve_trigger_f1_low(self):
        """Test evolve when only trigger F1 is low."""
        decider = EvolutionDecider()
        result = decider.should_evolve_usage_metrics(
            trigger_f1=0.80,
            task_rate=0.85,
            current_score=580,
        )
        assert result.decision == "evolve"

    def test_should_evolve_task_rate_low(self):
        """Test evolve when only task rate is low."""
        decider = EvolutionDecider()
        result = decider.should_evolve_usage_metrics(
            trigger_f1=0.90,
            task_rate=0.70,
            current_score=580,
        )
        assert result.decision == "evolve"


class TestEvolutionRecommendations:
    """Test suite for evolution recommendations."""

    def test_recommendations_low_trigger_f1(self):
        """Test recommendations when trigger F1 is low."""
        decider = EvolutionDecider()
        recs = decider.get_recommendations(
            trigger_f1=0.80, task_rate=0.85, avg_feedback=4.0
        )
        assert len(recs) > 0
        assert any("trigger" in r.lower() for r in recs)

    def test_recommendations_low_task_rate(self):
        """Test recommendations when task rate is low."""
        decider = EvolutionDecider()
        recs = decider.get_recommendations(
            trigger_f1=0.90, task_rate=0.70, avg_feedback=4.0
        )
        assert len(recs) > 0
        assert any("task" in r.lower() for r in recs)

    def test_recommendations_low_feedback(self):
        """Test recommendations when feedback is low."""
        decider = EvolutionDecider()
        recs = decider.get_recommendations(
            trigger_f1=0.90, task_rate=0.85, avg_feedback=3.0
        )
        assert len(recs) > 0
        assert any("feedback" in r.lower() for r in recs)

    def test_recommendations_all_good(self):
        """Test recommendations when all metrics are good."""
        decider = EvolutionDecider()
        recs = decider.get_recommendations(
            trigger_f1=0.95, task_rate=0.90, avg_feedback=4.5
        )
        assert len(recs) == 1
        assert "good" in recs[0].lower() or "refinements" in recs[0].lower()
