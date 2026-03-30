# Skill 设计洞察总结

> 日期：2026-03-28
> 来源：设计讨论对话

---

## 一、好的 Skill 是什么样的

### 结构必备

```yaml
---
name: skill-name
description: "触发关键词 + 功能描述，≤1024 字符"
license: MIT
metadata:
  version: 1.0.0
  tags: [...]
---
```

**主体三节必备**：
- **§1.1 Identity** — 具体角色定义（不能写"专家"这类模糊词）
- **§1.2 Framework** — 决策层级和优先级规则
- **§1.3 Thinking** — 3-5 个命名推理模式

### 六维质量标准

| 维度 | 权重 | 关键标准 |
|------|------|---------|
| System Prompt | 20% | 三节齐全，身份明确无歧义 |
| Domain Knowledge | 20% | 有真实数据（具体数字/框架名），不能泛泛而谈 |
| Workflow | 20% | 4-6 个阶段，每阶段有明确的 Done/Fail 条件 |
| Error Handling | 15% | 具名失败模式 + 恢复步骤 |
| Examples | 15% | ≥5 个场景，含边界案例 |
| Metadata | 10% | 格式合规，描述 ≤1024 字符 |

### 认证等级

| 等级 | 文本分 | 运行时分 | 方差 |
|------|--------|---------|------|
| PLATINUM | ≥9.5 | ≥9.5 | <1.0 |
| GOLD | ≥9.0 | ≥9.0 | <1.5 |
| SILVER | ≥8.0 | ≥8.0 | <2.0 |
| BRONZE | ≥7.0 | ≥7.0 | <3.0 |

### 文档分层原则

