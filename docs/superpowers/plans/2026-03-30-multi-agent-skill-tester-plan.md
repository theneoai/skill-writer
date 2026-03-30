# Multi-Agent Skill Tester Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 创建 `scripts/multi_agent_tester.py`，实现 1000 轮自动化测试循环，使用 Minimax 和 Kimi Code agents 创建和评测 skill

**Architecture:** 简单的顺序执行循环，每个 round 创建两个 skill 并评测，记录问题

**Tech Stack:** Python 3.10+, requests, subprocess (调用 skill CLI)

---

## File Structure

```
scripts/
└── multi_agent_tester.py      # 主测试脚本

eval_results/                   # 临时 skill 文件 (已在 gitignore)
└── round_XXXX/                # 每轮的输出
```

## Task 1: 创建 multi_agent_tester.py 基础结构

**Files:**
- Create: `scripts/multi_agent_tester.py`

- [ ] **Step 1: 编写基础类和导入**

```python
#!/usr/bin/env python3
"""Multi-Agent Skill Tester - 使用 Minimax 和 Kimi Code 循环测试 skill"""

import os
import json
import subprocess
import argparse
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional
import requests


@dataclass
class AgentConfig:
    api_key: str
    api_base: str = "https://api.minimax.chat/v1"
    model: str = "Minimax-Text-01"


@dataclass
class RoundResult:
    round_num: int
    minimax_skill: str
    minimax_eval: dict
    kimi_skill: str
    kimi_eval: dict
    issues: list = field(default_factory=list)


class SkillTester:
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.round_num = 0

    def run_skill_evaluate(self, skill_path: str) -> dict:
        """运行 skill evaluate 命令"""
        result = subprocess.run(
            ["skill", "evaluate", skill_path, "--output", "/tmp/eval_result.json"],
            capture_output=True,
            text=True
        )
        try:
            with open("/tmp/eval_result.json") as f:
                return json.load(f)
        except:
            return {"error": result.stderr or result.stdout}
```

- [ ] **Step 2: 添加 Minimax Agent 类**

```python
class MinimaxAgent:
    def __init__(self, config: AgentConfig):
        self.config = config

    def create_evaluation_skill(self, round_num: int) -> str:
        prompt = f"""创建一个 evaluation skill，用于评估其他 skill 的质量。
        
要求:
- name: minimax_evaluator
- description: 使用 Minimax 模型评估 skill 质量
- 包含 evaluation 逻辑
- tier: BRONZE

只返回完整的 SKILL.md 内容。"""
        
        response = requests.post(
            f"{self.config.api_base}/text/chatcompletion_v2",
            headers={
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": self.config.model,
                "messages": [{"role": "user", "content": prompt}]
            }
        )
        
        content = response.json()["choices"][0]["message"]["content"]
        return self._extract_skill_md(content)
    
    def _extract_skill_md(self, text: str) -> str:
        """从响应中提取 SKILL.md 内容"""
        if "```markdown" in text:
            start = text.find("```markdown") + 11
            end = text.find("```", start)
            return text[start:end].strip()
        return text.strip()
```

- [ ] **Step 3: 添加 Kimi Agent 类**

```python
class KimiAgent:
    def __init__(self, config: AgentConfig):
        self.config = config
        self.config.api_base = "https://api.moonshot.cn/v1"
        self.config.model = "moonshot-v1-8k"

    def create_optimization_skill(self, round_num: int) -> str:
        prompt = f"""创建一个 optimization skill，用于优化其他 skill 的质量。
        
要求:
- name: kimi_optimizer
- description: 使用 Kimi 模型优化 skill 质量
- 包含 optimization 逻辑
- tier: BRONZE

只返回完整的 SKILL.md 内容。"""
        
        response = requests.post(
            f"{self.config.api_base}/chat/completions",
            headers={
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": self.config.model,
                "messages": [{"role": "user", "content": prompt}]
            }
        )
        
        content = response.json()["choices"][0]["message"]["content"]
        return self._extract_skill_md(content)
    
    def _extract_skill_md(self, text: str) -> str:
        if "```markdown" in text:
            start = text.find("```markdown") + 11
            end = text.find("```", start)
            return text[start:end].strip()
        return text.strip()
