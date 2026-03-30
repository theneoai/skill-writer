# Usage Examples Reference

> **Purpose**: Complete usage examples for all modes
> **Load**: When §6.0 Usage Examples is accessed
> **Full doc**: SKILL.md §6.0

---

## §6.1 CREATE Mode Example

**User Input**: "I need a skill that fetches weather data from OpenWeather API and returns temperature and conditions in Celsius"

**Keyword Extraction**:

```
Keywords detected: [skill, fetch, weather, API, returns, temperature]
CREATE keywords matched: [新建, create, build]
Confidence: 0.85
Language: EN
Mode: CREATE
```

**Requirements Elicitation**:

```
Q: What is the skill's primary purpose?
A: Fetch weather data and return formatted temperature/conditions

Q: What inputs does the skill accept?
A: city_name (string, required), units (enum: celsius/fahrenheit, default: celsius)

Q: What outputs does the skill produce?
A: { temperature: number, conditions: string, city: string, timestamp: ISO8601 }

Q: What security constraints apply?
A: API key must be environment variable, not hardcoded

Q: What are the acceptance criteria?
A: Successful API response returns valid data within 2 seconds
```

**Multi-LLM Deliberation**:

```
TURN 1:
MSG-LLM1: [Generates SKILL.md draft with weather-skill structure]
MSG-LLM2: [Reviews draft, flags: API key handling requires env var validation]
MSG-LLM3: [Validates structure, confirms API key flag is valid]

CONSENSUS: UNANIMOUS (after minor revision to include env var validation)
```

**Output Artifact**:

```
skill: weather-query
version: 1.0.0
status: CERTIFIED
quality: { f1: 0.95, mrr: 0.91 }
```

**Input/Output Schema Example**:

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| city_name | string | City to query | "Beijing" |
| units | enum | Temperature unit | "celsius" |
| api_key | string | API key (env var) | "$OPENWEATHER_API_KEY" |

Output:
```json
{
  "temperature": 22.5,
  "conditions": "sunny",
  "city": "Beijing",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

---

## §6.2 EVALUATE Mode Example

**User Input**: "评估这个技能的性能 weather-query"

**Keyword Extraction**:

```
Keywords detected: [评估, 技能, 性能, weather-query]
EVALUATE keywords matched: [评估, evaluate, 测试, 评分]
Confidence: 0.91
Language: ZH
Mode: EVALUATE
```

**Quality Metrics Calculation**:

```
Test corpus: 100 sample inputs
Relevant retrieved: 95
Relevant total: 100

F1 Score: 2 * (95/100) * (95/95) / ((95/100) + (95/95)) = 0.974

Mean Reciprocal Rank:
Query 1: rank=1 → MRR=1.0
Query 2: rank=2 → MRR=0.5
...
Average MRR: 0.92
```

**Evaluation Report**:

```
skill: weather-query
evaluation_timestamp: 2024-01-15T10:00:00Z
f1_score: 0.974
mrr_score: 0.92
threshold_f1: 0.90 ✓ PASS
threshold_mrr: 0.85 ✓ PASS
status: CERTIFIED
recommendation: Skill meets all quality thresholds
```

---

## §6.3 RESTORE Mode Example

**User Input**: "restore the deleted tool-wrapper pattern from skill backup"

**Keyword Extraction**:

```
Keywords detected: [restore, deleted, tool-wrapper, pattern, backup]
RESTORE keywords matched: [恢复, restore, repair, fix, 修复, 还原]
Confidence: 0.88
Language: EN
Mode: RESTORE
```

**Recovery Protocol**:

```
1. Locate backup: .skill-backup/skill-archive-2024-01-10.zip
2. Extract tool-wrapper pattern definition
3. Validate pattern integrity (checksum match)
4. Reintegrate into current SKILL.md
5. Re-run quality gates
```

**Recovery Output**:

```
restored_artifact: tool-wrapper pattern
backup_source: skill-archive-2024-01-10.zip
integrity_check: PASS (SHA-256 match)
reintegration_status: SUCCESS
verification: Quality gates re-passed (F1=0.93, MRR=0.89)
```

---

## §6.4 SECURITY Mode Example

**User Input**: "scan this skill for SQL injection vulnerabilities: sql-query-skill"

**Keyword Extraction**:

```
Keywords detected: [scan, SQL injection, vulnerabilities, skill]
SECURITY keywords matched: [安全, security, audit, scan, 审计, 检查]
Confidence: 0.94
Language: EN
Mode: SECURITY
```

**Security Audit Output**:

```
skill: sql-query-skill
audit_timestamp: 2024-01-15T11:00:00Z

FINDINGS:
  - CRITICAL: CWE-89 potential at line 45 (unsanitized user input in query)
  - WARNING: CWE-89 potential at line 67 (dynamic table name)
  - INFO: Consider parameterization at line 23

CWE-798 (Hardcoded credentials): PASS
CWE-89 (SQL injection): FAIL
CWE-79 (XSS): PASS
CWE-94 (Code injection): PASS

overall_status: FAILED
action_required: Fix CWE-89 before production use
```

---

## §6.5 OPTIMIZE Mode Example

**User Input**: "optimize skill performance because F1 dropped to 0.82"

**Keyword Extraction**:

```
Keywords detected: [optimize, skill, performance, F1, dropped, 0.82]
OPTIMIZE keywords matched: [优化, optimize, improve, enhance, 提升, refactor]
Confidence: 0.93
Language: EN
Mode: OPTIMIZE
```

**Trigger Verification**:

```
F1 Score: 0.82 < 0.90 threshold → TRIGGER CONFIRMED
MRR Score: 0.79 < 0.85 threshold → SECONDARY TRIGGER
Tier: Current tier maintained
Error Rate: 3% < 5% threshold → OK
```

**Optimization Protocol**:

```
1. Analyze F1 failure root cause
2. Identify low-performing test cases
3. Generate improved pattern variations
4. Multi-LLM deliberation on best approach
5. Apply changes with version bump
6. Re-evaluate and verify thresholds met
```

**Optimization Output**:

```
skill: query-generator
optimization_timestamp: 2024-01-15T12:00:00Z
previous_f1: 0.82
new_f1: 0.94
previous_mrr: 0.79
new_mrr: 0.91
changes_applied: 3
status: CERTIFIED (upgraded)
```
