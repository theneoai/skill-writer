"""Tests for HTML reporter module."""

from __future__ import annotations

import json
import os
import tempfile

import pytest


class TestGenerateHtmlReport:
    """Test suite for HTML report generation."""

    def test_creates_html_file(self, tmp_path):
        """Test HTML file is created."""
        from skill.eval.html_reporter import generate_html_report

        output_file = tmp_path / "report.html"
        dimension_json = json.dumps({})
        recommendations_json = json.dumps([])

        generate_html_report(
            output_file=str(output_file),
            skill_name="TestSkill",
            skill_version="1.0",
            evaluated_at="2024-01-01T00:00:00Z",
            lang="en",
            parse_score=95,
            text_score=300,
            runtime_score=400,
            certify_score=55,
            total_score=850,
            f1_score=0.92,
            mrr_score=0.88,
            trigger_accuracy=0.99,
            variance=15,
            tier="SILVER",
            certified="true",
            dimension_json=dimension_json,
            recommendations_json=recommendations_json,
        )

        assert output_file.exists()

    def test_html_contains_tier(self, tmp_path):
        """Test HTML contains correct tier."""
        from skill.eval.html_reporter import generate_html_report

        output_file = tmp_path / "report.html"
        dimension_json = json.dumps({})
        recommendations_json = json.dumps([])

        generate_html_report(
            output_file=str(output_file),
            skill_name="TestSkill",
            skill_version="1.0",
            evaluated_at="2024-01-01T00:00:00Z",
            lang="en",
            parse_score=95,
            text_score=300,
            runtime_score=400,
            certify_score=55,
            total_score=850,
            f1_score=0.92,
            mrr_score=0.88,
            trigger_accuracy=0.99,
            variance=15,
            tier="GOLD",
            certified="true",
            dimension_json=dimension_json,
            recommendations_json=recommendations_json,
        )

        content = output_file.read_text()
        assert "tier-GOLD" in content
        assert "GOLD" in content

    def test_html_contains_scores(self, tmp_path):
        """Test HTML contains correct scores."""
        from skill.eval.html_reporter import generate_html_report

        output_file = tmp_path / "report.html"
        dimension_json = json.dumps({})
        recommendations_json = json.dumps([])

        generate_html_report(
            output_file=str(output_file),
            skill_name="TestSkill",
            skill_version="1.0",
            evaluated_at="2024-01-01T00:00:00Z",
            lang="en",
            parse_score=95,
            text_score=300,
            runtime_score=400,
            certify_score=55,
            total_score=850,
            f1_score=0.92,
            mrr_score=0.88,
            trigger_accuracy=0.99,
            variance=15,
            tier="SILVER",
            certified="true",
            dimension_json=dimension_json,
            recommendations_json=recommendations_json,
        )

        content = output_file.read_text()
        assert "850" in content
        assert "95" in content
        assert "300" in content
        assert "400" in content

    def test_f1_pass_status(self, tmp_path):
        """Test F1 PASS status when above threshold."""
        from skill.eval.html_reporter import generate_html_report

        output_file = tmp_path / "report.html"
        dimension_json = json.dumps({})
        recommendations_json = json.dumps([])

        generate_html_report(
            output_file=str(output_file),
            skill_name="TestSkill",
            skill_version="1.0",
            evaluated_at="2024-01-01T00:00:00Z",
            lang="en",
            parse_score=95,
            text_score=300,
            runtime_score=400,
            certify_score=55,
            total_score=850,
            f1_score=0.95,
            mrr_score=0.90,
            trigger_accuracy=0.99,
            variance=15,
            tier="SILVER",
            certified="true",
            dimension_json=dimension_json,
            recommendations_json=recommendations_json,
        )

        content = output_file.read_text()
        assert 'class="PASS"' in content
        assert ">PASS<" in content

    def test_f1_fail_status(self, tmp_path):
        """Test F1 FAIL status when below threshold."""
        from skill.eval.html_reporter import generate_html_report

        output_file = tmp_path / "report.html"
        dimension_json = json.dumps({})
        recommendations_json = json.dumps([])

        generate_html_report(
            output_file=str(output_file),
            skill_name="TestSkill",
            skill_version="1.0",
            evaluated_at="2024-01-01T00:00:00Z",
            lang="en",
            parse_score=95,
            text_score=300,
            runtime_score=400,
            certify_score=55,
            total_score=850,
            f1_score=0.80,
            mrr_score=0.90,
            trigger_accuracy=0.99,
            variance=15,
            tier="SILVER",
            certified="true",
            dimension_json=dimension_json,
            recommendations_json=recommendations_json,
        )

        content = output_file.read_text()
        assert 'class="FAIL"' in content
        assert ">FAIL<" in content


class TestRadarChart:
    """Test suite for radar chart generation."""

    def test_radar_svg_generated(self, tmp_path):
        """Test radar SVG is generated."""
        from skill.eval.html_reporter import generate_radar_svg

        dimension_json = json.dumps(
            {
                "system_prompt": {"score": 65, "max": 70},
                "domain_knowledge": {"score": 62, "max": 70},
            }
        )

        svg = generate_radar_svg(dimension_json)

        assert "<defs>" in svg
        assert "</style>" in svg
        assert "System Prompt" in svg
        assert "grid-polygon" in svg

    def test_radar_contains_axis_labels(self, tmp_path):
        """Test radar SVG contains dimension labels."""
        from skill.eval.html_reporter import generate_radar_svg

        dimension_json = json.dumps(
            {
                "system_prompt": {"score": 65, "max": 70},
            }
        )

        svg = generate_radar_svg(dimension_json)

        assert "System Prompt" in svg


class TestTierTranslations:
    """Test suite for tier bilingual support."""

    def test_platinum_translation(self, tmp_path):
        """Test PLATINUM tier has Chinese translation."""
        from skill.eval.html_reporter import generate_html_report

        output_file = tmp_path / "report.html"
        dimension_json = json.dumps({})
        recommendations_json = json.dumps([])

        generate_html_report(
            output_file=str(output_file),
            skill_name="TestSkill",
            skill_version="1.0",
            evaluated_at="2024-01-01T00:00:00Z",
            lang="zh",
            parse_score=95,
            text_score=300,
            runtime_score=400,
            certify_score=55,
            total_score=950,
            f1_score=0.95,
            mrr_score=0.90,
            trigger_accuracy=0.99,
            variance=15,
            tier="PLATINUM",
            certified="true",
            dimension_json=dimension_json,
            recommendations_json=recommendations_json,
        )

        content = output_file.read_text()
        assert "白金" in content


class TestDimensionList:
    """Test suite for dimension list parsing."""

    def test_parses_dimension_list(self, tmp_path):
        """Test dimension list is parsed correctly."""
        from skill.eval.html_reporter import parse_dimension_list

        dimension_json = json.dumps(
            {
                "system_prompt": {"score": 65, "max": 70},
                "domain_knowledge": {"score": 62, "max": 70},
            }
        )

        html = parse_dimension_list(dimension_json)

        assert "System Prompt" in html
        assert "65/70" in html
