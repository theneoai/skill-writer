"""Tests for base agent infrastructure."""

import json
import tempfile
from unittest.mock import patch, MagicMock

import pytest

from skill.agents.agent import (
    AgentBase,
    AgentConfig,
    load_prompt,
    call_llm,
    call_llm_json,
    parse_json,
    validate_json,
    temp_file,
)


class TestAgentConfig:
    """Test suite for AgentConfig."""

    def test_default_config(self):
        """Test default agent configuration."""
        config = AgentConfig()
        assert config.model == "auto"
        assert config.provider == "auto"

    def test_custom_config(self):
        """Test custom agent configuration."""
        config = AgentConfig(model="gpt-4", provider="openai")
        assert config.model == "gpt-4"
        assert config.provider == "openai"


class TestAgentBase:
    """Test suite for AgentBase."""

    def test_init(self):
        """Test agent initialization."""
        agent = AgentBase()
        assert agent.config is not None
        assert agent.config.model == "auto"
        assert agent.config.provider == "auto"

    def test_init_with_config(self):
        """Test agent initialization with custom config."""
        config = AgentConfig(model="claude-3", provider="anthropic")
        agent = AgentBase(config)
        assert agent.config.model == "claude-3"
        assert agent.config.provider == "anthropic"


class TestLoadPrompt:
    """Test suite for load_prompt function."""

    def test_load_prompt_nonexistent(self):
        """Test loading non-existent prompt returns empty string."""
        result = load_prompt("nonexistent-prompt-xyz")
        assert result == ""


class TestCallLlm:
    """Test suite for call_llm function."""

    @patch("skill.agents.agent.get_llm_response")
    def test_call_llm_success(self, mock_get_response):
        """Test successful LLM call."""
        mock_get_response.return_value = {
            "status": "success",
            "content": "Test response",
        }
        result = call_llm("system prompt", "user prompt", "auto", "auto")
        assert result["status"] == "success"
        assert result["content"] == "Test response"

    @patch("skill.agents.agent.get_llm_response")
    def test_call_llm_error(self, mock_get_response):
        """Test LLM call with error."""
        mock_get_response.return_value = {"status": "error", "content": ""}
        result = call_llm("system prompt", "user prompt", "auto", "auto")
        assert result["status"] == "error"


class TestCallLlmJson:
    """Test suite for call_llm_json function."""

    @patch("skill.agents.agent.call_llm")
    def test_call_llm_json_success(self, mock_call_llm):
        """Test successful JSON LLM call."""
        mock_call_llm.return_value = {
            "status": "success",
            "content": '{"key": "value"}',
        }
        result = call_llm_json("system", "user", "auto", "auto")
        assert result["key"] == "value"


class TestParseJson:
    """Test suite for parse_json function."""

    def test_parse_json_valid(self):
        """Test parsing valid JSON."""
        json_str = '{"key": "value", "number": 42}'
        result = parse_json(json_str, "key")
        assert result == "value"

    def test_parse_json_missing_key(self):
        """Test parsing JSON with missing key."""
        json_str = '{"key": "value"}'
        result = parse_json(json_str, "missing")
        assert result == ""

    def test_parse_json_invalid(self):
        """Test parsing invalid JSON."""
        json_str = "not valid json"
        result = parse_json(json_str, "key")
        assert result == ""


class TestValidateJson:
    """Test suite for validate_json function."""

    def test_validate_json_valid(self):
        """Test validating valid JSON."""
        json_str = '{"key": "value"}'
        assert validate_json(json_str) is True

    def test_validate_json_invalid(self):
        """Test validating invalid JSON."""
        json_str = "not valid json"
        assert validate_json(json_str) is False

    def test_validate_json_empty(self):
        """Test validating empty string."""
        assert validate_json("") is False


class TestTempFile:
    """Test suite for temp_file function."""

    def test_temp_file_creates_file(self):
        """Test temp file creation."""
        filepath = temp_file()
        assert filepath is not None
        assert filepath.endswith(".json")
        import os

        os.unlink(filepath)

    def test_temp_file_unique(self):
        """Test temp files are unique."""
        filepath1 = temp_file()
        filepath2 = temp_file()
        assert filepath1 != filepath2
        import os

        os.unlink(filepath1)
        os.unlink(filepath2)
