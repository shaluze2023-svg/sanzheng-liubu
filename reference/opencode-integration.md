# OpenCode 集成参考

## OpenCode Agent 配置

OpenCode 支持两种方式定义 agent：

### JSON 配置（opencode.json）

```json
{
  "agent": {
    "agent-name": {
      "description": "Agent 描述",
      "mode": "primary|subagent",
      "model": "anthropic/claude-sonnet-4-20250514",
      "prompt": "系统提示词",
      "permission": {
        "edit": "allow|ask|deny",
        "bash": "allow|ask|deny"
      }
    }
  }
}
```

### Markdown 配置（.opencode/agents/）

在 `~/.config/opencode/agents/` 或 `.opencode/agents/` 目录下放置 markdown 文件：

```markdown
---
description: Agent 描述
mode: subagent
model: anthropic/claude-sonnet-4-20250514
temperature: 0.3
permission:
  edit: deny
  bash: deny
---

系统提示词内容...
```

## Agent 类型

- **primary**: 主代理，用户通过 Tab 键切换
- **subagent**: 子代理，主代理通过 @ 提及调用

## 内置 Agent

| Agent | 类型 | 说明 |
|-------|------|------|
| Build | primary | 默认代理，所有工具可用 |
| Plan | primary | 规划代理，编辑和 bash 默认 ask |
| General | subagent | 通用研究代理 |
| Explore | subagent | 只读代码探索代理 |

## Claude Code Skill 与 OpenCode 兼容

Claude Code Skill 的 SKILL.md 格式与 OpenCode 的 agent markdown 格式兼容：
- YAML frontmatter 字段映射到 OpenCode agent 配置
- Markdown 正文映射到 agent 的系统提示词
- `.claude/skills/` 目录可被 OpenCode 识别

## 安装三省六部制 Skill 到 OpenCode

### 方法 1：项目级安装

```bash
# 将 Skill 复制到项目目录
cp -r sanzheng-liubu/ .claude/skills/sanzheng-liubu/

# 将 agent 定义复制到 OpenCode 配置目录
cp -r sanzheng-liubu/opencode-config/agents/ .opencode/agents/
```

### 方法 2：全局安装

```bash
# Skill 全局安装
cp -r sanzheng-liubu/ ~/.claude/skills/sanzheng-liubu/

# Agent 全局安装
cp -r sanzheng-liubu/opencode-config/agents/ ~/.config/opencode/agents/
```

### 方法 3：使用 opencode.json 配置

将 `templates/settings.template.json` 的内容合并到项目的 `opencode.json` 中。

## 多提供商配置

OpenCode 支持 75+ 模型提供商，可以为不同 agent 配置不同提供商：

```json
{
  "provider": {
    "anthropic": {
      "options": { "apiKey": "{env:ANTHROPIC_API_KEY}" }
    },
    "openai": {
      "options": { "apiKey": "{env:OPENAI_API_KEY}" }
    },
    "google": {
      "options": { "apiKey": "{env:GOOGLE_API_KEY}" }
    }
  }
}
```

## 变量替换

OpenCode 配置支持环境变量和文件内容替换：

- `{env:VARIABLE_NAME}` — 替换为环境变量值
- `{file:path/to/file}` — 替换为文件内容