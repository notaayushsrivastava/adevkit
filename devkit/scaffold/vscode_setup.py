import json
from pathlib import Path
from typing import Dict, Any

def setup_vscode_config(target_dir: Path, has_python: bool, has_node: bool) -> Path:
    """Write customized .vscode/settings.json and extensions.json."""
    target_dir = Path(target_dir)
    vscode_dir = target_dir / ".vscode"
    vscode_dir.mkdir(parents=True, exist_ok=True)

    settings: Dict[str, Any] = {
        "editor.formatOnSave": True,
        "editor.tabSize": 2,
        "files.eol": "\n",
        "files.trimTrailingWhitespace": True,
    }

    extensions = [
        "eamodio.gitlens",
    ]

    if has_python:
        settings["python.defaultInterpreterPath"] = "${workspaceFolder}/.venv/Scripts/python.exe"
        settings["python.testing.pytestEnabled"] = True
        settings["python.testing.pytestArgs"] = ["tests"]
        extensions.extend(["ms-python.python", "ms-python.vscode-pylance", "charliermarsh.ruff"])

    if has_node:
        settings["editor.defaultFormatter"] = "esbenp.prettier-vscode"
        extensions.extend(["dbaeumer.vscode-eslint", "esbenp.prettier-vscode", "bradlc.vscode-tailwindcss"])

    settings_file = vscode_dir / "settings.json"
    settings_file.write_text(json.dumps(settings, indent=2), encoding="utf-8")

    extensions_file = vscode_dir / "extensions.json"
    extensions_file.write_text(json.dumps({"recommendations": extensions}, indent=2), encoding="utf-8")

    return vscode_dir
