# Code Reviewer Skill

[![Certification](https://img.shields.io/badge/Certification-GOLD-FFD700)](./eval-report.md)
[![Score](https://img.shields.io/badge/Score-947%2F1000-FFD700)](./eval-report.md)
[![Type](https://img.shields.io/badge/Type-Workflow%20Automation-blue)](./skill.md)

A comprehensive code review skill with multi-step workflow automation, security scanning, and bilingual support for the Skill Framework.

## Features

### Multi-Step Workflow
- **6-step review process** with clear entry/exit criteria
- **Automatic rollback** on failure with recovery actions
- **Quality gates** at each stage to ensure standards
- **Progress tracking** through the workflow

### Security Scanning
- **CWE-focused detection** for critical vulnerabilities:
  - CWE-798: Hardcoded Credentials
  - CWE-89: SQL Injection
  - CWE-78: OS Command Injection
  - CWE-22: Path Traversal
- **Severity-based reporting** (CRITICAL, HIGH, MEDIUM, LOW)
- **Baseline compliance** checks with PASS/FAIL status

### Style Checking
- Cyclomatic complexity analysis
- Function length validation
- Naming convention verification
- Documentation coverage assessment

### Bilingual Support
- English and Chinese language support
- Language detection from user input
- Consistent CWE references across languages

## Workflow Steps

| Step | Description | Rollback Trigger |
|------|-------------|------------------|
| 1 | Input Validation | Syntax errors, unreadable files |
| 2 | Static Analysis | Critical complexity > 20 |
| 3 | Security Scan | HIGH severity findings |
| 4 | Pattern Matching | Critical anti-patterns |
| 5 | Quality Gates | Gate failures |
| 6 | Report Generation | - |

### Rollback Mechanism

When a step fails:
1. Halt workflow execution
2. Log failure reason
3. Execute rollback action
4. Wait for resolution
5. Resume from appropriate step

## Usage

### REVIEW Mode (Full Review)

```yaml
skill: code-reviewer
mode: REVIEW
input:
  - src/auth.py
  - src/database.py
quality_gates:
  complexity: 15
  coverage: 80
```

### SCAN Mode (Security Only)

```yaml
skill: code-reviewer
mode: SCAN
targets:
  - CWE-798
  - CWE-89
  - CWE-78
  - CWE-22
```

### SUGGEST Mode (Non-blocking)

```yaml
skill: code-reviewer
mode: SUGGEST
categories:
  - style
  - performance
  - maintainability
```

### Bilingual Usage

```
# English
"Review this file for security issues"

# Chinese
"扫描这个项目的安全漏洞"
"审查这段代码的质量"
"建议改进方案"
```

## Certification

This skill has been evaluated and certified **GOLD** with a score of **947/1000**.

### Evaluation Highlights

| Phase | Score | Max |
|-------|-------|-----|
| Phase 1 — Parse & Validate | 96 | 100 |
| Phase 2 — Text Quality | 273 | 300 |
| Phase 3 — Runtime Testing | 385 | 400 |
| Phase 4 — Certification | 193 | 200 |
| **Total** | **947** | **1000** |

See the full [Evaluation Report](./eval-report.md) for detailed breakdown.

## File Structure

```
examples/code-reviewer/
├── skill.md           # Main skill definition
├── README.md          # This file
└── eval-report.md     # Certification report
```

## Requirements

- Skill Framework >= 2.0.0
- Workflow Automation template support
- Bilingual interface capability

## License

MIT License - See [skill.md](./skill.md) for details.

## Author

Skill Framework Team
