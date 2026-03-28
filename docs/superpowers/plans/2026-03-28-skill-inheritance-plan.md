# Skill Inheritance Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 为 skill 系统添加最小化继承机制，子skill可从父skill继承 §1.1 Identity + Red Lines + §6 Self-Evolution

**Architecture:** 通过 `--extends` 参数指定父skill，creator.sh 提取并注入继承章节到子skill

**Tech Stack:** Bash, jq, sed

---

## File Structure

- Modify: `engine/agents/creator.sh` - 添加继承逻辑
- Modify: `scripts/create-skill.sh` - 添加 `--extends` 参数
- Test: `scripts/create-skill.sh --extends skill` 验证继承

---

## Task 1: Add inheritance extraction to creator.sh

**Files:**
- Modify: `engine/agents/creator.sh:1-91`

- [ ] **Step 1: 添加 extract_inherited_sections 函数**

在 `creator_init_skill_file()` 函数之后添加：

```bash
extract_inherited_sections() {
    local parent_skill="$1"
    
    if [[ ! -f "$parent_skill" ]]; then
        echo "WARNING: Parent skill not found: $parent_skill" >&2
        return 1
    fi
    
    local content=""
    
    # 提取 §1.1 Identity (从 "## §1.1" 到下一个 "##" 之前)
    local identity
    identity=$(sed -n '/^## §1\.1\|^## 1\.1 Identity\|^# .*$/,/^## §[0-9]\|^## [0-9]\.[0-9]/p' "$parent_skill" | head -n -1)
    if [[ -n "$identity" ]]; then
        content+="$identity"$'\n'
    fi
    
    # 提取 Red Lines (严禁|Red Lines 段落)
    local redlines
    redlines=$(sed -n '/^**Red Lines\|^## Red Lines\|严禁/p' "$parent_skill" | head -10)
    if [[ -n "$redlines" ]]; then
        content+="$redlines"$'\n'
    fi
    
    # 提取 §6 Self-Evolution (从 "## §6" 到文件末尾或下一个顶级章节)
    local evolution
    evolution=$(sed -n '/^## §6\|^## 6\./p' "$parent_skill")
    if [[ -n "$evolution" ]]; then
        content+="$evolution"$'\n'
    fi
    
    echo "$content"
}
```

- [ ] **Step 2: 添加 apply_inheritance 函数**

在 `extract_inherited_sections` 之后添加：

```bash
apply_inheritance() {
    local parent_skill="$1"
    local target_file="$2"
    
    local inherited
    inherited=$(extract_inherited_sections "$parent_skill")
    
    if [[ -z "$inherited" ]]; then
        echo "No inheritance content found"
        return 1
    fi
    
    # 检查目标文件是否已有内容
    if [[ -s "$target_file" ]]; then
        echo "Target file already has content, inheritance skipped (child content priority)"
        return 0
    fi
    
    echo "$inherited" >> "$target_file"
    echo "" >> "$target_file"
}
```

- [ ] **Step 3: 在 creator_init_skill_file 中调用 apply_inheritance**

修改 `creator_init_skill_file` 函数，在创建初始内容后检查继承：

```bash
creator_init_skill_file() {
    local skill_file="$1"
    local skill_name="$2"
    local parent_skill="${3:-}"
    
    local content="# ${skill_name}

> **Version**: 0.1.0
> **Date**: $(date +%Y-%m-%d)
> **Status**: DRAFT

---

"
    
    echo "$content" > "$skill_file"
    
    # 如果指定了父skill，应用继承
    if [[ -n "$parent_skill" ]]; then
        apply_inheritance "$parent_skill" "$skill_file"
    fi
}
```

- [ ] **Step 4: Commit**

```bash
git add engine/agents/creator.sh
git commit -m "feat: 添加skill继承机制 - extract/apply_inheritance函数"
```

---

## Task 2: Add --extends parameter to create-skill.sh

**Files:**
- Modify: `scripts/create-skill.sh:1-61`

- [ ] **Step 1: 添加参数解析逻辑**

修改 `main()` 函数，在开头添加：

