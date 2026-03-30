"""Trigger-based intent detection module."""

from __future__ import annotations

import re


TRIGGER_VERSION = "1.0"


def detect_language(input_text: str) -> str:
    """Detect language of input text.

    Returns: ZH for Chinese-only, EN for English-only, MIXED for both
    """
    has_zh = len(re.findall(r"[一-龥]", input_text))
    has_en = len(re.findall(r"[a-zA-Z]", input_text))

    if has_zh > 0 and has_en == 0:
        return "ZH"
    elif has_en > 0 and has_zh == 0:
        return "EN"
    else:
        return "MIXED"


def score_primary_keywords(input_text: str, lang: str, mode: str) -> int:
    """Score primary keywords for intent detection.

    Args:
        input_text: User input
        lang: Detected language (EN/ZH/MIXED)
        mode: Intent mode (CREATE/EVALUATE/RESTORE/SECURITY/OPTIMIZE)

    Returns:
        Score based on keyword matches
    """
    input_lower = input_text.lower()
    score = 0

    if mode == "CREATE":
        if lang in ("EN", "MIXED"):
            if re.search(r"create.*skill|build.*skill|make.*skill", input_lower):
                score += 3
            elif re.search(r"new.*skill|develop.*skill|add.*skill", input_lower):
                score += 2
            elif re.search(r"generate.*skill|scaffold.*skill", input_lower):
                score += 1
        if lang in ("ZH", "MIXED"):
            if re.search(r"创建|新建", input_lower):
                score += 3
            elif re.search(r"开发|制作|生成", input_lower):
                score += 2
            elif re.search(r"脚手架", input_lower):
                score += 1

    elif mode == "EVALUATE":
        if lang in ("EN", "MIXED"):
            if re.search(r"evaluate.*skill|test.*skill|score.*skill", input_lower):
                score += 3
            elif re.search(r"review.*skill|assess.*skill|check.*skill", input_lower):
                score += 2
            elif re.search(r"validate.*skill|benchmark.*skill", input_lower):
                score += 1
        if lang in ("ZH", "MIXED"):
            if re.search(r"评估|测试|打分", input_lower):
                score += 3
            elif re.search(r"审查|验证|检查", input_lower):
                score += 2
            elif re.search(r"评分|基准", input_lower):
                score += 1

    elif mode == "RESTORE":
        if lang in ("EN", "MIXED"):
            if re.search(r"restore.*skill|fix.*skill|repair.*skill", input_lower):
                score += 3
            elif re.search(r"recover.*skill|undo|rollback.*skill", input_lower):
                score += 2
            elif re.search(r"broken.*skill|corrupt.*skill", input_lower):
                score += 1
        if lang in ("ZH", "MIXED"):
            if re.search(r"恢复|修复|还原", input_lower):
                score += 3
            elif re.search(r"补救|撤销|回滚", input_lower):
                score += 2
            elif re.search(r"损坏|失效|破坏", input_lower):
                score += 1

    elif mode == "SECURITY":
        if lang in ("EN", "MIXED"):
            if re.search(r"security audit|owasp|vulnerability", input_lower):
                score += 3
            elif re.search(r"cwe|security check|penetration test", input_lower):
                score += 2
            elif re.search(r"security scan|exploit check", input_lower):
                score += 1
        if lang in ("ZH", "MIXED"):
            if re.search(r"安全审计|漏洞扫描|owasp", input_lower):
                score += 3
            elif re.search(r"安全检查|渗透测试", input_lower):
                score += 2
            elif re.search(r"入侵|攻击", input_lower):
                score += 1

    elif mode == "OPTIMIZE":
        if lang in ("EN", "MIXED"):
            if re.search(r"optimize.*skill|improve.*skill|evolve.*skill", input_lower):
                score += 3
            elif re.search(r"enhance.*skill|tune.*skill|refine.*skill", input_lower):
                score += 2
            elif re.search(r"upgrade.*skill|performance", input_lower):
                score += 1
        if lang in ("ZH", "MIXED"):
            if re.search(r"优化|改进|进化", input_lower):
                score += 3
            elif re.search(r"提升|调优|完善", input_lower):
                score += 2
            elif re.search(r"增强|性能", input_lower):
                score += 1

    return score


