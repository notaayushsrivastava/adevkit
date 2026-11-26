from pathlib import Path
from typing import Optional, List, Annotated
import typer

from ..ui import (
    console,
    print_banner,
    success,
    info,
    warning,
    error,
    section,
    print_summary_table,
)
from ...core.utils.system import (
    detect_node_package_manager,
    detect_uv,
)
from ...core.skills.catalog import (
    AVAILABLE_SKILLS,
    get_recommended_skills_for_template,
)
from ...core.skills.installer import install_skills
from ...core.templates import (
    BUILTIN_TEMPLATES,
    get_all_templates,
    CustomProjectTemplate,
)
from ...core.scaffold import (
    generate_prd_template,
    import_prd_file,
    setup_git_repository,
    setup_python_environment,
    setup_node_environment,
    setup_rust_environment,
    setup_dotenv_file,
    setup_vscode_config,
    scaffold_agent_configs,
)
from ...core.vault import (
    get_config,
    get_default_agents,
    get_preferred_python_pm,
)
from ...core.prompts import (
    prompt_project_name,
    prompt_template_selection,
    prompt_expo_backend_stack,
    prompt_skills_selection,
    prompt_agents_selection,
    prompt_readme_template,
    prompt_prd_mode,
    prompt_env_options,
)
from ...core.readmes import (
    list_readme_templates,
    generate_project_readme,
)


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
        has_rust = False
    else:
        has_node = template_info["has_node"]
        has_python = template_info["has_python"]
        has_rust = template_info.get("has_rust", False)

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
            "rust": has_rust,
            "uv": use_uv_final,
        }
    else:
        env_config = prompt_env_options(has_python, has_node, default_use_uv=default_uv, has_rust=has_rust)

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

    # J. Rust dependencies check
    if env_config.get("rust") or (has_rust and (dest_path / "Cargo.toml").exists()):
        with console.status("[cyan]Verifying Rust toolchain and dependencies (cargo)...[/cyan]", spinner="dots"):
            r_ok, r_msg = setup_rust_environment(dest_path)
            if r_ok:
                success(r_msg)
            else:
                warning(r_msg)

    # Final Celebration Message
    section("Project Successfully Initialized!")
    console.print(f"[bold green]Location:[/bold green] [underline]{dest_path}[/underline]")
    console.print("[bold yellow]Next Steps:[/bold yellow]")
    console.print(f"  1. [cyan]cd {dest_path.name}[/cyan]")
    if has_rust:
        console.print("  2. Run or test Rust project:")
        console.print("     - Run:   [cyan]cargo run[/cyan]")
        console.print("     - Test:  [cyan]cargo test[/cyan]")
        console.print("     - Add:   [cyan]adevkit add <crate>[/cyan]")
    if has_python:
        console.print("  2. Activate virtual environment:")
        console.print("     - Windows: [cyan].\\.venv\\Scripts\\activate[/cyan]")
        console.print("     - POSIX:   [cyan]source .venv/bin/activate[/cyan]")
    if has_node:
        pm = detect_node_package_manager()
        console.print(f"  3. Start dev server: [cyan]{pm} run dev[/cyan]")
    console.print("  4. Open project in your favorite editor (e.g. [cyan]code .[/cyan])")
    console.print()
