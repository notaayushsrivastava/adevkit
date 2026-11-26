"""System & Toolchain Diagnostics view matching ui.html."""

import asyncio
from reactpy import component, html, use_context, use_effect, use_state

from ...state import AppContext
from ..primitives import Badge, CardRoot, PrimaryButton, SectionHeader
from ..icons import ICON_CHECK, ICON_REFRESH


@component
def DiagnosticsView():
    ctx = use_context(AppContext)
    bridge = ctx["bridge"]
    notify = ctx["notify"]

    diag, set_diag = use_state(None)
    checking_update, set_checking_update = use_state(False)
    update_res, set_update_res = use_state(None)

    async def load_diag():
        data = await bridge.get_diagnostics()
        set_diag(data)

    use_effect(lambda: asyncio.ensure_future(load_diag()) and None, [])

    async def handle_check_update(_event):
        set_checking_update(True)
        res = await bridge.check_updates()
        set_checking_update(False)
        set_update_res(res)
        if res and res.get("update_available"):
            notify(f"Update available: v{res['latest_version']}", "warning")
        elif res:
            notify("adevkit is up to date.", "success")
        else:
            notify("Could not check updates (offline or rate-limited).", "warning")

    if diag is None:
        return html.div(
            {"style": {"display": "flex", "alignItems": "center", "gap": "12px", "color": "#94A3B8", "padding": "24px"}},
            html.span({"className": "ak-spinner"}),
            "Inspecting system toolchains...",
        )

    return html.div(
        {"style": {"display": "flex", "flexDirection": "column", "gap": "20px", "maxWidth": "1100px"}},
        SectionHeader(
            "Diagnostics",
            f"adevkit v{diag['version']} · {diag['install_type']} ({diag['platform']})",
            right=PrimaryButton(
                "Checking..." if checking_update else "Check for Updates",
                on_click=lambda e: asyncio.ensure_future(handle_check_update(e)),
                disabled=checking_update,
                icon=ICON_REFRESH,
            ),
        ),
        (
            CardRoot(
                html.div(
                    {"style": {"display": "flex", "justifyContent": "space-between", "alignItems": "center"}},
                    html.span({"style": {"fontSize": "13.5px", "color": "#F1F5F9"}}, f"Latest Version: v{update_res.get('latest_version', 'unknown')}"),
                    Badge("Update available", "warning") if update_res.get("update_available") else Badge("Up to date", "success"),
                )
            )
            if update_res
            else None
        ),
        html.div(
            {"style": {"display": "grid", "gridTemplateColumns": "repeat(auto-fill, minmax(280px, 1fr))", "gap": "16px"}},
            _ToolchainCard("Python", diag["python"], "Toolchain ready", "#38BDF8", True),
            _ToolchainCard("uv (Astral)", diag["uv"] or "Not installed", "Fast Python PM ready" if diag["uv"] else "Optional", "#38BDF8", bool(diag["uv"])),
            _ToolchainCard("Rust", diag["rustc"] or "Not found", diag["cargo"] or "cargo not in PATH", "#DEA584", bool(diag["cargo"])),
            _ToolchainCard("Node.js PM", diag["active_node_pm"], diag["node_pms"].get(diag["active_node_pm"]) or "Not installed", "#22C55E", bool(diag["node_pms"].get(diag["active_node_pm"]))),
            _ToolchainCard("Git", "Available" if diag["git"] else "Not in PATH", "Repository initialization", "#10B981", bool(diag["git"])),
        ),
    )


@component
def _ToolchainCard(label: str, headline: str, detail: str, color: str, ready: bool):
    return CardRoot(
        html.div({"style": {"fontSize": "11px", "fontWeight": "600", "letterSpacing": "0.08em", "textTransform": "uppercase", "color": "#7B8AA0"}}, label),
        html.div({"style": {"fontFamily": "var(--font-mono)", "fontSize": "18px", "fontWeight": "600", "color": color, "wordBreak": "break-word"}}, headline),
        html.div({"style": {"fontFamily": "var(--font-mono)", "fontSize": "12px", "color": "#94A3B8", "wordBreak": "break-all"}}, detail),
        html.div(
            {"style": {"display": "flex", "alignItems": "center", "gap": "8px", "fontSize": "12.5px", "color": "#10B981" if ready else "#7B8AA0", "marginTop": "auto"}},
            ICON_CHECK if ready else None,
            "Toolchain ready" if ready else "Not detected",
        ),
    )
