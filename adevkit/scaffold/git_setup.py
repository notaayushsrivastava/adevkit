from pathlib import Path
from typing import Optional
from ..utils.system import detect_git, run_command

def setup_git_repository(target_dir: Path, has_python: bool, has_node: bool) -> bool:
    """Initialize git repository and write stack-tailored .gitignore."""
    target_dir = Path(target_dir)

    gitignore_lines = [
        "# General & OS",
        ".DS_Store",
        "Thumbs.db",
        "*.log",
        ".env",
        ".env.local",
        ".env.*.local",
        "",
        "# Editor & IDE",
        ".idea/",
        "*.suo",
        "*.ntvs*",
        "*.njsproj",
        "*.sln",
        "*.sw?",
    ]

    if has_node:
        gitignore_lines.extend([
            "",
            "# Node & Frontend",
            "node_modules/",
            "npm-debug.log*",
            "yarn-debug.log*",
            "yarn-error.log*",
            "pnpm-debug.log*",
            "dist/",
            "build/",
            ".next/",
            "out/",
            ".expo/",
            "web-build/",
            ".turbo/",
        ])

    if has_python:
        gitignore_lines.extend([
            "",
            "# Python",
            ".venv/",
            "env/",
            "venv/",
            "__pycache__/",
            "*.py[cod]",
            "*$py.class",
            ".pytest_cache/",
            ".coverage",
            "htmlcov/",
            "*.egg-info/",
            "dist/",
            "build/",
        ])

    gitignore_path = target_dir / ".gitignore"
    gitignore_path.write_text("\n".join(gitignore_lines) + "\n", encoding="utf-8")

    if detect_git():
        exit_code, _, _ = run_command(["git", "init"], cwd=target_dir)
        return exit_code == 0
    return False
