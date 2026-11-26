from pathlib import Path
from typing import Optional, Annotated
import typer
from rich.table import Table
from rich.panel import Panel

from ..ui import console, success, error
from ...core.vault import get_config
from ...core.readmes import (
    list_readme_templates,
    get_readme_template,
    save_custom_readme,
    delete_custom_readme,
    generate_project_readme,
)

readme_app = typer.Typer(help="Manage and customize project README.md templates.")


@readme_app.command(name="list")
def readme_list():
    """List all available built-in and user-custom README templates."""
    templates = list_readme_templates()
    table = Table(title="Available README Templates", border_style="cyan")
    table.add_column("Template ID", style="bold yellow", width=18)
    table.add_column("Type", style="magenta", width=10)
    table.add_column("Name", style="white", width=32)
    table.add_column("Description", style="dim")

    for t in templates:
        tmpl_type = "Custom" if t["is_custom"] else "Built-in"
        table.add_row(t["id"], tmpl_type, t["name"], t["description"])

    console.print(table)


@readme_app.command(name="save")
def readme_save(
    name: Annotated[str, typer.Argument(help="Name for the custom README template")],
    path: Annotated[
        Optional[str],
        typer.Option("--path", "-p", help="Path to markdown file (defaults to current dir README.md)"),
    ] = None,
    content: Annotated[
        Optional[str],
        typer.Option("--content", "-c", help="Inline markdown content for the template"),
    ] = None,
):
    """Save a custom reusable README.md template to ~/.adevkit/readmes/."""
    if content:
        raw_text = content
    else:
        src = Path(path).resolve() if path else Path.cwd() / "README.md"
        if not src.exists():
            error(f"README source file does not exist: {src}")
            raise typer.Exit(1)
        raw_text = src.read_text(encoding="utf-8", errors="ignore")

    saved_path = save_custom_readme(name=name, content_or_path=raw_text)
    success(f"Custom README template '{name}' saved successfully at: {saved_path}")


@readme_app.command(name="show")
def readme_show(
    name: Annotated[str, typer.Argument(help="Template ID (e.g. modern, minimal, enterprise, agentic, custom:<NAME>)")],
):
    """Preview a README template's raw content."""
    text = get_readme_template(name)
    console.print(Panel(text, title=f"README Template: {name}", border_style="cyan"))


@readme_app.command(name="delete")
def readme_delete(
    name: Annotated[str, typer.Argument(help="Name of the custom README template to delete")],
):
    """Delete a user-saved custom README template."""
    if delete_custom_readme(name):
        success(f"Custom README template '{name}' deleted.")
    else:
        error(f"Custom README template '{name}' not found.")


@readme_app.command(name="generate")
def readme_generate(
    style: Annotated[str, typer.Option("--style", "-s", help="Template style to use")] = "modern",
    target: Annotated[
        Optional[str],
        typer.Option("--target", "-t", help="Target project root directory (defaults to current dir)"),
    ] = None,
    name: Annotated[
        Optional[str],
        typer.Option("--name", "-n", help="Project name override"),
    ] = None,
):
    """Generate or overwrite README.md for an existing project folder."""
    target_path = Path(target).resolve() if target else Path.cwd()
    proj_name = name or target_path.name
    ctx = {
        "project_name": proj_name,
        "template_id": "custom",
        "template_name": "Project",
        "description": f"Documentation for {proj_name}.",
        "author": get_config("default_author", "Developer"),
    }
    dest = generate_project_readme(target_path, template_style=style, context=ctx)
    success(f"Generated {dest} using '{style}' template.")
