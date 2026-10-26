from pathlib import Path
from devkit.skills.custom import (
    create_custom_skill,
    add_custom_skill,
    remove_custom_skill,
    list_custom_skills,
)
from devkit.skills.catalog import load_all_skills


def test_custom_skill_lifecycle(tmp_path, monkeypatch):
    test_user_skills = tmp_path / "user_skills"
    test_user_skills.mkdir()
    monkeypatch.setattr("devkit.skills.custom.USER_SKILLS_DIR", test_user_skills)
    monkeypatch.setattr("devkit.skills.catalog.USER_SKILLS_DIR", test_user_skills)

    # 1. Create a custom skill
    dest = create_custom_skill(
        name="team-standards",
        is_global=True,
        description="Our team coding conventions",
    )
    assert dest.exists()
    assert (dest / "SKILL.md").exists()
    content = (dest / "SKILL.md").read_text(encoding="utf-8")
    assert "name: team-standards" in content

    # 2. Verify it is indexed in custom skills list
    custom_list = list_custom_skills()
    assert any(s["id"] == "team-standards" for s in custom_list)

    # 3. Verify it is loaded into the full skills catalog
    catalog = load_all_skills()
    assert "team-standards" in catalog
    assert catalog["team-standards"].category == "Custom User Skills"

    # 4. Add skill from local path into a project
    project_dir = tmp_path / "mock_project"
    project_dir.mkdir()
    res = add_custom_skill(source=str(dest), target_dir=project_dir, is_global=False)
    assert res["skill_id"] == "team-standards"
    assert (project_dir / ".agents" / "skills" / "team-standards" / "SKILL.md").exists()
    assert (project_dir / "skills-lock.json").exists()

    # 5. Remove custom skill
    removed = remove_custom_skill(name="team-standards", is_global=True)
    assert removed is True
    assert not dest.exists()
