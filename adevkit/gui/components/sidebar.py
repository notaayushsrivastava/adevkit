"""Collapsible 240px Sidebar navigation component matching ui.html."""

from reactpy import component, html

from .icons import (
    BrandLogo,
    ICON_PLUS,
    ICON_TERMINAL,
    ICON_PACKAGE,
    ICON_SPARKLES,
    ICON_LAYERS,
    ICON_SHIELD,
    ICON_ACTIVITY,
    ICON_CHEVRON_LEFT,
    ICON_CHEVRON_RIGHT,
)


NAV_GROUPS = [
    (
        "Workspace",
        [
            ("new_project", "New project", ICON_PLUS),
            ("live_generation", "Live generation", ICON_TERMINAL),
            ("dependencies", "Dependencies", ICON_PACKAGE),
        ],
    ),
    (
        "Library",
        [
            ("skills_hub", "Skills hub", ICON_SPARKLES),
            ("template_studio", "Template studio", ICON_LAYERS),
        ],
    ),
    (
        "System",
        [
            ("vault_settings", "Vault & settings", ICON_SHIELD),
            ("diagnostics", "Diagnostics", ICON_ACTIVITY),
        ],
    ),
]


@component
def Sidebar(active_route: str, version: str, collapsed: bool, on_toggle_collapse, on_navigate):
    width = "68px" if collapsed else "240px"
    return html.nav(
        {
            "aria-label": "Primary",
            "style": {
                "width": width,
                "flex": "none",
                "background": "#12141C",
                "borderRight": "1px solid #242838",
                "display": "flex",
                "flexDirection": "column",
                "padding": "20px 12px 16px",
                "transition": "width 200ms cubic-bezier(0.16, 1, 0.3, 1)",
                "overflow": "hidden",
            },
        },
        # Brand Row
        html.div(
            {"style": {"display": "flex", "alignItems": "center", "gap": "10px", "padding": "0 6px 24px"}},
            BrandLogo(30),
            (
                html.div(
                    {"style": {"fontSize": "16px", "fontWeight": "700", "letterSpacing": "-0.01em", "color": "#F1F5F9"}},
                    "adevkit",
                )
                if not collapsed
                else None
            ),
            (
                html.div(
                    {"style": {"marginLeft": "auto", "fontFamily": "var(--font-mono)", "fontSize": "11px", "color": "#7B8AA0"}},
                    f"v{version}",
                )
                if not collapsed
                else None
            ),
        ),
        # Navigation Groups
        html.div(
            {"style": {"display": "flex", "flexDirection": "column", "gap": "18px", "flex": 1, "overflowY": "auto"}},
            *[
                html.div(
                    {"key": group_title, "style": {"display": "flex", "flexDirection": "column", "gap": "4px"}},
                    (
                        html.div(
                            {"style": {"padding": "0 8px 4px", "fontSize": "11px", "fontWeight": "600", "letterSpacing": "0.08em", "textTransform": "uppercase", "color": "#7B8AA0"}},
                            group_title,
                        )
                        if not collapsed
                        else None
                    ),
                    *[
                        html.button(
                            {
                                "key": route_id,
                                "type": "button",
                                "className": "ak-nav",
                                "title": label,
                                "on_click": lambda _e, r=route_id: on_navigate(r),
                                "style": {
                                    "width": "100%",
                                    "display": "flex",
                                    "alignItems": "center",
                                    "justifyContent": "center" if collapsed else "flex-start",
                                    "gap": "10px",
                                    "height": "36px",
                                    "padding": "0 10px",
                                    "borderRadius": "8px",
                                    "border": "none",
                                    "cursor": "pointer",
                                    "background": "#1A1D28" if active_route == route_id else "transparent",
                                    "color": "#38BDF8" if active_route == route_id else "#94A3B8",
                                    "fontSize": "13.5px",
                                    "fontWeight": "600" if active_route == route_id else "500",
                                    "fontFamily": "var(--font-ui)",
                                },
                            },
                            icon,
                            html.span({"style": {"whiteSpace": "nowrap"}}, label) if not collapsed else None,
                        )
                        for route_id, label, icon in items
                    ],
                )
                for group_title, items in NAV_GROUPS
            ],
        ),
        # Collapse Toggle
        html.button(
            {
                "type": "button",
                "className": "ak-nav",
                "on_click": on_toggle_collapse,
                "style": {
                    "marginTop": "12px",
                    "display": "flex",
                    "alignItems": "center",
                    "justifyContent": "center" if collapsed else "flex-start",
                    "gap": "8px",
                    "height": "34px",
                    "padding": "0 10px",
                    "borderRadius": "8px",
                    "border": "1px solid #242838",
                    "background": "#090A0F",
                    "color": "#7B8AA0",
                    "fontSize": "12px",
                    "cursor": "pointer",
                },
            },
            ICON_CHEVRON_RIGHT if collapsed else ICON_CHEVRON_LEFT,
            "Collapse" if not collapsed else None,
        ),
    )
