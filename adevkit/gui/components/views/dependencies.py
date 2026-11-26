"""Dependencies manager view matching ui.html."""

import asyncio
from pathlib import Path
from reactpy import component, html, use_context, use_state

from ...state import AppContext
from ..primitives import (
    Badge,
    CardRoot,
    DangerButton,
    PathInput,
    PrimaryButton,
    SecondaryButton,
    SectionHeader,
)
from ..icons import ICON_PLUS, ICON_REFRESH


@component
def DependenciesView():
    ctx = use_context(AppContext)
    bridge = ctx["bridge"]
    notify = ctx["notify"]

    cwd, set_cwd = use_state(str(Path.cwd()))
    pkg_input, set_pkg_input = use_state("")
    is_dev, set_is_dev = use_state(False)
    busy, set_busy = use_state(False)
    dep_data, set_dep_data = use_state(lambda: bridge.get_project_dependencies(str(Path.cwd())))

    def refresh(target_path: str):
        set_dep_data(bridge.get_project_dependencies(target_path))

    def handle_browse(_event):
        picked = bridge.pick_folder("Select Project Directory")
        if picked:
            set_cwd(picked)
            refresh(picked)

    async def handle_add(_event):
        pkgs = [p.strip() for p in pkg_input.split() if p.strip()]
        if not pkgs:
            return
        set_busy(True)
        ok, msg = await bridge.install_dependency(pkgs, dev=is_dev, cwd=cwd)
        set_busy(False)
        notify(msg, "success" if ok else "danger")
        if ok:
            set_pkg_input("")
            refresh(cwd)

    async def handle_remove(pkg_name: str):
        set_busy(True)
        ok, msg = await bridge.uninstall_dependency([pkg_name], cwd=cwd)
        set_busy(False)
        notify(msg, "success" if ok else "danger")
        if ok:
            refresh(cwd)

    eco = dep_data.get("ecosystem", "unknown")
    eco_badge = {
        "rust": Badge("Rust · Cargo", "rust"),
        "node": Badge("Node.js", "node"),
        "python": Badge("Python", "python"),
    }.get(eco, Badge("No manifest", "neutral"))

    all_rows = [
        {**d, "kind": "Runtime", "variant": "neutral"} for d in dep_data.get("dependencies", [])
    ] + [
        {**d, "kind": "Dev", "variant": "dev"} for d in dep_data.get("dev_dependencies", [])
    ]

    return html.div(
        {"style": {"display": "flex", "flexDirection": "column", "gap": "20px", "maxWidth": "1100px"}},
        SectionHeader(
            "Dependencies",
            "Add, inspect, and remove Rust crates, JS/TS packages, or Python libraries.",
            right=html.div(
                {"style": {"display": "flex", "alignItems": "center", "gap": "10px"}},
                eco_badge,
                SecondaryButton("Refresh", on_click=lambda _e: refresh(cwd), icon=ICON_REFRESH),
            ),
        ),
        CardRoot(
            html.div(
                {"style": {"display": "grid", "gridTemplateColumns": "1.3fr 1fr auto auto", "gap": "12px", "alignItems": "end"}},
                PathInput("Project Directory", cwd, set_cwd, on_browse=handle_browse),
                html.div(
                    {"style": {"display": "flex", "flexDirection": "column", "gap": "6px"}},
                    html.label(
                        {"style": {"fontSize": "11px", "fontWeight": "600", "letterSpacing": "0.08em", "textTransform": "uppercase", "color": "#7B8AA0"}},
                        "Add Package(s)",
                    ),
                    html.input(
                        {
                            "type": "text",
                            "className": "ak-input ak-input-mono",
                            "placeholder": "e.g. zod lucide-react",
                            "value": pkg_input,
                            "on_change": lambda e: set_pkg_input(e["target"]["value"]),
                        }
                    ),
                ),
                html.button(
                    {
                        "type": "button",
                        "className": "ak-btn",
                        "on_click": lambda _e: set_is_dev(not is_dev),
                        "style": {
                            "height": "36px",
                            "padding": "0 12px",
                            "borderRadius": "8px",
                            "border": f"1px solid {'#F59E0B' if is_dev else '#242838'}",
                            "backgroundColor": "rgba(245,158,11,0.12)" if is_dev else "#090A0F",
                            "color": "#F59E0B" if is_dev else "#94A3B8",
                            "fontSize": "12.5px",
                        },
                    },
                    "--dev",
                ),
                PrimaryButton(
                    "Installing..." if busy else "Install",
                    on_click=lambda e: asyncio.ensure_future(handle_add(e)),
                    disabled=busy or not pkg_input.strip(),
                    icon=ICON_PLUS,
                ),
            ),
        ),
        html.div(
            {"style": {"background": "#12141C", "border": "1px solid #242838", "borderRadius": "12px", "overflow": "hidden"}},
            html.div(
                {"style": {"display": "grid", "gridTemplateColumns": "minmax(0,2fr) minmax(0,1fr) minmax(0,1fr) 110px", "height": "40px", "alignItems": "center", "padding": "0 20px", "borderBottom": "1px solid #242838", "fontSize": "11px", "fontWeight": "600", "letterSpacing": "0.08em", "textTransform": "uppercase", "color": "#7B8AA0"}},
                html.span("Package"),
                html.span("Version"),
                html.span("Type"),
                html.span({"style": {"textAlign": "right"}}, "Action"),
            ),
            *(
                [
                    html.div(
                        {
                            "key": f"{row['name']}-{row['kind']}",
                            "className": "ak-virtual-row",
                            "style": {"display": "grid", "gridTemplateColumns": "minmax(0,2fr) minmax(0,1fr) minmax(0,1fr) 110px", "height": "44px", "alignItems": "center", "padding": "0 20px", "borderBottom": "1px solid #242838", "fontSize": "13.5px"},
                        },
                        html.span({"style": {"fontFamily": "var(--font-mono)", "fontWeight": "500"}}, row["name"]),
                        html.span({"style": {"fontFamily": "var(--font-mono)", "color": "#94A3B8"}}, row.get("version") or "-"),
                        html.span(Badge(row["kind"], row["variant"])),
                        html.span(
                            {"style": {"textAlign": "right"}},
                            DangerButton(
                                "Uninstall",
                                size="sm",
                                disabled=busy,
                                on_click=lambda _e, n=row["name"]: asyncio.ensure_future(handle_remove(n)),
                            ),
                        ),
                    )
                    for row in all_rows
                ]
                if all_rows
                else [
                    html.div(
                        {"style": {"padding": "28px 20px", "textAlign": "center", "color": "#7B8AA0", "fontSize": "13px"}},
                        "No dependencies found in this directory.",
                    )
                ]
            ),
        ),
    )
