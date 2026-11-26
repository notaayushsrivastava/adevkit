"""IPC & async service bridge connecting adevkit Studio UI to adevkit.core."""

import asyncio
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional, Callable

from .. import __version__
from ..core.templates import (
    BUILTIN_TEMPLATES,
    get_all_templates,
    CustomProjectTemplate,
    save_custom_template,
    delete_custom_template,
)
from ..core.skills.catalog import (
    AVAILABLE_SKILLS,
    get_recommended_skills_for_template,
    load_all_skills,
)
from ..core.skills.installer import install_skills
from ..core.skills.custom import (
    add_custom_skill,
    create_custom_skill,
    remove_custom_skill,
    list_custom_skills,
)
from ..core.scaffold import (
    scaffold_agent_configs,
    SUPPORTED_AGENTS,
    generate_prd_template,
    setup_git_repository,
    setup_dotenv_file,
    setup_vscode_config,
    setup_python_environment,
    setup_node_environment,
    setup_rust_environment,
)
from ..core.readmes import list_readme_templates, generate_project_readme
from ..core.deps import (
    list_dependencies,
    add_dependencies,
    remove_dependencies,
)
from ..core.vault import (
    list_configs,
    set_config,
    delete_config,
    get_config,
    get_default_agents,
    set_default_agents,
    get_preferred_python_pm,
    set_preferred_python_pm,
    get_preferred_node_pm,
    set_preferred_node_pm,
)
from ..core.updater import (
    detect_installation_type,
    check_for_updates,
    load_cached_update,
)
from ..core.utils.system import (
    detect_python,
    detect_git,
    detect_uv,
    detect_cargo,
    get_rustc_version,
    detect_node_package_manager,
    which_tool,
)


