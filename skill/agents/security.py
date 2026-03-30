"""Security Agent - OWASP AST10 security audit."""

from __future__ import annotations

import json
import os
import re
from typing import Any, Optional

from skill.agents.agent import AgentBase, call_llm, call_llm_json, validate_json


class SecurityAgent(AgentBase):
    """Agent for security auditing with OWASP AST10 checklist."""

    def __init__(self) -> None:
        """Initialize Security agent."""
        super().__init__()


OWASP_AST10_ITEMS = [
    "Credential Scan",
    "Input Validation",
    "Path Traversal",
    "Trigger Sanitization",
    "YAML Parsing Safety",
    "Command Injection Prevention",
    "SQL Injection Prevention",
    "Data Exposure Prevention",
    "Log信息安全",
    "Error Handling Security",
]


def audit_security(skill_file: str, audit_level: str = "FULL") -> dict:
    """Audit a skill file for security issues.

    Args:
        skill_file: Path to skill file.
        audit_level: Audit level (FULL or BASIC).

    Returns:
        Dictionary with security audit results.
    """
    if not os.path.exists(skill_file):
        return {"error": "Skill file not found"}

    try:
        with open(skill_file, "r") as f:
            content = f.read()
    except IOError:
        return {"error": "Could not read skill file"}

    results = []
    overall_status = "PASS"
    p0_count = 0
    p1_count = 0
    p2_count = 0

    for item in OWASP_AST10_ITEMS:
        item_result = {
            "item": item,
            "status": "PASS",
            "severity": "NONE",
            "findings": "No issues found",
            "llm_providers": [],
        }

        item_status = "PASS"
        item_severity = "NONE"
        item_findings = "No issues found"
        providers_checked = []

        if item == "Credential Scan":
            scan_result = multi_llm_credential_scan(content)
            item_status = scan_result.get("status", "PASS")
            item_severity = scan_result.get("severity", "NONE")
            item_findings = scan_result.get("findings", "")
            providers_checked = ["anthropic", "openai", "kimi"]
        elif item == "Input Validation":
            input_result = multi_llm_input_validation(content)
            item_status = input_result.get("status", "PASS")
            item_severity = input_result.get("severity", "NONE")
            item_findings = input_result.get("findings", "")
            providers_checked = ["anthropic", "openai", "kimi"]
        elif item == "Path Traversal":
            path_result = multi_llm_path_traversal(content)
            item_status = path_result.get("status", "PASS")
            item_severity = path_result.get("severity", "NONE")
            item_findings = path_result.get("findings", "")
            providers_checked = ["anthropic", "openai", "kimi"]
        elif item == "Trigger Sanitization":
            trigger_result = multi_llm_trigger_validation(content)
            item_status = trigger_result.get("status", "PASS")
            item_severity = trigger_result.get("severity", "NONE")
            item_findings = trigger_result.get("findings", "")
            providers_checked = ["anthropic", "openai", "kimi"]
        elif item == "YAML Parsing Safety":
            yaml_result = multi_llm_yaml_safety(content)
            item_status = yaml_result.get("status", "PASS")
            item_severity = yaml_result.get("severity", "NONE")
            item_findings = yaml_result.get("findings", "")
            providers_checked = ["anthropic", "openai"]
        elif item == "Command Injection Prevention":
            cmd_result = multi_llm_command_injection(content)
            item_status = cmd_result.get("status", "PASS")
            item_severity = cmd_result.get("severity", "NONE")
            item_findings = cmd_result.get("findings", "")
            providers_checked = ["anthropic", "openai", "kimi"]
        elif item == "SQL Injection Prevention":
            sql_result = multi_llm_sql_injection(content)
            item_status = sql_result.get("status", "PASS")
            item_severity = sql_result.get("severity", "NONE")
            item_findings = sql_result.get("findings", "")
            providers_checked = ["anthropic", "openai"]
        elif item == "Data Exposure Prevention":
            data_result = multi_llm_data_exposure(content)
            item_status = data_result.get("status", "PASS")
            item_severity = data_result.get("severity", "NONE")
            item_findings = data_result.get("findings", "")
            providers_checked = ["anthropic", "openai", "kimi"]
        elif item == "Log信息安全":
            log_result = multi_llm_log_security(content)
            item_status = log_result.get("status", "PASS")
            item_severity = log_result.get("severity", "NONE")
            item_findings = log_result.get("findings", "")
            providers_checked = ["anthropic", "openai"]
        elif item == "Error Handling Security":
            error_result = multi_llm_error_handling(content)
            item_status = error_result.get("status", "PASS")
            item_severity = error_result.get("severity", "NONE")
            item_findings = error_result.get("findings", "")
            providers_checked = ["anthropic", "openai"]

        if item_status == "FAIL":
            if item_severity == "P0":
                p0_count += 1
            elif item_severity == "P1":
                p1_count += 1
            elif item_severity == "P2":
                p2_count += 1
            overall_status = "FAIL"

        results.append(
            {
                "item": item,
                "status": item_status,
                "severity": item_severity,
                "findings": item_findings,
                "llm_providers": providers_checked,
            }
        )

    recommendation = "APPROVED"
    if overall_status == "FAIL":
        if p0_count > 0:
            recommendation = "BLOCK_DEPLOYMENT"
        elif p1_count > 0:
            recommendation = "REVIEW_REQUIRED"

    return {
        "security_status": overall_status,
        "p0_violations": p0_count,
        "p1_violations": p1_count,
        "p2_violations": p2_count,
        "items_checked": results,
        "recommendation": recommendation,
    }


