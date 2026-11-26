# Quickstart

## Interactive Wizard

Run `adevkit` or `adevkit init` in any directory to launch the interactive scaffolding wizard:

```bash
adevkit init
```

You will be guided through:
1. Project name and target directory
2. Starter template selection (built-in or custom)
3. Curated AI agent skills (`.agents/skills/`)
4. Target AI coding assistants (`AGENTS.md`, `.cursor/rules/`, `CLAUDE.md`, etc.)
5. `README.md` template style and `PRD.md` mode
6. Git, `.env`, `.vscode/`, and package installation (`uv`/`pip`, Node PM, Cargo)

## Non-Interactive Mode (CI / Scripts)

Use `--yes` (`-y`) with flags for single-command automation:

```bash
adevkit init my-api \
  --template python_fastapi \
  --agent antigravity \
  --agent cursor \
  --readme modern \
  --uv \
  --yes
```