```

- [ ] **Step 4: 添加 Round 执行逻辑**

```python
    def execute_round(self) -> RoundResult:
        self.round_num += 1
        round_dir = self.output_dir / f"round_{self.round_num:04d}"
        round_dir.mkdir(parents=True, exist_ok=True)
        
        # 1. Minimax 创建 evaluation skill
        minimax_skill_md = self.minimax_agent.create_evaluation_skill(self.round_num)
        minimax_skill_path = round_dir / "minimax_eval_skill.md"
        minimax_skill_path.write_text(minimax_skill_md)
        
        # 2. Kimi 创建 optimization skill
        kimi_skill_md = self.kimi_agent.create_optimization_skill(self.round_num)
        kimi_skill_path = round_dir / "kimi_opt_skill.md"
        kimi_skill_path.write_text(kimi_skill_md)
        
        # 3. 评测
        minimax_eval = self.run_skill_evaluate(str(minimax_skill_path))
        kimi_eval = self.run_skill_evaluate(str(kimi_skill_path))
        
        # 4. 检查问题
        issues = self._check_issues(minimax_eval, kimi_eval)
        
        # 5. 保存结果
        self._save_results(round_dir, minimax_eval, kimi_eval, issues)
        
        return RoundResult(
            round_num=self.round_num,
            minimax_skill=str(minimax_skill_path),
            minimax_eval=minimax_eval,
            kimi_skill=str(kimi_skill_path),
            kimi_eval=kimi_eval,
            issues=issues
        )
    
    def _check_issues(self, minimax_eval: dict, kimi_eval: dict) -> list:
        issues = []
        for name, eval_result in [("minimax", minimax_eval), ("kimi", kimi_eval)]:
            if "error" in eval_result:
                issues.append({
                    "severity": "HIGH",
                    "source": name,
                    "message": eval_result["error"]
                })
            score = eval_result.get("total_score", 0)
            if score < 700:
                issues.append({
                    "severity": "MEDIUM",
                    "source": name,
                    "message": f"Low score: {score}"
                })
        return issues
    
    def _save_results(self, round_dir: Path, minimax_eval: dict, kimi_eval: dict, issues: list):
        with open(round_dir / "minimax_eval_result.json", "w") as f:
            json.dump(minimax_eval, f, indent=2)
        with open(round_dir / "kimi_opt_eval_result.json", "w") as f:
            json.dump(kimi_eval, f, indent=2)
        with open(round_dir / "issues.json", "w") as f:
            json.dump(issues, f, indent=2)