def multi_llm_credential_scan(content: str) -> dict:
    """Scan for credentials using multiple LLMs.

    Args:
        content: Skill file content.

    Returns:
        Dictionary with scan results.
    """
    r1 = llm_credential_scan_single("anthropic", content)
    r2 = llm_credential_scan_single("openai", content)
    r3 = llm_credential_scan_single("kimi", content)

    return cross_validate_results(
        json.dumps(r1) if isinstance(r1, dict) else r1,
        json.dumps(r2) if isinstance(r2, dict) else r2,
        json.dumps(r3) if isinstance(r3, dict) else r3,
        "credential_scan",
    )


def llm_credential_scan_single(provider: str, content: str) -> dict:
    """Scan for credentials using a single LLM.

    Args:
        provider: LLM provider.
        content: Skill file content.

    Returns:
        Dictionary with scan results.
    """
    prompt = f"""Scan this skill file for credential vulnerabilities:

CWE-798: Hardcoded credentials
CWE-259: Hard-coded password
CWE-321: Use of hard-coded cryptographic key
CWE-260: Password in configuration file

Check for patterns like:
- password=, api_key=, secret=, token=
- sk-[a-zA-Z0-9]{{20,}} (OpenAI keys)
- AKIA[0-9A-Z]{{16,}} (AWS keys)
- any obvious password strings

Content:
{content}

Respond with JSON:
{{
  "status": "PASS" or "FAIL",
  "severity": "NONE" or "P0" or "P1" or "P2",
  "findings": "Description of any credentials found"
}}"""

    response = call_llm(
        "You are a security expert. Scan for credential vulnerabilities.", prompt, "auto", provider
    )

    if response.get("status") == "success" and response.get("content"):
        try:
            return json.loads(response["content"])
        except json.JSONDecodeError:
            return {"status": "PASS", "severity": "NONE", "findings": ""}
    return {"status": "PASS", "severity": "NONE", "findings": ""}


def multi_llm_input_validation(content: str) -> dict:
    """Check input validation using multiple LLMs.

    Args:
        content: Skill file content.

    Returns:
        Dictionary with validation results.
    """
    r1 = llm_input_validation_single("anthropic", content)
    r2 = llm_input_validation_single("openai", content)
    r3 = llm_input_validation_single("kimi", content)

    return cross_validate_results(
        json.dumps(r1) if isinstance(r1, dict) else r1,
        json.dumps(r2) if isinstance(r2, dict) else r2,
        json.dumps(r3) if isinstance(r3, dict) else r3,
        "input_validation",
    )


