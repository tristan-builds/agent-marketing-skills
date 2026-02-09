# Agent Marketing Skills

A collection of [Agent Skills](https://agentskills.io) for digital marketing workflows — SEO audits, metadata validation, content optimization, and more.

These skills follow the open [Agent Skills specification](https://agentskills.io/specification) and work with any compatible agent, including [Claude Code](https://docs.anthropic.com/en/docs/agents-and-tools/claude-code/overview).

## Skills

| Skill | Description |
|-------|-------------|
| [serp-pixel-checker](./serp-pixel-checker/) | Validate meta title and description pixel widths against Google SERP limits (580px title, 990px description). Uses HarfBuzz text shaping with automatic font fallback for accuracy across Latin, Cyrillic, Greek, Arabic, Korean, Thai, Chinese, Japanese, and more. Supports single strings, small batches, and full spreadsheet audits. |

## Installation

### Claude Code

```bash
claude install-skill /path/to/agent-marketing-skills/serp-pixel-checker
```

Or clone the repo and copy the skill folder into your project's `.claude/skills/` directory.

### Other agents

Copy the skill folder into your agent's skills directory. See the [Agent Skills integration guide](https://agentskills.io/integrate-skills) for details.

## Requirements

Skills may bundle Python scripts with their own dependencies. Check each skill's `SKILL.md` for specifics.

```bash
pip install uharfbuzz openpyxl
```

## Language Support

The SERP pixel checker uses the same fonts browsers apply on Google SERPs, with automatic script detection and font fallback:

| Script | Font | Accuracy |
|--------|------|----------|
| Latin, Cyrillic, Greek, Arabic | Arial | 0–1px |
| Korean | Malgun Gothic | 0–5px |
| Thai | Tahoma | 0–5px |
| Chinese / Japanese / CJK | Microsoft YaHei | 0–4px |

## Platform Support

Scripts in this collection support **Windows**, **macOS**, and **Linux** out of the box. Fonts are auto-detected from system directories. Override the primary font with the `SERP_FONT_PATH` environment variable if needed.

## Contributing

Have a marketing skill to share? Open a PR. Each skill should be a self-contained folder with a `SKILL.md` and any bundled scripts or assets.

## License

MIT
