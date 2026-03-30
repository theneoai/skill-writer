"""Tests for skill metadata schema."""

from __future__ import annotations

from skill.schema import (
    EvolutionConfig,
    LLMConfig,
    Mode,
    SecurityConfig,
    SignoffType,
    SkillMetadata,
    SkillType,
    Tier,
    TriggerConfig,
    ValidationConfig,
)


class TestEnums:
    """Test suite for schema enums."""

    def test_mode_values(self):
        """Test Mode enum has correct values."""
        assert Mode.CREATE.value == "create"
        assert Mode.EVALUATE.value == "evaluate"
        assert Mode.RESTORE.value == "restore"
        assert Mode.SECURITY.value == "security"
        assert Mode.OPTIMIZE.value == "optimize"

    def test_mode_count(self):
        """Test Mode enum has exactly 5 modes."""
        assert len(Mode) == 5

    def test_tier_values(self):
        """Test Tier enum has correct values."""
        assert Tier.PLATINUM.value == "platinum"
        assert Tier.GOLD.value == "gold"
        assert Tier.SILVER.value == "silver"
        assert Tier.BRONZE.value == "bronze"

    def test_tier_count(self):
        """Test Tier enum has exactly 4 tiers."""
        assert len(Tier) == 4

    def test_signoff_type_values(self):
        """Test SignoffType enum has correct values."""
        assert SignoffType.HUMAN.value == "human"
        assert SignoffType.AUTOMATED.value == "automated"
        assert SignoffType.TEMP_CERT.value == "temp_cert"

    def test_signoff_type_count(self):
        """Test SignoffType enum has exactly 3 types."""
        assert len(SignoffType) == 3

    def test_skill_type_values(self):
        """Test SkillType enum has correct values."""
        assert SkillType.MANAGER.value == "manager"
        assert SkillType.WORKER.value == "worker"
        assert SkillType.ORCHESTRATOR.value == "orchestrator"
        assert SkillType.UTILITY.value == "utility"


class TestSkillMetadata:
    """Test suite for SkillMetadata dataclass."""

    def test_parse_minimal_yaml(self):
        """Test parsing minimal valid YAML frontmatter."""
        yaml_str = """---
name: test-skill
description: A test skill description here
---"""
        metadata = SkillMetadata.from_yaml(yaml_str)
        assert metadata.name == "test-skill"
        assert metadata.description == "A test skill description here"
        assert metadata.version == "0.1.0"
        assert metadata.license == "MIT"
        assert metadata.author is None
        assert metadata.tags == []
        assert metadata.type == SkillType.WORKER
        assert metadata.tier == Tier.BRONZE

    def test_parse_full_yaml(self):
        """Test parsing complete YAML frontmatter."""
        yaml_str = """---
name: full-skill
description: >
  A comprehensive skill with all fields configured.
  Multi-line description for testing purposes.
version: 2.15.0
license: Apache-2.0
author: theneoai <lucas_hsueh@hotmail.com>
tags: [meta, agent, lifecycle]
type: manager
modes: [create, evaluate, restore]
tier: platinum
signoff: human
---"""
        metadata = SkillMetadata.from_yaml(yaml_str)
        assert metadata.name == "full-skill"
        assert "comprehensive skill" in metadata.description
        assert metadata.version == "2.15.0"
        assert metadata.license == "Apache-2.0"
        assert metadata.author == "theneoai <lucas_hsueh@hotmail.com>"
        assert metadata.tags == ["meta", "agent", "lifecycle"]
        assert metadata.type == SkillType.MANAGER
        assert Mode.CREATE in metadata.modes
        assert Mode.EVALUATE in metadata.modes
        assert Mode.RESTORE in metadata.modes
        assert metadata.tier == Tier.PLATINUM
        assert metadata.signoff == SignoffType.HUMAN

    def test_default_values(self):
        """Test default values for optional fields."""
        metadata = SkillMetadata(name="defaults", description="Testing defaults")
        assert metadata.version == "0.1.0"
        assert metadata.license == "MIT"
        assert metadata.author is None
        assert metadata.tags == []
        assert metadata.type == SkillType.WORKER
        assert metadata.modes == []
        assert metadata.tier == Tier.BRONZE
        assert metadata.signoff == SignoffType.AUTOMATED
        assert metadata.evolution.enabled is False
        assert metadata.security.cwe_enabled is True
        assert metadata.validation.require_description is True

    def test_from_dict(self):
        """Test creating SkillMetadata from dictionary."""
        data = {
            "name": "dict-skill",
            "description": "Created from dictionary",
            "version": "1.0.0",
            "tier": "GOLD",
            "modes": ["create", "optimize"],
        }
        metadata = SkillMetadata.from_dict(data)
        assert metadata.name == "dict-skill"
        assert metadata.tier == Tier.GOLD
        assert Mode.CREATE in metadata.modes
        assert Mode.OPTIMIZE in metadata.modes

    def test_to_dict(self):
        """Test converting SkillMetadata to dictionary."""
        metadata = SkillMetadata(
            name="convert-skill",
            description="Testing to_dict",
            tier=Tier.SILVER,
            modes=[Mode.EVALUATE, Mode.SECURITY],
        )
        result = metadata.to_dict()
        assert result["name"] == "convert-skill"
        assert result["tier"] == "silver"
        assert result["modes"] == ["evaluate", "security"]