- **SKILL.md** ≤300 行：导航表 + 摘要
- **references/** 目录：详细 SOP、完整示例、反模式分析

---

## 二、触发正确性

### 核心定义

触发正确性 = 用户的自然输入，能被正确路由到对应的 skill 和 mode。
目标：**1000 轮测试 ≥99% 匹配率**。

### 触发失败的典型根因（真实案例）

> 用户输入"项目下随机找一个 skill 评价下" → skill 未触发
>
> 根因：触发短语要求 `"skill" + 关键词` 固定顺序，
> 而用户输入是`"评价 skill"`（关键词在前）

### 四个设计原则

**1. 双向匹配**
```
❌ 仅匹配 "skill evaluate"
✅ 包含 "skill" 且包含 "evaluate"（顺序无关）
```

**2. 覆盖中英文同义词**

| 模式 | 英文关键词 | 中文关键词 |
|------|-----------|-----------|
| CREATE | create, write, build, make, develop | 新建技能, 创建技能 |
| EVALUATE | evaluate, test, score, assess, certify | 评估技能, 打分, 评分 |
| RESTORE | restore, fix, repair, recover | 修复技能, 恢复技能 |
| TUNE | optimize, tune, autotune, boost | 调优技能, 优化技能, 自优化 |

**3. 优先级顺序防冲突**
```
SECURITY → CREATE → EVALUATE → RESTORE → TUNE
```

**4. 宁可误触发，不漏触发**
```
误触发成本：用户多确认一步（低）
漏触发成本：绕过专业方法论（高）
```

### 反模式

| 反模式 | 问题 | 修复 |
|--------|------|------|
| 固定顺序 `"skill" + 关键词` | "评价skill"不触发 | 双向匹配 |
| 仅英文关键词 | 中文用户漏触发 | 中英文都覆盖 |
| 关键词列表过短 | 同义词漏触发 | 覆盖评价/审查/打分/审计... |
| 依赖用户知道专业术语 | "优化这个"不触发 | 检测领域行为意图 |

---

## 三、安全检查体系

### 优先级原则

**Security First — 优先级高于 Correctness，高于 Efficiency**

### P0：敏感信息保护

**硬编码凭证（CWE-798）**
```bash
# 发布前必跑
grep -rE "password|secret|api_key|token" ./skills/
# 要求：0 matches
```

| 禁止 | 正确做法 |
|------|---------|
| `api_key: sk-abc123` | `api_key: ${OPENAI_API_KEY}` |
| 密钥写在注释里 | 全部用环境变量引用 |

**日志不泄露（CWE-200）**
- 禁止在日志中打印 API Key、用户数据、系统路径
- 临时文件处理后立即删除

### P0：防注入攻击

**Prompt Injection（LLM 特有）**

进入 LLM 评分前清洗：
```bash
sed -e 's/ignore previous instructions//gi' \
    -e 's/you are now //gi' \
    -e 's/\[SYSTEM\]//g'
```

**命令注入（CWE-77/78）**
```bash
eval "$user_input"   # ❌
bash script.sh "$sanitized_path"  # ✅
```

**路径遍历（CWE-22）**
```bash
cat "../../../etc/passwd"  # ❌
realpath --canonicalize-existing "$user_path"  # ✅
```

### P1：系统稳定性保护

- 外部调用：默认 30s 超时，最大 300s
- 熔断规则：3 次失败 → 60s 冷却
- 危险操作（rm -rf）需先验证路径

### OWASP AST10 发布门禁

| 检查项 | 通过标准 |
|--------|---------|
| 凭证扫描 | 0 matches |
| 输入验证 | 无语法错误 |
| 路径遍历 | 无遍历检测 |
| Prompt 注入 | 注入模式已清洗 |
| 角色边界 | 拒绝角色切换 |

---

## 四、使用即学习：日常进化机制

### 与批量优化的区别

| | 批量优化（现有） | 使用即学习（新设计） |
|--|----------------|-------------------|
| 触发时机 | 手动运行 tune.sh | 每次对话结束自动触发 |
| 存储位置 | 修改 SKILL.md 本体 | knowledge-journal.md |
| 粒度 | 大版本迭代 | 单条经验增量 |
| 验证 | 评分脚本 | 置信度标记 |

### 核心架构

```
每次调用
   ↓
执行任务（正常工作）
   ↓
结束时：自动提取 → 写入 knowledge-journal.md
   ↓
下次调用开始：自动读取近期 journal → 注入上下文
```

### 提取什么（四类有价值的经验）

| 类型 | 触发条件 | 示例 |
|------|---------|------|
| 新案例 | 用户带来以前没见过的场景 | "金融领域合规审查" |
| 新方法 | 解决问题时用了新策略 | "分步拆解比直接给答案效果好" |
| 用户纠正 | 用户说"不对""换一种" | "法律领域不用 McKinsey 框架" |
| 边界发现 | 遇到以前没测试过的边界 | "输入超 500 行时触发器失效" |

### knowledge-journal.md 格式

```markdown
## 2026-03-28 | session-042
**类型**: 新案例
**领域**: 金融合规
**发现**: 用户用 EVALUATE 模式审查合规文档，触发词是"合规审查"
**可用**: 扩展 EVALUATE 的触发词覆盖
**置信度**: medium

## 2026-03-27 | session-039
**类型**: 用户纠正
**发现**: 法律类 skill 不适合用 McKinsey 7-S，用户明确拒绝
**可用**: 领域知识库增加"法律领域→避免管理咨询框架"
**置信度**: high
```

### 在 §1.3 Thinking 里声明这个行为

```markdown
**Session Learning**: At the end of each interaction, ask:
- Did I encounter a pattern I hadn't seen before?
- Did the user correct or redirect me?
- Did I find a method that worked better than expected?
If yes → append to knowledge-journal.md with type tag.
At start → scan last 10 journal entries for relevance.
```

### 防退化机制

**防垃圾积累**
- 只保存有用户反馈或明显效果的经验
- 置信度 low 且 3 次未被使用 → 自动清除

**防 journal 过长**
- 保留最近 50 条活跃条目
- 每月 consolidate：同类条目合并成规律性总结
- 原始条目归档

### 与现有系统的协作关系

```
knowledge-journal.md（草稿本）
   ↓ 积累到一定程度
触发 tune → 把 journal 里验证过的规律
   ↓ 正式合并进
SKILL.md 本体（正式版）
```

---

## 关键结论

1. **好的 skill** = 结构完整（三节）+ 内容具体（真实数据）+ 示例充足（≥5）+ 安全合规
2. **触发正确性** = 双向匹配 + 中英文覆盖 + 宁可误触发不漏触发
3. **安全** = Security First，P0 是凭证/注入/遍历，发布前跑 OWASP 门禁
4. **持续进化** = 批量优化改本体 + 使用即学习积累 journal，两者协作形成飞轮
