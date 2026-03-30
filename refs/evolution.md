# Self-Evolution Reference

> **Purpose**: Complete self-evolution specification
> **Load**: When §6 Self-Evolution is accessed
> **Full doc**: SKILL.md §6 Self-Evolution

---

## §6.1 Evolution Overview

The skill implements a three-trigger self-evolution system that continuously improves trigger accuracy and skill quality based on usage data and periodic review.

## §6.2 Evolution Triggers (evolve_decider)

| Trigger Type | Condition | Action |
|--------------|-----------|--------|
| **Threshold-Based** | F1 < 0.90 or MRR < 0.85 | Auto-flag for OPTIMIZE mode |
| **Time-Based** | No update in 30 days | Schedule staleness review |
| **Usage-Based** | < 5 invocations in 90 days | Deprecate or relevance review |

## §6.3 Usage Tracker (usage_tracker)

The system tracks the following metrics per skill:

| Metric | Description | Collection Method |
|--------|-------------|-------------------|
| invocation_count | Number of times skill invoked | Increment on each trigger |
| success_count | Successful executions (all steps complete) | Count when Done criteria met |
| failure_count | Failed executions | Count when Fail criteria met |
| avg_latency_ms | Average execution time | Rolling average of duration_ms |
| trigger_accuracy | Correct mode routing rate | % of inputs where confidence ≥ 0.85 |

**Usage Data Schema**:
```yaml
usage_tracker:
  skill_name: [string]
  period: [start_date, end_date]
  invocation_count: [integer]
  success_count: [integer]
  failure_count: [integer]
  avg_latency_ms: [float]
  trigger_accuracy: [float]
  last_updated: [ISO8601]
```

## §6.4 Evolution Decision Logic (evolution trigger)

```
IF trigger_accuracy < 0.85:
    → Analyze misrouted inputs
    → Update keyword weights in Mode Router
    → Re-evaluate with test corpus

IF error_rate > 10% per 100 calls:
    → Flag for immediate review
    → Invoke SECURITY mode for audit
    → Apply hotfix if critical

IF F1 < 0.90 OR MRR < 0.85:
    → Queue for OPTIMIZE mode
    → Apply pattern improvements
    → Re-evaluate thresholds

IF usage_based_trigger AND staleness detected:
    → Send notification to maintainer
    → Provide relevance assessment
    → Offer deprecation or refresh choice
```

## §6.5 Self-Evolution Done Criteria

- Done: Usage tracker updated after each operation
- Done: Evolution triggers evaluated every 7 days
- Done: F1 and MRR re-measured after OPTIMIZE
- Done: Trigger accuracy ≥ 0.90 achieved
- Done: Evolution audit trail maintained

## §6.6 进化触发 (Chinese Triggers)

| 触发条件 | 阈值 | 执行动作 |
|-----------|------|----------|
| 触发准确率 | < 85% | 分析误路由案例，更新关键词权重 |
| 错误率 | > 10% per 100次 | 立即标记，启动SECURITY审计 |
| F1分数 | < 0.90 | 队列进入OPTIMIZE模式 |
| MRR分数 | < 0.85 | 队列进入OPTIMIZE模式 |
| 闲置时间 | > 90天无调用 | 发送维护通知，提供选择 |
