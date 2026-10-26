from pathlib import Path
from typing import List, Dict, Any, Optional
from InquirerPy import inquirer
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
    """Prompt the user to select from available templates."""
    choices = []
    for t in templates:
        choices.append(
            Choice(
                value=t["id"],
                name=f"{t['name']} - {t['description']}",
            )
        )

    return inquirer.select(
        message="Select a project template:",
        choices=choices,
        default=choices[0].value if choices else None,
    ).execute()

def prompt_skills_selection(
    available_skills: Dict[str, Any],
    recommended_skills: List[str],
) -> List[str]:
    """Prompt the user to choose skills to install into .agents/skills/."""
    choices = []
    for sid, skill in available_skills.items():
        is_rec = sid in recommended_skills
        label = f"{skill.name} [{'RECOMMENDED' if is_rec else skill.category}]"
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
