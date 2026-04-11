# Skill 工程研究综合报告 2026

> **日期**: 2026-04-11
> **覆盖**: 学界论文、行业实践、社区最佳实践、安全生态
> **目标**: 识别业界最新 skill 工程方法论，提炼可落地到 skill-writer 的改进点
> **影响文件**: `skill-framework.md`, `refs/security-patterns.md`, `refs/session-artifact.md`, `templates/base.md`, `ARCHITECTURE-REVIEW.md`

---

## 一、学界最新研究综述

### 1.1 EvoSkills — 协同进化验证框架（arxiv:2604.01687）

**核心贡献**: 用独立的"代理验证者（Surrogate Verifier）"替代自审，彻底消除生成偏差。

| 机制 | 描述 |
|------|------|
| Skill Generator | 持久对话上下文，积累生成历史 |
| Surrogate Verifier | **独立 LLM 会话**，不继承生成器偏见 |
| 多轮进化 | Round 1→3 超越人工精选；Round 5 达 75% Pass Rate |
| 跨模型迁移 | 在 Claude Opus 4.6 上进化的 skill 迁移到 GPT-5.2、Qwen3-Coder 等六个模型，增益 +35~+44pp |

**对 skill-writer 的启示**:
- 当前 OPTIMIZE 模式使用同一 LLM 会话的 3-pass 自审，存在确认偏差风险
- 应在 OPTIMIZE 收敛后引入独立视角验证（**VERIFY 阶段**）
- VERIFY 应显式声明"不继承 OPTIMIZE 上下文"，用全新视角审查

---

### 1.2 SkillX — 三层层级 Skill 知识库（arxiv:2604.04804）

**核心贡献**: 将 skill 抽象为三个互补层级，形成可组合、可迁移的知识体系。

```
Planning Skills  ← 高层任务组织（what to do）
      ↓
Functional Skills ← 可复用、基于工具的子程序（how to do）
      ↓  
Atomic Skills    ← 执行导向的使用模式和约束（constraints）
```

**三个核心创新**:
1. **Multi-Level Skills Design**: 从原始轨迹提炼三层层级
2. **Iterative Skills Refinement**: 基于执行反馈自动修订
3. **Exploratory Skills Expansion**: 主动生成并验证超出训练数据的新 skill

**对 skill-writer 的启示**:
- 当前模板设计为"平面文档"，无层级概念
- CREATE 模式应引导用户声明 skill 所属层级（planning / functional / atomic）
- LEAN 评分应对层级定位清晰度给予额外分值
- 模板中应提供 `depends_on` 字段声明 Atomic Skill 依赖

---

### 1.3 SkillRL — 递归 Skill 增强强化学习（arxiv:2602.08234）

**核心贡献**: 从成功和失败轨迹中分别提炼不同类型的 skill 知识。

| 来源 | 提炼内容 |
|------|---------|
| 成功轨迹 | 战略模式（strategic patterns）→ General Skills |
| 失败轨迹 | 简洁教训（concise lessons from failure）→ Task-Specific Skills |

**层级 SkillBank**:
- General Skills：通用战略指导
- Task-Specific Skills：类别级启发式规则

**效果**: 与原始轨迹存储相比，token 压缩 10-20%，同时提升推理质量。

**对 skill-writer 的启示**:
- 当前 COLLECT 模式的 `session_summary` 不区分成功/失败模式类型
- session-artifact 应增加 `lesson_type: strategic_pattern | failure_lesson` 字段
- AGGREGATE 模式应分开处理两类教训，避免混淆

---

### 1.4 SkillRouter — 大规模 Skill 路由（arxiv:2603.22455）

**核心发现（颠覆性）**: **Skill Body 是决定性路由信号**，不是 name+description。

| 信号 | 影响 |
|------|------|
| 移除 body 文本 | 准确率下降 **29~44pp**（跨所有方法） |
| cross-encoder 注意力 | **91.7% 集中在 body 字段** |
| 仅用 name+description | 远低于包含 body 的基准线 |

**SkillRouter 系统**: 1.2B 参数检索-重排管道，达 74.0% Hit@1，比最强基准快 5.8×。

**对 skill-writer 的启示**:
- 当前 LEAN 评分中 Metadata 仅占 25/500（5%），严重低估
- **Skill Body 第一段**应作为高密度信息摘要，集中编码领域知识
- CREATE 模式应要求第一段为"Skill Summary"（检索优化段）
- description 字段的质量评分权重需要调整

---

### 1.5 "Agentic Skills in the Wild" — 现实环境基准（arxiv:2604.04323）

