import hashlib
import json
import shutil
from pathlib import Path
from typing import List, Dict, Any

from .catalog import AVAILABLE_SKILLS, SkillInfo
from ..config import EMBEDDED_SKILLS_DIR, USER_SKILLS_DIR

def _compute_sha256(file_path: Path) -> str:
    """Compute sha256 hash of a file."""
    if not file_path.exists() or not file_path.is_file():
        return ""
    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(8192):
            hasher.update(chunk)
    return hasher.hexdigest()

def install_skills(target_dir: Path, skill_ids: List[str]) -> Dict[str, Any]:
    """
    Install specified skills into target_dir/.agents/skills/
    and generate/update skills-lock.json.
    """
    target_dir = Path(target_dir)
    agents_dir = target_dir / ".agents"
    skills_dir = agents_dir / "skills"
    skills_dir.mkdir(parents=True, exist_ok=True)

    lock_file = target_dir / "skills-lock.json"
    lock_data: Dict[str, Any] = {"version": 1, "skills": {}}
    if lock_file.exists():
        try:
            with open(lock_file, "r", encoding="utf-8") as f:
                lock_data = json.load(f)
                if "skills" not in lock_data:
                    lock_data["skills"] = {}
        except Exception:
            lock_data = {"version": 1, "skills": {}}

    # Read embedded master lockfile if available
    embedded_lock_file = EMBEDDED_SKILLS_DIR / "skills-lock.json"
    embedded_lock_data = {}
    if embedded_lock_file.exists():
        try:
            with open(embedded_lock_file, "r", encoding="utf-8") as f:
                embedded_lock_data = json.load(f).get("skills", {})
        except Exception:
            embedded_lock_data = {}

    installed_skills = []

    for sid in skill_ids:
        skill_info = AVAILABLE_SKILLS.get(sid)
        src_skill_dir = EMBEDDED_SKILLS_DIR / sid
        if not src_skill_dir.exists() and (USER_SKILLS_DIR / sid).exists():
            src_skill_dir = USER_SKILLS_DIR / sid

        dest_skill_dir = skills_dir / sid
        dest_skill_dir.mkdir(parents=True, exist_ok=True)

        skill_md = dest_skill_dir / "SKILL.md"

        if src_skill_dir.exists() and src_skill_dir.is_dir():
            # Copy all files from embedded skill directory
            for item in src_skill_dir.glob("**/*"):
                if item.is_file():
                    relative_path = item.relative_to(src_skill_dir)
                    dest_file = dest_skill_dir / relative_path
                    dest_file.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(item, dest_file)
        else:
            # Fallback: create a standard SKILL.md template
            name = skill_info.name if skill_info else sid
            desc = skill_info.description if skill_info else f"Skill for {sid}"
            content = f"""---
name: {sid}
description: {desc}
---

# {name}

{desc}

## Guidelines & Usage
- Follow standard project guidelines.
- Keep implementations concise, modular, and well-tested.
"""
            skill_md.write_text(content, encoding="utf-8")

        # Compute hash of primary SKILL.md or take from embedded master lockfile
        master_entry = embedded_lock_data.get(sid, {})
        computed_hash = master_entry.get("computedHash") or (_compute_sha256(skill_md) if skill_md.exists() else "")

        # Update lockfile data
        lock_data["skills"][sid] = {
            "source": master_entry.get("source") or (skill_info.source if skill_info else f"custom/{sid}"),
            "sourceType": master_entry.get("sourceType") or (skill_info.source_type if skill_info else "custom"),
            "skillPath": master_entry.get("skillPath") or f"skills/{sid}/SKILL.md",
            "computedHash": computed_hash,
        }
        installed_skills.append(sid)

    # Write updated lockfile
    with open(lock_file, "w", encoding="utf-8") as f:
        json.dump(lock_data, f, indent=2)

    return {
        "installed": installed_skills,
        "lock_file": str(lock_file),
        "skills_dir": str(skills_dir),
    }
