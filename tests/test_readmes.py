from pathlib import Path
from adevkit.readmes import (
    list_readme_templates,
    get_readme_template,
    save_custom_readme,
    delete_custom_readme,
    render_readme,
    generate_project_readme,
    BUILTIN_README_TEMPLATES,
)


def test_builtin_readme_templates():
    templates = list_readme_templates()
    template_ids = [t["id"] for t in templates]
    for expected in ["modern", "minimal", "enterprise", "agentic"]:
        assert expected in template_ids


def test_render_readme_placeholders():
    context = {
        "project_name": "PhoenixApp",
        "template_id": "nextjs",
        "template_name": "Full-Stack Next.js",
        "description": "High velocity web application.",
        "author": "Aayush",
        "license": "MIT",
        "skills": ["impeccable", "ponytail"],
        "agents": ["cursor", "claude"],
    }
    rendered = render_readme("modern", context)
    assert "# PhoenixApp" in rendered
    assert "High velocity web application." in rendered
    assert "Full-Stack Next.js" in rendered
    assert "Aayush" in rendered
    assert "Cursor, Claude" in rendered
    assert "`impeccable`" in rendered
    assert "`ponytail`" in rendered


def test_custom_readme_lifecycle(tmp_path, monkeypatch):
    test_readme_dir = tmp_path / "user_readmes"
    test_readme_dir.mkdir()
    monkeypatch.setattr("adevkit.readmes.USER_README_DIR", test_readme_dir)

    custom_text = """# {{project_name}} (Internal Microservice)

> {{description}}

## Maintainer
- {{author}}
"""
    saved_path = save_custom_readme("service-docs", custom_text)
    assert saved_path.exists()
    assert saved_path.name == "service-docs.md"

    # Verify custom template listed
    all_readmes = list_readme_templates()
    assert any(r["id"] == "custom:service-docs" for r in all_readmes)

    # Verify retrieval and rendering
    retrieved = get_readme_template("custom:service-docs")
    assert "{{project_name}} (Internal Microservice)" in retrieved

    rendered = render_readme("custom:service-docs", {
        "project_name": "AuthService",
        "description": "Authentication microservice",
        "author": "Security Team",
    })
    assert "# AuthService (Internal Microservice)" in rendered
    assert "Security Team" in rendered

    # Delete
    deleted = delete_custom_readme("service-docs")
    assert deleted is True
    assert not saved_path.exists()


def test_generate_project_readme(tmp_path):
    project_dir = tmp_path / "my_project"
    project_dir.mkdir()

    dest = generate_project_readme(
        target_dir=project_dir,
        template_style="minimal",
        context={
            "project_name": "MinimalDemo",
            "description": "Testing minimal readme generation",
            "author": "Dev",
            "skills": ["ponytail"],
            "agents": ["antigravity"],
        },
    )
    assert dest.exists()
    assert dest.name == "README.md"
    content = dest.read_text(encoding="utf-8")
    assert "# MinimalDemo" in content
    assert "Testing minimal readme generation" in content
