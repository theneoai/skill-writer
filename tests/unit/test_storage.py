"""Tests for storage module."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

from skill.engine.storage import (
    storage_calculate_threshold,
    storage_get_all_scores,
    storage_get_eval_count,
    storage_get_last_score,
    storage_log_usage,
)


class TestStorageEvalCount:
    """Test suite for storage_get_eval_count."""

    def test_returns_zero_when_no_log(self, tmp_path, monkeypatch):
        """Test returns 0 when usage log doesn't exist."""
        monkeypatch.setattr(
            "skill.engine.storage.USAGE_LOG", str(tmp_path / "no_log.jsonl")
        )
        result = storage_get_eval_count("some_skill")
        assert result == 0

    def test_returns_zero_when_no_matching_entries(self, tmp_path, monkeypatch):
        """Test returns 0 when no entries for skill."""
        log_file = tmp_path / "usage.jsonl"
        log_file.write_text('{"skill_name":"other_skill","score":85}\n')
        monkeypatch.setattr("skill.engine.storage.USAGE_LOG", str(log_file))
        result = storage_get_eval_count("my_skill")
        assert result == 0

    def test_counts_matching_entries(self, tmp_path, monkeypatch):
        """Test counts all entries for skill."""
        log_file = tmp_path / "usage.jsonl"
        log_file.write_text(
            '{"skill_name":"test_skill","score":80}\n'
            '{"skill_name":"test_skill","score":85}\n'
            '{"skill_name":"test_skill","score":90}\n'
        )
        monkeypatch.setattr("skill.engine.storage.USAGE_LOG", str(log_file))
        result = storage_get_eval_count("test_skill")
        assert result == 3


class TestStorageGetLastScore:
    """Test suite for storage_get_last_score."""

    def test_returns_zero_when_no_log(self, tmp_path, monkeypatch):
        """Test returns 0 when no log file."""
        monkeypatch.setattr(
            "skill.engine.storage.USAGE_LOG", str(tmp_path / "no_log.jsonl")
        )
        result = storage_get_last_score("some_skill")
        assert result == 0

    def test_returns_last_score(self, tmp_path, monkeypatch):
        """Test returns last score for skill."""
        log_file = tmp_path / "usage.jsonl"
        log_file.write_text(
            '{"skill_name":"test_skill","score":80}\n'
            '{"skill_name":"test_skill","score":85}\n'
            '{"skill_name":"test_skill","score":90}\n'
        )
        monkeypatch.setattr("skill.engine.storage.USAGE_LOG", str(log_file))
        result = storage_get_last_score("test_skill")
        assert result == 90


class TestStorageGetAllScores:
    """Test suite for storage_get_all_scores."""

    def test_returns_empty_list_when_no_log(self, tmp_path, monkeypatch):
        """Test returns empty list when no log file."""
        monkeypatch.setattr(
            "skill.engine.storage.USAGE_LOG", str(tmp_path / "no_log.jsonl")
        )
        result = storage_get_all_scores("some_skill")
        assert result == []

    def test_returns_scores_for_skill(self, tmp_path, monkeypatch):
        """Test returns all scores for skill."""
        log_file = tmp_path / "usage.jsonl"
        log_file.write_text(
            '{"skill_name":"test_skill","score":80}\n'
            '{"skill_name":"test_skill","score":85}\n'
            '{"skill_name":"other","score":70}\n'
        )
        monkeypatch.setattr("skill.engine.storage.USAGE_LOG", str(log_file))
        result = storage_get_all_scores("test_skill")
        assert len(result) == 2


class TestStorageLogUsage:
    """Test suite for storage_log_usage."""

    def test_creates_log_entry(self, tmp_path, monkeypatch):
        """Test creates log entry with correct data."""
        log_file = tmp_path / "usage.jsonl"
        monkeypatch.setattr("skill.engine.storage.USAGE_LOG", str(log_file))
        monkeypatch.setattr(
            "skill.engine.storage.get_timestamp", lambda: "20240101_120000"
        )
        storage_log_usage("test_skill", 85, "tier_1", 10)
        with open(log_file) as f:
            lines = f.readlines()
        assert len(lines) == 1
        entry = json.loads(lines[0])
        assert entry["skill_name"] == "test_skill"
        assert entry["score"] == 85


class TestStorageCalculateThreshold:
    """Test suite for storage_calculate_threshold."""

    def test_returns_new_threshold_when_low_count(self):
        """Test returns NEW threshold when eval_count < 10."""
        result = storage_calculate_threshold(5)
        assert result == 10

    def test_returns_growing_threshold_when_medium_count(self):
        """Test returns GROWING threshold when 10 <= eval_count < 50."""
        result = storage_calculate_threshold(25)
        assert result == 5

    def test_returns_stable_threshold_when_high_count(self):
        """Test returns STABLE threshold when eval_count >= 50."""
        result = storage_calculate_threshold(100)
        assert result == 2
