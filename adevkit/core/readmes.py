import re
import json
import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

from .config import USER_README_DIR, ensure_user_dirs


BUILTIN_README_TEMPLATES: Dict[str, Dict[str, str]] = {
    "modern": {
        "name": "Modern Developer (Recommended)",
        "description": "Clean, structured, professional layout with Quick Start, Architecture, and AI Agent setup.",
        "content": """# {{project_name}}

> {{description}}

Built with **{{template_name}}** and configured with **adevkit** for modern agentic engineering.

---

## Overview

{{project_name}} is engineered for high performance, modular architecture, and seamless AI agent pair programming.

- **Stack**: {{template_name}} (`{{template_id}}`)
- **Author**: {{author}}
- **License**: {{license}}

---

## Features

- **Production-Ready Architecture**: Clean separation of concerns with modern TypeScript / Python tooling.
- **AI Agent Guidelines**: Configured with rules and instructions for: {{agents_list}}
- **Curated Agent Skills**: Pre-installed domain expertise in `.agents/skills/`:
{{skills_list}}

---

## Quick Start

{{run_commands}}

---

## Project Structure

Refer to `AGENTS.md` and `PRD.md` for complete architectural blueprints and system requirements.

```
{{project_name}}/
├── .agents/skills/    # Installed agent skills and domain rules
├── skills-lock.json   # Reproducible skill lockfile
├── AGENTS.md          # Multi-agent architectural instructions
├── PRD.md             # Product Requirements Document
└── ...                # Core application source
```

---

## AI Agent Integration

This repository is optimized for AI pair programming. If you are using:
- **Cursor**: See `.cursorrules` and `.cursor/rules/`
- **Claude Code**: See `CLAUDE.md`
- **GitHub Copilot**: See `.github/copilot-instructions.md`
- **Antigravity / Gemini CLI**: See `AGENTS.md` and `.agents/skills/`

---

## License

MIT © {{year}} {{author}}
""",
    },
    "minimal": {
        "name": "Minimalist",
        "description": "Crisp and concise overview, quick start, and command reference.",
        "content": """# {{project_name}}

{{description}}

## Quick Start

{{run_commands}}

## Active Skills & Agents
- **Agents**: {{agents_list}}
- **Skills**: {{skills_badges}}

## License
{{license}} © {{year}} {{author}}
""",
    },
    "enterprise": {
        "name": "Enterprise / SaaS",
        "description": "Comprehensive specification layout with Architecture, Security, CI/CD, and Compliance.",
        "content": """# {{project_name}}

[![Build Status](https://img.shields.io/badge/status-active-brightgreen.svg)]()
[![Stack](https://img.shields.io/badge/stack-{{template_id}}-blue.svg)]()
[![License](https://img.shields.io/badge/license-{{license}}-blue.svg)]()

> {{description}}

---

## System Architecture

{{project_name}} is built on the **{{template_name}}** foundation, designed for scalability, zero-trust security, and maintainability.

### Key Capabilities
- **Strict Typing & Validation**: End-to-end type safety.
- **Environment Isolation**: Reproducible dependencies and environment variables.
- **Agentic Governance**: Governed by standardized agent skills and guidelines.

---

## Getting Started

### Prerequisites
- Node.js >= 18 or Python >= 3.10
- Git 2.30+

### Execution Commands
{{run_commands}}

---

## Security & Secrets

Do not commit `.env` or sensitive credentials to source control. Use the `adevkit config` vault or approved cloud secret managers.

---

## Agentic Engineering

Installed Skills in `.agents/skills/`:
{{skills_list}}

Configured Agents:
{{agents_list}}

---

## License & Copyright

Copyright (c) {{year}} {{author}}. All rights reserved under the {{license}} License.
""",
    },
    "agentic": {
        "name": "AI Agentic Focus",
        "description": "Focused on autonomous AI agents, prompt instructions, lockfiles, and pair programming.",
        "content": """# {{project_name}} (Agentic Workspace)

> {{description}}

This repository is designed from the ground up for collaborative human-AI software engineering using **adevkit**.

---

## Configured AI Agents
{{agents_list}}

All agent prompts and guidelines are synchronized across `AGENTS.md`, `.cursorrules`, and `CLAUDE.md`.

---

## Curated Agent Skills (`.agents/skills/`)
{{skills_list}}

Every skill is pinned and verified with cryptographic hashes in `skills-lock.json`.

---

## Developer Commands

{{run_commands}}

---

## Instructions for Agents

1. Always read `PRD.md` before implementing major architectural changes.
2. Check `.agents/skills/` for domain-specific implementation rules before writing new components.
3. Write test coverage in `tests/` for all newly introduced endpoints or utilities.

---

## License
{{license}} © {{year}} {{author}}
""",
    },
}


def _get_commands_for_template(template_id: str) -> str:
    """Format default run commands for a given template."""
    if "python" in template_id or "ai_agents" in template_id:
        return """```powershell
# 1. Activate virtual environment
.\\.venv\\Scripts\\activate   # Windows
source .venv/bin/activate     # POSIX

# 2. Run application / API
python -m app.main

# 3. Execute tests
pytest tests/ -v
```"""
    elif "nextjs" in template_id or "saas" in template_id or "vite" in template_id or "content" in template_id:
        return """```bash
# 1. Run local development server
npm run dev

# 2. Build for production
npm run build

# 3. Run typecheck & tests
npm test
```"""
    elif "expo" in template_id:
        return """```bash
# Start Expo development server
npm start
```"""
    else:
        return """```bash
# Inspect package.json or pyproject.toml for dev and build commands.
```"""


