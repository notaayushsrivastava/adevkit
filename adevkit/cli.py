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
    detect_uv,
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
    scaffold_agent_configs,
    SUPPORTED_AGENTS,
)
from .vault import (
    get_config,
    set_config,
    delete_config,
    list_configs,
    get_default_agents,
    set_default_agents,
    get_preferred_python_pm,
    set_preferred_python_pm,
    _is_sensitive_key,
)
from .skills.custom import (
    add_custom_skill,
    create_custom_skill,
    remove_custom_skill,
    list_custom_skills,
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
    prompt_agents_selection,
    prompt_readme_template,
    prompt_prd_mode,
    prompt_env_options,
)
from .readmes import (
    list_readme_templates,
    get_readme_template,
    save_custom_readme,
    delete_custom_readme,
    generate_project_readme,
)

app = typer.Typer(
    name="adevkit",
    help="adevkit (Aayush's DevKit) - Single-command project initialization with Agentic skills, AI agents, and environments.",
    add_completion=False,
)

template_app = typer.Typer(help="Manage and save custom reusable templates.")
skills_app = typer.Typer(help="Inspect, create, and install agent skills (like skills.sh).")
config_app = typer.Typer(help="Manage secure configuration vault and AI agent defaults.")

readme_app = typer.Typer(help="Manage and customize project README.md templates.")

app.add_typer(template_app, name="template")
app.add_typer(skills_app, name="skills")
app.add_typer(config_app, name="config")
app.add_typer(readme_app, name="readme")


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
    agents: Annotated[
        Optional[List[str]],
        typer.Option("--agent", "-a", help="Target AI agent ID(s) (e.g. antigravity, cursor, claude, copilot, windsurf, aider)"),
    ] = None,
    readme: Annotated[
        Optional[str],
        typer.Option("--readme", "-r", help="README template style (modern, minimal, enterprise, agentic, custom:<NAME>, or skip)"),
    ] = None,
    uv: Annotated[
        Optional[bool],
        typer.Option("--uv/--no-uv", help="Use uv for ultra-fast Python environment setup & package installation"),
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
    if agents is not None and not isinstance(agents, list):
        agents = None
    if readme is not None and not isinstance(readme, str):
        readme = None
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

    # 3b. AI Agents Selection
    if yes or agents:
        chosen_agents = agents or get_default_agents()
    else:
        chosen_agents = prompt_agents_selection(default_agents=agents)

    # 3c. README Template Selection
    if yes or readme:
        chosen_readme = (readme or "modern").lower()
    else:
        chosen_readme = prompt_readme_template(list_readme_templates())

    # 4. PRD Mode Selection
    if yes:
        prd_config = {"mode": "quick", "overview": "", "target_users": "", "core_features": ""}
    else:
        prd_config = prompt_prd_mode()

    # 5. Environment Options
    pref_pm = get_preferred_python_pm()
    default_uv = uv if uv is not None else (True if pref_pm == "uv" else (False if pref_pm in ("pip", "venv") else None))

    if yes:
        use_uv_final = default_uv if default_uv is not None else (detect_uv() is not None)
        env_config = {
            "git": True,
            "dotenv": True,
            "vscode": True,
            "venv": has_python,
            "node": has_node,
            "uv": use_uv_final,
        }
    else:
        env_config = prompt_env_options(has_python, has_node, default_use_uv=default_uv)

    # Summary
    print_summary_table(
        project_name=project_name,
        target_dir=str(dest_path),
        template=template_info["name"],
        skills=chosen_skills,
        prd_mode=prd_config["mode"],
        agents=chosen_agents,
        readme_style=chosen_readme,
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

    # C. AI Agent Configurations (AGENTS.md, Cursor, Claude Code, Copilot, etc.)
    with console.status("[cyan]Generating customized AI Agent configurations...[/cyan]", spinner="dots"):
        agent_files = scaffold_agent_configs(
            target_dir=dest_path,
            project_name=project_name,
            template_id=chosen_template_id,
            installed_skills=chosen_skills,
            selected_agents=chosen_agents,
        )
        success(f"Configured {len(agent_files)} AI agent guideline(s): {', '.join(chosen_agents)}")

    # D. README.md
    if chosen_readme != "skip":
        with console.status(f"[cyan]Generating {chosen_readme} README.md...[/cyan]", spinner="dots"):
            readme_ctx = {
                "project_name": project_name,
                "template_id": chosen_template_id,
                "template_name": template_info["name"],
                "description": prd_config.get("overview") or template_info.get("description", ""),
                "author": get_config("default_author", "Developer"),
                "skills": chosen_skills,
                "agents": chosen_agents,
            }
            generate_project_readme(dest_path, template_style=chosen_readme, context=readme_ctx)
            success(f"Generated customized README.md ({chosen_readme} style).")

    # E. PRD.md
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

    # H. Python venv & pip / uv
    if env_config.get("venv"):
        use_uv = bool(env_config.get("uv", False))
        pm_label = "uv" if (use_uv and detect_uv()) else "venv & pip"
        with console.status(f"[cyan]Setting up Python virtual environment and dependencies ({pm_label})...[/cyan]", spinner="dots"):
            v_ok, v_msg = setup_python_environment(dest_path, use_uv=use_uv)
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
        from .skills.catalog import load_all_skills
        refreshed = load_all_skills()
        success(f"Successfully synced and indexed {len(refreshed)} agent skills in catalog.")


# --- README Commands ---

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


# --- Config Commands ---

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


@app.command(name="info")
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