```

- [ ] **Step 5: 添加主循环和 CLI**

```python
def main():
    parser = argparse.ArgumentParser(description="Multi-Agent Skill Tester")
    parser.add_argument("--rounds", type=int, default=1000, help="Number of rounds to run")
    parser.add_argument("--output", type=str, default="eval_results", help="Output directory")
    args = parser.parse_args()
    
    output_dir = Path(args.output)
    tester = SkillTester(output_dir)
    
    minimax_config = AgentConfig(
        api_key=os.environ.get("MINIMAX_API_KEY", ""),
        api_base="https://api.minimax.chat/v1"
    )
    kimi_config = AgentConfig(
        api_key=os.environ.get("KIMI_API_KEY", ""),
        api_base="https://api.moonshot.cn/v1"
    )
    
    tester.minimax_agent = MinimaxAgent(minimax_config)
    tester.kimi_agent = KimiAgent(kimi_config)
    
    print(f"Starting {args.rounds} rounds of testing...")
    
    all_results = []
    for i in range(args.rounds):
        result = tester.execute_round()
        all_results.append(result)
        
        if (i + 1) % 10 == 0:
            print(f"Completed round {i + 1}")
    
    # 保存汇总
    summary = {
        "total_rounds": args.rounds,
        "results": [{"round": r.round_num, "issues": len(r.issues)} for r in all_results]
    }
    with open(output_dir / "summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    
    print("Done!")


if __name__ == "__main__":
    main()
```

- [ ] **Step 6: 测试运行 (单轮测试)**

```bash
cd /Users/lucas/Documents/Projects/skill
source .venv/bin/activate
export MINIMAX_API_KEY="test_key"
export KIMI_API_KEY="test_key"
python scripts/multi_agent_tester.py --rounds 1
```

Expected: 脚本应该能够运行（即使 API 调用失败也要能捕获错误）

- [ ] **Step 7: 提交**

```bash
git add scripts/multi_agent_tester.py
git commit -m "feat: add multi-agent skill tester script

- MinimaxAgent class for creating evaluation skills
- KimiAgent class for creating optimization skills
- Round-based execution loop
- Issue detection and reporting"
```

---

## Task 2: 添加错误处理和重试逻辑

**Files:**
- Modify: `scripts/multi_agent_tester.py`

- [ ] **Step 1: 添加 API 重试装饰器**

```python
import time
from functools import wraps

def retry_on_failure(max_retries=3, delay=1):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise
                    print(f"Attempt {attempt + 1} failed: {e}, retrying...")
                    time.sleep(delay)
            return None
        return wrapper
    return decorator
```

- [ ] **Step 2: 应用重试装饰器到 API 调用**

```python
@retry_on_failure(max_retries=3, delay=2)
def _call_api(self, prompt: str) -> str:
    response = requests.post(
        # ... (同前)
    )
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]
```

- [ ] **Step 3: 添加详细的错误日志**

```python
def run_skill_evaluate(self, skill_path: str) -> dict:
    result = subprocess.run(
        ["skill", "evaluate", skill_path],
        capture_output=True,
        text=True,
        timeout=60
    )
    if result.returncode != 0:
        return {
            "error": result.stderr,
            "stdout": result.stdout,
            "returncode": result.returncode
        }
    # 尝试解析 JSON 输出
    try:
        lines = result.stdout.strip().split("\n")
        for line in lines:
            if line.startswith("{"):
                return json.loads(line)
    except:
        pass
    return {"raw_output": result.stdout}
```

- [ ] **Step 4: 提交**

```bash
git add scripts/multi_agent_tester.py
git commit -m "feat: add retry logic and error handling to multi_agent_tester"
```

---

## Task 3: 添加进度保存和恢复

**Files:**
- Modify: `scripts/multi_agent_tester.py`

- [ ] **Step 1: 添加检查点文件**

```python
CHECKPOINT_FILE = "eval_results/.checkpoint.json"

def save_checkpoint(self, round_num: int):
    with open(CHECKPOINT_FILE, "w") as f:
        json.dump({"last_round": round_num}, f)

def load_checkpoint(self) -> int:
    try:
        with open(CHECKPOINT_FILE) as f:
            return json.load(f)["last_round"]
    except:
        return 0
```

- [ ] **Step 2: 修改主循环支持恢复**

```python
def run_loop(self, total_rounds: int):
    start_round = self.load_checkpoint()
    print(f"Resuming from round {start_round + 1}")
    
    for i in range(start_round, total_rounds):
        result = self.execute_round()
        self.save_checkpoint(result.round_num)
        
        if (i + 1) % 10 == 0:
            print(f"Completed round {i + 1}")
            self.git_commit_if_issues(result.issues)
```

- [ ] **Step 3: 添加自动提交逻辑**

```python
def git_commit_if_issues(self, issues: list):
    critical_issues = [i for i in issues if i.get("severity") == "CRITICAL"]
    if critical_issues:
        subprocess.run(["git", "add", "eval_results/"], cwd=self.output_dir.parent)
        subprocess.run([
            "git", "commit", "-m", 
            f"fix: auto-fix critical issues from round {self.round_num}"
        ])