def list_readme_templates() -> List[Dict[str, Any]]:
    """List all available built-in and user-custom README templates."""
    results = []

    # Built-in templates
    for tid, data in BUILTIN_README_TEMPLATES.items():
        results.append({
            "id": tid,
            "name": data["name"],
            "description": data["description"],
            "is_custom": False,
        })

    # User custom templates
    if USER_README_DIR.exists():
        for p in sorted(USER_README_DIR.glob("*.md")):
            tid = f"custom:{p.stem}"
            raw_content = p.read_text(encoding="utf-8", errors="ignore")
            content = raw_content.replace("\\n", "\n")
            lines = [line.strip() for line in content.splitlines() if line.strip()]

            # Extract clean title from first heading
            name = p.stem.replace("-", " ").title()
            for line in lines:
                if line.startswith("#"):
                    name = line.lstrip("#").strip()
                    break

            # Extract clean description from blockquote or first non-heading line
            desc = "Custom user README template."
            for line in lines:
                if line.startswith(">"):
                    desc = line.lstrip(">").strip()
                    break
                elif not line.startswith("#") and len(line) > 3:
                    desc = line[:80]
                    break

            results.append({
                "id": tid,
                "name": f"* {name} (Custom)",
                "description": desc,
                "is_custom": True,
                "path": str(p),
            })

    return results


def get_readme_template(template_id: str) -> str:
    """Retrieve raw template content by ID (built-in or custom:NAME)."""
    tid = template_id.strip().lower()
    if tid in BUILTIN_README_TEMPLATES:
        return BUILTIN_README_TEMPLATES[tid]["content"]

    # Check custom
    cleaned_id = tid.replace("custom:", "")
    custom_path = USER_README_DIR / f"{cleaned_id}.md"
    if custom_path.exists():
        return custom_path.read_text(encoding="utf-8", errors="ignore")

    # Fallback to modern
    return BUILTIN_README_TEMPLATES["modern"]["content"]


def save_custom_readme(name: str, content_or_path: str, description: str = "") -> Path:
    """Save a user-defined custom README template into ~/.adevkit/readmes/<name>.md."""
    ensure_user_dirs()
    clean_name = re.sub(r"[^a-zA-Z0-9_\-]+", "-", name.strip().lower()).strip("-")
    dest_path = USER_README_DIR / f"{clean_name}.md"

    p = Path(content_or_path)
    if p.exists() and p.is_file():
        content = p.read_text(encoding="utf-8", errors="ignore")
    else:
        content = content_or_path

    if "\\n" in content and "\n" not in content:
        content = content.replace("\\n", "\n")

    dest_path.write_text(content, encoding="utf-8")
    return dest_path


def delete_custom_readme(name: str) -> bool:
    """Delete a user-defined custom README template."""
    clean_name = re.sub(r"[^a-zA-Z0-9_\-]+", "-", name.strip().lower()).strip("-")
    target = USER_README_DIR / f"{clean_name}.md"
    if target.exists():
        target.unlink()
        return True
    return False


def render_readme(template_id_or_content: str, context: Dict[str, Any]) -> str:
    """
    Render a README template by interpolating context placeholders.
    """
    if "\n" in template_id_or_content or "#" in template_id_or_content:
        raw_text = template_id_or_content
    else:
        raw_text = get_readme_template(template_id_or_content)

    project_name = context.get("project_name", "My Project")
    template_id = context.get("template_id", "nextjs")
    template_name = context.get("template_name", template_id.replace("_", " ").title())
    description = context.get("description") or f"A modern {template_name} application created with adevkit."
    author = context.get("author", "Developer")
    license_type = context.get("license", "MIT")
    year = str(datetime.datetime.now().year)

    # Format skills
    installed_skills = context.get("skills", [])
    if installed_skills:
        skills_list = "\n".join([f"- **`{s}`**" for s in installed_skills])
        skills_badges = ", ".join([f"`{s}`" for s in installed_skills])
    else:
        skills_list = "- None installed"
        skills_badges = "None"

    # Format agents
    agents = context.get("agents", ["antigravity"])
    agents_list = ", ".join([a.title() for a in agents]) if agents else "Antigravity"

    run_commands = context.get("run_commands") or _get_commands_for_template(template_id)

    replacements = {
        "{{project_name}}": project_name,
        "{{template_id}}": template_id,
        "{{template_name}}": template_name,
        "{{description}}": description,
        "{{author}}": author,
        "{{license}}": license_type,
        "{{year}}": year,
        "{{skills_list}}": skills_list,
        "{{skills_badges}}": skills_badges,
        "{{agents_list}}": agents_list,
        "{{run_commands}}": run_commands,
    }

    rendered = raw_text
    for placeholder, val in replacements.items():
        rendered = rendered.replace(placeholder, str(val))

    return rendered


def generate_project_readme(
    target_dir: Path,
    template_style: str = "modern",
    context: Optional[Dict[str, Any]] = None,
) -> Path:
    """Render and write README.md to the target project directory."""
    target_dir = Path(target_dir)
    ctx = context or {}
    rendered_content = render_readme(template_style, ctx)
    dest_file = target_dir / "README.md"
    dest_file.write_text(rendered_content, encoding="utf-8")
    return dest_file
