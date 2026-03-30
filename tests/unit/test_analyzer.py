"""Tests for analyzer module."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

from skill.engine.analyzer import (
    analyze_logs,
    analyze_score_distribution,
    analyze_trigger_effectiveness,
)


class TestAnalyzeScoreDistribution:
    """Test suite for analyze_score_distribution."""

    def test_returns_zeros_when_no_logs(self, tmp_path, monkeypatch):
        """Test returns zeros when no usage log exists."""
        monkeypatch.setattr(
            "skill.engine.analyzer.USAGE_LOG", str(tmp_path / "no_log.jsonl")
        )
        result = analyze_score_distribution("nonexistent")
        assert result["avg"] == 0
        assert result["min"] == 0
        assert result["max"] == 0
        assert result["count"] == 0

    def test_returns_zeros_when_no_matching_skill(self, tmp_path, monkeypatch):
        """Test returns zeros when no logs for the skill."""
        log_file = tmp_path / "usage.jsonl"
        log_file.write_text('{"skill_name":"other_skill","score":85}\n')
        monkeypatch.setattr("skill.engine.analyzer.USAGE_LOG", str(log_file))
        result = analyze_score_distribution("my_skill")
        assert result["avg"] == 0
        assert result["min"] == 0
        assert result["max"] == 0
        assert result["count"] == 0

    def test_calculates_correct_statistics(self, tmp_path, monkeypatch):
        """Test calculates correct avg, min, max from logs."""
        log_file = tmp_path / "usage.jsonl"
        log_file.write_text(
            '{"skill_name":"test_skill","score":80}\n'
            '{"skill_name":"test_skill","score":90}\n'
            '{"skill_name":"test_skill","score":70}\n'
        )
        monkeypatch.setattr("skill.engine.analyzer.USAGE_LOG", str(log_file))
        result = analyze_score_distribution("test_skill")
        assert result["avg"] == 80
        assert result["min"] == 70
        assert result["max"] == 90
        assert result["count"] == 3

    def test_handles_single_score(self, tmp_path, monkeypatch):
        """Test handles single score entry."""
        log_file = tmp_path / "usage.jsonl"
        log_file.write_text('{"skill_name":"solo","score":95}\n')
        monkeypatch.setattr("skill.engine.analyzer.USAGE_LOG", str(log_file))
        result = analyze_score_distribution("solo")
        assert result["avg"] == 95
        assert result["min"] == 95
        assert result["max"] == 95
        assert result["count"] == 1
