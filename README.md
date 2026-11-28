# Skills

A collection of reusable [Agent Skills](https://agentskills.io/) for AI coding agents and workflows.

## Available Skills

| Skill | Description | Location |
| :--- | :--- | :--- |
| `diagram-crafting` | Create, convert, and validate diagrams across Mermaid, Obsidian `.canvas`, and Archify interactive HTML | [`skills/diagram-crafting/`](./skills/diagram-crafting/SKILL.md) |
| `prompt-crafting` | Craft, critique, and tailor prompts using Antigravity, CRAFT, and harness-specific patterns | [`skills/prompt-crafting/`](./skills/prompt-crafting/SKILL.md) |

## Installing Skills

### Using `npx skills` (Recommended)

This repository follows the [Agent Skills](https://agentskills.io/) directory convention, so [`npx skills`](https://skills.sh/) can install skills directly to either **project** or **global** scope from GitHub (`luismiddleton/skills`) or a local clone:

```bash
# List available skills in the repo
npx skills add luismiddleton/skills --list

# Install a skill to the current project (.agents/skills/)
npx skills add luismiddleton/skills --skill prompt-crafting

# Install a skill globally (~/.agents/skills/)
npx skills add luismiddleton/skills -g --skill prompt-crafting

# Install from a local clone instead of GitHub
npx skills add /path/to/skills --skill prompt-crafting        # project scope
npx skills add /path/to/skills -g --skill prompt-crafting     # global scope

# Install all skills non-interactively for all detected agents
npx skills add luismiddleton/skills -g --all
```

Useful options and management commands:

- `-a <agent>` — target specific agent(s) (e.g., `antigravity`, `claude-code`, `codex`, or `'*'` for all)
- `--copy` — copy files into agent-specific folders instead of symlinking from `.agents/skills/`
- `-y` — skip confirmation prompts
- `npx skills ls [-g]` / `npx skills update [-g]` / `npx skills remove [-g] <skill>` — list, update, or remove installed skills

### Manual Copy

Copy any skill directory directly into your project or global agent skills folder:

```bash
# Project scope
mkdir -p .agents/skills && cp -r skills/prompt-crafting .agents/skills/

# Global scope (Antigravity / generic Agent Skills)
cp -r skills/prompt-crafting ~/.agents/skills/

# Global scope (Gemini CLI / Antigravity config)
cp -r skills/prompt-crafting ~/.gemini/config/skills/
```
