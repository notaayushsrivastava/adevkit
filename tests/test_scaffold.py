import json
import tempfile
from pathlib import Path
from devkit.scaffold import (
    generate_agents_md,
    generate_prd_template,
    import_prd_file,
    setup_git_repository,
    setup_dotenv_file,
    setup_vscode_config,
)

def test_generate_agents_md():
    with tempfile.TemporaryDirectory() as tmpdir:
        target = Path(tmpdir)
        path = generate_agents_md(
            target_dir=target,
            project_name="MegaProject",
            template_id="python_fastapi",
            installed_skills=["ponytail", "gemini-api-dev"],
        )
        assert path.exists()
        content = path.read_text(encoding="utf-8")
        assert "MegaProject" in content
        assert "ponytail" in content
        assert "pytest" in content

def test_generate_prd_template():
    with tempfile.TemporaryDirectory() as tmpdir:
        target = Path(tmpdir)
        path = generate_prd_template(
            target_dir=target,
            project_name="AI Dashboard",
            overview="Real-time analytics tool",
            target_users="Data engineers",
            core_features="- Real-time streaming\n- Visual charts",
        )
        assert path.exists()
        content = path.read_text(encoding="utf-8")
        assert "AI Dashboard" in content
        assert "Real-time streaming" in content

def test_import_prd_file():
    with tempfile.TemporaryDirectory() as tmpdir:
        target = Path(tmpdir)
        src = target / "custom_prd.md"
        src.write_text("# My Custom PRD", encoding="utf-8")

        dest_dir = target / "subproject"
        dest_dir.mkdir()
        imported = import_prd_file(dest_dir, src)
        assert imported.exists()
        assert imported.read_text(encoding="utf-8") == "# My Custom PRD"

def test_setup_vscode_config():
    with tempfile.TemporaryDirectory() as tmpdir:
        target = Path(tmpdir)
        setup_vscode_config(target, has_python=True, has_node=True)

        settings_file = target / ".vscode" / "settings.json"
        extensions_file = target / ".vscode" / "extensions.json"
        assert settings_file.exists()
        assert extensions_file.exists()

        settings = json.loads(settings_file.read_text(encoding="utf-8"))
        assert "python.defaultInterpreterPath" in settings
        assert "editor.defaultFormatter" in settings

def test_setup_dotenv_file():
    with tempfile.TemporaryDirectory() as tmpdir:
        target = Path(tmpdir)
        (target / ".env.example").write_text("PORT=3000\n", encoding="utf-8")
        assert setup_dotenv_file(target) is True
        assert (target / ".env").exists()
        assert (target / ".env").read_text(encoding="utf-8") == "PORT=3000\n"
