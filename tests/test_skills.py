import json
import tempfile
from pathlib import Path
from adevkit.skills.installer import install_skills
from adevkit.skills.catalog import AVAILABLE_SKILLS, get_recommended_skills_for_template

def test_install_skills():
    with tempfile.TemporaryDirectory() as tmpdir:
        target = Path(tmpdir)
        skills_to_install = ["ponytail", "gemini-api-dev"]
        res = install_skills(target, skills_to_install)

        assert len(res["installed"]) == 2
        
        # Verify .agents/skills/<skill>/SKILL.md exists
        for sid in skills_to_install:
            skill_md = target / ".agents" / "skills" / sid / "SKILL.md"
            assert skill_md.exists()

        # Verify skills-lock.json exists and is valid JSON
        lock_path = target / "skills-lock.json"
        assert lock_path.exists()
        with open(lock_path, "r", encoding="utf-8") as f:
            lock_data = json.load(f)
            assert lock_data["version"] == 1
            for sid in skills_to_install:
                assert sid in lock_data["skills"]
                assert "computedHash" in lock_data["skills"][sid]

def test_recommended_skills():
    rec_next = get_recommended_skills_for_template("nextjs")
    assert "modern-web-guidance" in rec_next
    assert "chrome-devtools" in rec_next

    rec_py = get_recommended_skills_for_template("python_fastapi")
    assert "ponytail" in rec_py
    assert "gemini-api-dev" in rec_py
