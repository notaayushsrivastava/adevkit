import os
import re
import shutil
import tempfile
import urllib.request
from pathlib import Path
from typing import Dict, Any, Optional, List

from ..config import USER_SKILLS_DIR, EMBEDDED_SKILLS_DIR, ensure_user_dirs
from ..utils.system import run_command


def _sanitize_skill_name(name: str) -> str:
    """Sanitize skill identifier into kebab-case."""
    cleaned = re.sub(r"[^a-zA-Z0-9_\-]+", "-", name.strip().lower())
    return cleaned.strip("-") or "custom-skill"


def _extract_skill_id_and_subpath(source: str) -> tuple[str, str, Optional[str]]:
    """
    Parse a source string into (type, repo_or_path, subpath).
    Supported forms:
      - 'github.com/owner/repo/tree/main/subpath'
      - 'https://github.com/owner/repo'
      - 'owner/repo' or 'owner/repo/subpath'
      - 'http://.../SKILL.md' or 'https://.../SKILL.md'
      - local directory or file path
    """
    s = source.strip()
    if s.startswith("http://") or s.startswith("https://"):
        if s.endswith(".md") or s.endswith(".txt"):
            return ("raw_url", s, None)
        # GitHub tree url: https://github.com/owner/repo/tree/branch/path/to/skill
        tree_match = re.match(r"^https?://github\.com/([^/]+/[^/]+)/tree/[^/]+/(.+)$", s)
        if tree_match:
            return ("git_repo", f"https://github.com/{tree_match.group(1)}.git", tree_match.group(2))
        return ("git_repo", s, None)

    # Local path
    p = Path(s)
    if p.exists() or s.startswith(".") or s.startswith("/") or (len(s) > 1 and s[1] == ":"):
        return ("local_path", str(p.resolve()), None)

    # Shorthand: owner/repo or owner/repo/path
    parts = s.split("/")
    if len(parts) >= 2 and not s.startswith("@"):
        owner_repo = f"{parts[0]}/{parts[1]}"
        subpath = "/".join(parts[2:]) if len(parts) > 2 else None
        return ("git_repo", f"https://github.com/{owner_repo}.git", subpath)

    return ("catalog_or_name", s, None)


def create_custom_skill(
    name: str,
    target_dir: Optional[Path] = None,
    is_global: bool = True,
    description: str = "",
) -> Path:
    """Scaffold a new custom skill with frontmatter and references directory."""
    skill_id = _sanitize_skill_name(name)
    if is_global:
        ensure_user_dirs()
        dest_dir = USER_SKILLS_DIR / skill_id
    else:
        base = Path(target_dir) if target_dir else Path.cwd()
        dest_dir = base / ".agents" / "skills" / skill_id

    dest_dir.mkdir(parents=True, exist_ok=True)
    refs_dir = dest_dir / "references"
    refs_dir.mkdir(parents=True, exist_ok=True)

    desc_text = description.strip() or f"Custom agent skill for {name}."
    skill_md = dest_dir / "SKILL.md"

    if not skill_md.exists():
        content = f"""---
name: {name}
description: {desc_text}
---

# {name}

{desc_text}

## When to Activate
- Use this skill when working on tasks involving {name}.

## Guidelines & Rules
1. Maintain consistent standards and modular design.
2. Ensure comprehensive test coverage.
"""
        skill_md.write_text(content, encoding="utf-8")

    return dest_dir