def llm_input_validation_single(provider: str, content: str) -> dict:
    """Check input validation using a single LLM.

    Args:
        provider: LLM provider.
        content: Skill file content.

    Returns:
        Dictionary with validation results.
    """
    prompt = f"""Check this skill file for input validation issues:

CWE-20: Improper Input Validation
CWE-79: Cross-site Scripting (XSS)
CWE-89: SQL Injection (in skill references)

Look for:
- User inputs that are not validated
- File paths from user input used unsanitized
- Command arguments not validated

Content:
{content}

Respond with JSON:
{{
  "status": "PASS" or "FAIL",
  "severity": "NONE" or "P0" or "P1" or "P2",
  "findings": "Description of validation issues"
}}"""

    response = call_llm(
        "You are a security expert. Check input validation.", prompt, "auto", provider
    )

    if response.get("status") == "success" and response.get("content"):
        try:
            return json.loads(response["content"])
        except json.JSONDecodeError:
            return {"status": "PASS", "severity": "NONE", "findings": ""}
    return {"status": "PASS", "severity": "NONE", "findings": ""}


def multi_llm_path_traversal(content: str) -> dict:
    """Check path traversal using multiple LLMs.

    Args:
        content: Skill file content.

    Returns:
        Dictionary with check results.
    """
    r1 = llm_path_traversal_single("anthropic", content)
    r2 = llm_path_traversal_single("openai", content)
    r3 = llm_path_traversal_single("kimi", content)

    return cross_validate_results(
        json.dumps(r1) if isinstance(r1, dict) else r1,
        json.dumps(r2) if isinstance(r2, dict) else r2,
        json.dumps(r3) if isinstance(r3, dict) else r3,
        "path_traversal",
    )


def llm_path_traversal_single(provider: str, content: str) -> dict:
    """Check path traversal using a single LLM.

    Args:
        provider: LLM provider.
        content: Skill file content.

    Returns:
        Dictionary with check results.
    """
    prompt = f"""Check this skill file for path traversal vulnerabilities:

CWE-22: Path Traversal
CWE-23: Relative Path Traversal
CWE-24: Path Equivalence

Look for:
- File operations without realpath validation
- .. in file paths
- Unsanitized path concatenation

Content:
{content}

Respond with JSON:
{{
  "status": "PASS" or "FAIL",
  "severity": "NONE" or "P0" or "P1" or "P2",
  "findings": "Description of path issues"
}}"""

    response = call_llm(
        "You are a security expert. Check path traversal risks.", prompt, "auto", provider
    )

    if response.get("status") == "success" and response.get("content"):
        try:
            return json.loads(response["content"])
        except json.JSONDecodeError:
            return {"status": "PASS", "severity": "NONE", "findings": ""}
    return {"status": "PASS", "severity": "NONE", "findings": ""}


def multi_llm_trigger_validation(content: str) -> dict:
    """Check trigger sanitization using multiple LLMs.

    Args:
        content: Skill file content.

    Returns:
        Dictionary with check results.
    """
    r1 = llm_trigger_validation_single("anthropic", content)
    r2 = llm_trigger_validation_single("openai", content)
    r3 = llm_trigger_validation_single("kimi", content)

    return cross_validate_results(
        json.dumps(r1) if isinstance(r1, dict) else r1,
        json.dumps(r2) if isinstance(r2, dict) else r2,
        json.dumps(r3) if isinstance(r3, dict) else r3,
        "trigger_validation",
    )


