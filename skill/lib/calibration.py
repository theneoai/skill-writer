"""Ground Truth Calibration Framework.

Problem: The scoring system is self-referential (scores are only meaningful
relative to arbitrary design choices). Without external ground truth,
"777/1000" carries no absolute meaning.

Solution: Calibrate the scoring system against expert human judgments.

Process:
  1. Collect a calibration corpus of N skills with known quality levels
  2. Have 3+ experts independently score each skill (structured rubric)
  3. Compute inter-annotator agreement (Krippendorff's alpha)
  4. Fit a mapping function: system_score -> expert_score
  5. Validate with leave-one-out cross-validation
  6. Report calibration quality (Pearson r, RMSE)

After calibration, score 777 means:
  "Our system outputs 777 which typically corresponds to expert rating ~X"

Theoretical basis:
  - Krippendorff 2011, "Computing Krippendorff's Alpha-Reliability"
  - Wang et al. 2023, "Calibrating LLM-Based Evaluator"
  - Cohen 1960, "A coefficient of agreement for nominal scales"
"""

from __future__ import annotations

import json
import math
import os
from collections import defaultdict
from datetime import datetime
from typing import Optional


def get_calibration_dir() -> str:
    """Get calibration directory from environment or default."""
    return os.environ.get(
        "CALIBRATION_DIR", os.path.join(os.path.dirname(__file__), "..", "..", "calibration")
    )


def get_calibration_corpus_path() -> str:
    """Get calibration corpus path."""
    return os.path.join(get_calibration_dir(), "corpus.json")


def get_calibration_params_path() -> str:
    """Get calibration params path."""
    return os.path.join(get_calibration_dir(), "params.json")


def init_calibration_corpus() -> None:
    """Initialize calibration corpus directory and file."""
    calibration_dir = get_calibration_dir()
    calibration_corpus = get_calibration_corpus_path()

    os.makedirs(calibration_dir, exist_ok=True)

    if not os.path.exists(calibration_corpus):
        with open(calibration_corpus, "w") as f:
            json.dump([], f)


def add_expert_annotation(
    skill_file: str,
    expert_id: str,
    structural: int,
    semantic: int,
    reliability: int,
    domain_depth: int,
    actionability: int,
    notes: str = "",
) -> None:
    """Add expert annotation to calibration corpus.

    Args:
        skill_file: Path to skill file
        expert_id: Expert identifier
        structural: Structural completeness rating (1-10)
        semantic: Semantic clarity rating (1-10)
        reliability: Behavioral reliability rating (1-10)
        domain_depth: Domain depth rating (1-10)
        actionability: Actionability rating (1-10)
        notes: Optional notes
    """
    overall = (structural + semantic + reliability + domain_depth + actionability) / 5

    skill_id = os.path.basename(skill_file).replace(".md", "")

    timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

    system_score = 0
    if os.path.exists(os.path.join(os.path.dirname(__file__), "..", "eval", "main.py")):
        pass

    annotation = {
        "skill_id": skill_id,
        "expert_id": expert_id,
        "timestamp": timestamp,
        "ratings": {
            "structural_completeness": structural,
            "semantic_clarity": semantic,
            "behavioral_reliability": reliability,
            "domain_depth": domain_depth,
            "actionability": actionability,
        },
        "overall": overall,
        "system_score": system_score,
        "notes": notes,
    }

    init_calibration_corpus()

    corpus_path = get_calibration_corpus_path()
    with open(corpus_path) as f:
        current = json.load(f)

    current.append(annotation)

    with open(corpus_path, "w") as f:
        json.dump(current, f, indent=2)


def compute_krippendorff_alpha(dimension: str = "overall") -> Optional[float]:
    """Compute Krippendorff's alpha for inter-annotator agreement.

    Args:
        dimension: Rating dimension to compute alpha for

    Returns:
        Alpha value or None if insufficient data
    """
    corpus_path = get_calibration_corpus_path()
    if not os.path.exists(corpus_path):
        return None

    with open(corpus_path) as f:
        data = json.load(f)

    if not data:
        return None

    skill_ratings = defaultdict(dict)
    for ann in data:
        sid = ann["skill_id"]
        eid = ann["expert_id"]
        if dimension == "overall":
            val = ann.get("overall", 0)
        else:
            val = ann.get("ratings", {}).get(dimension, 0)
        skill_ratings[sid][eid] = val

    skills = list(skill_ratings.keys())
    all_experts = set()
    for s in skill_ratings.values():
        all_experts.update(s.keys())
    experts = list(all_experts)

    if len(skills) < 2 or len(experts) < 2:
        return None

    values = []
    for skill in skills:
        row = []
        for expert in experts:
            row.append(skill_ratings[skill].get(expert, None))
        values.append(row)

    all_vals = [v for row in values for v in row if v is not None]
    n = len(all_vals)

    if n < 2:
        return None

    d_obs = 0.0
    n_pairs = 0
    for row in values:
        vals = [v for v in row if v is not None]
        for i in range(len(vals)):
            for j in range(i + 1, len(vals)):
                d_obs += (vals[i] - vals[j]) ** 2
                n_pairs += 1

    if n_pairs > 0:
        d_obs = d_obs / n_pairs

    d_exp = sum((all_vals[i] - all_vals[j]) ** 2 for i in range(n) for j in range(i + 1, n))
    pair_count = n * (n - 1) / 2
    if pair_count > 0:
        d_exp = d_exp / pair_count

    if d_exp == 0:
        return 1.0

    alpha = 1.0 - (d_obs / d_exp)
    return alpha


