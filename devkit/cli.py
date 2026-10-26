import os
import sys
from pathlib import Path
from typing import Optional, List
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
from .prompts import (
    prompt_project_name,
    prompt_template_selection,
    prompt_skills_selection,
    prompt_prd_mode,
    prompt_env_options,
)

app = typer.Typer(
    name="devkit",
    help="⚡ Aayush's DevKit - Single-command project initialization with Agentic skills and environments.",
    add_completion=False,
)

template_app = typer.Typer(help="Manage and save custom reusable templates.")
skills_app = typer.Typer(help="Inspect and install agent skills.")
app.add_typer(template_app, name="template")
app.add_typer(skills_app, name="skills")


@app.callback(invoke_without_command=True)
def main_entry(ctx: typer.Context):
    """If no subcommand is passed, default to interactive init."""
    if ctx.invoked_subcommand is None:
        init()


@app.command(name="init")
def init(
    target_dir: Optional[str] = typer.Argument(
        None, help="Directory to initialize the project in (defaults to project name)"
    ),
    name: Optional[str] = typer.Option(
        None, "--name", "-n", help="Project name"
    ),
    template: Optional[str] = typer.Option(
        None, "--template", "-t", help="Template ID (e.g. nextjs, python_fastapi, vite_react, minimal_agentic, expo_mobile)"
    ),
    skills: Optional[List[str]] = typer.Option(
        None, "--skill", "-s", help="Skill ID(s) to install"
    ),
    yes: bool = typer.Option(
        False, "--yes", "-y", help="Skip interactive prompts and use defaults"
    ),
):
    """Initialize a brand new project with templates, agent skills, environments, and docs."""
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
    section("🎉 Project Successfully Initialized!")
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
    name: str = typer.Argument(..., help="Name for the new custom template"),
    path: Optional[str] = typer.Option(
        None, "--path", "-p", help="Directory path to snapshot (defaults to current directory)"
    ),
    description: str = typer.Option(
        "", "--desc", "-d", help="Description of the template"
    ),
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
    table = Table(title="📦 Available Project Templates", border_style="cyan")
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
    name: str = typer.Argument(..., help="Name or ID of the custom template to delete"),
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
    table = Table(title="🤖 Curated Agent Skills Catalog", border_style="green")
    table.add_column("Skill ID", style="bold yellow", width=22)
    table.add_column("Category", style="cyan", width=25)
    table.add_column("Description", style="white")

    for sid, s in AVAILABLE_SKILLS.items():
        table.add_row(sid, s.category, s.description)

    console.print(table)


@skills_app.command(name="add")
def skills_add(
    skill_name: str = typer.Argument(..., help="ID of the skill to install"),
    target: Optional[str] = typer.Option(
        None, "--target", "-t", help="Target project root directory (defaults to current dir)"
    ),
):
    """Install an agent skill into the target project's .agents/skills/."""
    target_path = Path(target).resolve() if target else Path.cwd()
    if skill_name not in AVAILABLE_SKILLS:
        error(f"Skill '{skill_name}' not found in catalog. Run `devkit skills list` to view options.")
        raise typer.Exit(1)

    with console.status(f"[cyan]Installing {skill_name}...[/cyan]", spinner="dots"):
        res = install_skills(target_path, [skill_name])
        success(f"Installed '{skill_name}' into {res['skills_dir']}")


# --- Info Command ---

@app.command(name="info")
def system_info():
    """Display environment diagnostics and detected tooling."""
    print_banner()
    table = Table(title="🛠 System & Runtime Diagnostics", border_style="blue")
    table.add_column("Tool / Property", style="bold yellow", width=25)
    table.add_column("Status / Path", style="white")

    table.add_row("DevKit Version", __version__)
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
