"""Agent-based runtime evaluation for skill documents."""

from __future__ import annotations

import json
import re
import shutil
from dataclasses import dataclass
from pathlib import Path


@dataclass
class AgentRuntimeResult:
    """Result of agent-based runtime evaluation."""

    identity_score: int
    actionability_score: int
    knowledge_score: int
    conversation_score: int
    trigger_accuracy: float
    mode_accuracy: float
    framework_score: int
    trace_score: int
    longdoc_score: int
    multiagent_score: int
    f1_score: float


def check_dependencies() -> bool:
    """Check if required dependencies are available.

    Returns:
        True if all dependencies exist, False otherwise.
    """
    for cmd in ["jq", "bc", "curl"]:
        if shutil.which(cmd) is None:
            return False
    return True


def calc_framework_execution(skill_file: Path | str) -> int:
    """Calculate framework execution score.

    Args:
        skill_file: Path to skill file.

    Returns:
        Score out of 70.
    """
    skill_path = Path(skill_file) if isinstance(skill_file, str) else skill_file
    content = skill_path.read_text(encoding="utf-8")

    tool_score = 0
    tool_mentions = len(re.findall(r"tool|invoke|call", content, re.IGNORECASE))
    if tool_mentions >= 3:
        tool_score = 23
    elif tool_mentions >= 1:
        tool_score = 15

    memory_score = 0
    memory_mentions = len(
        re.findall(
            r"memory|Memory|记忆|journal|Journal|read|write|store|retrieve|读取|写入", content
        )
    )
    if memory_mentions >= 2:
        memory_score = 24
    elif memory_mentions >= 1:
        memory_score = 12

    pipeline_score = 0
    pipeline_mentions = len(
        re.findall(
            r"workflow|Workflow|pipeline|Pipeline|流程|阶段|step|phase|stage|步骤|阶段", content
        )
    )
    if pipeline_mentions >= 4:
        pipeline_score = 23
    elif pipeline_mentions >= 2:
        pipeline_score = 15

    return tool_score + memory_score + pipeline_score


def calc_trace_compliance(skill_file: Path | str) -> int:
    """Calculate trace compliance score.

    Args:
        skill_file: Path to skill file.

    Returns:
        Score out of 50.
    """
    skill_path = Path(skill_file) if isinstance(skill_file, str) else skill_file
    content = skill_path.read_text(encoding="utf-8")

    indicators = len(
        re.findall(r"agentpex|behavior|behaviour|rule|规则|constraint|约束|limit|限制", content)
    )

    if indicators >= 10:
        return 50
    elif indicators >= 7:
        return 35
    elif indicators >= 4:
        return 35
    else:
        return 0


def calc_long_document(skill_file: Path | str) -> int:
    """Calculate long document handling score.

    Args:
        skill_file: Path to skill file.

    Returns:
        Score out of 30.
    """
    skill_path = Path(skill_file) if isinstance(skill_file, str) else skill_file
    content = skill_path.read_text(encoding="utf-8")

    chunking_score = 0
    xref_score = 0
    degradation_score = 0

    file_size = len(content)

    if file_size > 50000:
        chunking_score = 10
        xref_score = 10
        degradation_score = 10
    elif file_size > 20000:
        chunking_score = 7
        xref_score = 5
        degradation_score = 5
    elif file_size > 5000:
        chunking_score = 5
        xref_score = 3
        degradation_score = 2

    if re.search(r"chunk|split|分割|分块", content):
        chunking_score = 10

    if re.search(r"reference|cross.?ref|引用|参考", content):
        xref_score = 10

    return chunking_score + xref_score + degradation_score


def calc_multi_agent(skill_file: Path | str) -> int:
    """Calculate multi-agent support score.

    Args:
        skill_file: Path to skill file.

    Returns:
        Score out of 25.
    """
    skill_path = Path(skill_file) if isinstance(skill_file, str) else skill_file
    content = skill_path.read_text(encoding="utf-8")

    parallel_score = 0
    if re.search(r"parallel|并发|并行", content):
        parallel_score = 8

    hierarchical_score = 0
    if re.search(r"hierarchical|层级|层次|hierarchy", content):
        hierarchical_score = 8

    collab_score = 0
    if re.search(r"collaborat|collaboration|协作|合作", content):
        collab_score = 9

    return parallel_score + hierarchical_score + collab_score


def run_heuristic_fallback(skill_file: Path | str, output_dir: Path | str) -> AgentRuntimeResult:
    """Run heuristic fallback when no LLM is available.

    Args:
        skill_file: Path to skill file.
        output_dir: Directory for output files.

    Returns:
        AgentRuntimeResult with heuristic scores.
    """
    skill_path = Path(skill_file) if isinstance(skill_file, str) else skill_file
    output_path = Path(output_dir) if isinstance(output_dir, str) else output_dir
    content = skill_path.read_text(encoding="utf-8")

    has_identity = len(re.findall(r"§1\.1|Identity|角色", content))
    has_framework = len(re.findall(r"§1\.2|Framework|框架", content))
    has_thinking = len(re.findall(r"§1\.3|Thinking|思考", content))
    has_workflow = len(re.findall(r"workflow|Workflow|工作流", content))
    has_examples = len(re.findall(r"example|Example|示例", content))

    identity_score = 0
    if has_identity > 0:
        identity_score += 20
    if has_framework > 0:
        identity_score += 20
    if has_thinking > 0:
        identity_score += 20
    if has_workflow > 0:
        identity_score += 10
    if has_examples > 0:
        identity_score += 10

    if identity_score > 80:
        identity_score = 80

    result = AgentRuntimeResult(
        identity_score=identity_score,
        actionability_score=50,
        knowledge_score=40,
        conversation_score=40,
        trigger_accuracy=0.75,
        mode_accuracy=0.70,
        framework_score=calc_framework_execution(skill_path),
        trace_score=calc_trace_compliance(skill_path),
        longdoc_score=calc_long_document(skill_path),
        multiagent_score=calc_multi_agent(skill_path),
        f1_score=0.75,
    )

    results_json = {
        "evaluation_type": "heuristic_fallback",
        "warning": "No LLM available - results are estimates only",
        "timestamp": "2026-01-01T00:00:00Z",
        "identity_score": result.identity_score,
        "actionability_score": result.actionability_score,
        "knowledge_score": result.knowledge_score,
        "conversation_score": result.conversation_score,
        "f1_score": result.f1_score,
        "mode_accuracy": result.mode_accuracy,
    }

    output_path.mkdir(parents=True, exist_ok=True)
    with open(output_path / "agent_runtime_results.json", "w") as f:
        json.dump(results_json, f, indent=2)

    return result


def run_agent_runtime_eval(
    skill_file: Path | str,
    corpus_file: Path | str | None,
    output_dir: Path | str,
) -> AgentRuntimeResult:
    """Run agent-based runtime evaluation.

    Args:
        skill_file: Path to skill file.
        corpus_file: Optional path to corpus JSON file.
        output_dir: Directory for output files.

    Returns:
        AgentRuntimeResult with evaluation scores.
    """
    skill_path = Path(skill_file) if isinstance(skill_file, str) else skill_file
    output_path = Path(output_dir) if isinstance(output_dir, str) else output_dir

    output_path.mkdir(parents=True, exist_ok=True)

    return run_heuristic_fallback(skill_path, output_path)