```

- [ ] **Step 4: 提交**

```bash
git add scripts/multi_agent_tester.py
git commit -m "feat: add checkpoint and auto-commit to multi_agent_tester"
```

---

## Task 4: 增强 issue 检测

**Files:**
- Modify: `scripts/multi_agent_tester.py`

- [ ] **Step 1: 添加更多 issue 检测规则**

```python
def _check_issues(self, minimax_eval: dict, kimi_eval: dict, minimax_skill: str, kimi_skill: str) -> list:
    issues = []
    
    for name, eval_result, skill_path in [
        ("minimax", minimax_eval, minimax_skill),
        ("kimi", kimi_eval, kimi_skill)
    ]:
        # 检查解析错误
        parse_result = self.run_skill_parse(skill_path)
        if parse_result.get("returncode", 0) != 0:
            issues.append({
                "severity": "HIGH",
                "source": name,
                "type": "parse_error",
                "message": parse_result.get("stderr", "Unknown parse error")
            })
        
        # 检查验证错误
        validate_result = self.run_skill_validate(skill_path)
        if validate_result.get("returncode", 0) != 0:
            issues.append({
                "severity": "MEDIUM",
                "source": name,
                "type": "validation_error",
                "message": validate_result.get("stderr", "Unknown validation error")
            })
        
        # 检查评分
        score = eval_result.get("total_score", 0)
        if score < 500:
            issues.append({
                "severity": "HIGH",
                "source": name,
                "type": "low_score",
                "message": f"Score too low: {score}"
            })
    
    return issues

def run_skill_parse(self, skill_path: str) -> dict:
    result = subprocess.run(
        ["skill", "parse", skill_path],
        capture_output=True,
        text=True
    )
    return {"returncode": result.returncode, "stdout": result.stdout, "stderr": result.stderr}

def run_skill_validate(self, skill_path: str) -> dict:
    result = subprocess.run(
        ["skill", "validate", skill_path],
        capture_output=True,
        text=True
    )
    return {"returncode": result.returncode, "stdout": result.stdout, "stderr": result.stderr}
```

- [ ] **Step 2: 提交**

```bash
git add scripts/multi_agent_tester.py
git commit -m "feat: enhance issue detection in multi_agent_tester"
```

---

## Task 5: 添加报告生成

**Files:**
- Modify: `scripts/multi_agent_tester.py`

- [ ] **Step 1: 添加 HTML 报告生成**

```python
def generate_report(self, output_dir: Path):
    report_path = output_dir / "report.html"
    
    with open(report_path, "w") as f:
        f.write("""
<!DOCTYPE html>
<html>
<head>
    <title>Multi-Agent Skill Tester Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .issue { padding: 10px; margin: 5px 0; border-radius: 5px; }
        .CRITICAL { background: #ffcccc; }
        .HIGH { background: #ffe0cc; }
        .MEDIUM { background: #fff3cc; }
        .LOW { background: #e6ffcc; }
    </style>
</head>
<body>
    <h1>Multi-Agent Skill Tester Report</h1>
""")
        
        rounds = sorted(output_dir.glob("round_*"))
        for round_dir in rounds:
            issues_file = round_dir / "issues.json"
            if issues_file.exists():
                with open(issues_file) as f:
                    issues = json.load(f)
                f.write(f"<h2>Round {round_dir.name}</h2>")
                for issue in issues:
                    severity = issue.get("severity", "LOW")
                    f.write(f'<div class="issue {severity}">{severity}: {issue.get("message", "")}</div>')
        
        f.write("</body></html>")
    
    return report_path
```

- [ ] **Step 2: 在主循环结束时生成报告**

```python
def run_loop(self, total_rounds: int):
    # ... existing code ...
    
    print("Generating report...")
    self.generate_report(Path(args.output))
    print("Done!")
```

- [ ] **Step 3: 提交**

```bash
git add scripts/multi_agent_tester.py
git commit -m "feat: add HTML report generation to multi_agent_tester"
```

---

## 执行选项

**Plan complete and saved to `docs/superpowers/plans/2026-03-30-multi-agent-skill-tester-design.md`. Two execution options:**

1. **Subagent-Driven (recommended)** - I dispatch a fresh subagent per task, review between tasks, fast iteration

2. **Inline Execution** - Execute tasks in this session using executing-plans, batch execution with checkpoints

**Which approach?**
