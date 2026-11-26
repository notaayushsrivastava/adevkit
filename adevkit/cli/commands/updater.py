import sys
from typing import Optional, Annotated
import typer
from rich.table import Table

from ... import __version__
from ..ui import console, success, info, error
from ...core.updater import (
    detect_installation_type,
    check_for_updates,
    check_pypi_update,
    check_msi_update,
)


def check_update_command(
    mode: Annotated[
        Optional[str],
        typer.Option("--type", "-t", help="Installation type to check ('python', 'msi', or 'all')"),
    ] = None,
):
    """Check for latest updates for Aayush's DevKit via PyPI or GitHub MSI."""
    target_mode = (mode or "").lower()

    if target_mode == "all":
        with console.status("[cyan]Checking PyPI and GitHub for updates...[/cyan]", spinner="dots"):
            py_res = check_pypi_update(timeout=4.0)
            msi_res = check_msi_update(timeout=4.0)

        table = Table(title="Update Check Results", border_style="cyan")
        table.add_column("Channel / Package", style="bold yellow", width=25)
        table.add_column("Current Version", style="white", width=18)
        table.add_column("Latest Version", style="magenta", width=18)
        table.add_column("Status / Action", style="white")

        if py_res:
            py_status = "[bold green]Up to date[/bold green]" if not py_res["update_available"] else f"[bold yellow]Run: {py_res['update_command']}[/bold yellow]"
            table.add_row("Python Package (adevkit)", py_res["current_version"], py_res["latest_version"], py_status)
        else:
            table.add_row("Python Package (adevkit)", __version__, "Unknown", "[red]Check failed[/red]")

        if msi_res:
            msi_status = "[bold green]Up to date[/bold green]" if not msi_res["update_available"] else f"[bold yellow]{msi_res['update_command']}[/bold yellow]"
            table.add_row("Windows Native MSI", msi_res["current_version"], msi_res["latest_version"], msi_status)
        else:
            table.add_row("Windows Native MSI", __version__, "Unknown", "[red]Check failed[/red]")

        console.print(table)
        return

    active_type = target_mode if target_mode in ("msi", "python", "binary", "linux", "macos") else detect_installation_type()
    if active_type in ("msi", "binary", "linux_binary", "macos_binary"):
        if sys.platform == "win32":
            channel_name = "Windows Native MSI (GitHub Releases)"
        elif sys.platform.startswith("linux"):
            channel_name = "Linux Package / Binary (GitHub Releases)"
        elif sys.platform == "darwin":
            channel_name = "macOS Package / Binary (GitHub Releases)"
        else:
            channel_name = "Standalone Binary (GitHub Releases)"
    else:
        channel_name = "Python Package (PyPI adevkit)"

    with console.status(f"[cyan]Checking {channel_name} for updates...[/cyan]", spinner="dots"):
        res = check_for_updates(force=True, mode=active_type, timeout=4.0)

    if not res or not res.get("latest_version"):
        error(f"Failed to fetch update information for {channel_name}. Please check your internet connection.")
        return

    curr = res.get("current_version", __version__)
    latest = res.get("latest_version", "")
    has_update = res.get("update_available", False)

    if has_update:
        info(f"Update available for {channel_name}: v{curr} -> v{latest}")
        if active_type == "python":
            console.print(f"  Run: [bold cyan]{res['update_command']}[/bold cyan]")
        else:
            download_url = res.get("url", "")
            cmd_str = res.get("update_command") or f"Download from: {download_url}"
            console.print(f"  {cmd_str}")
    else:
        success(f"Aayush's DevKit is up to date (v{curr} via {channel_name}).")