class DevKitBridge:
    """Backend service bridge exposed to the ReactPy GUI components."""

    def __init__(self):
        self._window = None

    def attach_window(self, window: Any) -> None:
        self._window = window

    def pick_folder(self, title: str = "Select Directory") -> Optional[str]:
        """Open native PyWebView folder picker dialog if a window is attached."""
        if self._window is None:
            return None
        try:
            import webview

            selection = self._window.create_file_dialog(webview.FOLDER_DIALOG)
            if selection and len(selection) > 0:
                return str(selection[0])
        except Exception:
            return None
        return None

    def get_system_overview(self) -> Dict[str, Any]:
        return {
            "version": __version__,
            "python": detect_python(),
            "git": detect_git(),
            "uv": detect_uv(),
            "cargo": detect_cargo(),
            "node_pm": detect_node_package_manager(),
        }

    async def get_diagnostics(self) -> Dict[str, Any]:
        """Gather toolchain diagnostics in parallel to eliminate waterfalls."""
        (
            py_exe,
            git_ok,
            uv_path,
            cargo_path,
            rustc_ver,
            node_pm,
            install_type,
            cached_update,
        ) = await asyncio.gather(
            asyncio.to_thread(detect_python),
            asyncio.to_thread(detect_git),
            asyncio.to_thread(detect_uv),
            asyncio.to_thread(detect_cargo),
            asyncio.to_thread(get_rustc_version),
            asyncio.to_thread(detect_node_package_manager),
            asyncio.to_thread(detect_installation_type),
            asyncio.to_thread(load_cached_update),
        )
        node_pms = {pm: which_tool(pm) for pm in ("bun", "pnpm", "yarn", "npm")}
        return {
            "version": __version__,
            "platform": sys.platform,
            "install_type": install_type,
            "cached_update": cached_update,
            "python": py_exe,
            "git": git_ok,
            "uv": uv_path,
            "preferred_python_pm": get_preferred_python_pm(),
            "cargo": cargo_path,
            "rustc": rustc_ver,
            "preferred_node_pm": get_preferred_node_pm(),
            "active_node_pm": node_pm,
            "node_pms": node_pms,
        }

    async def check_updates(self) -> Optional[Dict[str, Any]]:
        return await asyncio.to_thread(check_for_updates, True, None, 4.0)

    def get_templates(self) -> List[Dict[str, Any]]:
        return get_all_templates()

    def get_recommended_skills(self, template_id: str) -> List[str]:
        return get_recommended_skills_for_template(template_id)

    def get_readme_styles(self) -> List[Dict[str, Any]]:
        return list_readme_templates()

    def get_supported_agents(self) -> Dict[str, Any]:
        return SUPPORTED_AGENTS

    def get_skills(self) -> List[Dict[str, str]]:
        catalog = load_all_skills()
        custom_ids = {s["id"] for s in list_custom_skills()}
        return [
            {
                "id": sid,
                "category": skill.category,
                "description": skill.description,
                "is_custom": sid in custom_ids,
            }
            for sid, skill in catalog.items()
        ]

    async def install_skill(self, source: str, target: str, is_global: bool = False) -> Dict[str, Any]:
        target_path = Path(target).resolve() if target else Path.cwd()
        return await asyncio.to_thread(
            add_custom_skill, source=source, target_dir=target_path, is_global=is_global
        )

    async def create_skill(self, name: str, description: str = "", target: str = "", is_global: bool = True) -> Path:
        target_path = Path(target).resolve() if target else Path.cwd()
        return await asyncio.to_thread(
            create_custom_skill, name=name, target_dir=target_path, is_global=is_global, description=description
        )

    async def remove_skill(self, name: str, target: str = "", is_global: bool = True) -> bool:
        target_path = Path(target).resolve() if target else Path.cwd()
        return await asyncio.to_thread(
            remove_custom_skill, name=name, target_dir=target_path, is_global=is_global
        )

    async def snapshot_template(self, name: str, source_dir: str, description: str = "") -> Path:
        return await asyncio.to_thread(
            save_custom_template, name=name, source_dir=Path(source_dir).resolve(), description=description
        )

    async def remove_template(self, name: str) -> bool:
        return await asyncio.to_thread(delete_custom_template, name)

    def get_project_dependencies(self, cwd: Optional[str] = None) -> Dict[str, Any]:
        path = Path(cwd).resolve() if cwd else Path.cwd()
        return list_dependencies(cwd=path)

    async def install_dependency(self, packages: List[str], dev: bool = False, cwd: Optional[str] = None):
        path = Path(cwd).resolve() if cwd else Path.cwd()
        return await asyncio.to_thread(add_dependencies, packages, dev, path)

    async def uninstall_dependency(self, packages: List[str], cwd: Optional[str] = None):
        path = Path(cwd).resolve() if cwd else Path.cwd()
        return await asyncio.to_thread(remove_dependencies, packages, path)

    def get_vault_state(self, reveal: bool = False) -> Dict[str, Any]:
        return {
            "backend": "Hardware Protected · Windows DPAPI" if sys.platform == "win32" else "Salted Derived Key · POSIX",
            "configs": list_configs(reveal_secrets=reveal),
            "default_agents": get_default_agents(),
            "python_pm": get_preferred_python_pm() or "auto",
            "node_pm": get_preferred_node_pm() or "auto",
        }

    def set_vault_item(self, key: str, value: str, secret: Optional[bool] = None) -> None:
        set_config(key, value, secret=secret)

    def delete_vault_item(self, key: str) -> bool:
        return delete_config(key)

    def update_preferences(self, default_agents: List[str], python_pm: str, node_pm: str) -> None:
        set_default_agents(default_agents)
        if python_pm in ("uv", "pip"):
            set_preferred_python_pm(python_pm)
        if node_pm in ("bun", "pnpm", "yarn", "npm"):
            set_preferred_node_pm(node_pm)

    async def run_project_generation(
        self,
        *,
        project_name: str,
        target_dir: str,
        template_id: str,
        skills: List[str],
        agents: List[str],
        readme_style: str,
        prd_mode: str,
        init_git: bool,
        init_dotenv: bool,
        init_vscode: bool,
        init_env: bool,
        use_uv: bool,
        on_log: Callable[[str, str, str], None],
    ) -> bool:
        """Execute full scaffolding pipeline off the event loop and stream log lines."""

        def _execute() -> bool:
            dest_path = Path(target_dir).resolve()
            dest_path.mkdir(parents=True, exist_ok=True)
            on_log("$", f"adevkit init {project_name} --template {template_id}", "neutral")

            all_templates = get_all_templates()
            tmpl_info = next((t for t in all_templates if t["id"] == template_id), None)
            if not tmpl_info:
                on_log("[err]", f"Unknown template '{template_id}'", "danger")
                return False

            if tmpl_info["is_custom"]:
                cdata = tmpl_info["custom_data"]
                tmpl_inst = CustomProjectTemplate(
                    project_name=project_name,
                    target_dir=dest_path,
                    template_dir=cdata["path"],
                    metadata=cdata,
                )
            else:
                tmpl_cls = BUILTIN_TEMPLATES[template_id]
                tmpl_inst = tmpl_cls(project_name=project_name, target_dir=dest_path)

            created = tmpl_inst.scaffold()
            on_log("[ok]", f"Generated {len(created)} template files in {dest_path}", "success")

            if skills:
                res = install_skills(dest_path, skills)
                on_log("[ok]", f"Installed {len(res['installed'])} agent skill(s)", "success")

            if agents:
                agent_files = scaffold_agent_configs(
                    target_dir=dest_path,
                    project_name=project_name,
                    template_id=template_id,
                    installed_skills=skills,
                    selected_agents=agents,
                )
                on_log("[ok]", f"Configured {len(agent_files)} AI agent guideline(s)", "success")

            if readme_style != "skip":
                ctx = {
                    "project_name": project_name,
                    "template_id": template_id,
                    "template_name": tmpl_info["name"],
                    "description": tmpl_info.get("description", ""),
                    "author": get_config("default_author", "Developer"),
                    "skills": skills,
                    "agents": agents,
                }
                generate_project_readme(dest_path, template_style=readme_style, context=ctx)
                on_log("[ok]", f"Generated README.md ({readme_style})", "success")

            if prd_mode == "generate":
                generate_prd_template(target_dir=dest_path, project_name=project_name)
                on_log("[ok]", "Generated PRD.md", "success")

            has_py = tmpl_info.get("has_python", False)
            has_node = tmpl_info.get("has_node", False)
            has_rust = tmpl_info.get("has_rust", False)

            if init_git:
                git_ok = setup_git_repository(dest_path, has_python=has_py, has_node=has_node)
                on_log("[ok]" if git_ok else "[warn]", "Initialized Git repository" if git_ok else "Created .gitignore (git not in PATH)", "success" if git_ok else "warning")

            if init_dotenv:
                copied = setup_dotenv_file(dest_path)
                on_log("[ok]" if copied else "[warn]", "Created .env from .env.example" if copied else ".env.example not found, skipped .env", "success" if copied else "warning")

            if init_vscode:
                setup_vscode_config(dest_path, has_python=has_py, has_node=has_node)
                on_log("[ok]", "Configured .vscode/ settings", "success")

            if init_env and has_py:
                ok, msg = setup_python_environment(dest_path, use_uv=use_uv)
                on_log("[ok]" if ok else "[warn]", msg, "success" if ok else "warning")
            if init_env and has_node:
                ok, msg = setup_node_environment(dest_path)
                on_log("[ok]" if ok else "[warn]", msg, "success" if ok else "warning")
            if init_env and has_rust:
                ok, msg = setup_rust_environment(dest_path)
                on_log("[ok]" if ok else "[warn]", msg, "success" if ok else "warning")

            on_log("[ok]", "Project scaffolding complete.", "success")
            return True

        return await asyncio.to_thread(_execute)
