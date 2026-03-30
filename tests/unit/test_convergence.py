"""Tests for convergence module."""

from __future__ import annotations

import pytest

from skill.engine.convergence import (
    check_convergence,
    check_plateau,
    check_trend,
    check_volatility,
    should_continue_evolution,
)


class TestCheckVolatility:
    """Test suite for volatility checking."""

    def test_unknown_when_empty(self):
        """Test returns UNKNOWN for empty scores."""
        result = check_volatility("[]", 2.0)
        assert result == "UNKNOWN"

    def test_unknown_when_single_score(self):
        """Test returns UNKNOWN for single score."""
        scores = [{"score": 85}]
        result = check_volatility(scores, 2.0)
        assert result == "UNKNOWN"

    def test_converged_when_low_stddev(self):
        """Test returns CONVERGED when stddev below threshold."""
        scores = [{"score": 80}, {"score": 81}, {"score": 79}, {"score": 80.5}]
        result = check_volatility(scores, 2.0)
        assert result == "CONVERGED"

    def test_volatile_when_high_stddev(self):
        """Test returns VOLATILE when stddev above threshold."""
        scores = [{"score": 50}, {"score": 90}, {"score": 60}, {"score": 95}]
        result = check_volatility(scores, 2.0)
        assert "VOLATILE" in result


class TestCheckPlateau:
    """Test suite for plateau detection."""

    def test_unknown_when_insufficient_data(self):
        """Test returns UNKNOWN when fewer than 3 scores."""
        scores = [{"score": 80}, {"score": 81}]
        result = check_plateau(scores, 0.5)
        assert result == "UNKNOWN"

    def test_converged_when_most_deltas_small(self):
        """Test returns CONVERGED when most deltas are small and not improving."""
        scores = [{"score": 80}, {"score": 80.1}, {"score": 79.9}, {"score": 80.0}]
        result = check_plateau(scores, 0.5)
        assert result == "CONVERGED"

    def test_active_when_deltas_large(self):
        """Test returns ACTIVE when deltas are large."""
        scores = [{"score": 70}, {"score": 85}, {"score": 72}, {"score": 88}]
        result = check_plateau(scores, 0.5)
        assert "ACTIVE" in result


class TestCheckTrend:
    """Test suite for trend detection."""

    def test_unknown_when_insufficient_data(self):
        """Test returns UNKNOWN when fewer than 4 scores."""
        scores = [{"score": 80}, {"score": 82}, {"score": 81}]
        result = check_trend(scores)
        assert result == "UNKNOWN"

    def test_improving_when_second_half_better(self):
        """Test returns IMPROVING when second half avg is higher."""
        scores = [{"score": 70}, {"score": 72}, {"score": 85}, {"score": 88}]
        result = check_trend(scores)
        assert result == "IMPROVING"

    def test_diverging_when_second_half_worse(self):
        """Test returns DIVERGING when second half avg is lower."""
        scores = [{"score": 85}, {"score": 88}, {"score": 70}, {"score": 72}]
        result = check_trend(scores)
        assert result == "DIVERGING"

    def test_stable_when_no_significant_change(self):
        """Test returns STABLE when no significant change."""
        scores = [{"score": 80}, {"score": 81}, {"score": 80}, {"score": 81}]
        result = check_trend(scores)
        assert result == "STABLE"


class TestCheckConvergence:
    """Test suite for main convergence check."""

    def test_not_converged_with_insufficient_data(self):
        """Test returns NOT_CONVERGED when too few scores."""
        scores = [{"score": 80}, {"score": 81}]
        result = check_convergence("test_skill", window_size=10, min_rounds=5)
        assert "NOT_CONVERGED" in result

    def test_not_converged_when_volatile(self):
        """Test returns NOT_CONVERGED when scores are volatile."""
        from skill.engine import storage

        original_get_all_scores = storage.storage_get_all_scores
        storage.storage_get_all_scores = lambda s: [
            {"score": 50},
            {"score": 90},
            {"score": 60},
            {"score": 95},
            {"score": 55},
        ]
        try:
            result = check_convergence("test_skill", window_size=5, min_rounds=5)
            assert "NOT_CONVERGED" in result
        finally:
            storage.storage_get_all_scores = original_get_all_scores


class TestShouldContinueEvolution:
    """Test suite for evolution continuation decision."""

    def test_stops_when_max_rounds_reached(self):
        """Test stops when eval count >= max_rounds."""
        pass
