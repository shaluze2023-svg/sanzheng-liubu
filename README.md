# 三省六部制 — 多角色代理扩展

> 模拟中国古代朝廷权力制衡结构的多角色 AI 代理系统，实现从指令输入到执行反馈的完整闭环。

[English](./README_EN.md) | 中文

## 概念

「三省六部制」是一套模块化的多角色代理 Skill，适用于 **Claude Code** 和 **OpenCode** 平台。系统模拟古代朝廷的三省审核与六部分工机制：

- **皇帝/天子** — 用户，最终裁决者
- **中书省** — 主 API，决策起草（总结/筛选/拟令）
- **门下省** — 次 API，审核复核（拥有独立驳回权）
- **尚书省** — 执行 API，任务分发与结果汇总
- **六部** — 六个专用 API，各司其职

```
皇帝 → 中书省(拟令) → 门下省(审核) → 尚书省(分发) → 六部(执行) → 皇帝(裁决)
```

## 六部分工

| 部门 | 职责领域 | 典型任务 |
|------|----------|----------|
| 吏部 | 项目管理、版本控制、团队协作 | CI/CD、Git 工作流、任务排期 |
| 户部 | 事务性数据处理、成本核算 | 代码量统计、依赖评估、预算分析 |
| 礼部 | 文档与代码规范、风格检查 | 代码格式修正、注释撰写、文档生成 |
| 兵部 | 安全性分析（防御型）、测试部署 | 漏洞检测、自动化测试、环境部署 |
| 刑部 | 合规性审计、错误溯源、调试 | 故障排查、日志分析、错误修复 |
| 工部 | 代码编写、功能构建、算法实现 | 底层编码、功能开发、API 集成 |

## 文件结构

```
sanzheng-liubu/
├── SKILL.md                          # Skill 核心定义文件
├── scripts/
│   └── liubu.py                      # 六部 API 协调脚本（Python）
├── templates/
│   ├── settings.template.json        # OpenCode 配置模板
│   └── .env.template                 # 环境变量模板
├── opencode-config/
│   ├── opencode.jsonc                # OpenCode 完整配置示例
│   └── agents/                       # 各机构 Agent 定义
│       ├── zhongshu.md               # 中书省
│       ├── menxia.md                 # 门下省
│       ├── shangshu.md               # 尚书省
│       ├── libu.md                   # 吏部
│       ├── hubu.md                   # 户部
│       ├── libu-li.md                # 礼部
│       ├── bingbu.md                 # 兵部
│       ├── xingbu.md                 # 刑部
│       └── gongbu.md                 # 工部
└── reference/
    ├── official-claude.md            # Claude Code Skill 规范参考
    └── opencode-integration.md       # OpenCode 集成参考
```

## 安装

### 前提条件

- 已安装 OpenCode 或 Claude Code
- 至少 1 个可用的 API Key（支持 Anthropic / OpenAI / Google Gemini 三种格式，可混用）

### 项目级安装（推荐）

```bash
# 克隆仓库
git clone https://github.com/shaluze2023-svg/sanzheng-liubu.git

# 将 Skill 复制到项目目录
cp -r sanzheng-liubu/ .claude/skills/sanzheng-liubu/

# 将 Agent 定义复制到 OpenCode 配置目录
cp -r sanzheng-liubu/opencode-config/agents/ .opencode/agents/
```

### 全局安装

```bash
# Skill 全局安装
cp -r sanzheng-liubu/ ~/.claude/skills/sanzheng-liubu/

# Agent 全局安装
cp -r sanzheng-liubu/opencode-config/agents/ ~/.config/opencode/agents/
```

### 使用 opencode.json 配置

将 `templates/settings.template.json` 的内容合并到项目的 `opencode.json` 中，一次性配置所有机构。

## 配置

### 环境变量

复制 `templates/.env.template` 为 `.env`，填入实际的 API Keys：

```bash
cp templates/.env.template .env
```

最少配置只需一个 `ANTHROPIC_API_KEY`，所有机构共用。也支持 OpenAI 和 Google Gemini 格式，可为不同机构配置不同提供商的 Key 以增强独立性。

### 多提供商支持

本项目支持三种 API 格式，可在 `.env` 中按需配置：

