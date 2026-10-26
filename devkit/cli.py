import os
import sys
from pathlib import Path

# Windows consoles may use a legacy code page (for example cp1252) that cannot
# encode Unicode symbols used by Rich/Typer (such as ⚡). Force UTF-8 output
# where supported, and replace any unsupported characters as a safe fallback.
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        try:
            _stream.reconfigure(encoding="utf-8", errors="replace")
        except (OSError, ValueError):
            pass

from typing import Optional, List, Annotated
import typer
from rich.table import Table
from rich.status import Status

from . import __version__
from .ui import (
    console,
    print_banner,
    success,
    info,
    warning,
    error,
    section,
    print_summary_table,
)
from .utils.system import (
    detect_node_package_manager,
    detect_git,
    detect_python,
    which_tool,
)
from .skills.catalog import (
    AVAILABLE_SKILLS,
    SKILL_BUNDLES,
    get_recommended_skills_for_template,
)
from .skills.installer import install_skills
from .templates import (
    BUILTIN_TEMPLATES,
    get_all_templates,
    CustomProjectTemplate,
    list_custom_templates,
    save_custom_template,
    delete_custom_template,
)
from .scaffold import (
    generate_agents_md,
    generate_prd_template,
    import_prd_file,
    setup_git_repository,
    setup_python_environment,
    setup_node_environment,
    setup_dotenv_file,
    setup_vscode_config,
)
from .updater import (
    detect_installation_type,
    check_for_updates,
    check_pypi_update,
    check_msi_update,
    load_cached_update,
    notify_update_if_available,
)
from .prompts import (
    prompt_project_name,
    prompt_template_selection,
    prompt_expo_backend_stack,
    prompt_skills_selection,
    prompt_prd_mode,
    prompt_env_options,
)

app = typer.Typer(
    name="devkit",
    help="Aayush's DevKit - Single-command project initialization with Agentic skills and environments.",
    add_completion=False,
)

template_app = typer.Typer(help="Manage and save custom reusable templates.")
skills_app = typer.Typer(help="Inspect and install agent skills.")
app.add_typer(template_app, name="template")
app.add_typer(skills_app, name="skills")


@app.callback(invoke_without_command=True)
def main_entry(ctx: typer.Context):
    """If no subcommand is passed, default to interactive init."""
    notify_update_if_available()
    if ctx.invoked_subcommand is None:
        init()


