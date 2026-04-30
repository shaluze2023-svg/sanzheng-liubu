# Claude Code Skill 规范参考

## SKILL.md 格式规范

SKILL.md 是 Skill 的核心入口文件，由两部分组成：

1. **YAML Frontmatter**（`---` 之间）：元数据，控制 Skill 的发现和加载行为
2. **Markdown 正文**：指令内容，Claude 在 Skill 被调用时读取

### Frontmatter 字段

| 字段 | 必填 | 说明 |
|------|------|------|
| `name` | 否 | Skill 显示名，省略则用目录名。仅限小写字母、数字、连字符（最长64字符） |
| `description` | 推荐 | Skill 功能描述，Claude 用于判断何时使用。与 when_to_use 合计截断至 1536 字符 |
| `when_to_use` | 否 | 额外触发上下文，追加到 description |
| `argument-hint` | 否 | 自动补全提示，如 `[issue-number]` |
| `arguments` | 否 | 命名位置参数，用于 `$name` 替换 |
| `disable-model-invocation` | 否 | `true` 阻止 Claude 自动加载，仅手动 `/name` 触发 |
| `user-invocable` | 否 | `false` 从 `/` 菜单隐藏，仅 Claude 可调用 |
| `allowed-tools` | 否 | Skill 激活时免确认的工具列表 |
| `model` | 否 | Skill 激活时覆盖的模型 |
| `effort` | 否 | 覆盖努力级别：low/medium/high/xhigh/max |
| `context` | 否 | 设为 `fork` 在子代理中运行 |
| `agent` | 否 | `context: fork` 时使用的子代理类型 |
| `hooks` | 否 | Skill 生命周期钩子 |
| `paths` | 否 | 限制 Skill 激活的文件 glob 模式 |
| `shell` | 否 | Shell 类型：bash（默认）或 powershell |

### 字符串替换变量

| 变量 | 说明 |
|------|------|
| `$ARGUMENTS` | 所有参数 |
| `$ARGUMENTS[N]` / `$N` | 按索引访问参数 |
| `$name` | 命名参数（需在 arguments 中声明） |
| `${CLAUDE_SESSION_ID}` | 当前会话 ID |
| `${CLAUDE_SKILL_DIR}` | Skill 目录路径 |

### 动态上下文注入

使用 `` !`command` `` 语法在 Skill 加载时执行 Shell 命令，输出替换占位符：

```markdown
当前分支: !`git branch --show-current`
```

### 渐进式加载

- 启动时仅加载所有 Skill 的 name + description
- SKILL.md 正文仅在 Skill 被调用时加载
- 引用文件（通过 `${CLAUDE_SKILL_DIR}/path` 引用）仅在需要时读取

## Skill 存储位置

| 级别 | 路径 | 作用范围 |
|------|------|----------|
| 企业 | 管理设置 | 组织内所有用户 |
| 个人 | `~/.claude/skills/<name>/SKILL.md` | 所有项目 |
| 项目 | `.claude/skills/<name>/SKILL.md` | 当前项目 |
| 插件 | `<plugin>/skills/<name>/SKILL.md` | 插件启用处 |

## 最佳实践

1. **简洁为王**：Claude 本身很聪明，只添加 Claude 不知道的信息
2. **设置适当的自由度**：根据任务脆弱性调整指令的具体程度
3. **测试所有计划使用的模型**：不同模型对 Skill 的响应可能不同
4. **使用渐进式加载**：大文件放在引用目录中，SKILL.md 只做概述
5. **description 要具体**：包含功能和触发场景，便于 Claude 从 100+ Skill 中选择