from pathlib import Path
from typing import List, Dict
from .agents_md import generate_agents_md

SUPPORTED_AGENTS = {
    "antigravity": "Antigravity (Google DeepMind) - AGENTS.md & .agents/ directory",
    "cursor": "Cursor - .cursorrules & .cursor/rules/main.mdc",
    "claude": "Claude Code - CLAUDE.md project guide",
    "copilot": "GitHub Copilot - .github/copilot-instructions.md",
    "windsurf": "Windsurf - .windsurfrules cascade instructions",
    "aider": "Aider - .aider.conf.yml configuration",
}


def generate_cursor_rules(
    target_dir: Path,
    project_name: str,
    template_id: str,
    installed_skills: List[str],
) -> Path:
    """Generate .cursorrules and .cursor/rules/main.mdc for Cursor AI."""
    target_dir = Path(target_dir)
    cursor_dir = target_dir / ".cursor" / "rules"
    cursor_dir.mkdir(parents=True, exist_ok=True)

    skills_summary = ", ".join(installed_skills) if installed_skills else "none"

    content = f"""# Cursor Project Rules - {project_name}

## Project Overview
- **Project**: {project_name}
- **Template Stack**: {template_id}
- **Agent Skills**: {skills_summary}

## Code Quality & Architecture
- Maintain modular, test-driven implementations.
- Read `.agents/skills/` for domain-specific skill guidelines.
- Always check `AGENTS.md` and `PRD.md` before making architectural changes.
- Avoid unnecessary bloat; prefer minimal dependency impact.
"""
    # Write .cursorrules
    (target_dir / ".cursorrules").write_text(content, encoding="utf-8")
    # Write .cursor/rules/main.mdc
    (cursor_dir / "main.mdc").write_text(content, encoding="utf-8")
    return target_dir / ".cursorrules"


def generate_claude_md(
    target_dir: Path,
    project_name: str,
    template_id: str,
    installed_skills: List[str],
) -> Path:
    """Generate CLAUDE.md tailored for Claude Code CLI."""
    target_dir = Path(target_dir)
    file_path = target_dir / "CLAUDE.md"

    cmd_guide = ""
    if "python" in template_id or "ai_agents" in template_id:
        cmd_guide = """## Common Commands
- Test: `pytest tests/ -v`
- Run: `python -m app.main`
- Lint: `flake8` or `ruff check .`
"""
    elif "nextjs" in template_id or "saas" in template_id:
        cmd_guide = """## Common Commands
- Dev: `npm run dev`
- Build: `npm run build`
- Lint: `npm run lint`
- Typecheck: `npx tsc --noEmit`
"""
    else:
        cmd_guide = """## Common Commands
- Inspect package scripts in `package.json` or `pyproject.toml`.
"""

    skills_text = "\n".join([f"- `.agents/skills/{s}/SKILL.md`" for s in installed_skills]) if installed_skills else "- None installed"

    content = f"""# {project_name} - Claude Code Guide

## Architecture Overview
- Stack template: `{template_id}`
- PRD & Specifications: see `PRD.md`
- Master Agent Instructions: see `AGENTS.md`

{cmd_guide}

## Installed Agent Skills
{skills_text}

## Development Guidelines
- Always write tests alongside new functionality.
- Adhere strictly to the project structure and skill guidelines.
"""
    file_path.write_text(content, encoding="utf-8")
    return file_path


def generate_copilot_instructions(
    target_dir: Path,
    project_name: str,
    template_id: str,
    installed_skills: List[str],
) -> Path:
    """Generate .github/copilot-instructions.md for GitHub Copilot."""
    target_dir = Path(target_dir)
    gh_dir = target_dir / ".github"
    gh_dir.mkdir(parents=True, exist_ok=True)
    file_path = gh_dir / "copilot-instructions.md"

    skills_summary = ", ".join(installed_skills) if installed_skills else "none"

    content = f"""# GitHub Copilot Instructions for {project_name}

- **Stack**: {template_id}
- **Active Skills**: {skills_summary}
- Refer to `AGENTS.md` and `PRD.md` for detailed system requirements.
- Produce clean, modern, type-safe code with error handling.
"""
    file_path.write_text(content, encoding="utf-8")
    return file_path


def generate_windsurf_rules(
    target_dir: Path,
    project_name: str,
    template_id: str,
    installed_skills: List[str],
) -> Path:
    """Generate .windsurfrules for Windsurf IDE."""
    target_dir = Path(target_dir)
    file_path = target_dir / ".windsurfrules"

    skills_summary = ", ".join(installed_skills) if installed_skills else "none"

    content = f"""# Windsurf Rules - {project_name}
- Stack: {template_id}
- Refer to `.agents/skills/` and `AGENTS.md` for guidelines.
- Active skills: {skills_summary}
"""
    file_path.write_text(content, encoding="utf-8")
    return file_path


def generate_aider_conf(
    target_dir: Path,
    project_name: str,
    template_id: str,
    installed_skills: List[str],
) -> Path:
    """Generate .aider.conf.yml for Aider CLI."""
    target_dir = Path(target_dir)
    file_path = target_dir / ".aider.conf.yml"

    content = f"""# Aider Configuration for {project_name}
read:
  - AGENTS.md
  - PRD.md
auto-commits: false
"""
    file_path.write_text(content, encoding="utf-8")
    return file_path


def scaffold_agent_configs(
    target_dir: Path,
    project_name: str,
    template_id: str,
    installed_skills: List[str],
    selected_agents: List[str],
) -> List[str]:
    """
    Generate rule and config files for all selected AI agents.
    Returns list of generated configuration file descriptions.
    """
    target_dir = Path(target_dir)
    created = []

    # Antigravity / generic AGENTS.md is always generated
    generate_agents_md(target_dir, project_name, template_id, installed_skills)
    created.append("AGENTS.md (Antigravity & Agentic Framework)")

    agents_set = set(a.lower().strip() for a in selected_agents)

    if "cursor" in agents_set:
        generate_cursor_rules(target_dir, project_name, template_id, installed_skills)
        created.append(".cursorrules & .cursor/rules/main.mdc (Cursor)")

    if "claude" in agents_set:
        generate_claude_md(target_dir, project_name, template_id, installed_skills)
        created.append("CLAUDE.md (Claude Code)")

    if "copilot" in agents_set:
        generate_copilot_instructions(target_dir, project_name, template_id, installed_skills)
        created.append(".github/copilot-instructions.md (GitHub Copilot)")

    if "windsurf" in agents_set:
        generate_windsurf_rules(target_dir, project_name, template_id, installed_skills)
        created.append(".windsurfrules (Windsurf)")

    if "aider" in agents_set:
        generate_aider_conf(target_dir, project_name, template_id, installed_skills)
        created.append(".aider.conf.yml (Aider)")

    return created
