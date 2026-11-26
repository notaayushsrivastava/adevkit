"""Header component for adevkit Studio."""

from typing import Optional
from reactpy import component, html

from ..state import ToastMessage
from .primitives import Badge


ROUTE_TITLES = {
    "new_project": "New project",
    "live_generation": "Live generation",
    "dependencies": "Dependencies",
    "skills_hub": "Skills hub",
    "template_studio": "Template studio",
    "vault_settings": "Vault & settings",
    "diagnostics": "Diagnostics",
}


@component
def Header(route: str, version: str, toast: Optional[ToastMessage] = None):
    title = ROUTE_TITLES.get(route, route.replace("_", " ").title())
    toast_variant = toast.tone if toast else "neutral"
    return html.header(
        {
            "style": {
                "display": "flex",
                "justifyContent": "space-between",
                "alignItems": "center",
                "height": "56px",
                "padding": "0 28px",
                "borderBottom": "1px solid #242838",
                "background": "#12141C",
                "flex": "none",
            }
        },
        html.div(
            {"style": {"display": "flex", "alignItems": "center", "gap": "12px"}},
            html.span({"style": {"fontSize": "15px", "fontWeight": "600", "color": "#F1F5F9"}}, title),
        ),
        html.div(
            {"style": {"display": "flex", "alignItems": "center", "gap": "12px"}},
            html.div({"key": toast.text, "className": "ak-toast"}, Badge(toast.text, toast_variant)) if toast else None,
            html.span(
                {
                    "style": {
                        "fontFamily": "var(--font-mono)",
                        "fontSize": "11.5px",
                        "padding": "4px 10px",
                        "borderRadius": "999px",
                        "backgroundColor": "#1A1D28",
                        "border": "1px solid #242838",
                        "color": "#94A3B8",
                    }
                },
                f"adevkit v{version}",
            ),
        ),
    )
