from pathlib import Path
from unittest.mock import patch

from adevkit.templates import BUILTIN_TEMPLATES, RustCliTemplate, RustAxumTemplate
from adevkit.scaffold.env_setup import setup_rust_environment


def test_rust_templates_registered():
    assert "rust_cli" in BUILTIN_TEMPLATES
    assert "rust_axum" in BUILTIN_TEMPLATES
    assert BUILTIN_TEMPLATES["rust_cli"] is RustCliTemplate
    assert BUILTIN_TEMPLATES["rust_axum"] is RustAxumTemplate


def test_scaffold_rust_cli(tmp_path: Path):
    project_dir = tmp_path / "my_cli_tool"
    tmpl = RustCliTemplate(project_name="My CLI Tool", target_dir=project_dir, author="Aayush")
    assert tmpl.has_rust is True
    assert tmpl.has_python is False
    assert tmpl.has_node is False

    files = tmpl.scaffold()
    assert "Cargo.toml" in files
    assert "src/main.rs" in files
    assert ".gitignore" in files
    assert "README.md" in files

    cargo_content = (project_dir / "Cargo.toml").read_text(encoding="utf-8")
    assert 'name = "my-cli-tool"' in cargo_content
    assert 'authors = ["Aayush"]' in cargo_content
    assert 'clap = ' in cargo_content
    assert 'tokio = ' in cargo_content

    main_rs = (project_dir / "src" / "main.rs").read_text(encoding="utf-8")
    assert "use clap::" in main_rs
    assert "#[tokio::main]" in main_rs


def test_scaffold_rust_axum(tmp_path: Path):
    project_dir = tmp_path / "my_web_service"
    tmpl = RustAxumTemplate(project_name="My Web Service", target_dir=project_dir, author="Aayush")
    assert tmpl.has_rust is True

    files = tmpl.scaffold()
    assert "Cargo.toml" in files
    assert "src/main.rs" in files

    cargo_content = (project_dir / "Cargo.toml").read_text(encoding="utf-8")
    assert 'name = "my-web-service"' in cargo_content
    assert 'axum = ' in cargo_content
    assert 'tower-http = ' in cargo_content

    main_rs = (project_dir / "src" / "main.rs").read_text(encoding="utf-8")
    assert "use axum::" in main_rs
    assert "async fn health_check()" in main_rs


def test_setup_rust_environment(tmp_path: Path):
    # Case 1: No Cargo.toml -> returns True (skipped)
    ok, msg = setup_rust_environment(tmp_path)
    assert ok is True
    assert "No Cargo.toml found" in msg

    (tmp_path / "Cargo.toml").write_text('[package]\nname = "test"\n', encoding="utf-8")

    # Case 2: Cargo missing
    with patch("adevkit.scaffold.env_setup.detect_cargo", return_value=None):
        ok, msg = setup_rust_environment(tmp_path)
        assert ok is False
        assert "not found in PATH" in msg

    # Case 3: Cargo check succeeds
    with patch("adevkit.scaffold.env_setup.detect_cargo", return_value="cargo"), \
         patch("adevkit.scaffold.env_setup.run_command", return_value=(0, "Finished dev", "")):
        ok, msg = setup_rust_environment(tmp_path)
        assert ok is True
        assert "Verified Rust toolchain" in msg
