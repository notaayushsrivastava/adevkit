"""Desktop Studio views for adevkit."""

from .new_project import NewProjectView
from .live_generation import LiveGenerationView
from .dependencies import DependenciesView
from .skills_hub import SkillsHubView
from .template_studio import TemplateStudioView
from .vault_settings import VaultSettingsView
from .diagnostics import DiagnosticsView

__all__ = [
    "NewProjectView",
    "LiveGenerationView",
    "DependenciesView",
    "SkillsHubView",
    "TemplateStudioView",
    "VaultSettingsView",
    "DiagnosticsView",
]
