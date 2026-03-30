# Audit Trail Specification Reference

> **Purpose**: Complete audit trail specification
> **Load**: When §4.0 Audit Trail is accessed
> **Full doc**: SKILL.md §4.0

---

## §4.1 Required Audit Fields

Every skill operation MUST produce an audit record containing:

| Field | Type | Description | Required |
|-------|------|-------------|----------|
| timestamp | ISO8601 | Operation start time | YES |
| duration_ms | integer | Total operation time | YES |
| mode | enum | CREATE/EVALUATE/RESTORE/SECURITY/OPTIMIZE | YES |
| user_input_hash | string | SHA-256 hash of user input | YES |
| confidence | float | Routing confidence score | YES |
| llm1_output_hash | string | SHA-256 hash of LLM-1 output | YES |
| llm2_issues_count | integer | Number of issues found | YES |
| llm3_consensus | enum | UNANIMOUS/MAJORITY/SPLIT/UNRESOLVED | YES |
| quality_gates_passed | boolean | F1 ≥ 0.90 AND MRR ≥ 0.85 | YES |
| security_baseline_passed | boolean | No CWE violations | YES |
| signoff_type | enum | HUMAN/AUTOMATED/TEMP_CERT | YES |
| signoff_timestamp | ISO8601 | When sign-off occurred | YES |
| artifact_version | string | Semantic version of output | YES |
| error_recovery_invoked | boolean | Any error recovery triggered | YES |
| error_recovery_actions | string[] | List of recovery actions taken | CONDITIONAL |

## §4.2 Audit Storage

- **Primary**: `.skill-audit/` directory in project root
- **Format**: JSON Lines (JSONL), one record per line
- **Retention**: 365 days minimum
- **Indexing**: By timestamp, mode, and artifact_version

## §4.3 Audit Log Entry Example

```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "duration_ms": 45230,
  "mode": "CREATE",
  "user_input_hash": "a1b2c3d4...",
  "confidence": 0.92,
  "llm1_output_hash": "e5f6g7h8...",
  "llm2_issues_count": 3,
  "llm3_consensus": "UNANIMOUS",
  "quality_gates_passed": true,
  "security_baseline_passed": true,
  "signoff_type": "HUMAN",
  "signoff_timestamp": "2024-01-15T10:31:30Z",
  "artifact_version": "1.0.0",
  "error_recovery_invoked": false,
  "error_recovery_actions": []
}
```

## §4.4 Audit Trail Done Criteria

- Done: Audit record created for every operation
- Done: All required fields populated
- Done: JSONL format valid
- Done: Stored in `.skill-audit/` directory
- Done: Retention policy maintained (365 days)