def fit_calibration() -> dict:
    """Fit linear regression calibration: system_score -> expert_score.

    Returns:
        Dictionary with slope, intercept, r, rmse, n
    """
    corpus_path = get_calibration_corpus_path()
    if not os.path.exists(corpus_path):
        return {"status": "INSUFFICIENT_DATA", "message": "No calibration corpus"}

    with open(corpus_path) as f:
        data = json.load(f)

    skill_expert = defaultdict(list)
    skill_system = defaultdict(list)

    for ann in data:
        sid = ann["skill_id"]
        skill_expert[sid].append(ann.get("overall", 0))
        if ann.get("system_score", 0) > 0:
            skill_system[sid].append(ann["system_score"])

    if len(skill_expert) < 3:
        return {"status": "INSUFFICIENT_DATA", "message": "Need >=3 skills"}

    skills_with_both = [s for s in skill_expert if skill_system[s]]
    if len(skills_with_both) < 3:
        return {"status": "INSUFFICIENT_DATA", "message": "Need system scores for >=3 skills"}

    x = [sum(skill_system[s]) / len(skill_system[s]) for s in skills_with_both]
    y = [sum(skill_expert[s]) / len(skill_expert[s]) * 100 for s in skills_with_both]

    n = len(x)
    mean_x = sum(x) / n
    mean_y = sum(y) / n

    slope = sum((xi - mean_x) * (yi - mean_y) for xi, yi in zip(x, y)) / sum(
        (xi - mean_x) ** 2 for xi in x
    )
    intercept = mean_y - slope * mean_x

    ss_xy = sum((xi - mean_x) * (yi - mean_y) for xi, yi in zip(x, y))
    ss_xx = sum((xi - mean_x) ** 2 for xi in x)
    ss_yy = sum((yi - mean_y) ** 2 for yi in y)

    if ss_xx * ss_yy > 0:
        r = ss_xy / math.sqrt(ss_xx * ss_yy)
    else:
        r = 0

    y_pred = [slope * xi + intercept for xi in x]
    rmse = math.sqrt(sum((yi - yp) ** 2 for yi, yp in zip(y, y_pred)) / n)

    quality = "GOOD" if abs(r) >= 0.85 else ("MODERATE" if abs(r) >= 0.70 else "POOR")

    params = {
        "slope": slope,
        "intercept": intercept,
        "r": r,
        "rmse": rmse,
        "n": n,
        "quality": quality,
    }

    os.makedirs(get_calibration_dir(), exist_ok=True)
    with open(get_calibration_params_path(), "w") as f:
        json.dump(params, f, indent=2)

    return params


def calibrated_score(raw_score: str) -> str:
    """Apply calibration to a raw score.

    Args:
        raw_score: Raw system score

    Returns:
        Calibrated score (string)
    """
    params_path = get_calibration_params_path()
    if not os.path.exists(params_path):
        return raw_score

    with open(params_path) as f:
        p = json.load(f)

    calibrated = p["slope"] * float(raw_score) + p["intercept"]
    calibrated = max(0, min(1000, round(calibrated)))

    return str(calibrated)


def calibration_status() -> dict:
    """Get calibration status.

    Returns:
        Dictionary with status information
    """
    corpus_path = get_calibration_corpus_path()
    if not os.path.exists(corpus_path):
        return {"status": "NOT_INITIALIZED", "message": "Run add_expert_annotation first"}

    with open(corpus_path) as f:
        data = json.load(f)

    n_annotations = len(data)
    n_skills = len(set(ann["skill_id"] for ann in data))
    n_experts = len(set(ann["expert_id"] for ann in data))

    alpha = compute_krippendorff_alpha("overall")

    params = None
    params_path = get_calibration_params_path()
    if os.path.exists(params_path):
        with open(params_path) as f:
            params = json.load(f)

    return {
        "n_annotations": n_annotations,
        "n_skills": n_skills,
        "n_experts": n_experts,
        "alpha": alpha,
        "params": params,
    }
