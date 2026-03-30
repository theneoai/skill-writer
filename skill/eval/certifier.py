"""Certification module - determines certification tier and score."""

from __future__ import annotations

import os
import re
from dataclasses import dataclass


PLATINUM_MIN = 950
GOLD_MIN = 900
SILVER_MIN = 800
BRONZE_MIN = 700

VARIANCE_MAX = 20

CWE_798_PATTERN = r"(sk-[a-zA-Z0-9]{20,}|AKIA[0-9A-Z]{16}|-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----|ghp_[a-zA-Z0-9]{36}|xox[baprs]-[0-9A-Za-z\-]{10,}|(api[-_]key|password|passwd|secret|credential)\s*=\s*[\"'\x27][^\"'${\x27]{6,}[\"'\x27])"
CWE_89_PATTERN = r"(mysql|psql|sqlite3|mongosh|sqlcmd)\s+.*\$\{|sql\s*=.*\$\{|[\"'\x27].*\$\w+|WHERE\s+\$\w+|SELECT\s+\$\w+|INSERT\s+INTO\s+\$\w+|UPDATE\s+\$\w+\s+SET|DELETE\s+FROM\s+\$\w+|--\s*\$\{|\"\s*\.\s*\$\{|\x27\s*\.\s*\$\{"
CWE_78_PATTERN = r"(eval\s*\$\{|\$\(\s*\$.*|exec\s+\$\{|system\s+\$\{|popen\s*\$\{|`[^`]*\$\{[^`]*`|\beval\s+\$\(|\bexec\s+\$\(|\bsystem\s+\$\(|\bsh\s+-c.*\$\{|\bbash\s+-c.*\$\{)"
CWE_22_PATTERN = r"(\.\.\/|\.\.\\|%00|/etc/passwd|/etc/shadow|\.\.\.\/|\.\.\\\.\\.)"
CWE_306_PATTERN = r"(if\s+\[\s*-z\s+\$\w+\s*\]\s*;?\s*then\s*return|if\s+\[\s*-z\s+\$\w+\s*\]\s*;?\s*then\s*exit|auth[_-]?check|is[_-]?auth[_-]?enticated|check[_-]?auth|verify[_-]?creds?|validate[_-]?token?|require[_-]?auth)"
CWE_862_PATTERN = r"(is[_-]?authorized|check[_-]?perm[_-]?s?|has[_-]?perm[_-]?s?|validate[_-]?role?|has[_-]?role?|require[_-]?role|check[_-]?ownership|is[_-]?owner)"


@dataclass
class CertificationResult:
    """Result of certification evaluation."""

    certify_total: int
    tier: str
    certified: str
    variance_points: int
    tier_points: int
    quality_gate_points: int
    security_points: int
    security_violations: int
    p0_violation: bool
    phase1_included: int
    total: float


def determine_tier(total: float, text_score: float, runtime_score: float, variance: float) -> str:
    """Determine certification tier based on scores.

    Args:
        total: Combined score total.
        text_score: Text quality score.
        runtime_score: Runtime evaluation score.
        variance: Score variance.

    Returns:
        Tier name: PLATINUM, GOLD, SILVER, BRONZE, or NOT_CERTIFIED.
    """
    lt_10 = variance < 10
    lt_15 = variance < 15
    lt_20 = variance < 20
    lt_30 = variance < 30

    if total >= PLATINUM_MIN and text_score >= 330 and runtime_score >= 430 and lt_10:
        return "PLATINUM"
    elif total >= GOLD_MIN and text_score >= 315 and runtime_score >= 405 and lt_15:
        return "GOLD"
    elif total >= SILVER_MIN and text_score >= 280 and runtime_score >= 360 and lt_20:
        return "SILVER"
    elif total >= BRONZE_MIN and text_score >= 245 and runtime_score >= 315 and lt_30:
        return "BRONZE"
    else:
        return "NOT_CERTIFIED"


def get_tier_points(tier: str) -> int:
    """Get points awarded for a tier.

    Args:
        tier: Tier name.

    Returns:
        Points value.
    """
    return {"PLATINUM": 30, "GOLD": 25, "SILVER": 20, "BRONZE": 15}.get(tier, 0)


def get_tier_badge(tier: str) -> str:
    """Get badge string for a tier.

    Args:
        tier: Tier name.

    Returns:
        Badge string with emoji.
    """
    badges = {
        "PLATINUM": "PLATINUM",
        "GOLD": "GOLD",
        "SILVER": "SILVER",
        "BRONZE": "BRONZE",
        "NOT_CERTIFIED": "NOT CERTIFIED",
    }
    return badges.get(tier, "UNKNOWN")


