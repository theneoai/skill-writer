"""Tests for calibration module."""

from __future__ import annotations

import json
import os
import tempfile

import pytest


class TestCalibrationCorpus:
    """Test suite for calibration corpus management."""

    def test_init_creates_directory(self, tmp_path):
        """Test that calibration corpus initializes correctly."""
        from skill.lib.calibration import init_calibration_corpus

        os.environ["CALIBRATION_DIR"] = str(tmp_path)
        os.environ["CALIBRATION_CORPUS"] = str(tmp_path / "corpus.json")

        init_calibration_corpus()

        corpus_path = tmp_path / "corpus.json"
        assert corpus_path.exists()
        with open(corpus_path) as f:
            assert json.load(f) == []

    def test_add_expert_annotation(self, tmp_path):
        """Test adding expert annotations."""
        from skill.lib.calibration import (
            init_calibration_corpus,
            add_expert_annotation,
        )

        os.environ["CALIBRATION_DIR"] = str(tmp_path)
        os.environ["CALIBRATION_CORPUS"] = str(tmp_path / "corpus.json")

        skill_file = tmp_path / "test_skill.md"
        skill_file.write_text("# Test Skill")

        init_calibration_corpus()
        add_expert_annotation(str(skill_file), "expert1", 8, 7, 6, 9, 7, "Good skill")

        corpus_path = tmp_path / "corpus.json"
        with open(corpus_path) as f:
            data = json.load(f)

        assert len(data) == 1
        assert data[0]["expert_id"] == "expert1"
        assert data[0]["ratings"]["structural_completeness"] == 8
        assert data[0]["overall"] == 7.4  # (8+7+6+9+7)/5 = 7.4


class TestCalibratedScore:
    """Test suite for calibrated score application."""

    def test_calibrated_score_no_params_returns_raw(self, tmp_path):
        """Test that without calibration params, raw score is returned."""
        from skill.lib.calibration import calibrated_score

        os.environ["CALIBRATION_DIR"] = str(tmp_path)
        os.environ["CALIBRATION_PARAMS"] = str(tmp_path / "params.json")

        result = calibrated_score("500")
        assert result == "500"

    def test_calibrated_score_with_params(self, tmp_path):
        """Test calibrated score with params file."""
        from skill.lib.calibration import calibrated_score

        os.environ["CALIBRATION_DIR"] = str(tmp_path)
        os.environ["CALIBRATION_PARAMS"] = str(tmp_path / "params.json")

        params = {"slope": 0.9, "intercept": 50, "r": 0.85, "rmse": 30, "n": 10}
        params_path = tmp_path / "params.json"
        with open(params_path, "w") as f:
            json.dump(params, f)

        result = calibrated_score("500")
        expected = 0.9 * 500 + 50  # = 500
        assert result == str(int(expected))

    def test_calibrated_score_clamps_to_0_1000(self, tmp_path):
        """Test that calibrated score is clamped to 0-1000 range."""
        from skill.lib.calibration import calibrated_score

        os.environ["CALIBRATION_DIR"] = str(tmp_path)
        os.environ["CALIBRATION_PARAMS"] = str(tmp_path / "params.json")

        params = {"slope": 2.0, "intercept": 0, "r": 0.85, "rmse": 30, "n": 10}
        params_path = tmp_path / "params.json"
        with open(params_path, "w") as f:
            json.dump(params, f)

        result = calibrated_score("600")
        assert result == "1000"  # 2*600 = 1200, clamped to 1000
