from pathlib import Path
from typing import List, Annotated
import typer
from rich.table import Table

from ..ui import console, success, warning, error
from ...core.deps import (
    add_dependencies,
    remove_dependencies,
    list_dependencies,
)

deps_app = typer.Typer(help="Manage project dependencies & libraries (Rust, JS/TS, Python).")


@deps_app.command(name="add")
def deps_add_cmd(
    packages: Annotated[List[str], typer.Argument(help="Names of packages/crates/libraries to install")],
    dev: Annotated[bool, typer.Option("--dev", "-D", help="Install as development dependency")] = False,
):
    """Add one or more libraries to the current project (Rust, JS/TS, Python)."""
    ok, msg = add_dependencies(packages, dev=dev)
    if ok:
        success(msg)
    else:
        error(msg)
        raise typer.Exit(1)


@deps_app.command(name="remove")
def deps_remove_cmd(
    packages: Annotated[List[str], typer.Argument(help="Names of packages/crates/libraries to remove")],
):
    """Remove one or more libraries from the current project."""
    ok, msg = remove_dependencies(packages)
    if ok:
        success(msg)
    else:
        error(msg)
        raise typer.Exit(1)


@deps_app.command(name="list")
def deps_list_cmd():
    """List dependencies of the current project."""
    info_data = list_dependencies()
    eco = info_data["ecosystem"]
    if eco == "unknown":
        warning("No recognized project manifest found in current directory (Cargo.toml, package.json, requirements.txt).")
        raise typer.Exit(0)

    manifest_name = Path(info_data["manifest"]).name if info_data["manifest"] else "manifest"
    table = Table(title=f"Project Dependencies ({eco.capitalize()} - {manifest_name})", border_style="cyan")
    table.add_column("Package", style="bold yellow")
    table.add_column("Version", style="magenta")
    table.add_column("Type", style="white")

    for d in info_data["dependencies"]:
        table.add_row(d["name"], d.get("version") or "-", "dependency")
    for d in info_data["dev_dependencies"]:
        table.add_row(d["name"], d.get("version") or "-", "[dim]devDependency[/dim]")

    console.print(table)
