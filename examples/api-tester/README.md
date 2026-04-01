# API Tester Skill

> **Type**: api-integration  
> **Version**: 1.0.0  
> **Certification**: GOLD 930/1000  
> **Framework**: Skill Framework v2.0.0

---

## 功能特性

- **TEST Mode**: 执行单个 HTTP API 请求并验证响应
- **VALIDATE Mode**: 验证响应数据结构、类型和值
- **BATCH Mode**: 批量执行测试套件并生成汇总报告
- **安全扫描**: 自动检测 CWE-798, CWE-89, CWE-200 等安全漏洞
- **双语支持**: 中英文触发词和错误提示
- **审计追踪**: 完整的测试历史记录

---

## 认证等级

![GOLD](https://img.shields.io/badge/Certification-GOLD-FFD700?style=for-the-badge)

**总分**: 930 / 1000

| 阶段 | 分数 | 满分 |
|------|------|------|
| Phase 1 - Parse & Validate | 95 | 100 |
| Phase 2 - Text Quality | 275 | 300 |
| Phase 3 - Runtime Testing | 370 | 400 |
| Phase 4 - Certification | 190 | 200 |

**质量指标**:
- F1 Score: 0.92 ✅
- MRR: 0.88 ✅
- Trigger Accuracy: 0.93 ✅
- Variance: 0.83 (< 15) ✅

---

## 使用示例

### 测试单个 API

```
输入: "测试 GET https://api.example.com/users/123"

输出:
{
  "mode": "TEST",
  "status": 200,
  "latency_ms": 145,
  "validation": {"passed": true},
  "security_scan": {"cwe_798": "CLEAR"}
}
```

### 批量测试

```
输入: "批量测试这些端点: /health, /users, /orders"

输出:
{
  "mode": "BATCH",
  "summary": {"total": 3, "passed": 3, "failed": 0},
  "duration_ms": 420
}
```

---

## 文件结构

```
examples/api-tester/
├── skill.md          # 技能定义文件 (主文件)
├── README.md         # 本说明文档
└── eval-report.md    # 详细评估报告
```

---

## 快速开始

1. 设置环境变量:
   ```bash
   export API_TEST_TOKEN="your-api-token"
   ```

2. 使用 TEST Mode:
   ```
   "测试 GET https://api.example.com/endpoint"
   ```

3. 使用 BATCH Mode:
   ```
   "批量测试: GET /api/v1/users, POST /api/v1/orders"
   ```

---

## 安全特性

- ✅ CWE-798: 无硬编码凭证
- ✅ CWE-89: SQL 注入防护
- ✅ CWE-200: 敏感信息掩码
- ✅ CWE-295: SSL 证书验证
- ✅ 请求超时和重试机制

---

## 评估报告

查看详细的评估报告: [eval-report.md](./eval-report.md)

---

## 许可证

MIT License - 详见 skill.md

---

**Powered by Skill Framework v2.0.0**
