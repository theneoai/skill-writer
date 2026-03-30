"""Base Agent infrastructure for skill framework."""

from __future__ import annotations

import json
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

PROMPT_DIR = Path(__file__).parent.parent / "prompts"


@dataclass
class AgentConfig:
    """Configuration for agent behavior."""

    model: str = "auto"
    provider: str = "auto"


class AgentBase:
    """Base class for all agents providing common infrastructure."""

    def __init__(self, config: Optional[AgentConfig] = None) -> None:
        """Initialize agent with configuration.

        Args:
            config: Optional agent configuration. Uses defaults if not provided.
        """
        self.config = config or AgentConfig()


def get_prompt_path(prompt_name: str) -> Path:
    """Get the file path for a prompt.

    Args:
        prompt_name: Name of the prompt file without extension.

    Returns:
        Path to the prompt file.
    """
    return PROMPT_DIR / f"{prompt_name}.txt"


def load_prompt(prompt_name: str) -> str:
    """Load a prompt template by name.

    Args:
        prompt_name: Name of the prompt to load.

    Returns:
        The prompt content as a string.
    """
    prompt_path = get_prompt_path(prompt_name)
    if prompt_path.exists():
        return prompt_path.read_text()
    return ""


def get_llm_response(system_prompt: str, user_prompt: str, model: str, provider: str) -> dict:
    """Get response from LLM.

    Args:
        system_prompt: System prompt for the LLM.
        user_prompt: User prompt for the LLM.
        model: Model to use.
        provider: Provider to use.

    Returns:
        Dictionary with status and content.
    """
    return {"status": "error", "content": ""}


def call_llm(
    system_prompt: str, user_prompt: str, model: str = "auto", provider: str = "auto"
) -> dict:
    """Call LLM and return response.

    Args:
        system_prompt: System prompt.
        user_prompt: User prompt.
        model: Model to use (default: auto).
        provider: Provider to use (default: auto).

    Returns:
        Dictionary with status and content.
    """
    return get_llm_response(system_prompt, user_prompt, model, provider)


def call_llm_json(
    system_prompt: str, user_prompt: str, model: str = "auto", provider: str = "auto"
) -> dict:
    """Call LLM and parse JSON response.

    Args:
        system_prompt: System prompt.
        user_prompt: User prompt.
        model: Model to use.
        provider: Provider to use.

    Returns:
        Parsed JSON as dictionary.
    """
    response = call_llm(system_prompt, user_prompt, model, provider)
    if response.get("status") == "success" and response.get("content"):
        try:
            return json.loads(response["content"])
        except json.JSONDecodeError:
            return {}
    return {}


def parse_json(json_str: str, key: str) -> str:
    """Parse JSON string and extract value by key.

    Args:
        json_str: JSON string to parse.
        key: Key to extract.

    Returns:
        Value for key or empty string if not found.
    """
    try:
        data = json.loads(json_str)
        return str(data.get(key, ""))
    except (json.JSONDecodeError, TypeError):
        return ""


def validate_json(json_str: str) -> bool:
    """Validate if string is valid JSON.

    Args:
        json_str: String to validate.

    Returns:
        True if valid JSON, False otherwise.
    """
    try:
        json.loads(json_str)
        return True
    except (json.JSONDecodeError, TypeError):
        return False


def temp_file() -> str:
    """Create a temporary file for agent use.

    Returns:
        Path to the created temporary file.
    """
    fd, path = tempfile.mkstemp(suffix=".json")
    os.close(fd)
    return path


def agent_init() -> None:
    """Initialize agent infrastructure."""
    pass
