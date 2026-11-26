"""Core headless engine for adevkit (scaffolding, templates, skills, deps, vault, updater)."""

from .config import (
    USER_DEVKIT_DIR,
    USER_TEMPLATES_DIR,
    USER_SKILLS_DIR,
    USER_README_DIR,
    USER_CONFIG_FILE,
    VAULT_FILE,
    UPDATE_CACHE_FILE,
    PACKAGE_ROOT,
    EMBEDDED_SKILLS_DIR,
    ensure_user_dirs,
)
from .deps import (
    detect_project_type,
    add_dependencies,
    remove_dependencies,
    list_dependencies,
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
    get_preferred_node_pm,
    set_preferred_node_pm,
)
from .updater import (
    detect_installation_type,
    check_for_updates,
)

__all__ = [
    "USER_DEVKIT_DIR",
    "USER_TEMPLATES_DIR",
    "USER_SKILLS_DIR",
    "USER_README_DIR",
    "USER_CONFIG_FILE",
    "VAULT_FILE",
    "UPDATE_CACHE_FILE",
    "PACKAGE_ROOT",
    "EMBEDDED_SKILLS_DIR",
    "ensure_user_dirs",
    "detect_project_type",
    "add_dependencies",
    "remove_dependencies",
    "list_dependencies",
    "get_config",
    "set_config",
    "delete_config",
    "list_configs",
    "get_default_agents",
    "set_default_agents",
    "get_preferred_python_pm",
    "set_preferred_python_pm",
    "get_preferred_node_pm",
    "set_preferred_node_pm",
    "detect_installation_type",
    "check_for_updates",
]
