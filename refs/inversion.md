# Inversion Pattern Methodology Reference

> **Purpose**: Complete inversion pattern specification
> **Load**: When §3.0 Inversion Pattern is accessed
> **Full doc**: SKILL.md §3.0

---

## §3.1 Purpose

The Inversion Pattern ensures complete requirements are gathered BEFORE execution begins. Instead of assuming requirements, the skill actively elicits them through structured questioning.

## §3.2 Required Elicitation Questions

| Question | Purpose | Required For |
|----------|---------|--------------|
| 1. What is the skill's primary purpose? | Define core functionality | ALL modes |
| 2. Who are the target users? | Determine interface complexity | ALL modes |
| 3. What inputs does the skill accept? | Define parameter schema | CREATE, OPTIMIZE |
| 4. What outputs does the skill produce? | Define return schema | CREATE, OPTIMIZE |
| 5. What are the acceptance criteria? | Define success metrics | ALL modes |
| 6. What security constraints apply? | Identify CWE risks | ALL modes |
| 7. What is the expected quality threshold? | Define F1/MRR targets | EVALUATE, OPTIMIZE |
| 8. What is the rollback plan? | Define recovery procedure | RESTORE |

## §3.3 Requirements Document Template

```yaml
requirements:
  skill_name: [string]
  purpose: [string]
  target_users: [string[]]
  inputs:
    - name: [string]
      type: [string]
      required: [boolean]
      validation: [string]
  outputs:
    - name: [string]
      type: [string]
      description: [string]
  acceptance_criteria:
    - criterion: [string]
      metric: [string]
      threshold: [number]
  security_constraints:
    - cwe_id: [string]
      mitigation: [string]
  quality_thresholds:
    f1_min: 0.90
    mrr_min: 0.85
  rollback_plan: [string]
  language: [ZH|EN|BOTH]

elicitation_status: [COMPLETE|PARTIAL|ESCALATED]
missing_fields: [string[]]
```

## §3.4 Blocking Rule

**RULE**: Step 4 (LLM-1 GENERATE DRAFT) MUST NOT begin until:
1. All Required fields in the requirements document are populated
2. Elicitation status is COMPLETE or user explicitly overrides
3. User sign-off obtained for any missing fields

## §3.5 Inversion Workflow

```
## Phase 1 — Problem Discovery (一次问一个问题，等回答)

Q1: "这个Skill为用户解决什么问题？"
   → Wait for answer before Q2

Q2: "主要用户是谁？他们的技术水平如何？"
   → Wait for answer before Q3

Q3: "预期规模是多少？（简单/中等/复杂）"
   → Wait for answer before synthesis

## Phase 2 — Technical Constraints (Phase 1 全部回答完之后)

Q4: "你有什么技术栈要求或偏好？"
   → Wait for answer before Q5

Q5: "有哪些不可妥协的要求？（质量/速度/安全性）"
   → Wait for answer before synthesis
```

## §3.6 Inversion Done Criteria

- All 8 required questions answered
- Requirements document complete with no missing fields
- User sign-off on any waived fields
- Elicitation status = COMPLETE
