from rich.table import Table

from ... import __version__
from ..ui import console, print_banner
from ...core.utils.system import (
    detect_node_package_manager,
    detect_git,
    detect_uv,
    detect_python,
    detect_cargo,
    get_rustc_version,
    which_tool,
)
from ...core.vault import (
    get_preferred_python_pm,
    get_preferred_node_pm,
)
from ...core.updater import (
    detect_installation_type,
    load_cached_update,
)


def system_info():
    """Display environment diagnostics and detected tooling."""
    print_banner()
    table = Table(title="System & Runtime Diagnostics", border_style="blue")
    table.add_column("Tool / Property", style="bold yellow", width=25)
    table.add_column("Status / Path", style="white")

    table.add_row("DevKit Version", __version__)

    install_type = detect_installation_type()
    if install_type == "msi":
        display_type = "Windows Native MSI / Executable"
    elif install_type in ("linux_binary", "linux"):
        display_type = "Linux Standalone Binary / Package"
    elif install_type in ("macos_binary", "macos"):
        display_type = "macOS Standalone Binary / PKG"
    else:
        display_type = "Python Package (pip / adevkit)"
    table.add_row("Installation Type", display_type)

    cached = load_cached_update()
    if cached and cached.get("install_type") == install_type:
        latest = cached.get("latest_version")
        if cached.get("update_available"):
            table.add_row("Update Status", f"[yellow]v{latest} available! (Run `adevkit check-update`)[/yellow]")
        else:
            table.add_row("Update Status", f"[green]Up to date (v{__version__})[/green]")
    else:
        table.add_row("Update Status", "Run `adevkit check-update` to verify")

    table.add_row("Python Executable", detect_python())

    uv_loc = detect_uv()
    table.add_row("uv Available", f"Yes ({uv_loc})" if uv_loc else "No (astral.sh/uv)")
    pref_pm = get_preferred_python_pm()
    table.add_row("Preferred Python PM", pref_pm or ("uv (auto)" if uv_loc else "pip / venv"))

    table.add_row("Git Available", "Yes" if detect_git() else "No (Not in PATH)")

    cargo_loc = detect_cargo()
    table.add_row("Cargo (Rust PM)", f"Yes ({cargo_loc})" if cargo_loc else "No (Not in PATH)")
    rustc_ver = get_rustc_version()
    table.add_row("Rust Compiler (rustc)", rustc_ver or "Not found")

    pref_node_pm = get_preferred_node_pm()
    node_pm = detect_node_package_manager()
    node_pm_display = f"{node_pm} ({which_tool(node_pm) or 'Not Installed'})"
    if pref_node_pm:
        node_pm_display += f" [cyan](configured: {pref_node_pm})[/cyan]"
    table.add_row("Preferred Node PM", node_pm_display)

    for pm in ["bun", "pnpm", "yarn", "npm"]:
        tool_loc = which_tool(pm)
        table.add_row(f"Node PM ({pm})", tool_loc or "Not found")

    console.print(table)
