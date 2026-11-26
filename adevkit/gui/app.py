"""Root ReactPy application for adevkit Studio."""

from typing import Optional
from reactpy import component, html, use_state

from .. import __version__
from .bridge import DevKitBridge
from .state import AppContext, GenerationJob, ToastMessage
from .styles import DESIGN_SYSTEM_CSS, VIEW_TRANSITION_SCRIPT
from .components.sidebar import Sidebar
from .components.header import Header
from .components.views import (
    NewProjectView,
    LiveGenerationView,
    DependenciesView,
    SkillsHubView,
    TemplateStudioView,
    VaultSettingsView,
    DiagnosticsView,
)


_VIEW_MAP = {
    "new_project": NewProjectView,
    "live_generation": LiveGenerationView,
    "dependencies": DependenciesView,
    "skills_hub": SkillsHubView,
    "template_studio": TemplateStudioView,
    "vault_settings": VaultSettingsView,
    "diagnostics": DiagnosticsView,
}


@component
def DevKitApp(bridge: Optional[DevKitBridge] = None):
    active_bridge = bridge or DevKitBridge()
    route, set_route = use_state("new_project")
    collapsed, set_collapsed = use_state(False)
    job, set_job = use_state(GenerationJob())
    toast, set_toast = use_state(None)

    def navigate(next_route: str, direction: str = ""):
        set_route(next_route)

    def notify(text: str, tone: str = "info"):
        set_toast(ToastMessage(text=text, tone=tone))

    ctx_value = {
        "route": route,
        "navigate": navigate,
        "bridge": active_bridge,
        "job": job,
        "set_job": set_job,
        "notify": notify,
    }

    ViewComponent = _VIEW_MAP.get(route, NewProjectView)

    return AppContext(
        html.div(
            {
                "style": {
                    "display": "flex",
                    "height": "100vh",
                    "background": "#090A0F",
                    "color": "#F1F5F9",
                    "overflow": "hidden",
                }
            },
            html.link(
                {
                    "rel": "stylesheet",
                    "href": "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap",
                }
            ),
            html.style(DESIGN_SYSTEM_CSS),
            html.script(VIEW_TRANSITION_SCRIPT),
            Sidebar(
                active_route=route,
                version=__version__,
                collapsed=collapsed,
                on_toggle_collapse=lambda _e: set_collapsed(not collapsed),
                on_navigate=lambda r: navigate(r),
            ),
            html.div(
                {"style": {"flex": 1, "display": "flex", "flexDirection": "column", "overflow": "hidden"}},
                Header(route=route, version=__version__, toast=toast),
                html.main(
                    {
                        "key": route,
                        "className": "ak-main-panel",
                        "style": {"padding": "28px", "overflowY": "auto", "flex": 1},
                    },
                    ViewComponent(),
                ),
            ),
        ),
        value=ctx_value,
    )