def score_secondary_keywords(input_text: str, lang: str, mode: str) -> int:
    """Score secondary/context keywords for intent detection."""
    input_lower = input_text.lower()
    score = 0

    if mode == "CREATE":
        if re.search(r'"generate"|"template"|"starter"|"boilerplate"', input_lower):
            score += 1
        if re.search(r"模板|起始框架|脚手架", input_lower):
            score += 1
    elif mode == "EVALUATE":
        if re.search(r'"compare"|"grade"|"rate"|"measure"', input_lower):
            score += 1
        if re.search(r"比较|评级|打分", input_lower):
            score += 1
    elif mode == "RESTORE":
        if re.search(r'"broken"|"corrupt"|"invalid"|"damage"', input_lower):
            score += 1
        if re.search(r"损坏|破坏|崩溃", input_lower):
            score += 1
    elif mode == "SECURITY":
        if re.search(r'"injection"|"xss"|"csrf"|"breach"', input_lower):
            score += 1
        if re.search(r"注入|跨站|攻击", input_lower):
            score += 1
    elif mode == "OPTIMIZE":
        if re.search(r'"speed"|"efficiency"|"refactor"|"dry"', input_lower):
            score += 1
        if re.search(r"速度|效率|重构", input_lower):
            score += 1

    return score


def check_negative_patterns(input_text: str, lang: str, mode: str) -> int:
    """Check for negative patterns that should filter out a mode.

    Returns:
        1 if negative pattern found, 0 otherwise
    """
    input_lower = input_text.lower()
    is_negative = 0

    if mode == "CREATE":
        if re.search(r"don\'t create|skill exists|check if exists", input_lower):
            is_negative = 1
        if re.search(r"不要创建|技能已存在", input_lower):
            is_negative = 1
    elif mode == "EVALUATE":
        if re.search(r"evaluate code|test function|lint", input_lower):
            is_negative = 1
        if re.search(r"评估代码|测试函数", input_lower):
            is_negative = 1
    elif mode == "RESTORE":
        if re.search(r"restore file|recover data", input_lower):
            is_negative = 1
        if re.search(r"恢复文件|恢复数据", input_lower):
            is_negative = 1
    elif mode == "SECURITY":
        if re.search(r"secure password|encrypt data", input_lower):
            is_negative = 1
        if re.search(r"加密密码|保护数据", input_lower):
            is_negative = 1
    elif mode == "OPTIMIZE":
        if re.search(r"optimize algorithm|speed up", input_lower):
            is_negative = 1
        if re.search(r"优化算法|加速", input_lower):
            is_negative = 1

    return is_negative


def calculate_confidence(
    primary: float, secondary: float, context: float, no_negative: float
) -> float:
    """Calculate confidence score based on components.

    Formula: primary * 0.5 + secondary * 0.2 + context * 0.2 + no_negative * 0.1
    """
    return primary * 0.5 + secondary * 0.2 + context * 0.2 + no_negative * 0.1


def detect_intent(input_text: str) -> str:
    """Detect intent mode from user input.

    Returns:
        String in format "MODE:confidence" or "ASK:MODE:confidence"
    """
    if not input_text:
        return "EVALUATE:0.30"

    lang = detect_language(input_text)

    modes = ["CREATE", "EVALUATE", "RESTORE", "SECURITY", "OPTIMIZE"]
    best_mode = "EVALUATE"
    best_score = 0.0
    best_confidence = 0.30

    for mode in modes:
        primary = score_primary_keywords(input_text, lang, mode)
        secondary = score_secondary_keywords(input_text, lang, mode)
        context = score_secondary_keywords(input_text, lang, mode)
        negative = check_negative_patterns(input_text, lang, mode)

        if negative == 1:
            confidence = 0.00
        else:
            no_negative_weight = 1.0
            confidence = calculate_confidence(primary, secondary, context, no_negative_weight)

        current_score = confidence * 10 + primary
        if current_score > best_score:
            best_mode = mode
            best_score = current_score
            best_confidence = confidence

    if best_confidence >= 0.80:
        return f"{best_mode}:{best_confidence}"

    if best_confidence >= 0.60:
        return f"{best_mode}:{best_confidence}"

    if best_confidence < 0.60:
        if best_confidence <= 0.30:
            return "EVALUATE:0.30"
        return f"ASK:{best_mode}:{best_confidence}"

    return "EVALUATE:0.30"


def get_detected_mode(result: str) -> str:
    """Extract mode from detect_intent result."""
    return result.split(":")[0]


def get_confidence(result: str) -> str:
    """Extract confidence from detect_intent result."""
    return result.split(":")[-1]


def is_ambiguous(result: str) -> bool:
    """Check if result indicates ambiguous intent."""
    return result.startswith("ASK:")