class TestValidation:
    """Test suite for SkillMetadata validation."""

    def test_valid_metadata(self):
        """Test validation passes for valid metadata."""
        metadata = SkillMetadata(
            name="valid-skill",
            description="A valid skill description that is long enough",
        )
        errors = metadata.validate()
        assert errors == []

    def test_empty_name(self):
        """Test validation fails for empty name."""
        metadata = SkillMetadata(name="", description="Valid description here")
        errors = metadata.validate()
        assert "name is required" in errors[0]

    def test_whitespace_name(self):
        """Test validation fails for whitespace-only name."""
        metadata = SkillMetadata(name="   ", description="Valid description here")
        errors = metadata.validate()
        assert "name is required" in errors[0]

    def test_empty_description(self):
        """Test validation fails for empty description."""
        metadata = SkillMetadata(name="test-skill", description="")
        errors = metadata.validate()
        assert "description is required" in errors[0]

    def test_short_description(self):
        """Test validation fails for description below minimum length."""
        metadata = SkillMetadata(name="test-skill", description="Short")
        errors = metadata.validate()
        assert "description must be at least 10 characters" in errors[0]

    def test_empty_version(self):
        """Test validation fails for empty version."""
        metadata = SkillMetadata(
            name="test-skill",
            description="Valid description here",
            version="",
        )
        errors = metadata.validate()
        assert "version is required" in errors[0]

    def test_empty_author(self):
        """Test validation fails for empty author string."""
        metadata = SkillMetadata(
            name="test-skill",
            description="Valid description here",
            author="",
        )
        errors = metadata.validate()
        assert "author must be empty string or non-empty if provided" in errors

    def test_multiple_errors(self):
        """Test validation returns multiple errors."""
        metadata = SkillMetadata(name="", description="", version="")
        errors = metadata.validate()
        assert len(errors) >= 3


class TestNestedConfigs:
    """Test suite for nested configuration dataclasses."""

    def test_evolution_config_defaults(self):
        """Test EvolutionConfig default values."""
        config = EvolutionConfig()
        assert config.enabled is False
        assert config.f1_target == 0.90
        assert config.trigger.threshold == 0.8
        assert config.trigger.interval_seconds == 3600
        assert config.trigger.min_usage_count == 10

    def test_security_config_defaults(self):
        """Test SecurityConfig default values."""
        config = SecurityConfig()
        assert config.cwe_enabled is True
        assert config.scan_on_create is True
        assert config.scan_on_update is True

    def test_validation_config_defaults(self):
        """Test ValidationConfig default values."""
        config = ValidationConfig()
        assert config.require_description is True
        assert config.min_description_length == 10
        assert config.require_tags is False
        assert config.min_tags == 0

    def test_llm_config_defaults(self):
        """Test LLMConfig default values."""
        config = LLMConfig()
        assert config.enabled is False
        assert config.model is None
        assert config.temperature == 0.7
        assert config.max_tokens == 2048

    def test_trigger_config_defaults(self):
        """Test TriggerConfig default values."""
        config = TriggerConfig()
        assert config.threshold == 0.8
        assert config.interval_seconds == 3600
        assert config.min_usage_count == 10


class TestEdgeCases:
    """Test suite for edge cases in parsing."""

    def test_empty_yaml(self):
        """Test parsing empty YAML returns defaults."""
        metadata = SkillMetadata.from_yaml("")
        assert metadata.name == ""
        assert metadata.description == ""

    def test_yaml_only_name_and_description(self):
        """Test parsing YAML with name and description fields."""
        yaml_str = "name: single-field\ndescription: A single field test"
        metadata = SkillMetadata.from_yaml(yaml_str)
        assert metadata.name == "single-field"
        assert metadata.description == "A single field test"

    def test_mode_case_insensitive(self):
        """Test modes are parsed case-insensitively."""
        yaml_str = """---
name: case-test
description: Testing case insensitive modes
modes: [CREATE, EVALUATE, Restore]
---"""
        metadata = SkillMetadata.from_yaml(yaml_str)
        assert Mode.CREATE in metadata.modes
        assert Mode.EVALUATE in metadata.modes
        assert Mode.RESTORE in metadata.modes

    def test_tier_case_insensitive(self):
        """Test tier is parsed case-insensitively."""
        yaml_str = """---
name: tier-test
description: Testing case insensitive tier
tier: PLATINUM
---"""
        metadata = SkillMetadata.from_yaml(yaml_str)
        assert metadata.tier == Tier.PLATINUM
