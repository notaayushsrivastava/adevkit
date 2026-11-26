"""Template Studio view matching ui.html."""

import asyncio
from pathlib import Path
from reactpy import component, html, use_context, use_state

from ...state import AppContext
from ..primitives import (
    Badge,
    CardRoot,
    CardHeader,
    CardBody,
    DangerButton,
    PathInput,
    PrimaryButton,
    SectionHeader,
)
from ..icons import ICON_PLUS


@component
def TemplateStudioView():
    ctx = use_context(AppContext)
    bridge = ctx["bridge"]
    notify = ctx["notify"]

    templates, set_templates = use_state(lambda: bridge.get_templates())
    name, set_name = use_state("")
    desc, set_desc = use_state("")
    source_dir, set_source_dir = use_state(str(Path.cwd()))

    def handle_browse(_event):
        picked = bridge.pick_folder("Select Folder to Snapshot as Template")
        if picked:
            set_source_dir(picked)

    async def handle_snapshot(_event):
        if not name.strip():
            return
        try:
            saved_path = await bridge.snapshot_template(name.strip(), source_dir, desc.strip())
            notify(f"Saved template '{name.strip()}' at {saved_path}", "success")
            set_name("")
            set_desc("")
            set_templates(bridge.get_templates())
        except Exception as exc:
            notify(f"Failed to save template: {exc}", "danger")

    async def handle_delete(tid: str):
        ok = await bridge.remove_template(tid)
        if ok:
            notify(f"Deleted custom template '{tid}'", "success")
            set_templates(bridge.get_templates())
        else:
            notify(f"Template '{tid}' not found", "warning")

    return html.div(
        {"style": {"display": "flex", "flexDirection": "column", "gap": "20px", "maxWidth": "1200px"}},
        SectionHeader("Template studio", "Snapshot local projects into reusable starters and manage templates."),
        CardRoot(
            CardHeader("Snapshot Folder to Custom Template"),
            html.div(
                {"style": {"display": "grid", "gridTemplateColumns": "1fr 1.4fr 1.4fr auto", "gap": "12px", "alignItems": "end"}},
                html.div(
                    {"style": {"display": "flex", "flexDirection": "column", "gap": "6px"}},
                    html.label({"style": {"fontSize": "11px", "fontWeight": "600", "letterSpacing": "0.08em", "textTransform": "uppercase", "color": "#7B8AA0"}}, "Template Name"),
                    html.input(
                        {
                            "type": "text",
                            "className": "ak-input ak-input-mono",
                            "placeholder": "client-portal",
                            "value": name,
                            "on_change": lambda e: set_name(e["target"]["value"]),
                        }
                    ),
                ),
                html.div(
                    {"style": {"display": "flex", "flexDirection": "column", "gap": "6px"}},
                    html.label({"style": {"fontSize": "11px", "fontWeight": "600", "letterSpacing": "0.08em", "textTransform": "uppercase", "color": "#7B8AA0"}}, "Description"),
                    html.input(
                        {
                            "type": "text",
                            "className": "ak-input",
                            "placeholder": "Short description...",
                            "value": desc,
                            "on_change": lambda e: set_desc(e["target"]["value"]),
                        }
                    ),
                ),
                PathInput("Source Folder", source_dir, set_source_dir, on_browse=handle_browse),
                PrimaryButton(
                    "Save Template",
                    on_click=lambda e: asyncio.ensure_future(handle_snapshot(e)),
                    disabled=not name.strip(),
                    icon=ICON_PLUS,
                ),
            ),
        ),
        html.div(
            {"style": {"display": "grid", "gridTemplateColumns": "repeat(auto-fill, minmax(280px, 1fr))", "gap": "14px"}},
            *[
                CardRoot(
                    CardHeader(
                        t["name"],
                        subtitle=t["id"],
                        badge=Badge("Custom", "python") if t["is_custom"] else Badge("Built-in", "neutral"),
                    ),
                    CardBody(t["description"]),
                    html.div(
                        {"style": {"marginTop": "auto", "display": "flex", "justifyContent": "flex-end"}},
                        DangerButton(
                            "Delete",
                            size="sm",
                            on_click=lambda _e, tid=t["id"]: asyncio.ensure_future(handle_delete(tid)),
                        ),
                    )
                    if t["is_custom"]
                    else None,
                )
                for t in templates
            ],
        ),
    )
