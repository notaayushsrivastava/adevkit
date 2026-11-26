import builtins
import tomllib
from pathlib import Path
from typer.testing import CliRunner

import adevkit
from adevkit.cli import app


runner = CliRunner()


def test_modular_architecture_and_facades():
    """Verify core, cli, gui subpackages and backward-compatible root facades."""
    import adevkit.core as core
    import adevkit.cli as cli
    import adevkit.deps as legacy_deps
    import adevkit.core.deps as core_deps
    import adevkit.vault as legacy_vault
    import adevkit.core.vault as core_vault
    import adevkit.ui as legacy_ui
    import adevkit.cli.ui as cli_ui

    assert legacy_deps is core_deps
    assert legacy_vault is core_vault
    assert legacy_ui is cli_ui
    assert hasattr(core, "add_dependencies")
    assert hasattr(cli, "app")
    assert adevkit.__version__


def test_gui_command_missing_deps(monkeypatch):
    """Verify `adevkit gui` prints styled instructions if GUI deps are missing."""
    real_import = builtins.__import__

    def fake_import(name, globals=None, locals=None, fromlist=(), level=0):
        if "gui.launcher" in name or name in ("webview", "reactpy"):
            raise ImportError("No module named 'webview'")
        return real_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", fake_import)
    result = runner.invoke(app, ["gui"])
    assert result.exit_code == 1
    assert "GUI dependencies are not installed" in result.output
    assert "adevkit[gui]" in result.output


def test_gui_command_launches_when_available(monkeypatch):
    """Verify `adevkit gui` delegates to launch_gui when dependencies exist."""
    import sys
    import types

    called = {}
    fake_launcher = types.ModuleType("adevkit.gui.launcher")

    def fake_launch_gui(debug: bool = False):
        called["debug"] = debug

    fake_launcher.launch_gui = fake_launch_gui
    monkeypatch.setitem(sys.modules, "adevkit.gui.launcher", fake_launcher)

    result = runner.invoke(app, ["gui", "--debug"])
    assert result.exit_code == 0
    assert called == {"debug": True}


def test_pyproject_extras_configuration():
    """Verify pyproject.toml defines base GUI dependencies and [gui]/[cli]/[all] extras."""
    pyproject_path = Path(__file__).resolve().parent.parent / "pyproject.toml"
    data = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))

    base_deps = data["project"]["dependencies"]
    assert any("reactpy" in d for d in base_deps)
    assert any("pywebview" in d for d in base_deps)

    extras = data["project"]["optional-dependencies"]
    assert "gui" in extras
    assert "cli" in extras
    assert "all" in extras
    assert extras["cli"] == []
    assert any("reactpy" in d for d in extras["gui"])
    assert any("pywebview" in d for d in extras["gui"])


def test_gui_design_system_and_view_transitions():
    """Verify ui.html tokens and View Transitions CSS are present in styles.py."""
    from adevkit.gui.styles import DESIGN_SYSTEM_CSS, VIEW_TRANSITION_SCRIPT

    assert "--bg-canvas: #090A0F;" in DESIGN_SYSTEM_CSS
    assert "--bg-surface: #12141C;" in DESIGN_SYSTEM_CSS
    assert "--accent-primary: #38BDF8;" in DESIGN_SYSTEM_CSS
    assert "::view-transition-old(main-panel)" in DESIGN_SYSTEM_CSS
    assert "prefers-reduced-motion: reduce" in DESIGN_SYSTEM_CSS
    assert "__adevkitNavigate" in VIEW_TRANSITION_SCRIPT


def test_gui_bridge_and_reactpy_layout_render(tmp_path):
    """Verify DevKitBridge project generation and ReactPy Layout render without errors."""
    import asyncio
    from reactpy.core.layout import Layout
    from adevkit.gui.app import DevKitApp
    from adevkit.gui.bridge import DevKitBridge

    bridge = DevKitBridge()
    assert len(bridge.get_templates()) >= 12
    assert len(bridge.get_skills()) > 0

    logs = []

    async def _run():
        ok = await bridge.run_project_generation(
            project_name="studio-demo",
            target_dir=str(tmp_path / "studio-demo"),
            template_id="minimal_agentic",
            skills=[],
            agents=["antigravity"],
            readme_style="modern",
            prd_mode="generate",
            init_git=False,
            init_dotenv=True,
            init_vscode=True,
            init_env=False,
            use_uv=False,
            on_log=lambda tag, text, tone: logs.append((tag, text, tone)),
        )
        assert ok is True
        assert (tmp_path / "studio-demo" / "AGENTS.md").exists()
        assert (tmp_path / "studio-demo" / "PRD.md").exists()

        diag = await bridge.get_diagnostics()
        assert "python" in diag
        assert "node_pms" in diag

        async with Layout(DevKitApp(bridge=bridge)) as layout:
            update = await layout.render()
            assert update is not None

    asyncio.run(_run())
    assert any(tag == "[ok]" for tag, _, _ in logs)


def test_gui_server_app_configuration():
    """Verify create_gui_app configures ReactPy WebSocket & HTTP routes on Starlette."""
    from adevkit.gui.bridge import DevKitBridge
    from adevkit.gui.launcher import create_gui_app, get_app_icon_path

    app = create_gui_app(DevKitBridge())
    paths = [getattr(r, "path", "") for r in app.routes]
    assert "/_reactpy/stream" in paths
    assert "/" in paths

    icon_path = get_app_icon_path()
    assert icon_path is not None
    assert Path(icon_path).exists()
    assert (Path(__file__).resolve().parent.parent / "assets" / "banner.svg").exists()


def test_web_landing_and_readthedocs_configs():
    """Verify web/ Vercel landing page and .readthedocs.yaml / docs/ Sphinx configs."""
    import json
    import yaml

    root = Path(__file__).resolve().parent.parent

    # Web landing page + Vercel
    web = root / "web"
    assert (web / "index.html").exists()
    assert (web / "styles.css").exists()
    assert (web / "app.js").exists()
    assert (web / "assets" / "favicon.svg").exists()
    vercel_cfg = json.loads((web / "vercel.json").read_text(encoding="utf-8"))
    assert vercel_cfg["cleanUrls"] is True
    assert "https://docs.adevkit.aayushsrivastava.com" in (web / "index.html").read_text(encoding="utf-8")

    # Read the Docs + Sphinx
    rtd_cfg = yaml.safe_load((root / ".readthedocs.yaml").read_text(encoding="utf-8"))
    assert rtd_cfg["version"] == 2
    assert rtd_cfg["build"]["os"] == "ubuntu-24.04"
    assert rtd_cfg["sphinx"]["configuration"] == "docs/conf.py"
    assert (root / "docs" / "conf.py").exists()
    assert (root / "docs" / "requirements.txt").exists()
    assert (root / "docs" / "index.md").exists()
