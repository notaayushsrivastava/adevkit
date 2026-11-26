"""Skills Hub view matching ui.html."""

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
    GhostButton,
    PathInput,
    PrimaryButton,
    SecondaryButton,
    SectionHeader,
)
from ..icons import ICON_PLUS


@component
def SkillsHubView():
    ctx = use_context(AppContext)
    bridge = ctx["bridge"]
    notify = ctx["notify"]

    skills, set_skills = use_state(lambda: bridge.get_skills())
    query, set_query = use_state("")
    category, set_category = use_state("All")
    target_dir, set_target_dir = use_state(str(Path.cwd()))
    new_name, set_new_name = use_state("")
    new_desc, set_new_desc = use_state("")

    categories = ["All", *sorted({s["category"] for s in skills})]
    filtered = [
        s
        for s in skills
        if (category == "All" or s["category"] == category)
        and (not query.strip() or query.lower() in s["id"].lower() or query.lower() in s["description"].lower())
    ]

    def handle_browse(_event):
        picked = bridge.pick_folder("Select Project for Skill Installation")
        if picked:
            set_target_dir(picked)

    async def handle_install(skill_id: str, is_global: bool):
        try:
            res = await bridge.install_skill(skill_id, target_dir, is_global=is_global)
            scope = "globally" if is_global else f"into {res['destination']}"
            notify(f"Installed skill '{res['skill_id']}' {scope}", "success")
        except Exception as exc:
            notify(f"Failed to install '{skill_id}': {exc}", "danger")

    async def handle_create(_event):
        if not new_name.strip():
            return
        await bridge.create_skill(new_name.strip(), description=new_desc.strip(), is_global=True)
        notify(f"Created custom skill '{new_name.strip()}'", "success")
        set_new_name("")
        set_new_desc("")
        set_skills(bridge.get_skills())

    async def handle_remove(skill_id: str):
        ok = await bridge.remove_skill(skill_id, is_global=True)
        if ok:
            notify(f"Removed custom skill '{skill_id}'", "success")
            set_skills(bridge.get_skills())
        else:
            notify(f"Could not remove '{skill_id}'", "warning")

    return html.div(
        {"style": {"display": "flex", "flexDirection": "column", "gap": "20px", "maxWidth": "1200px"}},
        SectionHeader("Skills hub", f"Browse {len(skills)} embedded and custom agent skills."),
        CardRoot(
            html.div(
                {"style": {"display": "grid", "gridTemplateColumns": "1fr 220px 1.2fr", "gap": "12px", "alignItems": "end"}},
                html.div(
                    {"style": {"display": "flex", "flexDirection": "column", "gap": "6px"}},
                    html.label({"style": {"fontSize": "11px", "fontWeight": "600", "letterSpacing": "0.08em", "textTransform": "uppercase", "color": "#7B8AA0"}}, "Search Skills"),
                    html.input(
                        {
                            "type": "text",
                            "className": "ak-input",
                            "placeholder": "Filter by name or description...",
                            "value": query,
                            "on_change": lambda e: set_query(e["target"]["value"]),
                        }
                    ),
                ),
                html.div(
                    {"style": {"display": "flex", "flexDirection": "column", "gap": "6px"}},
                    html.label({"style": {"fontSize": "11px", "fontWeight": "600", "letterSpacing": "0.08em", "textTransform": "uppercase", "color": "#7B8AA0"}}, "Category"),
                    html.select(
                        {
                            "className": "ak-input",
                            "value": category,
                            "on_change": lambda e: set_category(e["target"]["value"]),
                        },
                        *[html.option({"key": c, "value": c}, c) for c in categories],
                    ),
                ),
                PathInput("Target Project", target_dir, set_target_dir, on_browse=handle_browse),
            ),
        ),
        # Create custom skill bar
        CardRoot(
            html.div(
                {"style": {"display": "grid", "gridTemplateColumns": "1fr 1.6fr auto", "gap": "12px", "alignItems": "end"}},
                html.div(
                    {"style": {"display": "flex", "flexDirection": "column", "gap": "6px"}},
                    html.label({"style": {"fontSize": "11px", "fontWeight": "600", "letterSpacing": "0.08em", "textTransform": "uppercase", "color": "#7B8AA0"}}, "New Custom Skill"),
                    html.input(
                        {
                            "type": "text",
                            "className": "ak-input ak-input-mono",
                            "placeholder": "skill-name",
                            "value": new_name,
                            "on_change": lambda e: set_new_name(e["target"]["value"]),
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
                            "placeholder": "What this skill teaches your agent...",
                            "value": new_desc,
                            "on_change": lambda e: set_new_desc(e["target"]["value"]),
                        }
                    ),
                ),
                PrimaryButton(
                    "Create Skill",
                    on_click=lambda e: asyncio.ensure_future(handle_create(e)),
                    disabled=not new_name.strip(),
                    icon=ICON_PLUS,
                ),
            ),
        ),
        html.div(
            {"style": {"display": "grid", "gridTemplateColumns": "repeat(auto-fill, minmax(310px, 1fr))", "gap": "14px"}},
            *[
                CardRoot(
                    CardHeader(
                        s["id"],
                        subtitle=s["category"],
                        badge=Badge("Custom", "python") if s.get("is_custom") else Badge("Embedded", "success"),
                    ),
                    CardBody(s["description"]),
                    html.div(
                        {"style": {"display": "flex", "gap": "8px", "marginTop": "auto"}},
                        SecondaryButton(
                            "Install to project",
                            size="sm",
                            on_click=lambda _e, sid=s["id"]: asyncio.ensure_future(handle_install(sid, False)),
                        ),
                        GhostButton(
                            "Globally",
                            size="sm",
                            on_click=lambda _e, sid=s["id"]: asyncio.ensure_future(handle_install(sid, True)),
                        ),
                        DangerButton(
                            "Delete",
                            size="sm",
                            on_click=lambda _e, sid=s["id"]: asyncio.ensure_future(handle_remove(sid)),
                        )
                        if s.get("is_custom")
                        else None,
                    ),
                )
                for s in filtered[:45]
            ],
        ),
    )
