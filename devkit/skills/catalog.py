from dataclasses import dataclass
from typing import List, Dict, Optional

@dataclass
class SkillInfo:
    id: str
    name: str
    description: str
    category: str
    source: str = "embedded"
    source_type: str = "local"
    recommended_for: Optional[List[str]] = None

AVAILABLE_SKILLS: Dict[str, SkillInfo] = {
    "ponytail": SkillInfo(
        id="ponytail",
        name="Ponytail (Lazy Senior Dev Mode)",
        description="The smallest change that fully solves the task, avoiding bloat and over-engineering.",
        category="Code Quality & Architecture",
        source="DietrichGebert/ponytail",
        source_type="github",
        recommended_for=["all"],
    ),
    "ponytail-audit": SkillInfo(
        id="ponytail-audit",
        name="Ponytail Audit",
        description="Quality audit of a whole repo: bugs, security holes, performance, bloat, and what to delete.",
        category="Code Quality & Architecture",
        source="DietrichGebert/ponytail",
        source_type="github",
        recommended_for=["all"],
    ),
    "ponytail-review": SkillInfo(
        id="ponytail-review",
        name="Ponytail Review",
        description="Deep quality review of diffs and PRs for correctness, load safety, and minimal code.",
        category="Code Quality & Architecture",
        source="DietrichGebert/ponytail",
        source_type="github",
        recommended_for=["all"],
    ),
    "ponytail-debt": SkillInfo(
        id="ponytail-debt",
        name="Ponytail Debt",
        description="Tracks shortcuts and debt comments into an actionable ledger.",
        category="Code Quality & Architecture",
        source="DietrichGebert/ponytail",
        source_type="github",
        recommended_for=["all"],
    ),
    "modern-web-guidance": SkillInfo(
        id="modern-web-guidance",
        name="Modern Web Guidance",
        description="Official modern HTML, CSS, container queries, view transitions, and performance standards.",
        category="Frontend & Web",
        source="builtin/modern-web-guidance",
        source_type="builtin",
        recommended_for=["nextjs", "vite_react", "expo_mobile"],
    ),
    "chrome-devtools": SkillInfo(
        id="chrome-devtools",
        name="Chrome DevTools",
        description="Browser automation, DOM/CSS debugging, network inspection, and performance profiling.",
        category="Debugging & Browser",
        source="builtin/chrome-devtools",
        source_type="builtin",
        recommended_for=["nextjs", "vite_react"],
    ),
    "gemini-api-dev": SkillInfo(
        id="gemini-api-dev",
        name="Gemini API Developer",
        description="Best practices for multimodal prompts, structured outputs, streaming, and tool calling with Gemini models.",
        category="AI & Agentic",
        source="builtin/gemini-api-dev",
        source_type="builtin",
        recommended_for=["all"],
    ),
}

SKILL_BUNDLES: Dict[str, Dict] = {
    "ponytail_suite": {
        "title": "Ponytail Suite (Lazy Senior Dev Mode)",
        "skills": ["ponytail", "ponytail-audit", "ponytail-review", "ponytail-debt"],
        "description": "Essential code quality, minimal architecture, and anti-bloat review suite.",
    },
    "web_frontend": {
        "title": "Modern Web & DevTools Suite",
        "skills": ["modern-web-guidance", "chrome-devtools"],
        "description": "HTML/CSS standards, web performance, and browser debugging.",
    },
    "ai_agentic": {
        "title": "AI & Agentic Development Suite",
        "skills": ["gemini-api-dev", "ponytail"],
        "description": "Gemini API integration, structured prompting, and disciplined agentic code generation.",
    },
    "full_pack": {
        "title": "Full Developer Powerpack (All Skills)",
        "skills": list(AVAILABLE_SKILLS.keys()),
        "description": "Install all curated agent skills for maximum capability.",
    },
}

def get_recommended_skills_for_template(template_id: str) -> List[str]:
    """Get the list of skill IDs recommended for a particular template."""
    recommended = []
    for skill_id, skill in AVAILABLE_SKILLS.items():
        if skill.recommended_for and ("all" in skill.recommended_for or template_id in skill.recommended_for):
            recommended.append(skill_id)
    return recommended
