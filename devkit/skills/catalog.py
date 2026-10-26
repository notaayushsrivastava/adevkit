import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Optional
from ..config import EMBEDDED_SKILLS_DIR

@dataclass
class SkillInfo:
    id: str
    name: str
    description: str
    category: str
    source: str = "embedded"
    source_type: str = "local"
    recommended_for: Optional[List[str]] = None

def _categorize_skill(skill_id: str) -> str:
    """Categorize skills by their domain."""
    if any(k in skill_id for k in ["animat", "motion"]):
        return "Animations & Motion"
    elif any(k in skill_id for k in ["taste", "impeccable", "design", "ui-ux", "styling", "apple-design"]):
        return "Design & UI/UX"
    elif "vercel" in skill_id or "deploy" in skill_id or "web-design" in skill_id:
        return "Vercel & Next.js"
    elif "ponytail" in skill_id:
        return "Code Quality (Ponytail)"
    elif any(k in skill_id for k in ["mobile", "native", "swift"]):
        return "Mobile & Native"
    elif any(k in skill_id for k in ["gemini", "ai", "agent"]):
        return "AI & Agentic"
    elif any(k in skill_id for k in ["devtools", "guidance"]):
        return "Browser & Web Standards"
    return "Developer Tools"

def _extract_skill_meta(skill_id: str, skill_dir: Path) -> tuple[str, str]:
    """Extract name and description from SKILL.md frontmatter."""
    skill_md = skill_dir / "SKILL.md"
    name = skill_id.replace("-", " ").title()
    desc = f"Curated skill for {skill_id}."

    if skill_md.exists():
        try:
            content = skill_md.read_text(encoding="utf-8", errors="ignore")
            # Match frontmatter YAML block
            fm_match = re.search(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
            if fm_match:
                fm_text = fm_match.group(1)
                for line in fm_text.splitlines():
                    if line.startswith("name:"):
                        name = line.split(":", 1)[1].strip().strip('"').strip("'")
                    elif line.startswith("description:"):
                        desc = line.split(":", 1)[1].strip().strip('"').strip("'")
                        # Handle multiline YAML folded scalar >-
                        if desc in [">-", "|-", ">", "|"]:
                            # Look at next lines
                            lines = fm_text.splitlines()
                            idx = lines.index(line)
                            collected = []
                            for nxt in lines[idx + 1:]:
                                if nxt.startswith("  "):
                                    collected.append(nxt.strip())
                                else:
                                    break
                            if collected:
                                desc = " ".join(collected)
        except Exception:
            pass

    # Truncate overly long descriptions for display
    if len(desc) > 160:
        desc = desc[:157] + "..."

    return name, desc

def load_all_skills() -> Dict[str, SkillInfo]:
    """Dynamically discover and build the full catalog of embedded skills."""
    skills: Dict[str, SkillInfo] = {}

    lock_file = EMBEDDED_SKILLS_DIR / "skills-lock.json"
    lock_data: Dict = {}
    if lock_file.exists():
        try:
            with open(lock_file, "r", encoding="utf-8") as f:
                lock_data = json.load(f).get("skills", {})
        except Exception:
            lock_data = {}

    if EMBEDDED_SKILLS_DIR.exists():
        for item in sorted(EMBEDDED_SKILLS_DIR.iterdir()):
            if item.is_dir():
                sid = item.name
                name, desc = _extract_skill_meta(sid, item)
                cat = _categorize_skill(sid)

                lock_entry = lock_data.get(sid, {})
                source = lock_entry.get("source", f"embedded/{sid}")
                source_type = lock_entry.get("sourceType", "builtin")

                # Setup recommendation tags
                recs = ["all"] if "ponytail" in sid else []
                if sid in ["impeccable", "design-taste-frontend", "ui-ux-pro-max", "emil-design-eng", "animate"]:
                    recs.extend(["nextjs", "vite_react", "saas_fullstack", "design_system", "content_site", "expo_mobile", "expo_fullstack"])
                if "vercel" in sid or sid in ["web-design-guidelines"]:
                    recs.extend(["nextjs", "saas_fullstack", "design_system", "content_site"])
                if sid in ["modern-web-guidance", "chrome-devtools"]:
                    recs.extend(["nextjs", "vite_react", "saas_fullstack", "content_site", "design_system"])
                if "gemini" in sid:
                    recs.extend(["all"])
                if sid in ["mobile-native", "animate-expo", "vercel-react-native-skills"]:
                    recs.extend(["expo_mobile", "expo_fullstack"])

                skills[sid] = SkillInfo(
                    id=sid,
                    name=name,
                    description=desc,
                    category=cat,
                    source=source,
                    source_type=source_type,
                    recommended_for=recs,
                )

    return skills

AVAILABLE_SKILLS: Dict[str, SkillInfo] = load_all_skills()

SKILL_BUNDLES: Dict[str, Dict] = {
    "ponytail_suite": {
        "title": "Ponytail Suite (Lazy Senior Dev Mode)",
        "skills": ["ponytail", "ponytail-audit", "ponytail-review", "ponytail-debt"],
        "description": "Essential code quality, minimal architecture, and anti-bloat review suite.",
    },
    "design_craft_suite": {
        "title": "Design Craftsmanship & Aesthetics Suite",
        "skills": ["impeccable", "design-taste-frontend", "ui-ux-pro-max", "emil-design-eng", "animate"],
        "description": "World-class UI design, anti-generic art direction, and micro-interactions.",
    },
    "vercel_fullstack_suite": {
        "title": "Vercel & Next.js Performance Suite",
        "skills": ["vercel-react-best-practices", "vercel-composition-patterns", "vercel-optimize", "deploy-to-vercel"],
        "description": "Production Next.js App Router patterns, RSC, and deployment optimization.",
    },
    "mobile_native_suite": {
        "title": "Mobile Native & Fluid Interaction Suite",
        "skills": ["animate-expo", "mobile-native", "vercel-react-native-skills", "apple-design"],
        "description": "Touch physics, haptics, responsive gestures, and native performance.",
    },
}

def get_recommended_skills_for_template(template_id: str) -> List[str]:
    """Get the list of skill IDs recommended for a particular template."""
    recommended = []
    for skill_id, skill in AVAILABLE_SKILLS.items():
        if skill.recommended_for and ("all" in skill.recommended_for or template_id in skill.recommended_for):
            recommended.append(skill_id)
    return recommended
