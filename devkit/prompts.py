import shutil
import textwrap
from pathlib import Path
from typing import List, Dict, Any, Optional
from prompt_toolkit.layout.containers import Window, ConditionalContainer
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.filters import IsDone
from InquirerPy import inquirer
from InquirerPy.prompts.list import ListPrompt
from InquirerPy.base.control import Choice
from InquirerPy.separator import Separator

def prompt_project_name(default_name: str = "my-agentic-project") -> str:
    """Prompt the user for the project name."""
    return inquirer.text(
        message="Enter your project name:",
        default=default_name,
        validate=lambda result: len(result.strip()) > 0 or "Project name cannot be empty.",
    ).execute().strip()

def prompt_template_selection(templates: List[Dict]) -> str:
    """
    Prompt the user to select from available templates.
    Displays concise, uncluttered names in the menu and dynamically shows
    the full description of ONLY the currently highlighted template in a
    responsive box, optimized for all terminal sizes.
    """
    desc_map = {t["id"]: (t["name"], t.get("description", "")) for t in templates}
    choices = [
        Choice(
            value=t["id"],
            name=t.get("short_name") or t["name"],
        )
        for t in templates
    ]

    term_size = shutil.get_terminal_size((80, 24))
    prompt_height = max(5, min(10, term_size.lines - 8))

    prompt = ListPrompt(
        message="Select a project template:",
        choices=choices,
        cycle=True,
        max_height=prompt_height,
        wrap_lines=False,
    )

    def get_desc_formatted():
        sel = prompt.content_control.selection
        val = sel.get("value") if sel else None
        meta = desc_map.get(val, ("Template", ""))
        full_name, desc = meta

        tw = shutil.get_terminal_size((80, 24)).columns
        box_w = max(34, min(76, tw - 4))
        inner_w = box_w - 4

        header_text = f" [i] {full_name} "
        if len(header_text) > inner_w - 4:
            header_text = header_text[: max(10, inner_w - 7)] + "... "
        top_dashes = max(2, box_w - 4 - len(header_text))

        wrapped_lines = textwrap.wrap(desc, width=inner_w) if desc else ["No description provided."]

        out = [
            ("", "\n"),
            ("class:instruction", "  ┌─"),
            ("bold cyan", header_text),
            ("class:instruction", "─" * top_dashes + "┐\n"),
        ]
        for line in wrapped_lines:
            out.append(("", "  │ " + line.ljust(inner_w) + " │\n"))
        out.append(("class:instruction", "  └" + "─" * (box_w - 2) + "┘"))
        return out

    # Add dynamic description container that disappears once selection is made
    desc_window = ConditionalContainer(
        Window(content=FormattedTextControl(get_desc_formatted), dont_extend_height=True),
        filter=~IsDone(),
    )
    prompt._layout.content.children.append(desc_window)

    return prompt.execute()

def prompt_expo_backend_stack() -> str:
    """Prompt the user for their preferred backend stack in the Expo fullstack monorepo."""
    return inquirer.select(
        message="Select the backend stack for backend/:",
        choices=[
            Choice(value="fastapi", name="Python (FastAPI + Pydantic + Uvicorn)"),
            Choice(value="hono", name="Node.js / TypeScript (Hono + Node Server)"),
        ],
        default="fastapi",
    ).execute()

def prompt_agents_selection(default_agents: Optional[List[str]] = None) -> List[str]:
    """Prompt the user to select target AI coding assistants for the project."""
    from .scaffold.agent_configs import SUPPORTED_AGENTS
    from .vault import get_default_agents

    defaults = default_agents if default_agents is not None else get_default_agents()
    choices = [
        Choice(
            value=aid,
            name=desc,
            enabled=(aid in defaults),
        )
        for aid, desc in SUPPORTED_AGENTS.items()
    ]

    return inquirer.checkbox(
        message="Select target AI Coding Agents / Assistants (Space to toggle, Enter to confirm):",
        choices=choices,
        cycle=True,
    ).execute()