```bash
main() {
    if [[ $# -lt 1 ]]; then
        show_usage
        exit 1
    fi
    
    local description=""
    local output_path=""
    local tier="BRONZE"
    local parent_skill=""
    
    # 解析参数
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --extends|-e)
                parent_skill="$2"
                shift 2
                ;;
            --tier|-t)
                tier="$2"
                shift 2
                ;;
            --help|-h)
                show_usage
                exit 0
                ;;
            -*)
                echo "Unknown option: $1"
                show_usage
                exit 1
                ;;
            *)
                if [[ -z "$description" ]]; then
                    description="$1"
                elif [[ -z "$output_path" ]]; then
                    output_path="$1"
                else
                    tier="$1"
                fi
                shift
                ;;
        esac
    done
    
    if [[ -z "$description" ]]; then
        echo "Error: description required"
        show_usage
        exit 1
    fi
    
    local skill_name
    skill_name=$(echo "$description" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]+/-/g' | sed 's/^-//;s/-$//')
    
    if [[ -z "$output_path" ]]; then
        output_path="${PROJECT_ROOT}/${skill_name}.md"
    fi
    
    echo "Creating skill: $skill_name"
    echo "Target tier: $tier"
    echo "Output: $output_path"
    [[ -n "$parent_skill" ]] && echo "Parent skill: $parent_skill"
    echo ""
    
    # 传递 parent_skill 给 orchestrator
    PARENT_SKILL="$parent_skill" TARGET_TIER="$tier" "${PROJECT_ROOT}/engine/orchestrator.sh" "$description" "$output_path"
    
    echo ""
    echo "Skill created: $output_path"
}
```

- [ ] **Step 2: 更新 show_usage**

```bash
show_usage() {
    cat <<EOF
Usage: $(basename "$0") "skill description" [options] [output_path] [tier]

Options:
    -e, --extends PARENT   Inherit from parent skill (optional)
    -t, --tier TIER        Target tier: GOLD, SILVER, BRONZE (default: BRONZE)
    -h, --help             Show this help

Examples:
    $(basename "$0") "Create a code review skill"
    $(basename "$0") "Create a code review skill" --extends skill
    $(basename "$0") "Create a code review skill" -e skill ./my-skill.md GOLD
EOF
}
```

- [ ] **Step 3: Commit**

```bash
git add scripts/create-skill.sh
git commit -m "feat: create-skill.sh添加--extends参数支持继承"
```

---

## Task 3: Integration - pass parent_skill to orchestrator

**Files:**
- Modify: `engine/orchestrator.sh` 或 `engine/orchestrator/_workflow.sh`

- [ ] **Step 1: 在 orchestrator 中接收 PARENT_SKILL 环境变量**

在 `engine/orchestrator.sh` 或 workflow init 中添加对 `PARENT_SKILL` 的处理：

```bash
# 在 workflow_init 或 orchestrator.sh 中
if [[ -n "$PARENT_SKILL" ]]; then
    # 解析父skill路径
    if [[ "$PARENT_SKILL" == *".md"* ]]; then
        PARENT_SKILL_PATH="$PARENT_SKILL"
    else
        # 查找本地skill
        PARENT_SKILL_PATH="${PROJECT_ROOT}/${PARENT_SKILL}.md"
    fi
    
    if [[ -f "$PARENT_SKILL_PATH" ]]; then
        echo "Using parent skill: $PARENT_SKILL_PATH"
        export PARENT_SKILL_PATH
    fi
fi
```

- [ ] **Step 2: 在 workflow_init 中传递 parent_skill**

修改 `workflow_init()` 调用，使其接收 parent_skill 参数：

```bash
workflow_init() {
    local user_prompt="$1"
    local output_file="$2"
    local parent_skill="${3:-}"
    
    # ... 现有逻辑 ...
    
    if [[ -n "$parent_skill" ]]; then
        creator_init_skill_file "$TARGET_SKILL_FILE" "$(basename "$TARGET_SKILL_FILE" .md)" "$parent_skill"
    fi
}
```

- [ ] **Step 3: Commit**

```bash
git add engine/orchestrator.sh engine/orchestrator/_workflow.sh
git commit -m "feat: orchestrator支持PARENT_SKILL环境变量传递"
```

---

## Task 4: Test inheritance functionality

**Files:**
- Test: `scripts/create-skill.sh --extends skill`

- [ ] **Step 1: 运行测试**

```bash
cd /Users/lucas/Documents/Projects/skill
./scripts/create-skill.sh "test inheritance skill" --extends skill ./test-inherit.md
```

- [ ] **Step 2: 验证输出**

检查 `test-inherit.md` 是否包含：
- §1.1 Identity (来自skill)
- Red Lines (严禁)
- §6 Self-Evolution (来自skill)

```bash
grep -c "§1.1\|Identity\|严禁\|Self-Evolution" ./test-inherit.md
```

预期: 至少3处匹配

- [ ] **Step 3: 清理测试文件**

```bash
rm -f ./test-inherit.md
git add -A
git commit -m "test: 验证skill继承功能"
```

---

## Verification Checklist

- [ ] `extract_inherited_sections` 正确提取 §1.1 + Red Lines + §6
- [ ] `apply_inheritance` 在子文件为空时注入内容
- [ ] `create-skill.sh -e skill` 正确传递父skill路径
- [ ] lean-orchestrator 验证继承后的skill仍达到目标等级
- [ ] 无父skill时正常创建，无继承
