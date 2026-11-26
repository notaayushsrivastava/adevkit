import json
from pathlib import Path
from unittest.mock import patch
from typer.testing import CliRunner

from adevkit.deps import (
    detect_project_type,
    add_dependencies,
    remove_dependencies,
    list_dependencies,
)
from adevkit.cli import app

runner = CliRunner()


def test_detect_project_type(tmp_path: Path):
    assert detect_project_type(tmp_path) == "unknown"

    (tmp_path / "Cargo.toml").write_text('[package]\nname = "test"\n', encoding="utf-8")
    assert detect_project_type(tmp_path) == "rust"

    (tmp_path / "Cargo.toml").unlink()
    (tmp_path / "package.json").write_text('{"name": "test"}', encoding="utf-8")
    assert detect_project_type(tmp_path) == "node"

    (tmp_path / "package.json").unlink()
    (tmp_path / "requirements.txt").write_text("fastapi\n", encoding="utf-8")
    assert detect_project_type(tmp_path) == "python"

    (tmp_path / "requirements.txt").unlink()
    (tmp_path / "pyproject.toml").write_text('[project]\nname = "test"\n', encoding="utf-8")
    assert detect_project_type(tmp_path) == "python"


def test_add_dependencies_empty(tmp_path: Path):
    ok, msg = add_dependencies([], cwd=tmp_path)
    assert ok is False
    assert "No package names" in msg


def test_add_dependencies_unknown_project(tmp_path: Path):
    ok, msg = add_dependencies(["serde"], cwd=tmp_path)
    assert ok is False
    assert "No supported project manifest found" in msg


def test_add_dependencies_rust(tmp_path: Path):
    (tmp_path / "Cargo.toml").write_text('[package]\nname = "test"\n', encoding="utf-8")

    with patch("adevkit.deps.detect_cargo", return_value="cargo"), \
         patch("adevkit.deps.run_command", return_value=(0, "Added serde", "")) as mock_run:
        ok, msg = add_dependencies(["serde", "tokio"], dev=False, cwd=tmp_path)
        assert ok is True
        assert "Added Rust dependencies" in msg
        mock_run.assert_called_once_with(["cargo", "add", "serde", "tokio"], cwd=tmp_path)

    with patch("adevkit.deps.detect_cargo", return_value="cargo"), \
         patch("adevkit.deps.run_command", return_value=(0, "Added dev dep", "")) as mock_run:
        ok, msg = add_dependencies(["tempfile"], dev=True, cwd=tmp_path)
        assert ok is True
        assert "(dev)" in msg
        mock_run.assert_called_once_with(["cargo", "add", "--dev", "tempfile"], cwd=tmp_path)


def test_add_dependencies_node(tmp_path: Path):
    (tmp_path / "package.json").write_text('{"name": "test"}', encoding="utf-8")

    # npm test
    with patch("adevkit.deps.detect_node_package_manager", return_value="npm"), \
         patch("adevkit.deps.which_tool", return_value="npm"), \
         patch("adevkit.deps.run_command", return_value=(0, "added 1 package", "")) as mock_run:
        ok, msg = add_dependencies(["lodash"], dev=False, cwd=tmp_path)
        assert ok is True
        mock_run.assert_called_once_with(["npm", "install", "--save", "lodash"], cwd=tmp_path)

    # pnpm with dev
    with patch("adevkit.deps.detect_node_package_manager", return_value="pnpm"), \
         patch("adevkit.deps.which_tool", return_value="pnpm"), \
         patch("adevkit.deps.run_command", return_value=(0, "added 1 package", "")) as mock_run:
        ok, msg = add_dependencies(["typescript"], dev=True, cwd=tmp_path)
        assert ok is True
        mock_run.assert_called_once_with(["pnpm", "add", "-D", "typescript"], cwd=tmp_path)

    # bun with dev
    with patch("adevkit.deps.detect_node_package_manager", return_value="bun"), \
         patch("adevkit.deps.which_tool", return_value="bun"), \
         patch("adevkit.deps.run_command", return_value=(0, "added 1 package", "")) as mock_run:
        ok, msg = add_dependencies(["prettier"], dev=True, cwd=tmp_path)
        assert ok is True
        mock_run.assert_called_once_with(["bun", "add", "-d", "prettier"], cwd=tmp_path)


