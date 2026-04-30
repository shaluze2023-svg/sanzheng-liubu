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
│   ├── liubu.py                      # Six Ministries coordination script (Python)
│   └── web_viewer.py                 # Web visualization viewer (port 8080)
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
- At least 1 API Key (supports Anthropic / OpenAI / Google Gemini — can be mixed)

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

The minimum configuration requires only one `ANTHROPIC_API_KEY` shared by all agents. OpenAI and Google Gemini formats are also supported — you can configure different providers for different agents to enhance independence.

### Multi-Provider Support

This project supports three API formats, configurable in `.env`:

| Provider | Environment Variables | Supported Models |
|----------|----------------------|------------------|
| Anthropic | `ANTHROPIC_API_KEY` | claude-4-6-opus |
| OpenAI | `OPENAI_API_KEY` + `OPENAI_BASE_URL` | gpt-4o, gpt-4o-mini |
| Google Gemini | `GOOGLE_API_KEY` | gemini-2.5-pro, gemini-2.5-flash |

The OpenAI format is compatible with any OpenAI-compatible third-party service (e.g., DeepSeek, Azure OpenAI) — simply modify `OPENAI_BASE_URL`.

### Model Selection

| Agent | Recommended Model | Reason |
|-------|-------------------|--------|
| Zhongshu Sheng | claude-4-6-opus | Needs high-quality edict drafting |
| Menxia Sheng | claude-4-6-opus | Needs rigorous review judgment |
| Shangshu Sheng | claude-4-6-opus | Needs complex task orchestration |
| Li Bu (Personnel) | claude-4-6-opus | Project management & version control |
| Hu Bu (Revenue) | claude-4-6-opus | Transactional data & cost estimation |
| Li Bu (Rites) | claude-4-6-opus | Code standards & documentation |
| Bing Bu (War) | claude-4-6-opus | Security analysis & testing |
| Xing Bu (Justice) | claude-4-6-opus | Compliance auditing & debugging |
| Gong Bu (Works) | claude-4-6-opus | Code writing & feature building |

> You can also replace any agent's model with `openai/gpt-4o` or `google/gemini-2.5-pro` by modifying the `model` field in `opencode.json` or agent config files.

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

### Web Visualization Viewer

Start a local web server to view the agent workflow as a hierarchical tree in your browser:

```bash
# Default port 8080
python scripts/web_viewer.py

# Custom port
python scripts/web_viewer.py --port 3000

# Custom data directory
python scripts/web_viewer.py --data-dir /path/to/data
```

After starting, visit `http://localhost:8080` to:
- Enter instructions and watch the agent workflow tree expand in real time
- View complete work logs for all historical sessions
- Track total sessions, completed, rejected, and running counts

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

## Acknowledgments

This project was developed with AI assistance, powered by **MiMo-V2.5**.

## Related Resources

- [Claude Code Skills Official Documentation](https://docs.anthropic.com/en/docs/claude-code/skills)
- [OpenCode Official Website](https://opencode.ai)
- [OpenCode Plugin Creation Guide](https://opencode.ai/docs/plugins)