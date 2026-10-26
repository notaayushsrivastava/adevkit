from pathlib import Path
from typing import List
from ..skills.catalog import AVAILABLE_SKILLS

def generate_agents_md(
    target_dir: Path,
    project_name: str,
    template_id: str,
    installed_skills: List[str],
) -> Path:
    """Generate a comprehensive AGENTS.md guide tailored to the project stack and skills."""
    target_dir = Path(target_dir)
    file_path = target_dir / "AGENTS.md"

    # Stack-specific run commands
    commands_section = ""
    if "python" in template_id:
        commands_section = """### Environment & Commands
- **Activate Virtual Environment**: `.\\.venv\\Scripts\\activate` (Windows) or `source .venv/bin/activate` (POSIX)
- **Run API Server**: `python -m app.main` or `uvicorn app.main:app --reload`
- **Run Tests**: `pytest tests/ -v`
- **Install Dependencies**: `pip install -r requirements.txt`
"""
    elif "nextjs" in template_id:
        commands_section = """### Environment & Commands
- **Dev Server**: `npm run dev` (or `pnpm dev` / `bun dev`)
- **Build Production**: `npm run build`
- **Lint**: `npm run lint`
- **Typecheck**: `npx tsc --noEmit`
"""
    elif "vite" in template_id:
        commands_section = """### Environment & Commands
- **Dev Server**: `npm run dev`
- **Build Production**: `npm run build`
- **Preview Build**: `npm run preview`
"""
    elif "expo" in template_id:
        commands_section = """### Environment & Commands
- **Start Expo Metro**: `npm start`
- **Run Android**: `npm run android`
- **Run iOS**: `npm run ios`
- **Run Web**: `npm run web`
"""
    else:
        commands_section = """### Environment & Commands
- Inspect `package.json`, `pyproject.toml`, or `requirements.txt` for available build and run scripts.
"""

    # Skills descriptions
    skills_lines = []
    for sid in installed_skills:
        info = AVAILABLE_SKILLS.get(sid)
        desc = info.description if info else "Custom skill"
        name = info.name if info else sid
        skills_lines.append(f"- **`{sid}`** ({name}): {desc}")

    skills_section = "\n".join(skills_lines) if skills_lines else "- No special skills installed."

    content = f"""# AGENTS.md — AI Agent Pairing Guidelines for {project_name}

Welcome! This document provides essential architectural context, commands, and rules for AI coding assistants (Antigravity, Cursor, Claude Code, Gemini CLI, Copilot) collaborating on **{project_name}**.

---

## 1. Project Context & Stack
- **Project Name**: {project_name}
- **Template / Architecture**: {template_id}
- **Scaffolded by**: Aayush's DevKit

{commands_section}

---

## 2. Active Agent Skills (`.agents/skills/`)
The following skills are installed in `.agents/skills/` and tracked in `skills-lock.json`:

{skills_section}

> **Directive**: Before performing complex architectural decisions, refactors, or audits, consult the relevant skill in `.agents/skills/<skill-name>/SKILL.md`.

---

## 3. General Agent Principles & Coding Standards
1. **Minimal, High-Leverage Changes**:
   - Write the smallest amount of code that cleanly solves the problem.
   - Avoid speculative abstractions, unnecessary wrapper layers, or bloat.
2. **Preserve Integrity**:
   - Never remove existing docstrings, tests, or comments unrelated to your task.
   - Keep TypeScript types strict and Python type hints explicit.
3. **Verification First**:
   - Always run tests or build verification commands before claiming completion.
   - If tests fail, diagnose root causes rather than disabling the tests.
4. **Product Alignment**:
   - Consult `PRD.md` for functional requirements and scope constraints.
"""
    file_path.write_text(content, encoding="utf-8")
    return file_path