**核心发现**: Skill 收益随环境真实性递减，最终趋近无-skill 基线。

**两大瓶颈**:
1. **Skill 选择失败**：智能体难以判断应加载哪些 skill
2. **Skill 内容质量**：检索到的 skill 内容嘈杂或缺乏精准信息

**对 skill-writer 的启示**:
- CREATE 阶段应重点解决"内容精准性"（对应 LEAN 的 Domain Knowledge 维度）
- EVALUATE Phase 2 应新增"检索友好性"子维度
- 负向边界（"Do NOT use for"）是解决瓶颈 1 的关键机制

---

### 1.6 SkillProbe — Skill 市场安全审计（arxiv:2603.21019）

**大规模安全扫描结论**（31,132 个 skill）:
- 26.1% 包含至少一个漏洞（14 种模式）
- **13.4% 含严重级安全问题**（恶意软件、Prompt 注入、暴露的 secrets）
- 包含可执行脚本的 skill **漏洞率高 2.12×**
- ClawHavoc 活动：6 周内向 ClawHub 推送数百个恶意 skill

**对 skill-writer 的启示**:
- 当前 CWE 扫描覆盖代码注入类漏洞，但未覆盖 **Prompt 注入**（ASI01）
- 可执行脚本 skill 应触发更严格的安全门控
- 需新增供应链安全检查项

---

### 1.7 SoK: Agentic Skills（arxiv:2602.20867）

**核心贡献**: 对 skill 领域的系统化知识整理，建立统一分类法。

**Skill 生命周期模型**:
```
Discovery → Loading → Execution → Feedback → Evolution
```

**Skill 分类**:
- 工具增强型（Tool-augmenting）
- 知识注入型（Knowledge-injecting）
- 工作流编排型（Workflow-orchestrating）
- 自进化型（Self-evolving）

---

## 二、行业实践与社区最佳实践

### 2.1 SKILL.md 模式（Anthropic agentskills.io + 从业者博客）

#### 2.1.1 渐进式加载架构（Progressive Disclosure）

```
Stage 1: Metadata (~100 tokens, 始终在上下文中)
  ← Claude 基于此决定是否触发 skill
  
Stage 2: SKILL.md Body (仅在触发时加载)
  ← 完整的指令和工作流
```

**关键启示**: 每个 skill 实质上有两个"接口"——触发接口（metadata）和执行接口（body）。

#### 2.1.2 Description 是触发成败的关键

> "If your skill does not trigger, it is almost never the instructions — it is the description."

最佳实践:
- description 必须包含**what the skill does** + **when to use it**（具体触发场景）
- 包含明确的触发词/短语列表
- 一个 skill 只覆盖一个清晰定义的任务域

#### 2.1.3 负向边界（Negative Boundaries）— 必要条件

```yaml
# 必须包含
boundaries:
  not_for: |
    - Do NOT use for job interview preparation (triggers: "interview prep")
    - Do NOT use for cover letters (separate skill)
    - Do NOT use when user wants informal/casual formatting
```

**理由**: 没有负向边界时，语义相近的请求会错误触发 skill。

#### 2.1.4 示例模式（Examples Pattern）

```markdown
## Examples
Input:  "Added user authentication with JWT tokens"
Output: "feat(auth): implement JWT-based authentication"

Input:  "Fixed null pointer in payment service"  
Output: "fix(payment): resolve null pointer exception in payment processor"
```

---

### 2.2 OWASP Agentic Applications Top 10（2026）

100+ 行业专家协作制定的权威安全框架：

| ID | 风险 | 描述 |
|----|------|------|
| **ASI01** | Agent Goal Hijack | 通过注入指令或中毒内容重定向 agent 目标（Prompt 注入） |
| **ASI02** | Tool Misuse & Exploitation | 通过不安全链式调用、歧义指令或操纵工具输出滥用工具 |
| **ASI03** | Identity & Privilege Abuse | 利用委托信任、继承凭据或角色链获得未授权访问 |
| **ASI04** | Agentic Supply Chain Vulnerabilities | 被篡改的第三方 agent、工具、插件、注册表或更新渠道 |
| **ASI05** | Excessive Autonomy & Scope Creep | Agent 在授权范围外自主行动 |
| **ASI06** | Prompt Confidentiality Leakage | 通过 skill 内容泄露系统 prompt 或敏感上下文 |
| **ASI07** | Insecure Skill Composition | 单独安全的 skill 在特定组合时产生危险行为 |
| **ASI08** | Memory & State Poisoning | 通过污染持久记忆或跨会话状态影响未来行为 |
| **ASI09** | Lack of Human Oversight | 在高风险场景缺乏人工检查点和审批机制 |
| **ASI10** | Audit Trail Gaps | 缺乏可追溯的决策和行动记录 |

