from pathlib import Path
from typing import Optional, Annotated
import typer
from rich.table import Table

from ..ui import console, success, error
from ...core.skills.catalog import AVAILABLE_SKILLS, load_all_skills
from ...core.skills.custom import (
    add_custom_skill,
    create_custom_skill,
    remove_custom_skill,
)

skills_app = typer.Typer(help="Inspect, create, and install agent skills (like skills.sh).")


@skills_app.command(name="list")
def skills_list():
    """List all available curated agent skills in DevKit."""
    table = Table(title="Curated Agent Skills Catalog", border_style="green")
    table.add_column("Skill ID", style="bold yellow", width=22)
    table.add_column("Category", style="cyan", width=25)
    table.add_column("Description", style="white")

    for sid, s in AVAILABLE_SKILLS.items():
        table.add_row(sid, s.category, s.description)

    console.print(table)


@skills_app.command(name="add")
def skills_add(
    source: Annotated[str, typer.Argument(help="Skill ID, GitHub repo (owner/repo or URL), or local path to install")],
    target: Annotated[
        Optional[str],
        typer.Option("--target", "-t", help="Target project root directory (defaults to current dir)"),
    ] = None,
    is_global: Annotated[
        bool,
        typer.Option("--global", "-g", help="Install into global user skills store (~/.adevkit/skills/) for all projects"),
    ] = False,
    name: Annotated[
        Optional[str],
        typer.Option("--name", "-n", help="Custom alias or override name for the skill"),
    ] = None,
):
    """Add a skill from local path, GitHub repository/shorthand, URL, or catalog (like skills.sh)."""
    target_path = Path(target).resolve() if target else Path.cwd()
    with console.status(f"[cyan]Adding skill '{source}'...[/cyan]", spinner="dots"):
        try:
            res = add_custom_skill(
                source=source,
                target_dir=target_path,
                is_global=is_global,
                custom_name=name,
            )
            scope = "globally (~/.adevkit/skills/)" if is_global else f"into {res['destination']}"
            success(f"Successfully added skill '{res['skill_id']}' {scope}")
        except Exception as e:
            error(f"Failed to add skill '{source}': {e}")
            raise typer.Exit(1)


@skills_app.command(name="create")
def skills_create(
    name: Annotated[str, typer.Argument(help="Name of the new skill to scaffold")],
    target: Annotated[
        Optional[str],
        typer.Option("--target", "-t", help="Target project root directory (defaults to current dir)"),
    ] = None,
    is_global: Annotated[
        bool,
        typer.Option("--global", "-g", help="Create in global user skills store (~/.adevkit/skills/)"),
    ] = False,
    description: Annotated[
        str,
        typer.Option("--desc", "-d", help="Short description of what the skill does"),
    ] = "",
):
    """Scaffold a new custom agent skill (SKILL.md & references/)."""
    target_path = Path(target).resolve() if target else Path.cwd()
    dest = create_custom_skill(name=name, target_dir=target_path, is_global=is_global, description=description)
    scope = "globally (~/.adevkit/skills/)" if is_global else f"in {dest}"
    success(f"Custom skill '{name}' created {scope}")


@skills_app.command(name="remove")
def skills_remove(
    name: Annotated[str, typer.Argument(help="Name of the custom skill to remove")],
    target: Annotated[
        Optional[str],
        typer.Option("--target", "-t", help="Target project root directory (defaults to current dir)"),
    ] = None,
    is_global: Annotated[
        bool,
        typer.Option("--global", "-g", help="Remove from global user skills store"),
    ] = False,
):
    """Remove a custom agent skill."""
    target_path = Path(target).resolve() if target else Path.cwd()
    removed = remove_custom_skill(name=name, target_dir=target_path, is_global=is_global)
    if removed:
        success(f"Skill '{name}' removed successfully.")
    else:
        error(f"Skill '{name}' not found.")


@skills_app.command(name="update")
def skills_update():
    """Verify and reload the embedded agent skills catalog and lockfile."""
    with console.status("[cyan]Verifying embedded agent skills catalog...[/cyan]", spinner="dots"):
        refreshed = load_all_skills()
        success(f"Successfully synced and indexed {len(refreshed)} agent skills in catalog.")
