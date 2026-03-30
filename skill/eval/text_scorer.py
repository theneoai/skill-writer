"""Text quality scoring for skill documents."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class TextScoreResult:
    """Result of text scoring."""

    system_prompt_score: int
    domain_knowledge_score: int
    workflow_score: int
    error_handling_score: int
    examples_score: int
    metadata_score: int
    total_score: int


def score_system_prompt(content: str) -> int:
    """Score system prompt quality based on section markers and rules.

    Args:
        content: Skill document content.

    Returns:
        Score out of 70.
    """
    score = 0

    if re.search(r"(^|\n)#+\s+(§1\.1|1\.1 Identity|1\.1[\s:.\]])", content):
        score += 20
    if re.search(r"(^|\n)#+\s+(§1\.2|1\.2 Framework|1\.2[\s:.\]])", content):
        score += 20
    if re.search(r"(^|\n)#+\s+(§1\.3|1\.3 Thinking|1\.3[\s:.\]])", content):
        score += 20

    if re.search(
        r"(never|always|forbidden|never\s+[Dd]o|always\s+[Mm]ust|do\s+not|must\s+not)", content
    ):
        score += 10

    return score


def score_domain_knowledge(content: str) -> int:
    """Score domain knowledge based on quantitative data and frameworks.

    Args:
        content: Skill document content.

    Returns:
        Score out of 70.
    """
    score = 0

    quantitative_pattern = r"[0-9]+\.[0-9]+%|[0-9]+%|[0-9]+(x|倍|次|个|px|ms|s|min|hour|day|K|M|G|T|P)|\$[0-9]+|[0-9]+\.[0-9]+"
    quantitative_count = len(re.findall(quantitative_pattern, content))

    if quantitative_count >= 10:
        score += 20
    elif quantitative_count >= 5:
        score += 10
    elif quantitative_count >= 1:
        score += 5

    framework_pattern = r"(ReAct|CoT|ToT|RAG|Chain|Agent|Prompt|Retrieval|框架|方法|范式|案例|标准)"
    framework_count = len(re.findall(framework_pattern, content, re.IGNORECASE))

    if framework_count >= 4:
        score += 20
    elif framework_count >= 2:
        score += 10
    elif framework_count >= 1:
        score += 5

    benchmark_pattern = r"(NIST|OWASP|ISO|SECURITY|SANS|CVE|benchmark|standard|framework)"
    benchmark_count = len(re.findall(benchmark_pattern, content, re.IGNORECASE))

    if benchmark_count >= 3:
        score += 15
    elif benchmark_count >= 2:
        score += 10
    elif benchmark_count >= 1:
        score += 5

    case_study_pattern = r"(case|study|example|实例|案例|例如|例子|示例)"
    case_study_count = len(re.findall(case_study_pattern, content, re.IGNORECASE))

    if case_study_count >= 3:
        score += 15
    elif case_study_count >= 2:
        score += 10
    elif case_study_count >= 1:
        score += 5

    if (
        re.search(r"(best\s+practices|industry\s+leader|industry\s+standard)", content)
        and case_study_count < 2
    ):
        score -= 10

    if score < 0:
        score = 0

    return score


def score_workflow(content: str) -> int:
    """Score workflow quality.

    Args:
        content: Skill document content.

    Returns:
        Score out of 70.
    """
    score = 0

    if re.search(r"(workflow|phase|step|阶段|流程|步骤)", content):
        score += 15

    phase_count = len(re.findall(r"(Phase|阶段|Step|步骤|Pipeline)", content))
    if phase_count >= 4 and phase_count <= 6:
        score += 20
    elif phase_count >= 2:
        score += 10
    elif phase_count >= 1:
        score += 5

    done_count = len(re.findall(r"(Done|完成|done|success|成功)", content))
    if done_count >= 4:
        score += 15
    elif done_count >= 2:
        score += 10
    elif done_count >= 1:
        score += 5

    fail_count = len(re.findall(r"(Fail|失败|fail|error|错误|abort|终止)", content))
    if fail_count >= 4:
        score += 15
    elif fail_count >= 2:
        score += 10
    elif fail_count >= 1:
        score += 5

    if re.search(r"(decision|判断|if|else|switch|case|分支)", content):
        score += 5

    return score


def score_error_handling(content: str) -> int:
    """Score error handling quality.

    Args:
        content: Skill document content.

    Returns:
        Score out of 55.
    """
    score = 0

    failure_pattern = r"(failure|Failure|error|Error|fail|Fail|exception|Exception|问题|失败|错误)"
    failure_count = len(re.findall(failure_pattern, content))

    if failure_count >= 5:
        score += 20
    elif failure_count >= 3:
        score += 12
    elif failure_count >= 1:
        score += 5

    recovery_pattern = (
        r"(retry|Retry|fallback|Fallback|circuit|breaker|recovery|recover|重试|恢复|回退|备选)"
    )
    recovery_count = len(re.findall(recovery_pattern, content))

    if recovery_count >= 3:
        score += 20
    elif recovery_count >= 2:
        score += 12
    elif recovery_count >= 1:
        score += 6

    antipattern_pattern = r"(anti.?pattern|anti-pattern|avoid|不要|禁止)"
    antipattern_count = len(re.findall(antipattern_pattern, content))

    if antipattern_count >= 3:
        score += 10
    elif antipattern_count >= 1:
        score += 5

    if re.search(r"(risk|Risk|matrix|矩阵|severity|impact)", content):
        score += 5

    return score


def score_examples(content: str) -> int:
    """Score examples quality.

    Args:
        content: Skill document content.

    Returns:
        Score out of 55.
    """
    score = 0

    example_pattern = r"(example|Example|示例|例子|实例|case|Case|scenario|Scenario)"
    example_count = len(re.findall(example_pattern, content))

    table_example_pattern = r"\|.*\|.*\|"
    table_matches = re.findall(table_example_pattern, content)
    table_example_count = len(
        [
            t
            for t in table_matches
            if re.search(r"(example|示例|例子|实例|案例|case)", t, re.IGNORECASE)
        ]
    )

    example_count += table_example_count

    if example_count >= 5:
        score += 20
    elif example_count >= 3:
        score += 12
    elif example_count >= 1:
        score += 5

    input_pattern = r"(input|Input|输入|参数|param|request)"
    input_count = len(re.findall(input_pattern, content))

    if input_count >= 5:
        score += 10
    elif input_count >= 3:
        score += 6
    elif input_count >= 1:
        score += 3

    output_pattern = r"(output|Output|输出|返回|result|Response)"
    output_count = len(re.findall(output_pattern, content))

    if output_count >= 5:
        score += 10
    elif output_count >= 3:
        score += 6
    elif output_count >= 1:
        score += 3

    verify_pattern = r"(verify|Verify|验证|check|Check|assert|Assert|test|Test|校验)"
    verify_count = len(re.findall(verify_pattern, content))

    if verify_count >= 5:
        score += 10
    elif verify_count >= 3:
        score += 6
    elif verify_count >= 1:
        score += 3

    if re.search(r"(\{[a-z_]+\}|\[.*\]|\w+\s*:)", content):
        score += 5

    return score


def score_metadata(content: str) -> int:
    """Score metadata quality.

    Args:
        content: Skill document content.

    Returns:
        Score out of 30.
    """
    score = 0

    if re.search(r"^\s*name:\s*['\"]?[^\'\"]+", content, re.MULTILINE):
        score += 5

    if re.search(r"^\s*description:\s*['\"]?[^\'\"]+", content, re.MULTILINE):
        score += 5

    if re.search(r"^\s*license:\s*['\"]?[^\'\"]+", content, re.MULTILINE):
        score += 5

    if re.search(r"^\s*version:\s*['\"]?[^\'\"]+", content, re.MULTILINE):
        score += 5

    if re.search(r"^\s*author:\s*['\"]?[^\'\"]+", content, re.MULTILINE):
        score += 5

    if re.search(r"(tags:|categories:|tags |categories )", content):
        score += 5

    return score


def text_score(skill_file: Path | str) -> TextScoreResult:
    """Run full text scoring on a skill file.

    Args:
        skill_file: Path to SKILL.md file.

    Returns:
        TextScoreResult with all scores.

    Raises:
        FileNotFoundError: If skill file does not exist.
    """
    skill_path = Path(skill_file)
    if not skill_path.exists():
        raise FileNotFoundError(f"File not found: {skill_path}")

    content = skill_path.read_text(encoding="utf-8")

    system_prompt_score = score_system_prompt(content)
    domain_knowledge_score = score_domain_knowledge(content)
    workflow_score = score_workflow(content)
    error_handling_score = score_error_handling(content)
    examples_score = score_examples(content)
    metadata_score = score_metadata(content)

    total_score = (
        system_prompt_score
        + domain_knowledge_score
        + workflow_score
        + error_handling_score
        + examples_score
        + metadata_score
    )

    return TextScoreResult(
        system_prompt_score=system_prompt_score,
        domain_knowledge_score=domain_knowledge_score,
        workflow_score=workflow_score,
        error_handling_score=error_handling_score,
        examples_score=examples_score,
        metadata_score=metadata_score,
        total_score=total_score,
    )
