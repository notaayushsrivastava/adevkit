from typing import Optional, List, Annotated
import typer
from rich.table import Table

from ..ui import console, success, info, error
from ...core.utils.system import detect_node_package_manager
from ...core.vault import (
    get_config,
    set_config,
    delete_config,
    list_configs,
    set_default_agents,
    get_preferred_python_pm,
    set_preferred_python_pm,
    get_preferred_node_pm,
    set_preferred_node_pm,
    _is_sensitive_key,
)

config_app = typer.Typer(help="Manage secure configuration vault and AI agent defaults.")


@config_app.command(name="list")
def config_list(
    reveal: Annotated[bool, typer.Option("--reveal", "-r", help="Reveal decrypted secret values")] = False,
):
    """List all configured settings and secrets (secrets masked by default)."""
    configs = list_configs(reveal_secrets=reveal)
    if not configs:
        info("No configurations found in vault (~/.adevkit/vault.json).")
        return

    table = Table(title="Secure Configuration Vault", border_style="cyan")
    table.add_column("Key", style="bold yellow", width=25)
    table.add_column("Value", style="white")

    for k, v in configs.items():
        table.add_row(k, str(v))

    console.print(table)


@config_app.command(name="set")
def config_set_cmd(
    key: Annotated[str, typer.Argument(help="Configuration key (e.g. anthropic_api_key, default_agents)")],
    value: Annotated[str, typer.Argument(help="Value to store securely")],
    secret: Annotated[Optional[bool], typer.Option("--secret/--no-secret", help="Explicitly mark as secret/plaintext")] = None,
):
    """Securely store a configuration value or secret in the vault."""
    set_config(key, value, secret=secret)
    success(f"Stored '{key}' in secure vault.")


@config_app.command(name="get")
def config_get_cmd(
    key: Annotated[str, typer.Argument(help="Configuration key to retrieve")],
    reveal: Annotated[bool, typer.Option("--reveal", "-r", help="Reveal unmasked value")] = False,
):
    """Retrieve a value from the secure configuration vault."""
    val = get_config(key)
    if val is None:
        error(f"Key '{key}' not found in vault.")
        raise typer.Exit(1)
    if _is_sensitive_key(key) and not reveal and isinstance(val, str):
        masked = f"{val[:4]}...{val[-4:]} [encrypted]" if len(val) > 8 else "*** [encrypted]"
        console.print(f"[bold yellow]{key}:[/bold yellow] {masked}")
    else:
        console.print(f"[bold yellow]{key}:[/bold yellow] {val}")


@config_app.command(name="delete")
def config_delete_cmd(
    key: Annotated[str, typer.Argument(help="Configuration key to remove")],
):
    """Remove a key from the secure configuration vault."""
    if delete_config(key):
        success(f"Deleted '{key}' from vault.")
    else:
        error(f"Key '{key}' not found in vault.")


@config_app.command(name="set-agents")
def config_set_agents_cmd(
    agents: Annotated[List[str], typer.Argument(help="List of default AI agent IDs (e.g. antigravity cursor claude)")],
):
    """Set global default AI agents for new project scaffolding."""
    set_default_agents(agents)
    success(f"Updated default AI agents to: {', '.join(agents)}")


@config_app.command(name="set-python-pm")
def config_set_python_pm_cmd(
    pm: Annotated[str, typer.Argument(help="Preferred Python package/environment manager: 'uv' or 'pip'")],
):
    """Set default preferred Python environment and package manager ('uv' or 'pip')."""
    norm = pm.strip().lower()
    if norm not in ("uv", "pip", "venv"):
        error("Please specify 'uv' or 'pip'.")
        raise typer.Exit(1)
    chosen = "uv" if norm == "uv" else "pip"
    set_preferred_python_pm(chosen)
    success(f"Updated default Python tool preference to: {chosen}")


@config_app.command(name="get-python-pm")
def config_get_python_pm_cmd():
    """Get the configured default Python package manager preference."""
    val = get_preferred_python_pm()
    if val:
        console.print(f"[bold yellow]preferred_python_pm:[/bold yellow] {val}")
    else:
        console.print("[bold yellow]preferred_python_pm:[/bold yellow] not explicitly set (defaults to uv if available, else pip)")


@config_app.command(name="set-node-pm")
def config_set_node_pm_cmd(
    pm: Annotated[str, typer.Argument(help="Preferred Node.js package manager: 'bun', 'pnpm', 'yarn', or 'npm'")],
):
    """Set default preferred Node.js package manager ('bun', 'pnpm', 'yarn', or 'npm')."""
    norm = pm.strip().lower()
    if norm not in ("bun", "pnpm", "yarn", "npm"):
        error("Please specify 'bun', 'pnpm', 'yarn', or 'npm'.")
        raise typer.Exit(1)
    set_preferred_node_pm(norm)
    success(f"Updated default Node.js tool preference to: {norm}")


@config_app.command(name="get-node-pm")
def config_get_node_pm_cmd():
    """Get the configured default Node.js package manager preference."""
    val = get_preferred_node_pm()
    if val:
        console.print(f"[bold yellow]preferred_node_pm:[/bold yellow] {val}")
    else:
        detected = detect_node_package_manager()
        console.print(f"[bold yellow]preferred_node_pm:[/bold yellow] not explicitly set (auto-detects: [cyan]{detected}[/cyan])")