def _check_security_violations(skill_file: str) -> tuple[int, bool]:
    """Check for security pattern violations.

    Args:
        skill_file: Path to skill file.

    Returns:
        Tuple of (violation_count, p0_violation).
    """
    try:
        with open(skill_file) as f:
            content = f.read()
    except (OSError, IOError):
        return 0, False

    violations = 0
    p0_violation = False

    patterns = [
        (CWE_798_PATTERN, False),
        (CWE_89_PATTERN, True),
        (CWE_78_PATTERN, True),
        (CWE_22_PATTERN, False),
        (CWE_306_PATTERN, False),
        (CWE_862_PATTERN, False),
    ]

    for pattern, is_p0 in patterns:
        if re.search(pattern, content, re.IGNORECASE):
            violations += 1
            if is_p0:
                p0_violation = True

    return violations, p0_violation


def certify(
    skill_file: str,
    text_score: float,
    runtime_score: float,
    variance: float,
    f1_score: float,
    mrr_score: float,
    trigger_acc: float,
    phase1_score: float = 0,
) -> CertificationResult:
    """Calculate certification score and determine certification status.

    Args:
        skill_file: Path to skill file.
        text_score: Text quality score.
        runtime_score: Runtime evaluation score.
        variance: Score variance.
        f1_score: F1 score.
        mrr_score: MRR score.
        trigger_acc: Trigger accuracy.
        phase1_score: Phase 1 score (optional).

    Returns:
        CertificationResult with all details.
    """
    if not skill_file or not os.path.isfile(skill_file):
        return CertificationResult(
            certify_total=0,
            tier="NOT_CERTIFIED",
            certified="NO",
            variance_points=0,
            tier_points=0,
            quality_gate_points=0,
            security_points=0,
            security_violations=0,
            p0_violation=False,
            phase1_included=0,
            total=0,
        )

    total = phase1_score + text_score + runtime_score

    tier = determine_tier(total, text_score, runtime_score, variance)

    v_lt_10 = variance < 10
    v_lt_15 = variance < 15
    v_lt_20 = variance < 20
    v_lt_30 = variance < 30

    if v_lt_10:
        variance_points = 40
    elif v_lt_15:
        variance_points = 30
    elif v_lt_20:
        variance_points = 20
    elif v_lt_30:
        variance_points = 10
    else:
        variance_points = 0

    tier_points = get_tier_points(tier)

    f1_points = 0
    if f1_score and f1_score != 0:
        if f1_score >= 0.92:
            f1_points = 10
        elif f1_score >= 0.90:
            f1_points = 7
        elif f1_score >= 0.87:
            f1_points = 5

    mrr_points = 0
    if mrr_score and mrr_score != 0:
        if mrr_score >= 0.88:
            mrr_points = 10
        elif mrr_score >= 0.85:
            mrr_points = 7
        elif mrr_score >= 0.82:
            mrr_points = 5

    quality_gate_points = f1_points + mrr_points

    security_violations, p0_violation = _check_security_violations(skill_file)

    if p0_violation:
        security_points = 0
    elif security_violations > 0:
        security_points = max(0, 10 - security_violations * 3)
    else:
        security_points = 10

    certify_total = variance_points + tier_points + quality_gate_points + security_points

    certified = (
        "YES" if (certify_total >= 50 and not p0_violation and tier != "NOT_CERTIFIED") else "NO"
    )

    return CertificationResult(
        certify_total=certify_total,
        tier=tier,
        certified=certified,
        variance_points=variance_points,
        tier_points=tier_points,
        quality_gate_points=quality_gate_points,
        security_points=security_points,
        security_violations=security_violations,
        p0_violation=p0_violation,
        phase1_included=int(phase1_score),
        total=total,
    )


def certify_from_json(json_results: dict) -> CertificationResult:
    """Calculate certification from JSON results dict.

    Args:
        json_results: Dict with skill_file, text_score, runtime_score, etc.

    Returns:
        CertificationResult.
    """
    skill_file = json_results.get("skill_file", "unknown")
    text_score = float(json_results.get("text_score", 0))
    runtime_score = float(json_results.get("runtime_score", 0))
    variance = float(json_results.get("variance", 0))
    f1_score = float(json_results.get("f1_score", 0))
    mrr_score = float(json_results.get("mrr_score", 0))
    trigger_acc = float(json_results.get("trigger_accuracy", 0))
    phase1_score = float(json_results.get("phase1_score", 0))

    return certify(
        skill_file,
        text_score,
        runtime_score,
        variance,
        f1_score,
        mrr_score,
        trigger_acc,
        phase1_score,
    )