**对 skill-writer 的启示**:
- 当前 CWE 覆盖代码安全但不覆盖 ASI01（Prompt 注入）、ASI07（不安全组合）
- LEAN 安全维度（50分）需要扩展到覆盖 OWASP Agentic Top 10
- EVALUATE Phase 2/3 应引入 ASI 检查项

---

### 2.3 语义版本化与兼容性（社区实践）

**关键数据**：Tool versioning 导致 **60% 的生产环境 agent 失败**。

最佳实践：
```
MAJOR.MINOR.PATCH
- MAJOR: 破坏性变更（触发词变更、输出格式变更）
- MINOR: 向后兼容的新功能
- PATCH: Bug 修复，向后兼容
```

**对 skill-writer 的启示**:
- 当前 Edit Audit Guard 的 MICRO/MINOR/MAJOR/REWRITE 分类需要与 semver MAJOR 对齐
- `skill-registry.md` 应明确声明何为破坏性变更（影响触发词、输出契约的变更）

---

### 2.4 ClawHub 生态与市场设计（社区观察）

- ClawHub 已有 13,729+ 社区 skill
- 高质量 skill 评估标准：首次易用性、持续可靠性、无隐藏风险
- **12~20% 的社区 skill 存在恶意内容**（不同研究结果不同）
- 最小权限原则、版本固定（pin versions）是安全使用的基本要求

---

## 三、研究成果与 skill-writer 现状的差距分析

### 3.1 Gap 矩阵

| 研究发现 | 重要性 | 当前状态 | 改进优先级 |
|---------|--------|---------|----------|
| Skill Body 是决定性路由信号（SkillRouter） | 🔴 极高 | 缺失 — metadata 仅占 LEAN 5% | P0 |
| 负向边界是必要条件（SKILL.md Pattern） | 🔴 极高 | 完全缺失 | P0 |
| OWASP ASI01 Prompt 注入检测 | 🔴 极高 | 不在 CWE 覆盖范围 | P0 |
| 协同进化验证（EvoSkills Surrogate Verifier） | 🟠 高 | OPTIMIZE 只有同会话自审 | P1 |
| 三层层级结构（SkillX） | 🟠 高 | 模板为平面结构 | P1 |
| 成功/失败模式分类（SkillRL） | 🟠 高 | session_summary 不区分 | P1 |
| Skill Summary 段（检索优化，SkillRouter） | 🟠 高 | 无专门 summary 段 | P1 |
| OWASP ASI07 不安全组合检查 | 🟡 中 | 缺失 | P2 |
| Inversion extra_questions（模板自适应） | 🟡 中 | 已在 ARCHITECTURE-REVIEW 识别 | P2 |
| 语义版本兼容性矩阵 | 🟡 中 | semver 有但无 breaking change 规范 | P2 |
| SSOT 缺口修复（reader 未嵌入 3 个 refs） | 🟡 中 | 已在 ARCHITECTURE-REVIEW 识别 | P2 |
| Exploratory Skill Expansion（SkillX） | 🟢 低 | 完全缺失（较复杂） | P3 |

---

## 四、改进方案详述

### 改进 A：Skill Description 触发优化（P0）

**依据**: SkillRouter（skill body 信号决定性）+ SKILL.md Pattern（description 是触发关键）

**变更**:
1. `skill-framework.md §5 CREATE` — Phase 1 (ELICIT) 新增专项问题："描述 skill 的触发场景，用户会用什么词语"
2. `templates/base.md` — 新增标准化 `triggers` 字段和 `## Skill Summary` 段（第一个 H2，≤5 句话，密集编码领域知识）
3. `eval/rubrics.md` — Metadata 从 25 分提升到 50 分，新增"触发词覆盖率"子维度
4. LEAN 7 维度中 Metadata 权重从 5% 调整到 10%，Domain Knowledge 保持 20%

### 改进 B：负向边界强制要求（P0）

**依据**: SKILL.md Pattern（negative boundaries 是必要条件，防止误触发）

**变更**:
1. `templates/base.md` — 新增 `## Negative Boundaries` 必填段
2. `skill-framework.md §5 CREATE Phase 1` — 新增必问项："这个 skill 不应该在哪些场景触发？"
3. `skill-framework.md §6 LEAN` — 缺少 Negative Boundaries 扣 20 分（新规则）
4. `refs/security-patterns.md` — 新增"误触发（False Trigger）"作为 P2 风险

