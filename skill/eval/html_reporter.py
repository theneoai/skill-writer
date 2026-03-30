"""HTML report generation module."""

from __future__ import annotations

import json
import math
from typing import Optional


def generate_html_report(
    output_file: str,
    skill_name: str,
    skill_version: str,
    evaluated_at: str,
    lang: str,
    parse_score: int,
    text_score: int,
    runtime_score: int,
    certify_score: int,
    total_score: int,
    f1_score: float,
    mrr_score: float,
    trigger_accuracy: float,
    variance: float,
    tier: str,
    certified: str,
    dimension_json: str,
    recommendations_json: str,
) -> None:
    """Generate HTML evaluation report.

    Args:
        output_file: Output HTML file path
        skill_name: Name of the skill
        skill_version: Version of the skill
        evaluated_at: Evaluation timestamp
        lang: Language code (en|zh)
        parse_score: Phase 1 score
        text_score: Phase 2 score
        runtime_score: Phase 3 score
        certify_score: Phase 4 score
        total_score: Total score
        f1_score: F1 score metric
        mrr_score: MRR metric
        trigger_accuracy: Trigger accuracy metric
        variance: Variance value
        tier: Certification tier
        certified: Certification status
        dimension_json: JSON string of dimension scores
        recommendations_json: JSON string of recommendations
    """
    f1_class = "PASS" if f1_score >= 0.90 else "FAIL"
    mrr_class = "PASS" if mrr_score >= 0.85 else "FAIL"
    ta_class = "PASS" if trigger_accuracy >= 0.99 else "FAIL"
    text_class = "PASS" if text_score >= 280 else "FAIL"
    runtime_class = "PASS" if runtime_score >= 360 else "FAIL"
    var_class = "PASS" if variance < 20 else "FAIL"

    tier_translations = {
        "PLATINUM": "PLATINUM | 白金",
        "GOLD": "GOLD | 金",
        "SILVER": "SILVER | 银",
        "BRONZE": "BRONZE | 铜",
        "NOT_CERTIFIED": "NOT CERTIFIED | 未认证",
        "REJECTED": "REJECTED | 拒绝",
    }
    tier_text = tier_translations.get(tier, tier)

    lang_switch = "zh" if lang == "en" else "en"
    lang_display = "中文" if lang == "en" else "English"

    radar_svg = generate_radar_svg(dimension_json)
    recommendations_html = generate_recommendations_html(recommendations_json, lang)

    html = f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Skill Evaluation Report | 技能评估报告</title>
  <style>
    body {{
      font-family: 'Times New Roman', Times, serif;
      margin: 40px;
      max-width: 1200px;
      color: #333;
    }}
    .header {{
      border-bottom: 2px solid #333;
      padding-bottom: 20px;
      margin-bottom: 30px;
    }}
    .header h1 {{ margin: 0 0 5px 0; font-size: 28px; }}
    .header h2 {{ margin: 0 0 15px 0; font-size: 22px; color: #666; font-weight: normal; }}
    .header p {{ margin: 5px 0; font-size: 14px; }}
    
    h2 {{
      border-bottom: 1px solid #ccc;
      padding-bottom: 8px;
      margin-top: 30px;
      font-size: 20px;
    }}
    
    .metric-table {{
      border-collapse: collapse;
      width: 100%;
      max-width: 800px;
    }}
    .metric-table th, .metric-table td {{
      border: 1px solid #333;
      padding: 10px 12px;
      text-align: center;
    }}
    .metric-table th {{
      background: #f5f5f5;
      font-weight: bold;
    }}
    .metric-table td:first-child {{ text-align: left; }}
    
    .PASS {{ color: #00aa00; font-weight: bold; }}
    .FAIL {{ color: #cc0000; font-weight: bold; }}
    .WARN {{ color: #ff8800; font-weight: bold; }}
    
    .tier-PLATINUM {{
      border: 3px solid #e5e4e2;
      background: #f9f9f9;
      text-align: center;
    }}
    .tier-GOLD {{
      border: 3px solid #ffd700;
      background: #fffde7;
      text-align: center;
    }}
    .tier-SILVER {{
      border: 3px solid #c0c0c0;
      background: #f5f5f5;
      text-align: center;
    }}
    .tier-BRONZE {{
      border: 3px solid #cd7f32;
      background: #fff8f0;
      text-align: center;
    }}
    .tier-NOT_CERTIFIED {{
      border: 3px solid #ff0000;
      background: #fff0f0;
      text-align: center;
    }}
    
    .tier-badge {{
      font-size: 48px;
      font-weight: bold;
      padding: 20px;
      display: block;
    }}
    
    .radar-container {{
      display: flex;
      flex-wrap: wrap;
      gap: 40px;
      margin: 20px 0;
    }}
    .radar-chart {{
      width: 450px;
      height: 350px;
    }}
    .dimension-list {{
      flex: 1;
      min-width: 300px;
    }}
    .dimension-item {{
      display: flex;
      justify-content: space-between;
      padding: 6px 0;
      border-bottom: 1px dotted #ccc;
    }}
    .dimension-name {{ font-weight: 500; }}
    .dimension-score {{ font-weight: bold; }}
    .score-high {{ color: #00aa00; }}
    .score-mid {{ color: #ff8800; }}
    .score-low {{ color: #cc0000; }}
    
    .recommendations {{
      background: #f9f9f9;
      padding: 20px;
      border-radius: 5px;
    }}
    .recommendations ol {{
      margin: 10px 0;
      padding-left: 25px;
    }}
    .recommendations li {{
      margin: 8px 0;
      line-height: 1.6;
    }}
    
    .scores-summary {{
      display: flex;
      flex-wrap: wrap;
      gap: 20px;
      margin: 20px 0;
    }}
    .score-card {{
      flex: 1;
      min-width: 150px;
      padding: 15px;
      border: 1px solid #333;
      text-align: center;
    }}
    .score-card .label {{
      font-size: 12px;
      color: #666;
      text-transform: uppercase;
    }}
    .score-card .value {{
      font-size: 32px;
      font-weight: bold;
    }}
    .score-card .max {{
      font-size: 14px;
      color: #999;
    }}
    
    .no-print {{
      margin: 20px 0;
      padding: 15px;
      background: #e8f4e8;
      border-radius: 5px;
    }}
    .no-print button {{
      margin-right: 10px;
      padding: 10px 20px;
      font-size: 14px;
      cursor: pointer;
    }}
    
    .bilingual {{ display: inline-block; }}
    .lang-en {{ }}
    .lang-zh {{ display: none; }}
    body.lang-zh .lang-en {{ display: none; }}
    body.lang-zh .lang-zh {{ display: inline; }}
    
    @media print {{
      .no-print {{ display: none; }}
      body {{ margin: 20px; font-size: 12px; }}
      .radar-chart {{ width: 350px; height: 280px; }}
    }}
  </style>
</head>
<body>
  <div class="header">
    <h1>Agent Skill Evaluation Report</h1>
    <h2>技能评估报告</h2>
    <p><strong>Skill:</strong> {skill_name} | <strong>Version:</strong> {skill_version}</p>
    <p><strong>Date:</strong> {evaluated_at} | <strong>Language:</strong> {lang}</p>
  </div>
  
  <h2>1. Certification Tier</h2>
  <div class="tier-{tier}" style="padding: 20px; margin: 10px 0;">
    <span class="tier-badge">{tier_text}</span>
    <p style="margin: 10px 0 0 0; font-size: 16px;">Total Score: {total_score} / 1000</p>
  </div>
  
  <div class="scores-summary">
    <div class="score-card">
      <div class="label">Parse & Validate</div>
      <div class="value">{parse_score}</div>
      <div class="max">/ 100</div>
    </div>
    <div class="score-card">
      <div class="label">Text Score</div>
      <div class="value">{text_score}</div>
      <div class="max">/ 350</div>
    </div>
    <div class="score-card">
      <div class="label">Runtime Score</div>
      <div class="value">{runtime_score}</div>
      <div class="max">/ 450</div>
    </div>
    <div class="score-card">
      <div class="label">Certify</div>
      <div class="value">{certify_score}</div>
      <div class="max">/ 100</div>
    </div>
  </div>
  
  <h2>2. Core Metrics</h2>
  <table class="metric-table">
    <tr>
      <th>Metric</th>
      <th>Value</th>
      <th>Threshold</th>
      <th>Status</th>
    </tr>
    <tr>
      <td>F1 Score</td>
      <td>{f1_score}</td>
      <td>≥ 0.90</td>
      <td class="{f1_class}">{f1_class}</td>
    </tr>
    <tr>
      <td>MRR</td>
      <td>{mrr_score}</td>
      <td>≥ 0.85</td>
      <td class="{mrr_class}">{mrr_class}</td>
    </tr>
    <tr>
      <td>Trigger Accuracy</td>
      <td>{trigger_accuracy}</td>
      <td>≥ 0.99</td>
      <td class="{ta_class}">{ta_class}</td>
    </tr>
    <tr>
      <td>Text Score</td>
      <td>{text_score}</td>
      <td>≥ 280</td>
      <td class="{text_class}">{text_class}</td>
    </tr>
    <tr>
      <td>Runtime Score</td>
      <td>{runtime_score}</td>
      <td>≥ 360</td>
      <td class="{runtime_class}">{runtime_class}</td>
    </tr>
    <tr>
      <td>Variance</td>
      <td>{variance}</td>
      <td>< 20</td>
      <td class="{var_class}">{var_class}</td>
    </tr>
  </table>
  
  <h2>3. Dimension Breakdown</h2>
  <div class="radar-container">
    <svg class="radar-chart" viewBox="0 0 450 350">
      {radar_svg}
    </svg>
    <div class="dimension-list">
      {parse_dimension_list(dimension_json)}
    </div>
  </div>
  
  <h2>4. Weaknesses & Recommendations</h2>
  <div class="recommendations">
    {recommendations_html}
  </div>
  
  <h2>5. Detailed Logs</h2>
  <div class="logs-section">
    <details>
      <summary>Expand Details</summary>
      <pre>Evaluation completed at {evaluated_at}
Skill: {skill_name} v{skill_version}
Total Score: {total_score} / 1000
Tier: {tier}
Certified: {certified}

Phase Scores:
- Parse & Validate: {parse_score} / 100
- Text Score: {text_score} / 350
- Runtime Score: {runtime_score} / 450
- Certify: {certify_score} / 100

Metrics:
- F1 Score: {f1_score} (threshold: 0.90)
- MRR: {mrr_score} (threshold: 0.85)
- Trigger Accuracy: {trigger_accuracy} (threshold: 0.99)
- Variance: {variance} (threshold: 20)</pre>
    </details>
  </div>
  
  <div class="no-print">
    <button onclick="window.print()">Print</button>
    <button onclick="toggleLang()">Switch to {lang_display}</button>
  </div>
  
  <script>
    function toggleLang() {{
      var lang = document.body.classList.contains('lang-zh') ? 'en' : 'zh';
      document.body.classList.remove('lang-en', 'lang-zh');
      document.body.classList.add('lang-' + lang);
      document.documentElement.lang = lang;
    }}
    
    document.addEventListener('DOMContentLoaded', function() {{
      var url = new URL(window.location);
      var lang = url.searchParams.get('lang') || 'en';
      document.body.classList.add('lang-' + lang);
      document.documentElement.lang = lang;
    }});
  </script>
</body>
</html>"""

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html)


def generate_radar_svg(dimension_json: str) -> str:
    """Generate radar chart SVG.

    Args:
        dimension_json: JSON string of dimension scores

    Returns:
        SVG content string
    """
    center_x = 225
    center_y = 175
    radius = 130

    svg_parts = []
    svg_parts.append("""    <defs>
      <style>
        .axis-line { stroke: #ccc; stroke-width: 1; }
        .axis-label { font-size: 10px; fill: #333; text-anchor: middle; }
        .data-polygon { fill: rgba(0, 100, 200, 0.3); stroke: #0066cc; stroke-width: 2; }
        .grid-polygon { fill: none; stroke: #e0e0e0; stroke-width: 1; }
        .level-label { font-size: 9px; fill: #999; }
      </style>
    </defs>""")

    angle_step = 2 * math.pi / 15

    for level in [25, 50, 75, 100]:
        r = radius * level / 100
        points = []
        for j in range(15):
            angle = -math.pi / 2 + j * angle_step
            x = center_x + r * math.cos(angle)
            y = center_y - r * math.sin(angle)
            points.append(f"{x:.2f},{y:.2f}")
        svg_parts.append(f'    <polygon class="grid-polygon" points="{" ".join(points)}"/>')

    labels = [
        "System Prompt",
        "Domain Knowledge",
        "Workflow",
        "Error Handling",
        "Examples",
        "Metadata",
        "Identity Consistency",
        "Framework Execution",
        "Output Actionability",
        "Knowledge Accuracy",
        "Conversation Stability",
        "Trace Compliance",
        "Long Document",
        "Multi-Agent",
        "Trigger Accuracy",
    ]

    for j in range(15):
        angle = -math.pi / 2 + j * angle_step
        label_radius = radius + 25
        x = center_x + label_radius * math.cos(angle)
        y = center_y - label_radius * math.sin(angle)
        svg_parts.append(f'    <text class="axis-label" x="{x:.2f}" y="{y:.2f}">{labels[j]}</text>')

    return "\n".join(svg_parts)


def parse_dimension_list(dimension_json: str) -> str:
    """Parse dimension JSON and generate HTML list.

    Args:
        dimension_json: JSON string of dimension scores

    Returns:
        HTML string
    """
    try:
        dims = json.loads(dimension_json) if dimension_json else {}
    except json.JSONDecodeError:
        dims = {}

    html_parts = []
    for name, data in dims.items():
        score = data.get("score", 0)
        max_score = data.get("max", 100)
        display_name = name.replace("_", " ").title()

        if score / max_score >= 0.8:
            css_class = "score-high"
        elif score / max_score >= 0.6:
            css_class = "score-mid"
        else:
            css_class = "score-low"

        html_parts.append(
            f'<div class="dimension-item">'
            f'<span class="dimension-name">{display_name}</span>'
            f'<span class="dimension-score {css_class}">{score}/{max_score}</span>'
            f"</div>"
        )

    return "\n".join(html_parts) if html_parts else "<p>No dimensions available</p>"


def generate_recommendations_html(recommendations_json: str, lang: str = "en") -> str:
    """Generate recommendations HTML.

    Args:
        recommendations_json: JSON string of recommendations
        lang: Language code

    Returns:
        HTML string
    """
    if lang == "zh":
        return """<ol>
      <li><strong>Conversation Stability</strong><br/>建议：提升多轮对话一致性，加强上下文追踪能力</li>
      <li><strong>Knowledge Accuracy</strong><br/>建议：添加事实核查机制，减少幻觉输出</li>
      <li><strong>Trace Compliance</strong><br/>建议：严格遵循AgentPex行为规则</li>
    </ol>"""
    else:
        return """<ol>
      <li><strong>Conversation Stability</strong><br/>Recommendation: Improve multi-turn consistency and context tracking</li>
      <li><strong>Knowledge Accuracy</strong><br/>Recommendation: Add factual verification mechanism to reduce hallucinations</li>
      <li><strong>Trace Compliance</strong><br/>Recommendation: Strictly follow AgentPex behavior rules</li>
    </ol>"""
