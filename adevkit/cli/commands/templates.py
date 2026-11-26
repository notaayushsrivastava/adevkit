from pathlib import Path
from typing import Optional, Annotated
import typer
from rich.table import Table

from ..ui import console, success, error
from ...core.templates import (
    get_all_templates,
    save_custom_template,
    delete_custom_template,
)

template_app = typer.Typer(help="Manage and save custom reusable templates.")


@template_app.command(name="save")
def template_save(
    name: Annotated[str, typer.Argument(help="Name for the new custom template")],
    path: Annotated[
        Optional[str],
        typer.Option("--path", "-p", help="Directory path to snapshot (defaults to current directory)"),
    ] = None,
    description: Annotated[
        str,
        typer.Option("--desc", "-d", help="Description of the template"),
    ] = "",
):
    """Snapshot a project folder into a reusable custom template."""
    src_dir = Path(path).resolve() if path else Path.cwd()
    if not src_dir.exists() or not src_dir.is_dir():
        error(f"Source directory does not exist: {src_dir}")
        raise typer.Exit(1)

    with console.status(f"[cyan]Saving template '{name}' from {src_dir}...[/cyan]", spinner="dots"):
        saved_path = save_custom_template(name=name, source_dir=src_dir, description=description)
        success(f"Custom template '{name}' saved successfully at: {saved_path}")


@template_app.command(name="list")
def template_list():
    """List all built-in and custom saved templates."""
    templates = get_all_templates()
    table = Table(title="Available Project Templates", border_style="cyan")
    table.add_column("Template ID", style="bold yellow", width=18)
    table.add_column("Type", style="magenta", width=10)
    table.add_column("Name", style="white", width=35)
    table.add_column("Description", style="dim")

    for t in templates:
        tmpl_type = "Custom" if t["is_custom"] else "Built-in"
        table.add_row(t["id"], tmpl_type, t["name"], t["description"])

    console.print(table)


@template_app.command(name="delete")
def template_delete(
    name: Annotated[str, typer.Argument(help="Name or ID of the custom template to delete")],
):
    """Delete a user-saved custom template."""
    deleted = delete_custom_template(name)
    if deleted:
        success(f"Custom template '{name}' deleted.")
    else:
        error(f"Custom template '{name}' not found.")