def llm_trigger_validation_single(provider: str, content: str) -> dict:
    """Check trigger sanitization using a single LLM.

    Args:
        provider: LLM provider.
        content: Skill file content.

    Returns:
        Dictionary with check results.
    """
    prompt = f"""Check this skill file for trigger sanitization:

Verify that trigger keywords are validated:
- Regex should be alphanumeric only
- No special characters in trigger patterns
- Input sanitization before trigger matching

Content:
{content}

Respond with JSON:
{{
  "status": "PASS" or "FAIL",
  "severity": "NONE" or "P0" or "P1" or "P2",
  "findings": "Description of trigger issues"
}}"""

    response = call_llm(
        "You are a security expert. Validate trigger sanitization.", prompt, "auto", provider
    )

    if response.get("status") == "success" and response.get("content"):
        try:
            return json.loads(response["content"])
        except json.JSONDecodeError:
            return {"status": "PASS", "severity": "NONE", "findings": ""}
    return {"status": "PASS", "severity": "NONE", "findings": ""}


def multi_llm_yaml_safety(content: str) -> dict:
    """Check YAML safety using multiple LLMs.

    Args:
        content: Skill file content.

    Returns:
        Dictionary with check results.
    """
    r1 = llm_yaml_safety_single("anthropic", content)
    r2 = llm_yaml_safety_single("openai", content)

    return cross_validate_results(
        json.dumps(r1) if isinstance(r1, dict) else r1,
        json.dumps(r2) if isinstance(r2, dict) else r2,
        "",
        "yaml_safety",
    )


def llm_yaml_safety_single(provider: str, content: str) -> dict:
    """Check YAML safety using a single LLM.

    Args:
        provider: LLM provider.
        content: Skill file content.

    Returns:
        Dictionary with check results.
    """
    prompt = f"""Check YAML frontmatter parsing safety:

CWE-20: Improper Input Validation (YAML parsing)
CWE-94: Code Injection (YAML deserialization)

Verify:
- YAML frontmatter is properly formatted
- No injection via YAML special characters
- Safe YAML parsing without eval

Content:
{content}

Respond with JSON:
{{
  "status": "PASS" or "FAIL",
  "severity": "NONE" or "P0" or "P1" or "P2",
  "findings": "Description of YAML issues"
}}"""

    response = call_llm(
        "You are a security expert. Check YAML parsing safety.", prompt, "auto", provider
    )

    if response.get("status") == "success" and response.get("content"):
        try:
            return json.loads(response["content"])
        except json.JSONDecodeError:
            return {"status": "PASS", "severity": "NONE", "findings": ""}
    return {"status": "PASS", "severity": "NONE", "findings": ""}


def multi_llm_command_injection(content: str) -> dict:
    """Check command injection using multiple LLMs.

    Args:
        content: Skill file content.

    Returns:
        Dictionary with check results.
    """
    r1 = llm_command_injection_single("anthropic", content)
    r2 = llm_command_injection_single("openai", content)
    r3 = llm_command_injection_single("kimi", content)

    return cross_validate_results(
        json.dumps(r1) if isinstance(r1, dict) else r1,
        json.dumps(r2) if isinstance(r2, dict) else r2,
        json.dumps(r3) if isinstance(r3, dict) else r3,
        "command_injection",
    )


def llm_command_injection_single(provider: str, content: str) -> dict:
    """Check command injection using a single LLM.

    Args:
        provider: LLM provider.
        content: Skill file content.

    Returns:
        Dictionary with check results.
    """
    prompt = f"""Check for command injection vulnerabilities:

CWE-78: OS Command Injection
CWE-77: Command Injection (blank)

Look for:
- eval, system, exec calls with user input
- Shell commands built from unsanitized input
- Backticks or $() with user content

Content:
{content}

Respond with JSON:
{{
  "status": "PASS" or "FAIL",
  "severity": "NONE" or "P0" or "P1" or "P2",
  "findings": "Description of command injection risks"
}}"""

    response = call_llm(
        "You are a security expert. Check command injection vectors.", prompt, "auto", provider
    )

    if response.get("status") == "success" and response.get("content"):
        try:
            return json.loads(response["content"])
        except json.JSONDecodeError:
            return {"status": "PASS", "severity": "NONE", "findings": ""}
    return {"status": "PASS", "severity": "NONE", "findings": ""}


