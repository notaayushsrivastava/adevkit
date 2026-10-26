from pathlib import Path
from adevkit.vault import (
    set_config,
    get_config,
    delete_config,
    list_configs,
    get_default_agents,
    set_default_agents,
    get_preferred_python_pm,
    set_preferred_python_pm,
)


def test_vault_set_and_get(tmp_path, monkeypatch):
    test_vault = tmp_path / "test_vault.json"
    monkeypatch.setattr("adevkit.vault.VAULT_FILE", test_vault)

    set_config("my_plain_config", "alpha-value")
    set_config("my_api_key", "sk-secret-token-998877")

    assert get_config("my_plain_config") == "alpha-value"
    assert get_config("my_api_key") == "sk-secret-token-998877"

    # Test list masking
    listed = list_configs(reveal_secrets=False)
    assert listed["my_plain_config"] == "alpha-value"
    assert "sk-secret-token-998877" not in listed["my_api_key"]
    assert "[encrypted]" in listed["my_api_key"]

    # Test list reveal
    revealed = list_configs(reveal_secrets=True)
    assert revealed["my_api_key"] == "sk-secret-token-998877"

    # Test delete
    assert delete_config("my_api_key") is True
    assert get_config("my_api_key") is None
    assert delete_config("non_existent") is False


def test_vault_default_agents(tmp_path, monkeypatch):
    test_vault = tmp_path / "test_vault.json"
    monkeypatch.setattr("adevkit.vault.VAULT_FILE", test_vault)

    # Defaults before configuration
    assert "antigravity" in get_default_agents()

    # Custom configuration
    set_default_agents(["cursor", "windsurf"])
    assert get_default_agents() == ["cursor", "windsurf"]


def test_vault_python_pm_preference(tmp_path, monkeypatch):
    test_vault = tmp_path / "test_vault.json"
    monkeypatch.setattr("adevkit.vault.VAULT_FILE", test_vault)

    assert get_preferred_python_pm() is None
    set_preferred_python_pm("uv")
    assert get_preferred_python_pm() == "uv"
    set_preferred_python_pm("pip")
    assert get_preferred_python_pm() == "pip"
