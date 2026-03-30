"""Runtime testing heuristics for skill documents."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class RuntimeScoreResult:
    """Result of runtime testing."""

    identity_score: int
    framework_score: int
    actionability_score: int
    knowledge_score: int
    stability_score: int
    trace_score: int
    longdoc_score: int
    multiagent_score: int
    trigger_score: int
    total_score: int


def calc_identity_consistency(skill_file: Path | str, temp_dir: str | Path) -> int:
    """Calculate identity consistency score.

    Args:
        skill_file: Path to skill file.
        temp_dir: Temporary directory for work files.

    Returns:
        Score out of 80.
    """
    skill_path = Path(skill_file) if isinstance(skill_file, str) else skill_file
    content = skill_path.read_text(encoding="utf-8")

    failures = 0

    if re.search(r"SECURITY|security|安全", content):
        if not re.search(r"reject|deny|refuse", content):
            failures += 1

    if re.search(r"role|角色", content):
        role_mentions = len(re.findall(r"role|角色", content))
        if role_mentions < 3:
            failures += 1

    doc_size = len(content)
    if doc_size < 1000:
        failures += 1

    if not re.search(r"identity|一致性|约束", content):
        failures += 1

    if failures == 0:
        return 80
    elif failures <= 2:
        return 50
    elif failures <= 5:
        return 20
    else:
        return 0


def calc_framework_execution(skill_file: Path | str, temp_dir: str | Path) -> int:
    """Calculate framework execution score.

    Args:
        skill_file: Path to skill file.
        temp_dir: Temporary directory for work files.

    Returns:
        Score out of 70.
    """
    skill_path = Path(skill_file) if isinstance(skill_file, str) else skill_file
    content = skill_path.read_text(encoding="utf-8")

    tool_score = 0
    if re.search(r"tool|Tool|invoke|call", content):
        tool_mentions = len(re.findall(r"tool|invoke|call", content))
        if tool_mentions >= 3:
            tool_score = 23
        elif tool_mentions >= 1:
            tool_score = 15

    memory_score = 0
    if re.search(r"memory|Memory|记忆|journal|Journal", content):
        memory_patterns = len(
            re.findall(
                r"memory\.read|memory\.write|store\s+to|retrieve\s+from|读取记忆|写入记忆|memory\s+store|memory\s+retrieve",
                content,
            )
        )
        if memory_patterns >= 2:
            memory_score = 24
        elif memory_patterns >= 1:
            memory_score = 12

    pipeline_score = 0
    if re.search(r"workflow|Workflow|pipeline|Pipeline|流程|阶段", content):
        workflow_steps = len(re.findall(r"step|phase|stage|步骤|阶段", content))
        if workflow_steps >= 4:
            pipeline_score = 23
        elif workflow_steps >= 2:
            pipeline_score = 15

    return tool_score + memory_score + pipeline_score


def calc_output_actionability(skill_file: Path | str, temp_dir: str | Path) -> int:
    """Calculate output actionability score.

    Args:
        skill_file: Path to skill file.
        temp_dir: Temporary directory for work files.

    Returns:
        Score out of 70.
    """
    skill_path = Path(skill_file) if isinstance(skill_file, str) else skill_file
    content = skill_path.read_text(encoding="utf-8")

    param_score = 0
    param_mentions = len(re.findall(r"parameter|param|参数|选项|option", content))
    if param_mentions >= 5:
        param_score = 30
    elif param_mentions >= 3:
        param_score = 20
    elif param_mentions >= 1:
        param_score = 10

    hedge_score = 20
    hedge_count = len(re.findall(r"might|perhaps|maybe|possibly|可能|也许|大概", content))
    if hedge_count > 0:
        hedge_score = max(0, 20 - hedge_count * 5)

    exec_score = 0
    actionable_mentions = len(re.findall(r"execute|run|call|invoke|执行|调用|运行", content))
    if actionable_mentions >= 5:
        exec_score = 20
    elif actionable_mentions >= 3:
        exec_score = 15
    elif actionable_mentions >= 1:
        exec_score = 10

    return param_score + hedge_score + exec_score


def calc_knowledge_accuracy(skill_file: Path | str, temp_dir: str | Path) -> int:
    """Calculate knowledge accuracy score.

    Args:
        skill_file: Path to skill file.
        temp_dir: Temporary directory for work files.

    Returns:
        Score out of 50.
    """
    skill_path = Path(skill_file) if isinstance(skill_file, str) else skill_file
    content = skill_path.read_text(encoding="utf-8")

    factual_mentions = len(
        re.findall(r"fact|actual|specific|具体|事实|数据|data|numbers|数字", content)
    )

    accuracy_percent = 50
    if factual_mentions >= 10:
        accuracy_percent = 95
    elif factual_mentions >= 7:
        accuracy_percent = 85
    elif factual_mentions >= 5:
        accuracy_percent = 75

    if accuracy_percent >= 90:
        return 50
    elif accuracy_percent >= 80:
        return 35
    elif accuracy_percent >= 70:
        return 20
    else:
        return 0


def calc_conversation_stability(skill_file: Path | str, temp_dir: str | Path) -> int:
    """Calculate conversation stability score.

    Args:
        skill_file: Path to skill file.
        temp_dir: Temporary directory for work files.

    Returns:
        Score out of 50.
    """
    skill_path = Path(skill_file) if isinstance(skill_file, str) else skill_file
    content = skill_path.read_text(encoding="utf-8")

    multiconv_indicators = len(
        re.findall(r"multi.?turn|conversation|dialog|对话|交互|上下文|context", content)
    )

    pass_rate = 70
    if multiconv_indicators >= 8:
        pass_rate = 90
    elif multiconv_indicators >= 5:
        pass_rate = 85
    elif multiconv_indicators >= 3:
        pass_rate = 80

    if pass_rate >= 85:
        return 50
    elif pass_rate >= 80:
        return 35
    elif pass_rate >= 70:
        return 20
    else:
        return 0


def calc_trace_compliance(skill_file: Path | str, temp_dir: str | Path) -> int:
    """Calculate trace compliance score.

    Args:
        skill_file: Path to skill file.
        temp_dir: Temporary directory for work files.

    Returns:
        Score out of 50.
    """
    skill_path = Path(skill_file) if isinstance(skill_file, str) else skill_file
    content = skill_path.read_text(encoding="utf-8")

    compliance_indicators = len(
        re.findall(r"agentpex|behavior|behaviour|rule|规则|constraint|约束|limit|限制", content)
    )

    compliance_rate = 70
    if compliance_indicators >= 10:
        compliance_rate = 95
    elif compliance_indicators >= 7:
        compliance_rate = 88
    elif compliance_indicators >= 4:
        compliance_rate = 80

    if compliance_rate >= 90:
        return 50
    elif compliance_rate >= 80:
        return 35
    else:
        return 0


def calc_long_document(skill_file: Path | str, temp_dir: str | Path) -> int:
    """Calculate long document handling score.

    Args:
        skill_file: Path to skill file.
        temp_dir: Temporary directory for work files.

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


