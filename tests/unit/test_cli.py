"""Tests for CLI commands."""

from __future__ import annotations

import pytest
from typer.testing import CliRunner

from skill.cli.main import app


class TestCLIApp:
    """Test suite for CLI application."""

    def setup_method(self):
        """Set up test runner."""
        self.runner = CliRunner()

    def test_cli_app_exists(self):
        """Test that CLI app is defined."""
        assert app is not None


class TestEvaluateCommand:
    """Test suite for evaluate command."""

    def setup_method(self):
        self.runner = CliRunner()

    def test_evaluate_requires_target(self):
        """Test that evaluate requires a target argument."""
        result = self.runner.invoke(app, ["evaluate"])
        assert result.exit_code != 0

    def test_evaluate_with_target(self):
        """Test evaluate with a target argument."""
        result = self.runner.invoke(app, ["evaluate", "test_skill"])
        assert result.exit_code == 0
        assert "Evaluating: test_skill" in result.output

    def test_evaluate_with_output_option(self):
        """Test evaluate with output option."""
        result = self.runner.invoke(
            app, ["evaluate", "test_skill", "--output", "results.json"]
        )
        assert result.exit_code == 0
        assert "Output will be saved to: results.json" in result.output

    def test_evaluate_with_verbose_option(self):
        """Test evaluate with verbose option."""
        result = self.runner.invoke(app, ["evaluate", "test_skill", "--verbose"])
        assert result.exit_code == 0
        assert "Verbose mode enabled" in result.output


class TestCreateCommand:
    """Test suite for create command."""

    def setup_method(self):
        self.runner = CliRunner()

    def test_create_requires_prompt(self):
        """Test that create requires a prompt argument."""
        result = self.runner.invoke(app, ["create"])
        assert result.exit_code != 0

    def test_create_with_prompt(self):
        """Test create with a prompt argument."""
        result = self.runner.invoke(app, ["create", "Create a test skill"])
        assert result.exit_code == 0
        assert "Creating skill from: Create a test skill" in result.output
        assert "Target tier: BRONZE" in result.output

    def test_create_with_target_option(self):
        """Test create with target tier option."""
        result = self.runner.invoke(app, ["create", "prompt", "--target", "GOLD"])
        assert result.exit_code == 0
        assert "Target tier: GOLD" in result.output

    def test_create_with_dry_run(self):
        """Test create with dry-run option."""
        result = self.runner.invoke(app, ["create", "prompt", "--dry-run"])
        assert result.exit_code == 0
        assert "Dry run mode" in result.output


class TestEvolveCommand:
    """Test suite for evolve command."""

    def setup_method(self):
        self.runner = CliRunner()

    def test_evolve_requires_skill_file(self):
        """Test that evolve requires a skill file argument."""
        result = self.runner.invoke(app, ["evolve"])
        assert result.exit_code != 0

    def test_evolve_with_skill_file(self):
        """Test evolve with a skill file argument."""
        result = self.runner.invoke(app, ["evolve", "skill.md"])
        assert result.exit_code == 0
        assert "Evolving skill: skill.md" in result.output
        assert "Iterations: 1" in result.output

    def test_evolve_with_iterations_option(self):
        """Test evolve with iterations option."""
        result = self.runner.invoke(app, ["evolve", "skill.md", "--iterations", "5"])
        assert result.exit_code == 0
        assert "Iterations: 5" in result.output


class TestVersionCommand:
    """Test suite for version command."""

    def setup_method(self):
        self.runner = CliRunner()

    def test_version(self):
        """Test version command."""
        result = self.runner.invoke(app, ["version"])
        assert result.exit_code == 0
        assert "skill version" in result.output


class TestParseCommand:
    """Test suite for parse command."""

    def setup_method(self):
        self.runner = CliRunner()

    def test_parse_requires_argument(self):
        """Test that parse requires a file argument."""
        result = self.runner.invoke(app, ["parse"])
        assert result.exit_code != 0

    def test_parse_nonexistent_file(self):
        """Test parse with non-existent file."""
        result = self.runner.invoke(app, ["parse", "nonexistent.md"])
        assert result.exit_code == 1

    def test_parse_valid_file(self, tmp_path):
        """Test parse with a valid SKILL.md file."""
        skill_md = tmp_path / "SKILL.md"
        skill_md.write_text("""---
name: test-skill
description: A test skill
---

# Test
""")
        result = self.runner.invoke(app, ["parse", str(skill_md)])
        assert result.exit_code == 0
        assert "test-skill" in result.output


class TestValidateCommand:
    """Test suite for validate command."""

    def setup_method(self):
        self.runner = CliRunner()

    def test_validate_requires_argument(self):
        """Test that validate requires a file argument."""
        result = self.runner.invoke(app, ["validate"])
        assert result.exit_code != 0

    def test_validate_nonexistent_file(self):
        """Test validate with non-existent file."""
        result = self.runner.invoke(app, ["validate", "nonexistent.md"])
        assert result.exit_code == 1

    def test_validate_valid_file(self, tmp_path):
        """Test validate with a valid SKILL.md file."""
        skill_md = tmp_path / "SKILL.md"
        skill_md.write_text("""---
name: test-skill
description: A test skill
version: 1.0.0
---

# Test
""")
        result = self.runner.invoke(app, ["validate", str(skill_md)])
        assert result.exit_code == 0
        assert "valid" in result.output.lower()


class TestGenerateCommand:
    """Test suite for generate command."""

    def setup_method(self):
        self.runner = CliRunner()

    def test_generate_requires_argument(self):
        """Test that generate requires a file argument."""
        result = self.runner.invoke(app, ["generate"])
        assert result.exit_code != 0

    def test_generate_nonexistent_file(self):
        """Test generate with non-existent file."""
        result = self.runner.invoke(app, ["generate", "nonexistent.yaml"])
        assert result.exit_code == 1

    def test_generate_missing_module(self):
        """Test generate when md_generator module is not available."""
        result = self.runner.invoke(app, ["generate", "metadata.yaml"])
        assert result.exit_code == 1


class TestInitCommand:
    """Test suite for init command."""

    def setup_method(self):
        self.runner = CliRunner()

    def test_init_requires_argument(self):
        """Test that init requires a skill name argument."""
        result = self.runner.invoke(app, ["init"])
        assert result.exit_code != 0

    def test_init_creates_skill(self, tmp_path):
        """Test init creates a skill scaffold."""
        result = self.runner.invoke(
            app, ["init", "my-skill", "--output", str(tmp_path / "my-skill")]
        )
        assert result.exit_code == 0
        assert (tmp_path / "my-skill" / "SKILL.md").exists()
