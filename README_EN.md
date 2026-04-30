# SanZheng-LiuBu — Multi-Agent Extension

> A multi-role AI agent system modeled after the ancient Chinese imperial power-balancing structure, implementing a complete closed-loop from instruction input to execution feedback.

[中文](./README.md) | English

## Concept

**SanZheng-LiuBu** (Three Departments and Six Ministries) is a modular multi-agent Skill for **Claude Code** and **OpenCode** platforms. The system simulates the ancient Chinese imperial court's review-and-execute mechanism:

- **Emperor** — The user, the ultimate decision-maker
- **Zhongshu Sheng** (Department of State Affairs) — Primary API, drafts edicts (summarize/filter/formulate)
- **Menxia Sheng** (Chancellery) — Secondary API, reviews and vetoes (independent rejection power)
- **Shangshu Sheng** (Department of Executive Affairs) — Execution API, dispatches tasks and aggregates results
- **Six Ministries** — Six specialized APIs, each handling a distinct domain

```
Emperor → Zhongshu Sheng (draft edict) → Menxia Sheng (review) → Shangshu Sheng (dispatch) → Six Ministries (execute) → Emperor (decide)
```

## Six Ministries

| Ministry | Domain | Typical Tasks |
|----------|--------|---------------|
| Li Bu (Personnel) | Project management, version control, team collaboration | CI/CD, Git workflows, task scheduling |
| Hu Bu (Revenue) | Transactional data processing, cost estimation | Code statistics, dependency evaluation, budget analysis |
| Li Bu (Rites) | Documentation & code standards, style checks | Code formatting, comment writing, doc generation |
| Bing Bu (War) | Security analysis (defensive), testing & deployment | Vulnerability detection, automated testing, environment setup |
| Xing Bu (Justice) | Compliance auditing, error tracing, debugging | Fault diagnosis, log analysis, bug fixing |
| Gong Bu (Works) | Code writing, feature building, algorithm implementation | Core coding, feature development, API integration |

## File Structure

```
sanzheng-liubu/
├── SKILL.md                          # Core Skill definition
├── scripts/
│   └── liubu.py                      # Six Ministries coordination script (Python)
├── templates/
│   ├── settings.template.json        # OpenCode configuration template
│   └── .env.template                 # Environment variables template
├── opencode-config/
│   ├── opencode.jsonc                # Full OpenCode configuration example
│   └── agents/                       # Agent definitions for each institution
│       ├── zhongshu.md               # Zhongshu Sheng
│       ├── menxia.md                 # Menxia Sheng
│       ├── shangshu.md               # Shangshu Sheng
│       ├── libu.md                   # Li Bu (Personnel)
│       ├── hubu.md                   # Hu Bu (Revenue)
│       ├── libu-li.md                # Li Bu (Rites)
│       ├── bingbu.md                 # Bing Bu (War)
│       ├── xingbu.md                 # Xing Bu (Justice)
│       └── gongbu.md                 # Gong Bu (Works)
└── reference/
    ├── official-claude.md            # Claude Code Skill specification reference
    └── opencode-integration.md       # OpenCode integration reference
```

## Installation

### Prerequisites

- OpenCode or Claude Code installed
- At least 1 Anthropic API Key (can be shared across all agents, or configured separately)

### Project-level Installation (Recommended)

```bash
# Clone the repository
git clone https://github.com/shaluze2023-svg/sanzheng-liubu.git

# Copy the Skill to your project directory
cp -r sanzheng-liubu/ .claude/skills/sanzheng-liubu/

# Copy Agent definitions to OpenCode config directory
cp -r sanzheng-liubu/opencode-config/agents/ .opencode/agents/
```

### Global Installation

```bash
# Global Skill installation
cp -r sanzheng-liubu/ ~/.claude/skills/sanzheng-liubu/

# Global Agent installation
cp -r sanzheng-liubu/opencode-config/agents/ ~/.config/opencode/agents/
```