def prompt_skills_selection(
    available_skills: Dict[str, Any],
    recommended_skills: List[str],
) -> List[str]:
    """Prompt the user to choose skills to install into .agents/skills/."""
    choices = []
    term_size = shutil.get_terminal_size((80, 24))
    max_label_w = max(30, min(60, term_size.columns - 18))

    for sid, skill in available_skills.items():
        is_rec = sid in recommended_skills
        tag = "RECOMMENDED" if is_rec else skill.category
        name = skill.name
        if len(name) > max_label_w:
            name = name[: max_label_w - 3] + "..."
        label = f"{name} [{tag}]"
        choices.append(
            Choice(
                value=sid,
                name=label,
                enabled=is_rec,
            )
        )

    return inquirer.checkbox(
        message="Select agent skills to install in .agents/skills (Space to toggle, Enter to confirm):",
        choices=choices,
        max_height=max(6, min(12, term_size.lines - 8)),
        wrap_lines=False,
        cycle=True,
    ).execute()

def prompt_readme_template(templates: List[Dict[str, Any]]) -> str:
    """Prompt the user to select their preferred README.md style."""
    choices = [
        Choice(
            value=t["id"],
            name=f"{t['name']} - {t['description']}",
        )
        for t in templates
    ]
    choices.append(Choice(value="skip", name="Skip README.md generation"))

    return inquirer.select(
        message="Select README.md template style:",
        choices=choices,
        default="modern",
    ).execute()

def prompt_prd_mode() -> Dict[str, Any]:
    """Prompt the user how they would like to handle PRD.md."""
    mode = inquirer.select(
        message="How would you like to handle PRD.md?",
        choices=[
            Choice(value="guided", name="Generate a structured PRD template with guided inputs"),
            Choice(value="quick", name="Generate default comprehensive PRD.md starter"),
            Choice(value="import", name="Attach / import an existing PRD.md file from disk"),
            Choice(value="skip", name="Skip PRD.md for now"),
        ],
        default="guided",
    ).execute()

    if mode == "guided":
        overview = inquirer.text(
            message="Brief project vision / overview (press Enter for default):",
            default="",
        ).execute()
        users = inquirer.text(
            message="Primary target users / audience (press Enter for default):",
            default="",
        ).execute()
        features = inquirer.text(
            message="Top 2-3 core features (comma-separated, or Enter for default):",
            default="",
        ).execute()
        return {
            "mode": "generate",
            "overview": overview,
            "target_users": users,
            "core_features": "\n".join([f"- {f.strip()}" for f in features.split(",") if f.strip()]) if features else "",
        }
    elif mode == "quick":
        return {"mode": "generate", "overview": "", "target_users": "", "core_features": ""}
    elif mode == "import":
        path_str = inquirer.filepath(
            message="Enter the path to your existing PRD.md file:",
            validate=lambda p: Path(p).is_file() or "File does not exist.",
            only_files=True,
        ).execute()
        return {"mode": "import", "source_path": Path(path_str)}
    else:
        return {"mode": "skip"}

def prompt_env_options(has_python: bool, has_node: bool) -> Dict[str, bool]:
    """Prompt for automated environment setup toggles."""
    choices = [
        Choice(value="git", name="Initialize Git repository & smart .gitignore", enabled=True),
        Choice(value="dotenv", name="Create .env from .env.example (if available)", enabled=True),
        Choice(value="vscode", name="Configure .vscode settings and recommended extensions", enabled=True),
    ]

    if has_python:
        choices.append(Choice(value="venv", name="Create Python .venv & install requirements.txt", enabled=True))

    if has_node:
        choices.append(Choice(value="node", name="Auto-detect package manager and install node_modules", enabled=True))

    selected = inquirer.checkbox(
        message="Select automated initialization tasks to execute:",
        choices=choices,
    ).execute()

    return {
        "git": "git" in selected,
        "dotenv": "dotenv" in selected,
        "vscode": "vscode" in selected,
        "venv": "venv" in selected,
        "node": "node" in selected,
    }