def add_custom_skill(
    source: str,
    target_dir: Optional[Path] = None,
    is_global: bool = False,
    custom_name: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Add a skill from local path, GitHub repository/shorthand, URL, or catalog.
    If is_global is True, saves into ~/.adevkit/skills/ for global reuse.
    Otherwise installs into <target_dir>/.agents/skills/ and updates skills-lock.json.
    """
    src_type, repo_or_path, subpath = _extract_skill_id_and_subpath(source)
    temp_dir_to_clean: Optional[Path] = None

    try:
        # 1. Raw URL download
        if src_type == "raw_url":
            skill_id = _sanitize_skill_name(custom_name or Path(repo_or_path).stem)
            dest_dir = (USER_SKILLS_DIR if is_global else (Path(target_dir or Path.cwd()) / ".agents" / "skills")) / skill_id
            dest_dir.mkdir(parents=True, exist_ok=True)

            req = urllib.request.Request(repo_or_path, headers={"User-Agent": "adevkit-skills"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                md_content = resp.read().decode("utf-8", errors="ignore")

            (dest_dir / "SKILL.md").write_text(md_content, encoding="utf-8")
            actual_source = repo_or_path

        # 2. Local path
        elif src_type == "local_path":
            src_path = Path(repo_or_path)
            if not src_path.exists():
                raise FileNotFoundError(f"Local skill path does not exist: {src_path}")

            skill_id = _sanitize_skill_name(custom_name or src_path.stem)
            dest_dir = (USER_SKILLS_DIR if is_global else (Path(target_dir or Path.cwd()) / ".agents" / "skills")) / skill_id
            dest_dir.mkdir(parents=True, exist_ok=True)

            if src_path.is_file():
                shutil.copy2(src_path, dest_dir / "SKILL.md")
            else:
                for item in src_path.glob("**/*"):
                    if item.is_file():
                        rel = item.relative_to(src_path)
                        target_file = dest_dir / rel
                        target_file.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(item, target_file)
            actual_source = str(src_path)

        # 3. Git Repo / GitHub shorthand
        elif src_type == "git_repo":
            temp_dir = Path(tempfile.mkdtemp(prefix="adevkit_skill_"))
            temp_dir_to_clean = temp_dir

            code, out, err = run_command(["git", "clone", "--depth", "1", repo_or_path, str(temp_dir)])
            if code != 0:
                raise RuntimeError(f"Failed to clone git repository {repo_or_path}: {err or out}")

            src_root = temp_dir
            if subpath:
                src_root = temp_dir / subpath
                if not src_root.exists():
                    raise FileNotFoundError(f"Subpath '{subpath}' not found in cloned repository {repo_or_path}")

            # Determine skill folder
            skill_source_dir = src_root
            if not (src_root / "SKILL.md").exists():
                # Search for SKILL.md in subdirectories
                found = list(src_root.glob("**/SKILL.md"))
                if found:
                    skill_source_dir = found[0].parent

            skill_id = _sanitize_skill_name(custom_name or (subpath.split("/")[-1] if subpath else skill_source_dir.name))
            dest_dir = (USER_SKILLS_DIR if is_global else (Path(target_dir or Path.cwd()) / ".agents" / "skills")) / skill_id
            dest_dir.mkdir(parents=True, exist_ok=True)

            for item in skill_source_dir.glob("**/*"):
                if item.is_file() and not any(part.startswith(".git") for part in item.parts):
                    rel = item.relative_to(skill_source_dir)
                    target_file = dest_dir / rel
                    target_file.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(item, target_file)
            actual_source = repo_or_path

        # 4. Catalog or name fallback
        else:
            from .catalog import AVAILABLE_SKILLS
            sid = source.strip().lower()
            if sid in AVAILABLE_SKILLS:
                skill_id = sid
                if is_global:
                    ensure_user_dirs()
                    dest_dir = USER_SKILLS_DIR / skill_id
                    src_skill = EMBEDDED_SKILLS_DIR / sid
                    if src_skill.exists() and src_skill.is_dir():
                        shutil.copytree(src_skill, dest_dir, dirs_exist_ok=True)
                    else:
                        create_custom_skill(sid, is_global=True)
                else:
                    from .installer import install_skills
                    res = install_skills(target_dir or Path.cwd(), [sid])
                    return {
                        "skill_id": sid,
                        "destination": str(res["skills_dir"]),
                        "is_global": False,
                        "source": f"catalog/{sid}",
                    }
                actual_source = f"catalog/{sid}"
            else:
                # Create a clean new skill with this name
                skill_id = _sanitize_skill_name(custom_name or source)
                dest_dir = create_custom_skill(skill_id, target_dir=target_dir, is_global=is_global)
                actual_source = "scaffold"

        # Guarantee SKILL.md exists
        skill_md = dest_dir / "SKILL.md"
        if not skill_md.exists():
            skill_md.write_text(
                f"---\nname: {skill_id}\ndescription: Custom skill for {skill_id}\n---\n\n# {skill_id}\n",
                encoding="utf-8",
            )

        # If project-level install, update skills-lock.json
        if not is_global:
            from .installer import _compute_sha256
            base_target = Path(target_dir) if target_dir else Path.cwd()
            lock_file = base_target / "skills-lock.json"
            lock_data = {"version": 1, "skills": {}}
            if lock_file.exists():
                try:
                    import json
                    with open(lock_file, "r", encoding="utf-8") as f:
                        lock_data = json.load(f)
                        if "skills" not in lock_data:
                            lock_data["skills"] = {}
                except Exception:
                    pass

            lock_data["skills"][skill_id] = {
                "source": actual_source,
                "sourceType": "custom",
                "skillPath": f"skills/{skill_id}/SKILL.md",
                "computedHash": _compute_sha256(skill_md),
            }
            import json
            with open(lock_file, "w", encoding="utf-8") as f:
                json.dump(lock_data, f, indent=2)

        return {
            "skill_id": skill_id,
            "destination": str(dest_dir),
            "is_global": is_global,
            "source": actual_source,
        }

    finally:
        if temp_dir_to_clean and temp_dir_to_clean.exists():
            shutil.rmtree(temp_dir_to_clean, ignore_errors=True)


def remove_custom_skill(name: str, target_dir: Optional[Path] = None, is_global: bool = False) -> bool:
    """Remove a custom skill directory."""
    skill_id = _sanitize_skill_name(name)
    if is_global:
        skill_dir = USER_SKILLS_DIR / skill_id
    else:
        base = Path(target_dir) if target_dir else Path.cwd()
        skill_dir = base / ".agents" / "skills" / skill_id
        # Also clean lockfile entry
        lock_file = base / "skills-lock.json"
        if lock_file.exists():
            try:
                import json
                with open(lock_file, "r", encoding="utf-8") as f:
                    lock_data = json.load(f)
                if skill_id in lock_data.get("skills", {}):
                    del lock_data["skills"][skill_id]
                    with open(lock_file, "w", encoding="utf-8") as f:
                        json.dump(lock_data, f, indent=2)
            except Exception:
                pass

    if skill_dir.exists() and skill_dir.is_dir():
        shutil.rmtree(skill_dir)
        return True
    return False


def list_custom_skills() -> List[Dict[str, str]]:
    """List all user-saved global custom skills."""
    skills = []
    if USER_SKILLS_DIR.exists():
        for item in sorted(USER_SKILLS_DIR.iterdir()):
            if item.is_dir():
                md = item / "SKILL.md"
                desc = "Custom skill"
                if md.exists():
                    try:
                        content = md.read_text(encoding="utf-8", errors="ignore")
                        match = re.search(r"description:\s*([^\n\r]+)", content)
                        if match:
                            desc = match.group(1).strip().strip('"').strip("'")
                    except Exception:
                        pass
                skills.append({
                    "id": item.name,
                    "path": str(item),
                    "description": desc,
                })
    return skills