### Using opencode.json Configuration

Merge the contents of `templates/settings.template.json` into your project's `opencode.json` to configure all agents at once.

## Configuration

### Environment Variables

Copy `templates/.env.template` to `.env` and fill in your actual API Keys:

```bash
cp templates/.env.template .env
```

The minimum configuration requires only one `ANTHROPIC_API_KEY` shared by all agents. For enhanced independence, you can configure separate keys from different providers for Zhongshu Sheng and Menxia Sheng.

### Model Selection

| Agent | Recommended Model | Reason |
|-------|-------------------|--------|
| Zhongshu Sheng | claude-sonnet-4 | Needs high-quality edict drafting |
| Menxia Sheng | claude-sonnet-4 | Needs rigorous review judgment |
| Shangshu Sheng | claude-sonnet-4 | Needs complex task orchestration |
| Personnel / Revenue / Rites | claude-haiku-4 | Standard tasks, lightweight model suffices |
| War / Justice / Works | claude-sonnet-4 | Needs deep analysis or code generation |

## Usage Examples

### Feature Building

```
Emperor: "Add user registration with email verification"

→ Zhongshu Sheng: Drafts edict (API routes, controllers, email verification, data models, encryption)
→ Menxia Sheng: Approves (completeness/security/consistency all pass)
→ Shangshu Sheng: Dispatches
  → Gong Bu (Works): Database models & route configuration
  → Gong Bu + Li Bu (Rites): Email service & encryption strategy
  → Bing Bu (War): Security scan
  → Xing Bu (Justice): Unit tests
→ Results aggregated → Reported to Emperor
```

### Security Audit (Rejection Flow)

```
Emperor: "Scan all API endpoints and report security vulnerabilities"

→ Zhongshu Sheng: Drafts edict
→ Menxia Sheng: REJECTS — detects sensitive file read risk, suggests limiting scan scope
→ Emperor: Reviews rejection reason → Adjusts instruction → Resubmits
```

### Python Script Invocation

```bash
python scripts/liubu.py "Add user registration feature" --verbose
```

## Execution Closed-Loop

1. **Emperor issues instruction** → Received by Zhongshu Sheng
2. **Zhongshu Sheng summarizes/filters/restates** → Forms edict → Submitted to Menxia Sheng
3. **Menxia Sheng reviews**:
   - Rejected → Reason reported to Emperor
   - Approved → Edict forwarded to Shangshu Sheng
4. **Shangshu Sheng decomposes tasks** → Dispatches to appropriate ministries
5. **Ministries execute** → Results returned to Shangshu Sheng
6. **Shangshu Sheng aggregates** → Reported to Emperor
7. **Emperor decides** → May exercise final veto power

## Advanced Customization

- Refine ministry capabilities: Add specialized toolsets per ministry
- Add review layers: Insert additional checkpoints before/after Menxia Sheng
- Optimize dynamic routing: Use Claude Code Router for intelligent dispatch
- Integrate MCP servers: Extend toolchains with external services and data sources
- Create custom OpenCode plugins: Develop multi-layer plugins per the plugin interface spec

## Troubleshooting

| Issue | Possible Cause | Solution |
|-------|----------------|----------|
| Menxia Sheng rejects too frequently | Poor edict quality | Increase Zhongshu Sheng temperature, refine system prompt |
| Ministries misassigned | Classification logic insufficient | Adjust keyword mappings or add typical examples |
| Slow API calls | Too many model dependencies | Use smaller models or optimize requests |
| Rejections lack specific reasons | Menxia Sheng prompt insufficient | Enforce "rejections must include reasons" |

## License

[MIT License](./LICENSE)

## Related Resources

- [Claude Code Skills Official Documentation](https://docs.anthropic.com/en/docs/claude-code/skills)
- [OpenCode Official Website](https://opencode.ai)
- [OpenCode Plugin Creation Guide](https://opencode.ai/docs/plugins)