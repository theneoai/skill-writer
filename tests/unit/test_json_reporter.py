"""Tests for JSON reporter module."""

from __future__ import annotations

import json
import os
import tempfile

import pytest


class TestGenerateJsonReport:
    """Test suite for JSON report generation."""

    def test_creates_json_file(self, tmp_path):
        """Test JSON file is created."""
        from skill.eval.json_reporter import generate_json_report

        output_file = tmp_path / "report.json"
        dimension_json = json.dumps({})
        recommendations_json = json.dumps([])

        generate_json_report(
            output_file=str(output_file),
            skill_name="TestSkill",
            skill_version="1.0",
            evaluated_at="2024-01-01T00:00:00Z",
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

    def test_json_contains_scores(self, tmp_path):
        """Test JSON contains correct scores."""
        from skill.eval.json_reporter import generate_json_report

        output_file = tmp_path / "report.json"
        dimension_json = json.dumps({})
        recommendations_json = json.dumps([])

        generate_json_report(
            output_file=str(output_file),
            skill_name="TestSkill",
            skill_version="1.0",
            evaluated_at="2024-01-01T00:00:00Z",
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

        with open(output_file) as f:
            data = json.load(f)

        assert data["scores"]["parse_validate"] == 95
        assert data["scores"]["text_score"] == 300
        assert data["scores"]["runtime_score"] == 400
        assert data["scores"]["certify"] == 55
        assert data["scores"]["total"] == 850

    def test_json_contains_tier(self, tmp_path):
        """Test JSON contains correct tier."""
        from skill.eval.json_reporter import generate_json_report

        output_file = tmp_path / "report.json"
        dimension_json = json.dumps({})
        recommendations_json = json.dumps([])

        generate_json_report(
            output_file=str(output_file),
            skill_name="TestSkill",
            skill_version="1.0",
            evaluated_at="2024-01-01T00:00:00Z",
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

        with open(output_file) as f:
            data = json.load(f)

        assert data["tier"] == "GOLD"

    def test_f1_threshold_met(self, tmp_path):
        """Test F1 threshold met is true when above threshold."""
        from skill.eval.json_reporter import generate_json_report

        output_file = tmp_path / "report.json"
        dimension_json = json.dumps({})
        recommendations_json = json.dumps([])

        generate_json_report(
            output_file=str(output_file),
            skill_name="TestSkill",
            skill_version="1.0",
            evaluated_at="2024-01-01T00:00:00Z",
            parse_score=95,
            text_score=300,
            runtime_score=400,
            certify_score=55,
            total_score=850,
            f1_score=0.95,
            mrr_score=0.90,
            trigger_accuracy=0.99,
            variance=15,
            tier="GOLD",
            certified="true",
            dimension_json=dimension_json,
            recommendations_json=recommendations_json,
        )

        with open(output_file) as f:
            data = json.load(f)

        assert data["thresholds_met"]["f1"] is True

    def test_f1_threshold_not_met(self, tmp_path):
        """Test F1 threshold met is false when below threshold."""
        from skill.eval.json_reporter import generate_json_report

        output_file = tmp_path / "report.json"
        dimension_json = json.dumps({})
        recommendations_json = json.dumps([])

        generate_json_report(
            output_file=str(output_file),
            skill_name="TestSkill",
            skill_version="1.0",
            evaluated_at="2024-01-01T00:00:00Z",
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

        with open(output_file) as f:
            data = json.load(f)

        assert data["thresholds_met"]["f1"] is False


class TestGenerateDimensionJson:
    """Test suite for dimension JSON generation."""

    def test_generates_dimension_json(self, tmp_path):
        """Test dimension JSON is generated correctly."""
        from skill.eval.json_reporter import generate_dimension_json

        result = generate_dimension_json(
            system_prompt_score=65,
            domain_knowledge_score=62,
            workflow_score=58,
            error_handling_score=48,
            examples_score=50,
            metadata_score=27,
            identity_consistency_score=75,
            framework_execution_score=62,
            output_actionability_score=65,
            knowledge_accuracy_score=45,
            conversation_stability_score=45,
            trace_compliance_score=45,
            long_document_score=25,
            multi_agent_score=22,
            trigger_accuracy_score=23,
        )

        data = json.loads(result)

        assert data["system_prompt"]["score"] == 65
        assert data["system_prompt"]["max"] == 70
        assert data["domain_knowledge"]["score"] == 62
        assert data["trigger_accuracy_score"]["score"] == 23
