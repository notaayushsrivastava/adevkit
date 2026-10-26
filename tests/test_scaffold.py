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
    setup_python_environment,
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


def test_setup_python_environment_standard(monkeypatch, tmp_path):
    # Mock run_command to simulate successful execution
    commands_run = []
    def mock_run(cmd, cwd=None, timeout=300):
        commands_run.append(cmd)
        return 0, "Success", ""

    monkeypatch.setattr("devkit.scaffold.env_setup.run_command", mock_run)

    (tmp_path / "requirements.txt").write_text("fastapi\n", encoding="utf-8")
    ok, msg = setup_python_environment(tmp_path, use_uv=False)
    assert ok is True
    assert "configured" in msg
    assert any("-m" in c and "venv" in c for c in commands_run)


def test_setup_python_environment_with_uv(monkeypatch, tmp_path):
    commands_run = []
    def mock_run(cmd, cwd=None, timeout=300):
        commands_run.append(cmd)
        return 0, "Success", ""

    monkeypatch.setattr("devkit.scaffold.env_setup.run_command", mock_run)
    monkeypatch.setattr("devkit.scaffold.env_setup.which_tool", lambda tool: "/usr/bin/uv" if tool == "uv" else None)

    (tmp_path / "requirements.txt").write_text("fastapi\n", encoding="utf-8")
    ok, msg = setup_python_environment(tmp_path, use_uv=True)
    assert ok is True
    assert "uv" in msg
    assert any("uv" in c[0] and "venv" in c for c in commands_run)
    assert any("uv" in c[0] and "pip" in c for c in commands_run)


def test_setup_python_environment_uv_fallback(monkeypatch, tmp_path):
    commands_run = []
    def mock_run(cmd, cwd=None, timeout=300):
        commands_run.append(cmd)
        return 0, "Success", ""

    monkeypatch.setattr("devkit.scaffold.env_setup.run_command", mock_run)
    # uv is not installed
    monkeypatch.setattr("devkit.scaffold.env_setup.which_tool", lambda tool: None)

    ok, msg = setup_python_environment(tmp_path, use_uv=True)
    assert ok is True
    # Falls back to standard python -m venv
    assert any("-m" in c and "venv" in c for c in commands_run)