@app.command(name="init")
def init(
    target_dir: Annotated[
        Optional[str],
        typer.Argument(help="Directory to initialize the project in (defaults to project name)"),
    ] = None,
    name: Annotated[
        Optional[str],
        typer.Option("--name", "-n", help="Project name"),
    ] = None,
    template: Annotated[
        Optional[str],
        typer.Option("--template", "-t", help="Template ID (e.g. nextjs, python_fastapi, vite_react, minimal_agentic, expo_mobile)"),
    ] = None,
    skills: Annotated[
        Optional[List[str]],
        typer.Option("--skill", "-s", help="Skill ID(s) to install"),
    ] = None,
    yes: Annotated[
        bool,
        typer.Option("--yes", "-y", help="Skip interactive prompts and use defaults"),
    ] = False,
):
    """Initialize a brand new project with templates, agent skills, environments, and docs."""
    # Defensive guard in case called directly as a Python function with default models
    if target_dir is not None and not isinstance(target_dir, str):
        target_dir = None
    if name is not None and not isinstance(name, str):
        name = None
    if template is not None and not isinstance(template, str):
        template = None
    if skills is not None and not isinstance(skills, list):
        skills = None
    if not isinstance(yes, bool):
        yes = False

    print_banner()

    all_templates = get_all_templates()

    # 1. Project Name & Target Directory
    if not name:
        if yes:
            project_name = target_dir or "my-agentic-project"
        else:
            default_proj = Path(target_dir).name if target_dir else "my-agentic-project"
            project_name = prompt_project_name(default_name=default_proj)
    else:
        project_name = name

    dest_path = Path(target_dir or project_name.lower().replace(" ", "-")).resolve()

    if dest_path.exists() and any(dest_path.iterdir()):
        warning(f"Target directory '{dest_path}' already exists and is not empty.")
        if not yes:
            if not typer.confirm("Continue and scaffold inside this directory?", default=True):
                info("Initialization cancelled.")
                raise typer.Exit(0)

    dest_path.mkdir(parents=True, exist_ok=True)

    # 2. Template Selection
    if not template:
        if yes:
            chosen_template_id = "minimal_agentic"
        else:
            chosen_template_id = prompt_template_selection(all_templates)
    else:
        chosen_template_id = template

    # Find template info
    template_info = next((t for t in all_templates if t["id"] == chosen_template_id), None)
    if not template_info:
        error(f"Unknown template ID: '{chosen_template_id}'")
        raise typer.Exit(1)

    expo_backend_stack = "fastapi"
    if chosen_template_id == "expo_fullstack":
        if not yes:
            expo_backend_stack = prompt_expo_backend_stack()
        has_node = True
        has_python = "fastapi" in expo_backend_stack or "python" in expo_backend_stack
    else:
        has_node = template_info["has_node"]
        has_python = template_info["has_python"]

    # 3. Agent Skills Selection
    recommended_skills = get_recommended_skills_for_template(chosen_template_id)
    if skills is None:
        if yes:
            chosen_skills = recommended_skills
        else:
            chosen_skills = prompt_skills_selection(AVAILABLE_SKILLS, recommended_skills)
    else:
        chosen_skills = skills

    # 4. PRD Mode Selection
    if yes:
        prd_config = {"mode": "quick", "overview": "", "target_users": "", "core_features": ""}
    else:
        prd_config = prompt_prd_mode()

    # 5. Environment Options
    if yes:
        env_config = {
            "git": True,
            "dotenv": True,
            "vscode": True,
            "venv": has_python,
            "node": has_node,
        }
    else:
        env_config = prompt_env_options(has_python, has_node)

    # Summary
    print_summary_table(
        project_name=project_name,
        target_dir=str(dest_path),
        template=template_info["name"],
        skills=chosen_skills,
        prd_mode=prd_config["mode"],
    )

    if not yes:
        if not typer.confirm("Ready to generate project?", default=True):
            info("Aborted by user.")
            raise typer.Exit(0)

    section("Scaffolding Project Files")

    # A. Template Files
    with console.status(f"[cyan]Scaffolding {template_info['name']} files...[/cyan]", spinner="dots"):
        if template_info["is_custom"]:
            custom_data = template_info["custom_data"]
            tmpl_instance = CustomProjectTemplate(
                project_name=project_name,
                target_dir=dest_path,
                template_dir=custom_data["path"],
                metadata=custom_data,
            )
        else:
            tmpl_cls = BUILTIN_TEMPLATES[chosen_template_id]
            if chosen_template_id == "expo_fullstack":
                tmpl_instance = tmpl_cls(project_name=project_name, target_dir=dest_path, backend_stack=expo_backend_stack)
            else:
                tmpl_instance = tmpl_cls(project_name=project_name, target_dir=dest_path)

        created_files = tmpl_instance.scaffold()
        success(f"Generated {len(created_files)} template files.")

    # B. Agent Skills & Lockfile
    if chosen_skills:
        with console.status("[cyan]Installing agent skills & generating skills-lock.json...[/cyan]", spinner="dots"):
            skill_res = install_skills(dest_path, chosen_skills)
            success(f"Installed {len(skill_res['installed'])} agent skill(s) into .agents/skills/")

    # C. AGENTS.md
    with console.status("[cyan]Generating customized AGENTS.md...[/cyan]", spinner="dots"):
        generate_agents_md(
            target_dir=dest_path,
            project_name=project_name,
            template_id=chosen_template_id,
            installed_skills=chosen_skills,
        )
        success("Created AGENTS.md with architecture & agent instructions.")

    # D. PRD.md
    if prd_config["mode"] == "generate":
        with console.status("[cyan]Generating PRD.md...[/cyan]", spinner="dots"):
            generate_prd_template(
                target_dir=dest_path,
                project_name=project_name,
                overview=prd_config.get("overview", ""),
                target_users=prd_config.get("target_users", ""),
                core_features=prd_config.get("core_features", ""),
            )
            success("Generated structured PRD.md.")
    elif prd_config["mode"] == "import" and prd_config.get("source_path"):
        with console.status("[cyan]Importing PRD.md...[/cyan]", spinner="dots"):
            import_prd_file(dest_path, prd_config["source_path"])
            success(f"Imported PRD.md from {prd_config['source_path']}")

    # E. Git & .gitignore
    if env_config.get("git"):
        with console.status("[cyan]Initializing Git repository & .gitignore...[/cyan]", spinner="dots"):
            git_ok = setup_git_repository(dest_path, has_python=has_python, has_node=has_node)
            if git_ok:
                success("Initialized Git repository and created .gitignore.")
            else:
                warning("Git initialization skipped or git not in PATH (created .gitignore).")

    # F. .env setup
    if env_config.get("dotenv"):
        copied = setup_dotenv_file(dest_path)
        if copied:
            success("Created .env from .env.example.")

    # G. .vscode setup
    if env_config.get("vscode"):
        setup_vscode_config(dest_path, has_python=has_python, has_node=has_node)
        success("Configured .vscode/ settings and recommended extensions.")

    # H. Python venv & pip
    if env_config.get("venv"):
        with console.status("[cyan]Setting up Python virtual environment and dependencies...[/cyan]", spinner="dots"):
            v_ok, v_msg = setup_python_environment(dest_path)
            if v_ok:
                success(v_msg)
            else:
                warning(v_msg)

    # I. Node modules install
    if env_config.get("node"):
        with console.status("[cyan]Installing Node.js dependencies...[/cyan]", spinner="dots"):
            n_ok, n_msg = setup_node_environment(dest_path)
            if n_ok:
                success(n_msg)
            else:
                warning(n_msg)

    # Final Celebration Message
    section("Project Successfully Initialized!")
    console.print(f"[bold green]Location:[/bold green] [underline]{dest_path}[/underline]")
    console.print("[bold yellow]Next Steps:[/bold yellow]")
    console.print(f"  1. [cyan]cd {dest_path.name}[/cyan]")
    if has_python:
        console.print("  2. Activate virtual environment:")
        console.print("     - Windows: [cyan].\\.venv\\Scripts\\activate[/cyan]")
        console.print("     - POSIX:   [cyan]source .venv/bin/activate[/cyan]")
    if has_node:
        pm = detect_node_package_manager()
        console.print(f"  3. Start dev server: [cyan]{pm} run dev[/cyan]")
    console.print("  4. Open project in your favorite editor (e.g. [cyan]code .[/cyan])")
    console.print()


