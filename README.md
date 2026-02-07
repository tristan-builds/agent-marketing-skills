# Agent Marketing Skills

A collection of [Agent Skills](https://agentskills.io) for digital marketing workflows — SEO audits, metadata validation, content optimization, and more.

These skills follow the open [Agent Skills specification](https://agentskills.io/specification) and work with any compatible agent, including [Claude Code](https://docs.anthropic.com/en/docs/agents-and-tools/claude-code/overview).

## Skills

| Skill | Description |
|-------|-------------|
| [serp-pixel-checker](./serp-pixel-checker/) | Validate meta title and description pixel widths against Google SERP limits (580px title, 990px description). Uses Arial font rendering via Pillow for accuracy within 0–4px of browser-based checkers. Supports single strings, small batches, and full spreadsheet audits. |

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

Common dependencies across this collection:

```bash
pip install pillow openpyxl
```

## Platform Support

Scripts in this collection support **Windows**, **macOS**, and **Linux** out of the box.

## Contributing

Have a marketing skill to share? Open a PR. Each skill should be a self-contained folder with a `SKILL.md` and any bundled scripts or assets.

## License

MIT
