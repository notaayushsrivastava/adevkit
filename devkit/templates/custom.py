import json
import os
import shutil
from pathlib import Path
from typing import List, Dict, Optional
from .base import BaseTemplate
from ..config import USER_TEMPLATES_DIR, ensure_user_dirs

class CustomProjectTemplate(BaseTemplate):
    """Scaffolds a project from a user-saved custom template directory."""

    def __init__(self, project_name: str, target_dir: Path, template_dir: Path, metadata: Dict):
        super().__init__(project_name, target_dir)
        self.template_dir = template_dir
        self.metadata = metadata
        self.id = f"custom_{template_dir.name}"
        self.name = metadata.get("name", template_dir.name)
        self.description = metadata.get("description", "Custom user-defined template")
        self.category = "Custom"
        self.has_node = metadata.get("has_node", False)
        self.has_python = metadata.get("has_python", False)

    def scaffold(self) -> List[str]:
        files_created = []
        files_dir = self.template_dir / "files"
        if not files_dir.exists():
            return files_created

        for item in files_dir.glob("**/*"):
            if item.is_file():
                rel_path = item.relative_to(files_dir)
                dest = self.target_dir / rel_path
                dest.parent.mkdir(parents=True, exist_ok=True)
                
                try:
                    # Attempt text rendering with variable replacements
                    content = item.read_text(encoding="utf-8")
                    rendered = self.render_text(content)
                    dest.write_text(rendered, encoding="utf-8")
                except UnicodeDecodeError:
                    # Binary file, copy raw
                    shutil.copy2(item, dest)

                files_created.append(str(rel_path))
        return files_created

def list_custom_templates() -> List[Dict]:
    """List all user-saved custom templates in ~/.aayush-devkit/templates."""
    ensure_user_dirs()
    templates = []
    for entry in USER_TEMPLATES_DIR.iterdir():
        if entry.is_dir():
            meta_file = entry / "template.json"
            meta = {}
            if meta_file.exists():
                try:
                    with open(meta_file, "r", encoding="utf-8") as f:
                        meta = json.load(f)
                except Exception:
                    pass
            templates.append({
                "id": entry.name,
                "name": meta.get("name", entry.name),
                "description": meta.get("description", "Custom template"),
                "path": entry,
                "has_node": meta.get("has_node", False),
                "has_python": meta.get("has_python", False),
                "created_at": meta.get("created_at", ""),
            })
    return templates

def save_custom_template(name: str, source_dir: Path, description: str = "") -> Path:
    """Save an existing project folder as a reusable custom template."""
    ensure_user_dirs()
    template_name = name.strip().lower().replace(" ", "-")
    dest_dir = USER_TEMPLATES_DIR / template_name
    if dest_dir.exists():
        shutil.rmtree(dest_dir)

    dest_dir.mkdir(parents=True, exist_ok=True)
    files_dir = dest_dir / "files"
    files_dir.mkdir(parents=True, exist_ok=True)

    # Ignore heavy or ephemeral folders
    ignored_patterns = {
        "node_modules", ".git", ".venv", "__pycache__",
        "dist", "build", ".next", ".expo", ".turbo"
    }

    has_node = False
    has_python = False

    for root, dirs, files in os.walk(source_dir):
        # Prune ignored directories
        dirs[:] = [d for d in dirs if d not in ignored_patterns]

        for file in files:
            src_file = Path(root) / file
            rel_file = src_file.relative_to(source_dir)
            dest_file = files_dir / rel_file
            dest_file.parent.mkdir(parents=True, exist_ok=True)

            if file == "package.json":
                has_node = True
            elif file in ["requirements.txt", "pyproject.toml"]:
                has_python = True

            shutil.copy2(src_file, dest_file)

    meta = {
        "name": name,
        "description": description or f"Custom template created from {source_dir.name}",
        "has_node": has_node,
        "has_python": has_python,
    }
    with open(dest_dir / "template.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)

    return dest_dir

def delete_custom_template(name: str) -> bool:
    """Delete a custom template by name."""
    ensure_user_dirs()
    template_name = name.strip().lower().replace(" ", "-")
    target_dir = USER_TEMPLATES_DIR / template_name
    if target_dir.exists() and target_dir.is_dir():
        shutil.rmtree(target_dir)
        return True
    return False