def multi_llm_sql_injection(content: str) -> dict:
    """Check SQL injection using multiple LLMs.

    Args:
        content: Skill file content.

    Returns:
        Dictionary with check results.
    """
    r1 = llm_sql_injection_single("anthropic", content)
    r2 = llm_sql_injection_single("openai", content)

    return cross_validate_results(
        json.dumps(r1) if isinstance(r1, dict) else r1,
        json.dumps(r2) if isinstance(r2, dict) else r2,
        "",
        "sql_injection",
    )


def llm_sql_injection_single(provider: str, content: str) -> dict:
    """Check SQL injection using a single LLM.

    Args:
        provider: LLM provider.
        content: Skill file content.

    Returns:
        Dictionary with check results.
    """
    prompt = f"""Check for SQL injection vulnerabilities:

CWE-89: SQL Injection

Look for:
- SQL queries built from user input
- String concatenation in SQL statements
- No parameterized queries

Content:
{content}

Respond with JSON:
{{
  "status": "PASS" or "FAIL",
  "severity": "NONE" or "P0" or "P1" or "P2",
  "findings": "Description of SQL injection risks"
}}"""

    response = call_llm(
        "You are a security expert. Check SQL injection vectors.", prompt, "auto", provider
    )

    if response.get("status") == "success" and response.get("content"):
        try:
            return json.loads(response["content"])
        except json.JSONDecodeError:
            return {"status": "PASS", "severity": "NONE", "findings": ""}
    return {"status": "PASS", "severity": "NONE", "findings": ""}


def multi_llm_data_exposure(content: str) -> dict:
    """Check data exposure using multiple LLMs.

    Args:
        content: Skill file content.

    Returns:
        Dictionary with check results.
    """
    r1 = llm_data_exposure_single("anthropic", content)
    r2 = llm_data_exposure_single("openai", content)
    r3 = llm_data_exposure_single("kimi", content)

    return cross_validate_results(
        json.dumps(r1) if isinstance(r1, dict) else r1,
        json.dumps(r2) if isinstance(r2, dict) else r2,
        json.dumps(r3) if isinstance(r3, dict) else r3,
        "data_exposure",
    )


def llm_data_exposure_single(provider: str, content: str) -> dict:
    """Check data exposure using a single LLM.

    Args:
        provider: LLM provider.
        content: Skill file content.

    Returns:
        Dictionary with check results.
    """
    prompt = f"""Check for data exposure vulnerabilities:

CWE-200: Exposure of Sensitive Information to an Unauthorized Actor
CWE-359: Exposure of Private Personal Information

Look for:
- Logging sensitive data
- Error messages revealing internal info
- Exposing API keys, tokens, passwords in output

Content:
{content}

Respond with JSON:
{{
  "status": "PASS" or "FAIL",
  "severity": "NONE" or "P0" or "P1" or "P2",
  "findings": "Description of data exposure risks"
}}"""

    response = call_llm(
        "You are a security expert. Check data exposure risks.", prompt, "auto", provider
    )

    if response.get("status") == "success" and response.get("content"):
        try:
            return json.loads(response["content"])
        except json.JSONDecodeError:
            return {"status": "PASS", "severity": "NONE", "findings": ""}
    return {"status": "PASS", "severity": "NONE", "findings": ""}


def multi_llm_log_security(content: str) -> dict:
    """Check log security using multiple LLMs.

    Args:
        content: Skill file content.

    Returns:
        Dictionary with check results.
    """
    r1 = llm_log_security_single("anthropic", content)
    r2 = llm_log_security_single("openai", content)

    return cross_validate_results(
        json.dumps(r1) if isinstance(r1, dict) else r1,
        json.dumps(r2) if isinstance(r2, dict) else r2,
        "",
        "log_security",
    )


