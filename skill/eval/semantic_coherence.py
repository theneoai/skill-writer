"""Semantic Coherence module - embedding-based semantic cohesion scoring."""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class SemanticCoherenceResult:
    """Result of semantic coherence evaluation."""

    semantic_score: int
    cohesion_score: float
    sections_analyzed: int
    drift_status: str
    raw_cohesion: float


def extract_section(content: str, section_pattern: str) -> str:
    """Extract text of a section matching the given pattern.

    Args:
        content: The full skill content.
        section_pattern: Regex pattern to match section header.

    Returns:
        Extracted section text (up to 50 lines).
    """
    lines = content.split("\n")
    in_section = False
    result_lines = []
    line_count = 0

    for line in lines:
        header_match = re.match(r"^#{1,4}\s+(.*)", line)
        if header_match:
            if in_section:
                in_section = False
            header_text = header_match.group(1)
            if re.search(section_pattern, header_text):
                in_section = True
                continue
        if in_section:
            result_lines.append(line)
            line_count += 1
            if line_count >= 50:
                break

    return "\n".join(result_lines).strip()


def extract_all_sections(content: str) -> dict[str, str]:
    """Extract all major sections from skill content.

    Args:
        content: The full skill content.

    Returns:
        Dictionary with keys: identity, framework, workflow, examples.
    """
    sections = {}
    sections["identity"] = extract_section(content, r"§1\.1|1\.1 Identity|1\.1\s")
    sections["framework"] = extract_section(content, r"§1\.2|1\.2 Framework|1\.2\s")
    sections["workflow"] = extract_section(content, r"§3\.|3\.[0-9] |[Ww]orkflow")
    sections["examples"] = extract_section(content, r"§4\.|4\.[0-9] |[Ee]xample")
    return sections


def jaccard_similarity(text_a: str, text_b: str) -> float:
    """Compute Jaccard similarity between two texts based on word overlap.

    Args:
        text_a: First text.
        text_b: Second text.

    Returns:
        Jaccard similarity score (0.0 to 1.0).
    """
    if not text_a.strip() or not text_b.strip():
        return 0.5

    words_a = re.findall(r"[a-z]{5,}", text_a.lower())
    words_b = re.findall(r"[a-z]{5,}", text_b.lower())

    set_a = set(words_a)
    set_b = set(words_b)

    if not set_a and not set_b:
        return 0.5
    if not set_a or not set_b:
        return 0.0

    intersection = len(set_a & set_b)
    union = len(set_a | set_b)

    if union == 0:
        return 0.5

    return intersection / union


def cosine_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    """Compute cosine similarity between two vectors.

    Args:
        vec_a: First vector.
        vec_b: Second vector.

    Returns:
        Cosine similarity score.
    """
    if not vec_a or not vec_b:
        return 0.5

    dot = sum(a * b for a, b in zip(vec_a, vec_b))
    norm_a = sum(a * a for a in vec_a) ** 0.5
    norm_b = sum(b * b for b in vec_b) ** 0.5

    if norm_a == 0 or norm_b == 0:
        return 0.5

    return dot / (norm_a * norm_b)


def mean_pairwise_similarity(texts: list[str], use_embeddings: bool = False) -> float:
    """Compute mean pairwise similarity across all text pairs.

    Uses Jaccard similarity as fallback since embedding API is not available.

    Args:
        texts: List of text strings to compare.
        use_embeddings: Whether to use embedding API (not implemented).

    Returns:
        Mean pairwise similarity score (0.0 to 1.0).
    """
    n = len(texts)
    if n < 2:
        return 1.0

    if n == 0:
        return 1.0

    total_sim = 0.0
    pair_count = 0

    for i in range(n):
        for j in range(i + 1, n):
            sim = jaccard_similarity(texts[i], texts[j])
            total_sim += sim
            pair_count += 1

    if pair_count == 0:
        return 1.0

    return round(total_sim / pair_count, 4)


def detect_identity_drift(identity_text: str, examples_text: str) -> str:
    """Detect if identity and examples sections describe different domains.

    Args:
        identity_text: The identity section text.
        examples_text: The examples section text.

    Returns:
        "DRIFT_DETECTED(sim=X)" or "COHERENT(sim=X)" where X is similarity.
    """
    if not identity_text.strip() or not examples_text.strip():
        return "UNKNOWN"

    sim = jaccard_similarity(identity_text, examples_text)

    if sim < 0.2:
        return f"DRIFT_DETECTED(sim={sim:.4f})"
    else:
        return f"COHERENT(sim={sim:.4f})"


def semantic_coherence_score(skill_file_or_content: str) -> SemanticCoherenceResult:
    """Calculate semantic coherence score for a skill.

    Args:
        skill_file_or_content: Path to skill file or skill content string.

    Returns:
        SemanticCoherenceResult with score and details.
    """
    import os

    if os.path.isfile(skill_file_or_content):
        try:
            with open(skill_file_or_content) as f:
                content = f.read()
        except (OSError, IOError):
            return SemanticCoherenceResult(
                semantic_score=0,
                cohesion_score=0.0,
                sections_analyzed=0,
                drift_status="ERROR",
                raw_cohesion=0.0,
            )
    else:
        content = skill_file_or_content

    sections = extract_all_sections(content)

    texts = []
    sections_found = 0

    if sections["identity"].strip():
        texts.append(sections["identity"])
        sections_found += 1
    if sections["framework"].strip():
        texts.append(sections["framework"])
        sections_found += 1
    if sections["workflow"].strip():
        texts.append(sections["workflow"])
        sections_found += 1
    if sections["examples"].strip():
        texts.append(sections["examples"])
        sections_found += 1

    if sections_found < 2:
        return SemanticCoherenceResult(
            semantic_score=0,
            cohesion_score=0.0,
            sections_analyzed=sections_found,
            drift_status="N/A",
            raw_cohesion=0.0,
        )

    cohesion = mean_pairwise_similarity(texts)

    drift_status = "N/A"
    if sections["identity"].strip() and sections["examples"].strip():
        drift_status = detect_identity_drift(sections["identity"], sections["examples"])

    if cohesion >= 0.85:
        score = 50
    elif cohesion >= 0.70:
        score = 35
    elif cohesion >= 0.55:
        score = 20
    else:
        score = 0

    return SemanticCoherenceResult(
        semantic_score=score,
        cohesion_score=cohesion,
        sections_analyzed=sections_found,
        drift_status=drift_status,
        raw_cohesion=cohesion,
    )
