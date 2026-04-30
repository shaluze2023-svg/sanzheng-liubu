# Claude Code Skill 规范参考

## Skill 文件结构

每个 Skill 是一个目录，以 `SKILL.md` 作为入口文件：

```
skill-name/
├── SKILL.md              # 主指令文件（必需）
├── scripts/              # 脚本文件（可选）
├── templates/            # 模板文件（可选）
└── reference/            # 参考文档（可选）
```

## SKILL.md 格式

SKILL.md 包含两部分：YAML frontmatter 和 markdown 内容。

### Frontmatter 字段

| 字段 | 必需 | 说明 |
|------|------|------|
| `name` | 否 | Skill 显示名，省略则使用目录名。仅允许小写字母、数字和连字符（最长64字符） |
| `description` | 推荐 | Skill 功能描述和触发时机，Claude 用此决定何时加载 |
| `when_to_use` | 否 | 额外的触发上下文，附加到 description 中 |
| `argument-hint` | 否 | 自动补全时显示的参数提示 |
| `arguments` | 否 | 命名参数，用于 `$name` 替换 |
| `disable-model-invocation` | 否 | 设为 true 防止 Claude 自动加载 |
| `user-invocable` | 否 | 设为 false 从 / 菜单隐藏 |
| `allowed-tools` | 否 | Skill 活跃时免审批的工具列表 |
| `model` | 否 | Skill 活跃时使用的模型覆盖 |
| `effort` | 否 | 努力级别覆盖 |
| `context` | 否 | 设为 fork 在子代理中运行 |
| `agent` | 否 | context: fork 时使用的子代理类型 |
| `paths` | 否 | 限制 Skill 激活的 glob 模式 |

### 字符串替换

| 变量 | 说明 |
|------|------|
| `$ARGUMENTS` | 所有传入参数 |
| `$ARGUMENTS[N]` / `$N` | 按位置访问参数 |
| `$name` | 命名参数 |
| `${CLAUDE_SESSION_ID}` | 当前会话 ID |
| `${CLAUDE_SKILL_DIR}` | Skill 目录路径 |

### Shell 命令注入

使用 `!`command`` 语法在 Skill 内容发送前执行 shell 命令，输出替换占位符。

## Skill 存储位置

| 位置 | 路径 | 适用范围 |
|------|------|----------|
| 个人 | `~/.claude/skills/<name>/SKILL.md` | 所有项目 |
| 项目 | `.claude/skills/<name>/SKILL.md` | 当前项目 |
| 插件 | `<plugin>/skills/<name>/SKILL.md` | 插件启用处 |

## 渐进式加载

- 启动时仅加载所有 Skill 的元数据（name + description）
- SKILL.md 正文仅在 Skill 被触发时加载
- 参考文件等仅在 SKILL.md 中引用时才加载

## 最佳实践

1. 保持简洁 — Claude 已经很聪明，只添加它不知道的信息
2. 设置适当的自由度 — 脆弱任务用低自由度（脚本），灵活任务用高自由度（文字指令）
3. 在所有计划使用的模型上测试
4. description 用第三人称编写，包含关键词
5. 使用渐进式披露 — SKILL.md 作为概览，指向详细参考文件