def llm_log_security_single(provider: str, content: str) -> dict:
    """Check log security using a single LLM.

    Args:
        provider: LLM provider.
        content: Skill file content.

    Returns:
        Dictionary with check results.
    """
    prompt = f"""Check log security:

CWE-117: Improper Output Neutralization for Logs
CWE-532: Information Exposure Through Log

Look for:
- Log injection attacks
- Sensitive data in logs
- Improper log sanitization

Content:
{content}

Respond with JSON:
{{
  "status": "PASS" or "FAIL",
  "severity": "NONE" or "P0" or "P1" or "P2",
  "findings": "Description of log security issues"
}}"""

    response = call_llm("You are a security expert. Check log security.", prompt, "auto", provider)

    if response.get("status") == "success" and response.get("content"):
        try:
            return json.loads(response["content"])
        except json.JSONDecodeError:
            return {"status": "PASS", "severity": "NONE", "findings": ""}
    return {"status": "PASS", "severity": "NONE", "findings": ""}


def multi_llm_error_handling(content: str) -> dict:
    """Check error handling using multiple LLMs.

    Args:
        content: Skill file content.

    Returns:
        Dictionary with check results.
    """
    r1 = llm_error_handling_single("anthropic", content)
    r2 = llm_error_handling_single("openai", content)

    return cross_validate_results(
        json.dumps(r1) if isinstance(r1, dict) else r1,
        json.dumps(r2) if isinstance(r2, dict) else r2,
        "",
        "error_handling",
    )


def llm_error_handling_single(provider: str, content: str) -> dict:
    """Check error handling using a single LLM.

    Args:
        provider: LLM provider.
        content: Skill file content.

    Returns:
        Dictionary with check results.
    """
    prompt = f"""Check error handling security:

CWE-209: Generation of Error Message Containing Sensitive Information
CWE-390: Detection of Error Condition Without Action

Look for:
- Error messages revealing system info
- Unhandled exceptions
- Silent failures

Content:
{content}

Respond with JSON:
{{
  "status": "PASS" or "FAIL",
  "severity": "NONE" or "P0" or "P1" or "P2",
  "findings": "Description of error handling issues"
}}"""

    response = call_llm(
        "You are a security expert. Check error handling security.", prompt, "auto", provider
    )

    if response.get("status") == "success" and response.get("content"):
        try:
            return json.loads(response["content"])
        except json.JSONDecodeError:
            return {"status": "PASS", "severity": "NONE", "findings": ""}
    return {"status": "PASS", "severity": "NONE", "findings": ""}


def cross_validate_results(r1: str, r2: str, r3: str, check_type: str) -> dict:
    """Cross-validate results from multiple LLMs.

    Args:
        r1: JSON result from first LLM.
        r2: JSON result from second LLM.
        r3: JSON result from third LLM (can be empty).
        check_type: Type of check being validated.

    Returns:
        Dictionary with validated results.
    """
    try:
        dict1 = json.loads(r1) if r1 else {"status": "UNKNOWN"}
        dict2 = json.loads(r2) if r2 else {"status": "UNKNOWN"}
        dict3 = json.loads(r3) if r3 else {"status": "UNKNOWN"}
    except json.JSONDecodeError:
        return {"status": "PASS", "severity": "NONE", "findings": ""}

    s1 = dict1.get("status", "UNKNOWN")
    s2 = dict2.get("status", "UNKNOWN")

    if s1 == s2:
        return dict1

    s3 = dict3.get("status", "UNKNOWN") if r3 else None

    if s3 and (s1 == s3 or s2 == s3):
        majority = s1 if s1 == s3 else s2
        result = dict1.copy()
        result["status"] = majority
        return result

    result = dict1.copy()
    result["conflict"] = True
    result["resolution"] = "HUMAN_REVIEW_REQUIRED"
    return result
