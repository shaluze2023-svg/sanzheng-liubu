# 三省六部制 — OpenCode 集成指南

## 安装方式

### 方式一：作为 Claude Code Skill 使用

将 `sanzheng-liubu` 目录复制到以下任一位置：

```bash
# 个人全局 Skill
cp -r sanzheng-liubu ~/.claude/skills/sanzheng-liubu

# 项目级 Skill
cp -r sanzheng-liubu .claude/skills/sanzheng-liubu
```

### 方式二：作为 OpenCode Agent 配置使用

1. 将 `opencode-config/agents/` 下的 agent 定义文件复制到 OpenCode 配置目录：

```bash
# 全局 agents
cp opencode-config/agents/*.md ~/.config/opencode/agents/

# 项目级 agents
cp opencode-config/agents/*.md .opencode/agents/
```

2. 将 `settings.template.json` 中的 agent 配置合并到你的 `opencode.json` 中。

3. 配置环境变量：

```bash
cp templates/.env.template .env
# 编辑 .env 填入实际 API Keys
```

## OpenCode Agent 配置详解

OpenCode 支持通过 JSON 或 Markdown 两种方式定义 Agent。

### JSON 配置方式

在 `opencode.json` 中添加 `agent` 字段：

```jsonc
{
  "$schema": "https://opencode.ai/config.json",
  "model": "anthropic/claude-sonnet-4-20250514",
  "agent": {
    "zhongshu": {
      "description": "中书省·决策起草机构",
      "mode": "primary",
      "model": "anthropic/claude-sonnet-4-20250514",
      "prompt": "你是中书省·决策起草机构...",
      "permission": { "edit": "ask", "bash": "ask" }
    },
    "menxia": {
      "description": "门下省·审核复核机构",
      "mode": "subagent",
      "model": "anthropic/claude-sonnet-4-20250514",
      "prompt": "你是门下省·审核复核机构...",
      "permission": { "edit": "deny", "bash": "deny" }
    }
    // ... 其他 agent
  }
}
```

### Markdown 配置方式

在 `~/.config/opencode/agents/` 或 `.opencode/agents/` 中创建 `.md` 文件：

```markdown
---
description: 中书省·决策起草机构
mode: primary
model: anthropic/claude-sonnet-4-20250514
permission:
  edit: ask
  bash: ask
---

你是中书省·决策起草机构。你的职责是对用户（皇帝）输入的指令进行总结、概括、筛选和重述...
```

## Agent 角色与权限设计

| 角色 | mode | 权限 | 说明 |
|------|------|------|------|
| 中书省 | primary | edit:ask, bash:ask | 可浏览代码，修改需确认 |
| 门下省 | subagent | edit:deny, bash:deny | 只读审核，不可修改 |
| 尚书省 | primary | edit:allow, bash:allow | 完全执行权限 |
| 吏部 | subagent | edit:ask, bash:ask | 项目管理操作 |
| 户部 | subagent | edit:deny, bash:ask | 只读分析 |
| 礼部 | subagent | edit:allow, bash:deny | 可编辑代码格式 |
| 兵部 | subagent | edit:ask, bash:allow | 可执行测试部署 |
| 刑部 | subagent | edit:allow, bash:allow | 可修复和调试 |
| 工部 | subagent | edit:allow, bash:allow | 完全开发权限 |

## 多提供商配置

三省六部制支持混合使用不同 AI 提供商，增强权力制衡：

```jsonc
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
  },
  "agent": {
    "zhongshu": {
      "model": "anthropic/claude-sonnet-4-20250514",
      // ...
    },
    "menxia": {
      "model": "openai/gpt-4o",  // 使用不同提供商增强独立性
      // ...
    }
  }
}
```

## 使用流程

1. 启动 OpenCode：`opencode`
2. 使用 Tab 键切换到「中书省」agent
3. 以皇帝身份下达指令
4. 中书省形成拟令后，@menxia 调用门下省审核
5. 审核通过后，@shangshu 调用尚书省执行
6. 尚书省根据任务类型 @mention 对应部门执行
7. 结果汇总后反馈给皇帝

## 最小化配置（2个 API Key）

如果 API Key 数量有限，可使用以下最小化方案：

- **中书省 + 门下省**：共用 1 个 Key（Anthropic）
- **尚书省 + 六部**：共用 1 个 Key（可以是同一提供商的不同模型）

```jsonc
{
  "model": "anthropic/claude-sonnet-4-20250514",
  "small_model": "anthropic/claude-haiku-4-20250514",
  "provider": {
    "anthropic": {
      "options": { "apiKey": "{env:ANTHROPIC_API_KEY}" }
    }
  }
}
```

六部可统一使用 `small_model`（haiku），三省使用主模型（sonnet），以降低成本。