### 改进 C：OWASP Agentic Skills Top 10 安全检测（P0）

**依据**: SkillProbe（26.1% skill 含漏洞）+ OWASP Agentic Apps Top 10（2026）

**变更**:
1. `refs/security-patterns.md` — 新增 §5 OWASP Agentic Skills 检测规则
2. `skill-framework.md §11 Security` — Red Lines 新增 ASI01 Prompt 注入检测
3. EVALUATE Phase 3 — 新增 ASI 检测子阶段

### 改进 D：协同进化验证（VERIFY 阶段）（P1）

**依据**: EvoSkills（独立验证者消除生成偏差，从 32% 提升至 75%）

**变更**:
1. `skill-framework.md §9 OPTIMIZE` — 收敛后新增 VERIFY 步骤（Step 10）
2. VERIFY 明确要求："不使用 OPTIMIZE 上下文；以全新视角重新评估"
3. VERIFY 使用 LEAN 7 维打分，与 OPTIMIZE 末轮分数对比

### 改进 E：三层层级结构（P1）

**依据**: SkillX（三层：Planning / Functional / Atomic）

**变更**:
1. `templates/base.md` YAML frontmatter — 新增 `skill_tier: planning | functional | atomic`
2. `skill-framework.md §5 CREATE` — ELICIT 新增："这个 skill 是高层规划、中层功能、还是原子操作？"
3. `skill-framework.md §2 Mode Router` — 路由规则新增 tier 感知提示
4. `refs/skill-registry.md` — 注册表支持按 tier 分组查询

### 改进 F：Session Artifact 成功/失败模式分类（P1）

**依据**: SkillRL（成功轨迹→战略模式；失败轨迹→简洁教训，10-20% token 压缩）

**变更**:
1. `refs/session-artifact.md` — 新增 `lesson_type: strategic_pattern | failure_lesson` 字段
2. 新增 `lesson_summary` 字段（≤3 句话的蒸馏教训）
3. AGGREGATE 模式应分类处理两种 artifact

### 改进 G：Skill Summary 检索优化段（P1）

**依据**: SkillRouter（skill body 是决定性信号，91.7% 注意力在 body）

**变更**:
1. `templates/base.md` — 将原 `## Overview` 改为 `## Skill Summary`，置于文档开头
2. Skill Summary 格式要求：≤5 句话，密集编码 what/when/who/not-for
3. `skill-framework.md §5 CREATE Phase 4 (GENERATE)` — 新增 Skill Summary 生成规则

---

## 五、参考文献

### 学术论文

- **EvoSkills**: [arxiv:2604.01687](https://arxiv.org/abs/2604.01687) — Self-Evolving Agent Skills via Co-Evolutionary Verification
- **SkillClaw**: [arxiv:2604.08377](https://arxiv.org/abs/2604.08377) — Let Skills Evolve Collectively with Agentic Evolver
- **SkillX**: [arxiv:2604.04804](https://arxiv.org/abs/2604.04804) — Automatically Constructing Skill Knowledge Bases
- **SkillRL**: [arxiv:2602.08234](https://arxiv.org/abs/2602.08234) — Evolving Agents via Recursive Skill-Augmented RL
- **SkillRouter**: [arxiv:2603.22455](https://arxiv.org/abs/2603.22455) — Retrieve-and-Rerank Skill Selection at Scale
- **Skills in the Wild**: [arxiv:2604.04323](https://arxiv.org/abs/2604.04323) — Benchmarking LLM Skill Usage in Realistic Settings
- **SkillProbe**: [arxiv:2603.21019](https://arxiv.org/abs/2603.21019) — Security Auditing for Agent Skill Marketplaces
- **SoK: Agentic Skills**: [arxiv:2602.20867](https://arxiv.org/abs/2602.20867) — Beyond Tool Use in LLM Agents
- **Agent Skills Survey**: [arxiv:2602.12430](https://arxiv.org/abs/2602.12430) — Architecture, Acquisition, Security

### 行业与社区

- **OWASP Agentic Applications Top 10** (2026): https://owasp.org/www-project-agentic-skills-top-10/
- **SKILL.md Pattern**: The SKILL.md Pattern: How to Write AI Agent Skills That Actually Work (Medium, 2026)
- **Claude Skill Best Practices**: https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices
- **SkillsBench Benchmark**: Used in EvoSkills, SkillRouter evaluations
- **agentskills.io Specification**: Open standard published by Anthropic, Dec 2025
- **SkillSieve**: [arxiv:2604.06550](https://arxiv.org/abs/2604.06550) — Hierarchical Triage for Malicious Skills