def test_remove_dependencies_rust_and_node(tmp_path: Path):
    # Rust remove
    (tmp_path / "Cargo.toml").write_text('[package]\nname = "test"\n', encoding="utf-8")
    with patch("adevkit.deps.detect_cargo", return_value="cargo"), \
         patch("adevkit.deps.run_command", return_value=(0, "", "")) as mock_run:
        ok, msg = remove_dependencies(["serde"], cwd=tmp_path)
        assert ok is True
        assert "Removed Rust dependencies: serde" in msg
        mock_run.assert_called_once_with(["cargo", "remove", "serde"], cwd=tmp_path)

    (tmp_path / "Cargo.toml").unlink()

    # Node remove
    (tmp_path / "package.json").write_text('{"name": "test"}', encoding="utf-8")
    with patch("adevkit.deps.detect_node_package_manager", return_value="pnpm"), \
         patch("adevkit.deps.which_tool", return_value="pnpm"), \
         patch("adevkit.deps.run_command", return_value=(0, "", "")) as mock_run:
        ok, msg = remove_dependencies(["lodash"], cwd=tmp_path)
        assert ok is True
        assert "Removed JavaScript dependencies via pnpm: lodash" in msg
        mock_run.assert_called_once_with(["pnpm", "remove", "lodash"], cwd=tmp_path)


def test_list_dependencies(tmp_path: Path):
    # Rust parsing
    cargo_toml = """[package]
name = "demo"
version = "0.1.0"

[dependencies]
clap = "4.5"
tokio = { version = "1.0", features = ["full"] }

[dev-dependencies]
tempfile = "3.8"
"""
    (tmp_path / "Cargo.toml").write_text(cargo_toml, encoding="utf-8")
    res = list_dependencies(cwd=tmp_path)
    assert res["ecosystem"] == "rust"
    dep_names = [d["name"] for d in res["dependencies"]]
    dev_names = [d["name"] for d in res["dev_dependencies"]]
    assert "clap" in dep_names
    assert "tokio" in dep_names
    assert "tempfile" in dev_names

    (tmp_path / "Cargo.toml").unlink()

    # Node parsing
    pkg_json = {
        "name": "demo",
        "dependencies": {"react": "^18.0.0", "next": "^14.0.0"},
        "devDependencies": {"typescript": "^5.0.0"}
    }
    (tmp_path / "package.json").write_text(json.dumps(pkg_json), encoding="utf-8")
    res_node = list_dependencies(cwd=tmp_path)
    assert res_node["ecosystem"] == "node"
    assert len(res_node["dependencies"]) == 2
    assert len(res_node["dev_dependencies"]) == 1


def test_cli_deps_commands(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "Cargo.toml").write_text('[package]\nname = "test"\n', encoding="utf-8")

    with patch("adevkit.deps.detect_cargo", return_value="cargo"), \
         patch("adevkit.deps.run_command", return_value=(0, "ok", "")):
        # Test adevkit add
        res_add = runner.invoke(app, ["add", "serde"])
        assert res_add.exit_code == 0
        assert "Added Rust dependencies" in res_add.stdout

        # Test adevkit deps add
        res_deps_add = runner.invoke(app, ["deps", "add", "tokio", "--dev"])
        assert res_deps_add.exit_code == 0
        assert "(dev)" in res_deps_add.stdout

        # Test adevkit remove
        res_rm = runner.invoke(app, ["remove", "serde"])
        assert res_rm.exit_code == 0
        assert "Removed Rust dependencies: serde" in res_rm.stdout

        # Test adevkit deps list
        res_list = runner.invoke(app, ["deps", "list"])
        assert res_list.exit_code == 0
        assert "Project Dependencies" in res_list.stdout
