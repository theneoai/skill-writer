# Skill Inheritance Design

**Date**: 2026-03-28
**Status**: Approved
**Parent Spec**: N/A (new feature)

## Overview

本项目(skill)是创建和优化其他skill的系统。被创建/优化的skill应继承父skill的核心设计原则，实现最小化继承机制。

## Design Principles

- **最小化继承**: 只继承核心约束性内容，不限制子skill的灵活性
- **显式继承**: 通过 `--extends` 参数显式指定，不自动继承
- **可覆盖**: 子skill已有内容优先，父内容仅作为默认值

## Inherited Content

| 章节 | 来源 | 行为 |
|------|------|------|
| §1.1 Identity | 父skill | 完全复制 |
| Red Lines | 父skill §1.1 | 完全复制 |
| §6 Self-Evolution | 父skill | 完全复制 |

## Implementation

### 1. Modified Files

**`engine/agents/creator.sh`**:
- 新增 `extract_inherited_sections()` 函数
- 新增 `inherit_sections()` 函数

**`scripts/create-skill.sh`**:
- 新增 `--extends` / `-e` 参数
- 解析父skill路径并传递给 orchestrator

### 2. New Functions

```bash
extract_inherited_sections() {
    local parent_skill="$1"
    # 提取 §1.1 Identity (从 "## §1.1" 到下一个 "##" 之前)
    # 提取 Red Lines (严禁|Red Lines 段落)
    # 提取 §6 Self-Evolution (从 "## §6" 到文件末尾或下一个顶级章节)
}

inherit_sections() {
    local parent_skill="$1"
    local target_file="$2"
    # 合并继承内容到目标文件
    # 冲突处理: 子内容优先
}
```

### 3. CLI Interface

```bash
./scripts/create-skill.sh "创建code review skill" [--extends parent-skill] [output_path] [tier]

Examples:
  ./scripts/create-skill.sh "创建code review skill"
  ./scripts/create-skill.sh "创建code review skill" --extends skill
  ./scripts/create-skill.sh "创建code review skill" -e skill ./my-skill.md GOLD
```

### 4. Workflow

1. 解析 `--extends` 参数获取父skill路径
2. 如果父skill存在，提取继承章节
3. 创建子skill文件，先填充继承内容
4. 后续章节由creator生成（子内容覆盖父内容）
5. lean验证确保质量

## Edge Cases

| 场景 | 处理 |
|------|------|
| 父skill不存在 | 警告+跳过继承，继续创建 |
| 父skill无§6 | 只继承§1.1+Red Lines |
| 子skill已有同名章节 | 保留子内容，不覆盖 |
| 无--extends参数 | 正常创建，无继承 |

## Security Considerations

- 继承内容仅来自用户指定的父skill路径
- 不执行父skill中的任何代码
- 仅提取纯文本章节内容
