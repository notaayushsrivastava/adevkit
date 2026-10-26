import io
import json
import time
from unittest.mock import patch, MagicMock
from typer.testing import CliRunner
from rich.console import Console

from adevkit.updater import (
    detect_installation_type,
    is_newer_version,
    parse_semver,
    check_pypi_update,
    check_msi_update,
    check_binary_update,
    load_cached_update,
    save_cached_update,
    check_for_updates,
    notify_update_if_available,
    CACHE_TTL_SECONDS,
)
from adevkit.cli import app

runner = CliRunner()


def test_detect_installation_type(monkeypatch):
    # Test environment variable overrides
    monkeypatch.setenv("DEVKIT_INSTALL_TYPE", "msi")
    assert detect_installation_type() == "msi"

    monkeypatch.setenv("DEVKIT_INSTALL_TYPE", "python")
    assert detect_installation_type() == "python"

    monkeypatch.delenv("DEVKIT_INSTALL_TYPE", raising=False)
    # Default without sys.frozen
    assert detect_installation_type() == "python"


def test_version_comparisons():
    assert is_newer_version("0.1.3", "0.1.2") is True
    assert is_newer_version("0.1.2", "0.1.1") is True
    assert is_newer_version("1.0.0", "0.1.1") is True
    assert is_newer_version("v0.2.0", "0.1.1") is True
    assert is_newer_version("0.1.1", "0.1.1") is False
    assert is_newer_version("0.1.0", "0.1.1") is False
    assert is_newer_version("0.1.0", "v0.1.1") is False


def test_check_pypi_update_success():
    fake_response = {
        "info": {
            "version": "0.2.0",
            "project_url": "https://pypi.org/project/adevkit/",
        }
    }
    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.read.return_value = json.dumps(fake_response).encode("utf-8")
    mock_resp.__enter__.return_value = mock_resp

    with patch("urllib.request.urlopen", return_value=mock_resp):
        res = check_pypi_update(current_version="0.1.1")
        assert res is not None
        assert res["install_type"] == "python"
        assert res["latest_version"] == "0.2.0"
        assert res["update_available"] is True
        assert "pip install --upgrade adevkit" in res["update_command"]


def test_check_msi_update_success():
    fake_response = {
        "tag_name": "v0.2.0",
        "html_url": "https://github.com/notaayushsrivastava/adevkit/releases/tag/v0.2.0",
        "assets": [
            {
                "name": "AayushsDevKit-v0.2.0-x64.msi",
                "browser_download_url": "https://github.com/notaayushsrivastava/adevkit/releases/download/v0.2.0/AayushsDevKit-v0.2.0-x64.msi",
            }
        ],
    }
    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.read.return_value = json.dumps(fake_response).encode("utf-8")
    mock_resp.__enter__.return_value = mock_resp

    with patch("urllib.request.urlopen", return_value=mock_resp):
        res = check_msi_update(current_version="0.1.1")
        assert res is not None
        assert res["install_type"] == "msi"
        assert res["latest_version"] == "0.2.0"
        assert res["update_available"] is True
        assert res["url"].endswith(".msi")


def test_check_linux_and_macos_update_success():
    fake_response = {
        "tag_name": "v0.2.0",
        "html_url": "https://github.com/notaayushsrivastava/adevkit/releases/tag/v0.2.0",
        "assets": [
            {
                "name": "adevkit_0.2.0_amd64.deb",
                "browser_download_url": "https://github.com/notaayushsrivastava/adevkit/releases/download/v0.2.0/adevkit_0.2.0_amd64.deb",
            },
            {
                "name": "AayushsDevKit-v0.2.0-macos.pkg",
                "browser_download_url": "https://github.com/notaayushsrivastava/adevkit/releases/download/v0.2.0/AayushsDevKit-v0.2.0-macos.pkg",
            },
        ],
    }
    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.read.return_value = json.dumps(fake_response).encode("utf-8")
    mock_resp.__enter__.return_value = mock_resp

    with patch("urllib.request.urlopen", return_value=mock_resp):
        # Linux test
        res_linux = check_binary_update(current_version="0.1.1", target_platform="linux")
        assert res_linux is not None
        assert res_linux["install_type"] == "binary"
        assert res_linux["latest_version"] == "0.2.0"
        assert res_linux["url"].endswith(".deb")

        # macOS test
        res_mac = check_binary_update(current_version="0.1.1", target_platform="darwin")
        assert res_mac is not None
        assert res_mac["install_type"] == "binary"
        assert res_mac["latest_version"] == "0.2.0"
        assert res_mac["url"].endswith(".pkg")


def test_frozen_installation_platforms(monkeypatch):
    import sys
    monkeypatch.setattr(sys, "frozen", True, raising=False)

    monkeypatch.setattr(sys, "platform", "win32")
    assert detect_installation_type() == "msi"

    monkeypatch.setattr(sys, "platform", "linux")
    assert detect_installation_type() == "linux_binary"

    monkeypatch.setattr(sys, "platform", "darwin")
    assert detect_installation_type() == "macos_binary"


def test_check_update_network_error():
    with patch("urllib.request.urlopen", side_effect=Exception("Connection timed out")):
        res_pypi = check_pypi_update(current_version="0.1.1")
        assert res_pypi is None

        res_msi = check_msi_update(current_version="0.1.1")
        assert res_msi is None


def test_cache_lifecycle(tmp_path, monkeypatch):
    test_cache_file = tmp_path / "test_update_cache.json"
    monkeypatch.setattr("adevkit.updater.UPDATE_CACHE_FILE", test_cache_file)

    payload = {
        "install_type": "python",
        "current_version": "0.1.1",
        "latest_version": "0.2.0",
        "update_available": True,
        "update_command": "pip install --upgrade adevkit",
        "url": "https://pypi.org/project/adevkit/",
    }
    save_cached_update(payload)
    assert test_cache_file.exists()

    loaded = load_cached_update(max_age_seconds=100)
    assert loaded is not None
    assert loaded["latest_version"] == "0.2.0"

    # Expired cache test
    expired = load_cached_update(max_age_seconds=-1)
    assert expired is None


def test_notify_update_if_available(tmp_path, monkeypatch):
    test_cache_file = tmp_path / "test_update_cache.json"
    monkeypatch.setattr("adevkit.updater.UPDATE_CACHE_FILE", test_cache_file)

    # 1. When update is available
    save_cached_update({
        "install_type": "python",
        "current_version": "0.1.1",
        "latest_version": "0.3.0",
        "update_available": True,
        "update_command": "pip install --upgrade adevkit",
        "url": "https://pypi.org/project/adevkit/",
    })

    test_console = Console(record=True)
    notify_update_if_available(console_obj=test_console, auto_check_background=False)
    output = test_console.export_text()
    assert "Update Available" in output
    assert "v0.3.0" in output
    assert "pip install --upgrade adevkit" in output


def test_cli_check_update_command():
    fake_pypi = {
        "info": {
            "version": "0.1.1",
            "project_url": "https://pypi.org/project/adevkit/",
        }
    }
    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.read.return_value = json.dumps(fake_pypi).encode("utf-8")
    mock_resp.__enter__.return_value = mock_resp

    with patch("urllib.request.urlopen", return_value=mock_resp):
        res = runner.invoke(app, ["check-update", "--type", "python"])
        assert res.exit_code == 0
        assert "Aayush's DevKit is up to date" in res.output
