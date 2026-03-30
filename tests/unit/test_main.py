"""Tests for main eval module."""

from __future__ import annotations

import json
import os
import tempfile

import pytest


class TestParseArgs:
    """Test suite for argument parsing."""

    def test_requires_skill_path(self):
        """Test that --skill is required."""
        from skill.eval.main import parse_args

        with pytest.raises(SystemExit):
            parse_args([])

    def test_parses_skill_path(self):
        """Test parsing --skill argument."""
        from skill.eval.main import parse_args

        args = parse_args(["--skill", "/path/to/SKILL.md"])
        assert args.skill_path == "/path/to/SKILL.md"

    def test_default_eval_mode_is_fast(self):
        """Test default eval mode is fast."""
        from skill.eval.main import parse_args

        args = parse_args(["--skill", "/path/to/SKILL.md"])
        assert args.eval_mode == "fast"

    def test_parses_fast_mode(self):
        """Test --fast sets eval mode."""
        from skill.eval.main import parse_args

        args = parse_args(["--skill", "/path/to/SKILL.md", "--fast"])
        assert args.eval_mode == "fast"

    def test_parses_full_mode(self):
        """Test --full sets eval mode."""
        from skill.eval.main import parse_args

        args = parse_args(["--skill", "/path/to/SKILL.md", "--full"])
        assert args.eval_mode == "full"

    def test_parses_custom_corpus(self):
        """Test --corpus sets custom corpus path."""
        from skill.eval.main import parse_args

        args = parse_args(
            ["--skill", "/path/to/SKILL.md", "--corpus", "/custom/corpus.json"]
        )
        assert args.corpus_path == "/custom/corpus.json"
        assert args.eval_mode == "custom"

    def test_default_output_dir(self):
        """Test default output directory."""
        from skill.eval.main import parse_args

        args = parse_args(["--skill", "/path/to/SKILL.md"])
        assert args.output_dir == "./eval_results"

    def test_parses_output_dir(self):
        """Test --output sets directory."""
        from skill.eval.main import parse_args

        args = parse_args(["--skill", "/path/to/SKILL.md", "--output", "/my/output"])
        assert args.output_dir == "/my/output"

    def test_parses_lang(self):
        """Test --lang sets language."""
        from skill.eval.main import parse_args

        args = parse_args(["--skill", "/path/to/SKILL.md", "--lang", "zh"])
        assert args.lang == "zh"


class TestTierDetermination:
    """Test suite for tier determination logic."""

    def test_platinum_tier(self):
        """Test PLATINUM tier when score >= 950 and variance < 20."""
        from skill.eval.main import determine_tier

        tier, tier_score = determine_tier(
            grand_total=950, variance=19, security_violation=0
        )
        assert tier == "PLATINUM"
        assert tier_score == 30

    def test_gold_tier(self):
        """Test GOLD tier when score >= 900 and variance < 50."""
        from skill.eval.main import determine_tier

        tier, tier_score = determine_tier(
            grand_total=900, variance=49, security_violation=0
        )
        assert tier == "GOLD"
        assert tier_score == 25

    def test_silver_tier(self):
        """Test SILVER tier when score >= 800 and variance < 80."""
        from skill.eval.main import determine_tier

        tier, tier_score = determine_tier(
            grand_total=800, variance=79, security_violation=0
        )
        assert tier == "SILVER"
        assert tier_score == 20

    def test_bronze_tier(self):
        """Test BRONZE tier when score >= 700 and variance < 150."""
        from skill.eval.main import determine_tier

        tier, tier_score = determine_tier(
            grand_total=700, variance=149, security_violation=0
        )
        assert tier == "BRONZE"
        assert tier_score == 15

    def test_rejected_tier_on_security_violation(self):
        """Test REJECTED tier on security violation."""
        from skill.eval.main import determine_tier

        tier, tier_score = determine_tier(
            grand_total=950, variance=10, security_violation=1
        )
        assert tier == "REJECTED"
        assert tier_score == 0

    def test_not_certified_tier(self):
        """Test NOT_CERTIFIED tier when score too low."""
        from skill.eval.main import determine_tier

        tier, tier_score = determine_tier(
            grand_total=600, variance=100, security_violation=0
        )
        assert tier == "NOT_CERTIFIED"
        assert tier_score == 0


class TestVarianceCalculation:
    """Test suite for variance calculation."""

    def test_low_variance_score(self):
        """Test variance score 40 when variance < 30."""
        from skill.eval.main import calculate_variance_score

        score = calculate_variance_score(variance=25)
        assert score == 40

    def test_medium_variance_score(self):
        """Test variance score 30 when variance < 50."""
        from skill.eval.main import calculate_variance_score

        score = calculate_variance_score(variance=40)
        assert score == 30

    def test_high_variance_score(self):
        """Test variance score 20 when variance < 70."""
        from skill.eval.main import calculate_variance_score

        score = calculate_variance_score(variance=65)
        assert score == 20


class TestPhase1Validation:
    """Test suite for Phase 1 (Parse & Validate)."""

    def test_valid_yaml_frontmatter(self, tmp_path):
        """Test scoring YAML frontmatter."""
        from skill.eval.main import run_phase1

        skill_file = tmp_path / "SKILL.md"
        skill_file.write_text("""---
name: test
description: test skill
license: MIT
---

# Content
""")
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        score, details = run_phase1(str(skill_file), str(output_dir))
        assert score >= 30
        assert details["yaml_frontmatter"] == 30

    def test_detects_security_violation(self, tmp_path):
        """Test security violation detection."""
        from skill.eval.main import run_phase1

        skill_file = tmp_path / "SKILL.md"
        skill_file.write_text("""---
name: test
description: test
license: MIT
---

API Key: sk-1234567890abcdefghij
""")
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        score, details = run_phase1(str(skill_file), str(output_dir))
        assert details["security_violation"] == 1


class TestSummaryGeneration:
    """Test suite for summary generation."""

    def test_generates_summary_json(self, tmp_path):
        """Test summary JSON is generated correctly."""
        from skill.eval.main import generate_summary

        output_dir = tmp_path / "output"
        output_dir.mkdir()

        generate_summary(
            output_dir=str(output_dir),
            total=850,
            p1=95,
            p2=300,
            p3=400,
            p4=55,
            tier="SILVER",
            f1_score=0.92,
            mode_accuracy=0.88,
        )

        summary_file = output_dir / "summary.json"
        assert summary_file.exists()

        with open(summary_file) as f:
            data = json.load(f)

        assert data["total_score"] == 850
        assert data["tier"] == "SILVER"
        assert data["phases"]["parse_validate"] == 95