# --- Template Subcommands ---

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


# --- Skills Subcommands ---

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
    skill_name: Annotated[str, typer.Argument(help="ID of the skill to install")],
    target: Annotated[
        Optional[str],
        typer.Option("--target", "-t", help="Target project root directory (defaults to current dir)"),
    ] = None,
):
    """Install an agent skill into the target project's .agents/skills/."""
    target_path = Path(target).resolve() if target else Path.cwd()
    if skill_name not in AVAILABLE_SKILLS:
        error(f"Skill '{skill_name}' not found in catalog. Run `devkit skills list` to view options.")
        raise typer.Exit(1)

    with console.status(f"[cyan]Installing {skill_name}...[/cyan]", spinner="dots"):
        res = install_skills(target_path, [skill_name])
        success(f"Installed '{skill_name}' into {res['skills_dir']}")


@skills_app.command(name="update")
def skills_update():
    """Verify and reload the embedded agent skills catalog and lockfile."""
    with console.status("[cyan]Verifying embedded agent skills catalog...[/cyan]", spinner="dots"):
        from .skills.catalog import load_all_skills
        refreshed = load_all_skills()
        success(f"Successfully synced and indexed {len(refreshed)} agent skills in catalog.")


# --- Update & Info Commands ---

@app.command(name="check-update")
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

    active_type = target_mode if target_mode in ("msi", "python") else detect_installation_type()
    channel_name = "Windows Native MSI (GitHub Releases)" if active_type == "msi" else "Python Package (PyPI adevkit)"

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
            console.print(f"  Download MSI installer: [bold cyan]{res['url']}[/bold cyan]")
    else:
        success(f"Aayush's DevKit is up to date (v{curr} via {channel_name}).")


@app.command(name="info")
def system_info():
    """Display environment diagnostics and detected tooling."""
    print_banner()
    table = Table(title="System & Runtime Diagnostics", border_style="blue")
    table.add_column("Tool / Property", style="bold yellow", width=25)
    table.add_column("Status / Path", style="white")

    table.add_row("DevKit Version", __version__)

    install_type = detect_installation_type()
    table.add_row(
        "Installation Type",
        "Windows Native MSI / Executable" if install_type == "msi" else "Python Package (pip / adevkit)",
    )

    cached = load_cached_update()
    if cached and cached.get("install_type") == install_type:
        latest = cached.get("latest_version")
        if cached.get("update_available"):
            table.add_row("Update Status", f"[yellow]v{latest} available! (Run `devkit check-update`)[/yellow]")
        else:
            table.add_row("Update Status", f"[green]Up to date (v{__version__})[/green]")
    else:
        table.add_row("Update Status", "Run `devkit check-update` to verify")

    table.add_row("Python Executable", detect_python())
    table.add_row("Git Available", "Yes" if detect_git() else "No (Not in PATH)")
    
    node_pm = detect_node_package_manager()
    table.add_row("Preferred Node PM", f"{node_pm} ({which_tool(node_pm) or 'Not Installed'})")

    for pm in ["bun", "pnpm", "yarn", "npm"]:
        tool_loc = which_tool(pm)
        table.add_row(f"Node PM ({pm})", tool_loc or "Not found")

    console.print(table)


def main():
    """Main CLI entrypoint."""
    app()


if __name__ == "__main__":
    main()