| 提供商 | 环境变量 | 支持的模型示例 |
|--------|----------|----------------|
| Anthropic | `ANTHROPIC_API_KEY` | claude-4-6-opus |
| OpenAI | `OPENAI_API_KEY` + `OPENAI_BASE_URL` | gpt-4o, gpt-4o-mini |
| Google Gemini | `GOOGLE_API_KEY` | gemini-2.5-pro, gemini-2.5-flash |

OpenAI 格式兼容所有 OpenAI 兼容的第三方服务（如 DeepSeek、Azure OpenAI 等），只需修改 `OPENAI_BASE_URL` 即可。

### 模型选择

| 机构 | 推荐模型 | 说明 |
|------|----------|------|
| 中书省 | claude-4-6-opus | 需要高质量拟令起草 |
| 门下省 | claude-4-6-opus | 需要严谨审核判断 |
| 尚书省 | claude-4-6-opus | 需要复杂任务编排 |
| 吏部 | claude-4-6-opus | 项目管理与版本控制 |
| 户部 | claude-4-6-opus | 事务数据处理与成本核算 |
| 礼部 | claude-4-6-opus | 代码规范与文档生成 |
| 兵部 | claude-4-6-opus | 安全分析与测试部署 |
| 刑部 | claude-4-6-opus | 合规审计与故障调试 |
| 工部 | claude-4-6-opus | 代码编写与功能构建 |

> 也可按需将各机构模型替换为 `openai/gpt-4o` 或 `google/gemini-2.5-pro`，在 `opencode.json` 或 agent 配置中修改 `model` 字段即可。

## 使用示例

### 功能构建

```
皇帝：「为项目添加用户注册功能，支持邮箱验证」

→ 中书省：形成拟令（API路由、控制器、邮箱验证、数据模型、加密策略）
→ 门下省：审核通过（完整性/安全性/一致性均合格）
→ 尚书省：分发执行
  → 工部：数据库模型 & 路由配置
  → 工部+礼部：邮箱服务 & 加密策略
  → 兵部：安全扫描
  → 刑部：单元测试
→ 结果汇总 → 上报皇帝
```

### 安全审计（驳回流程）

```
皇帝：「扫描项目所有 API 端点，报告安全漏洞」

→ 中书省：形成拟令
→ 门下省：驳回 — 发现敏感文件读取风险，建议限定扫描路径
→ 皇帝：看到驳回理由 → 调整指令 → 重新提交
```

### Python 脚本调用

```bash
python scripts/liubu.py "为项目添加用户注册功能" --verbose
```

## 执行流程闭环

1. **皇帝下达指令** → 中书省接收
2. **中书省总结/筛选/重述** → 形成拟令 → 提交门下省
3. **门下省二次审核**：
   - 驳回 → 附理由反馈皇帝
   - 通过 → 拟令下发尚书省
4. **尚书省拆解任务** → 按类别分发给六部
5. **对应部门执行** → 结果返回尚书省
6. **尚书省汇总** → 上报皇帝
7. **皇帝裁决** → 可行使最终驳回权

## 进阶自定义

- 细化六部能力组合：为各部增加专属工具集
- 增加审核层级：在门下省前后加入更多审核点
- 优化动态路由：使用 Claude Code Router 实现智能分类调度
- 与 MCP 服务器集成：扩展工具链，调用外部服务与数据源
- 创建自定义 OpenCode 插件：依据插件接口规范开发多层插件

## 故障排查

| 问题 | 可能原因 | 解决办法 |
|------|----------|----------|
| 门下省驳回过频繁 | 拟令质量不够 | 调高中书省温度，细化系统提示词 |
| 六部分配不准 | 分类逻辑不够 | 调整关键词映射或增加典型示例 |
| API 调用速度慢 | 模型依赖多 | 使用更小的模型或优化请求 |
| 驳回无具体原因 | 门下省提示词不足 | 强制要求"驳回必须附带理由" |

## 许可证

[MIT License](./LICENSE)

## 相关资源

- [Claude Code Skills 官方文档](https://docs.anthropic.com/en/docs/claude-code/skills)
- [OpenCode 官方网站](https://opencode.ai)
- [OpenCode 插件创建指南](https://opencode.ai/docs/plugins)