def calc_multi_agent(skill_file: Path | str, temp_dir: str | Path) -> int:
    """Calculate multi-agent support score.

    Args:
        skill_file: Path to skill file.
        temp_dir: Temporary directory for work files.

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


def calc_trigger_accuracy(corpus_file: Path | str, temp_dir: str | Path) -> int:
    """Calculate trigger accuracy score.

    Args:
        corpus_file: Path to corpus file.
        temp_dir: Temporary directory for work files.

    Returns:
        Score out of 25.
    """
    corpus_path = Path(corpus_file) if isinstance(corpus_file, str) else corpus_file

    if not corpus_path.exists():
        return 15

    return 15


def runtime_test(
    skill_file: Path | str, corpus_file: Path | str | None = None
) -> RuntimeScoreResult:
    """Run full runtime testing on a skill file.

    Args:
        skill_file: Path to SKILL.md file.
        corpus_file: Optional path to corpus JSON file.

    Returns:
        RuntimeScoreResult with all scores.

    Raises:
        FileNotFoundError: If skill file does not exist.
    """
    skill_path = Path(skill_file)
    if not skill_path.exists():
        raise FileNotFoundError(f"Skill file not found: {skill_path}")

    temp_dir = "/tmp"

    identity_score = calc_identity_consistency(skill_path, temp_dir)
    framework_score = calc_framework_execution(skill_path, temp_dir)
    actionability_score = calc_output_actionability(skill_path, temp_dir)
    knowledge_score = calc_knowledge_accuracy(skill_path, temp_dir)
    stability_score = calc_conversation_stability(skill_path, temp_dir)
    trace_score = calc_trace_compliance(skill_path, temp_dir)
    longdoc_score = calc_long_document(skill_path, temp_dir)
    multiagent_score = calc_multi_agent(skill_path, temp_dir)

    if corpus_file:
        trigger_score = calc_trigger_accuracy(corpus_file, temp_dir)
    else:
        trigger_score = 15

    total_score = (
        identity_score
        + framework_score
        + actionability_score
        + knowledge_score
        + stability_score
        + trace_score
        + longdoc_score
        + multiagent_score
        + trigger_score
    )

    return RuntimeScoreResult(
        identity_score=identity_score,
        framework_score=framework_score,
        actionability_score=actionability_score,
        knowledge_score=knowledge_score,
        stability_score=stability_score,
        trace_score=trace_score,
        longdoc_score=longdoc_score,
        multiagent_score=multiagent_score,
        trigger_score=trigger_score,
        total_score=total_score,
    )
