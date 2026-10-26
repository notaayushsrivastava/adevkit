import tempfile
from pathlib import Path
from adevkit.templates.custom import (
    save_custom_template,
    list_custom_templates,
    delete_custom_template,
    CustomProjectTemplate,
)

def test_custom_template_lifecycle(monkeypatch):
    with tempfile.TemporaryDirectory() as tmp_user_dir:
        # Patch USER_TEMPLATES_DIR to a temporary folder
        mock_templates_dir = Path(tmp_user_dir) / "templates"
        mock_templates_dir.mkdir(parents=True, exist_ok=True)
        monkeypatch.setattr("adevkit.templates.custom.USER_TEMPLATES_DIR", mock_templates_dir)

        # 1. Create a source project folder to snapshot
        with tempfile.TemporaryDirectory() as src_dir:
            src = Path(src_dir)
            (src / "app").mkdir()
            (src / "app" / "server.js").write_text("console.log('{{PROJECT_NAME}}');", encoding="utf-8")
            (src / "package.json").write_text('{"name": "{{PROJECT_NAME_LOWER}}"}', encoding="utf-8")

            # Save as custom template
            saved = save_custom_template(name="My Microservice", source_dir=src, description="Express microservice")
            assert saved.exists()

            # 2. List custom templates
            customs = list_custom_templates()
            assert any(c["id"] == "my-microservice" for c in customs)

            # 3. Scaffold from the custom template
            with tempfile.TemporaryDirectory() as dest_dir:
                dest = Path(dest_dir)
                tmpl = CustomProjectTemplate(
                    project_name="Order Service",
                    target_dir=dest,
                    template_dir=saved,
                    metadata={"name": "My Microservice", "has_node": True},
                )
                files = tmpl.scaffold()
                assert any("server.js" in f for f in files)
                server_content = (dest / "app" / "server.js").read_text(encoding="utf-8")
                assert "Order Service" in server_content

            # 4. Delete custom template
            deleted = delete_custom_template("my-microservice")
            assert deleted is True
            assert not saved.exists()
