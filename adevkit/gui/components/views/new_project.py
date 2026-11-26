"""New Project wizard view matching ui.html."""

import asyncio
from pathlib import Path
from reactpy import component, html, use_context, use_state

from ...state import AppContext, GenerationJob
from ..primitives import (
    Badge,
    CardRoot,
    CardHeader,
    CardBody,
    PathInput,
    PrimaryButton,
    SectionHeader,
)
from ..icons import ICON_PLUS


def _ecosystem_badge(tmpl: dict):
    if tmpl.get("has_rust"):
        return Badge("Rust", "rust")
    if tmpl.get("has_node") and tmpl.get("has_python"):
        return Badge("Fullstack", "python")
    if tmpl.get("has_node"):
        return Badge("JS / TS", "node")
    if tmpl.get("has_python"):
        return Badge("Python", "python")
    return Badge("Universal", "neutral")


@component
def NewProjectView():
    ctx = use_context(AppContext)
    bridge = ctx["bridge"]
    navigate = ctx["navigate"]
    set_job = ctx["set_job"]

    templates = bridge.get_templates()
    skills_list = bridge.get_skills()
    agents_map = bridge.get_supported_agents()
    readme_styles = bridge.get_readme_styles()

    project_name, set_project_name = use_state("my-agentic-app")
    target_dir, set_target_dir = use_state(str(Path.cwd() / "my-agentic-app"))
    selected_template, set_selected_template = use_state(templates[0]["id"] if templates else "minimal_agentic")
    selected_skills, set_selected_skills = use_state(bridge.get_recommended_skills(templates[0]["id"]) if templates else [])
    selected_agents, set_selected_agents = use_state(bridge.get_vault_state()["default_agents"])
    readme_style, set_readme_style = use_state("modern")
    prd_mode, set_prd_mode = use_state("generate")
    init_git, set_init_git = use_state(True)
    init_dotenv, set_init_dotenv = use_state(True)
    init_vscode, set_init_vscode = use_state(True)
    init_env, set_init_env = use_state(False)
    use_uv, set_use_uv = use_state(True)

    def handle_select_template(tid: str):
        set_selected_template(tid)
        set_selected_skills(bridge.get_recommended_skills(tid))

    def handle_browse(_event):
        picked = bridge.pick_folder("Select Target Project Directory")
        if picked:
            set_target_dir(str(Path(picked) / project_name))

    def toggle_item(items, set_items, item_id: str):
        if item_id in items:
            set_items([x for x in items if x != item_id])
        else:
            set_items([*items, item_id])

    async def handle_generate(_event):
        job = GenerationJob(
            status="running",
            project_name=project_name,
            target_dir=target_dir,
            logs=[("$", f"Initializing {project_name}...", "neutral")],
        )
        set_job(job)
        navigate("live_generation", direction="nav-forward")

        def on_log(tag: str, text: str, tone: str):
            def _append(prev):
                return GenerationJob(
                    status=prev.status,
                    project_name=prev.project_name,
                    target_dir=prev.target_dir,
                    logs=[*prev.logs, (tag, text, tone)],
                )
            set_job(_append)

        ok = await bridge.run_project_generation(
            project_name=project_name.strip() or "my-agentic-app",
            target_dir=target_dir.strip() or str(Path.cwd() / "my-agentic-app"),
            template_id=selected_template,
            skills=selected_skills,
            agents=selected_agents,
            readme_style=readme_style,
            prd_mode=prd_mode,
            init_git=init_git,
            init_dotenv=init_dotenv,
            init_vscode=init_vscode,
            init_env=init_env,
            use_uv=use_uv,
            on_log=on_log,
        )
        set_job(
            lambda prev: GenerationJob(
                status="success" if ok else "error",
                project_name=prev.project_name,
                target_dir=prev.target_dir,
                logs=prev.logs,
            )
        )

    return html.div(
        {"style": {"display": "flex", "flexDirection": "column", "gap": "24px", "maxWidth": "1200px"}},
        SectionHeader(
            "Scaffold a new project",
            "Choose a starter template, equip AI agent skills, and configure your workspace.",
            right=PrimaryButton(
                "Generate Project",
                on_click=lambda e: asyncio.ensure_future(handle_generate(e)),
                icon=ICON_PLUS,
            ),
        ),
        # Project Identity & Path
        CardRoot(
            html.div(
                {"style": {"display": "grid", "gridTemplateColumns": "1fr 1.5fr", "gap": "16px"}},
                html.div(
                    {"style": {"display": "flex", "flexDirection": "column", "gap": "6px"}},
                    html.label(
                        {"style": {"fontSize": "11px", "fontWeight": "600", "letterSpacing": "0.08em", "textTransform": "uppercase", "color": "#7B8AA0"}},
                        "Project Name",
                    ),
                    html.input(
                        {
                            "type": "text",
                            "className": "ak-input ak-input-mono",
                            "value": project_name,
                            "on_change": lambda e: set_project_name(e["target"]["value"]),
                        }
                    ),
                ),
                PathInput("Target Directory", target_dir, set_target_dir, on_browse=handle_browse),
            ),
        ),
        # Template Grid
        html.div(
            {"style": {"display": "flex", "flexDirection": "column", "gap": "12px"}},
            html.div(
                {"style": {"fontSize": "11px", "fontWeight": "600", "letterSpacing": "0.08em", "textTransform": "uppercase", "color": "#7B8AA0"}},
                f"1. Starter Template ({len(templates)} available)",
            ),
            html.div(
                {"style": {"display": "grid", "gridTemplateColumns": "repeat(auto-fill, minmax(260px, 1fr))", "gap": "12px"}},
                *[
                    html.button(
                        {
                            "key": t["id"],
                            "type": "button",
                            "className": f"ak-btn ak-card ak-card-interactive {'ak-card-selected' if selected_template == t['id'] else ''}",
                            "on_click": lambda _e, tid=t["id"]: handle_select_template(tid),
                            "style": {"textAlign": "left", "padding": "14px", "display": "flex", "flexDirection": "column", "gap": "8px"},
                        },
                        CardHeader(t["name"], subtitle=t["id"], badge=_ecosystem_badge(t)),
                        CardBody(t["description"]),
                    )
                    for t in templates
                ],
            ),
        ),
        # AI Agents & Skills
        html.div(
            {"style": {"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "16px"}},
            CardRoot(
                CardHeader("2. AI Agents", subtitle="Writes native guidelines & config files"),
                html.div(
                    {"style": {"display": "flex", "flexWrap": "wrap", "gap": "8px"}},
                    *[
                        html.button(
                            {
                                "key": aid,
                                "type": "button",
                                "className": "ak-btn",
                                "on_click": lambda _e, a=aid: toggle_item(selected_agents, set_selected_agents, a),
                                "style": {
                                    "padding": "6px 12px",
                                    "borderRadius": "8px",
                                    "fontSize": "12.5px",
                                    "fontWeight": "500",
                                    "border": f"1px solid {'#38BDF8' if aid in selected_agents else '#242838'}",
                                    "backgroundColor": "#1A1D28" if aid in selected_agents else "#090A0F",
                                    "color": "#F1F5F9" if aid in selected_agents else "#94A3B8",
                                },
                            },
                            meta["name"] if isinstance(meta, dict) else aid,
                        )
                        for aid, meta in agents_map.items()
                    ],
                ),
            ),
            CardRoot(
                CardHeader("3. Agent Skills", subtitle=f"{len(selected_skills)} selected for .agents/skills/"),
                html.div(
                    {"style": {"display": "flex", "flexWrap": "wrap", "gap": "6px", "maxHeight": "140px", "overflowY": "auto"}},
                    *[
                        html.button(
                            {
                                "key": s["id"],
                                "type": "button",
                                "className": "ak-btn",
                                "on_click": lambda _e, sid=s["id"]: toggle_item(selected_skills, set_selected_skills, sid),
                                "style": {
                                    "padding": "4px 10px",
                                    "borderRadius": "6px",
                                    "fontFamily": "var(--font-mono)",
                                    "fontSize": "11.5px",
                                    "border": f"1px solid {'#38BDF8' if s['id'] in selected_skills else '#242838'}",
                                    "backgroundColor": "rgba(56,189,248,0.12)" if s["id"] in selected_skills else "#090A0F",
                                    "color": "#38BDF8" if s["id"] in selected_skills else "#94A3B8",
                                },
                            },
                            s["id"],
                        )
                        for s in skills_list[:24]
                    ],
                ),
            ),
        ),
        # Docs & Environment
        CardRoot(
            CardHeader("4. Docs & Workspace Options"),
            html.div(
                {"style": {"display": "grid", "gridTemplateColumns": "1fr 1fr 2fr", "gap": "16px", "alignItems": "center"}},
                html.div(
                    {"style": {"display": "flex", "flexDirection": "column", "gap": "6px"}},
                    html.label({"style": {"fontSize": "11px", "color": "#7B8AA0", "textTransform": "uppercase", "fontWeight": "600"}}, "README Style"),
                    html.select(
                        {
                            "className": "ak-input",
                            "value": readme_style,
                            "on_change": lambda e: set_readme_style(e["target"]["value"]),
                        },
                        *[html.option({"key": r["id"], "value": r["id"]}, r["name"]) for r in readme_styles],
                        html.option({"key": "skip", "value": "skip"}, "Skip README"),
                    ),
                ),
                html.div(
                    {"style": {"display": "flex", "flexDirection": "column", "gap": "6px"}},
                    html.label({"style": {"fontSize": "11px", "color": "#7B8AA0", "textTransform": "uppercase", "fontWeight": "600"}}, "PRD Mode"),
                    html.select(
                        {
                            "className": "ak-input",
                            "value": prd_mode,
                            "on_change": lambda e: set_prd_mode(e["target"]["value"]),
                        },
                        html.option({"value": "generate"}, "Generate structured PRD.md"),
                        html.option({"value": "skip"}, "Skip PRD.md"),
                    ),
                ),
                html.div(
                    {"style": {"display": "flex", "flexWrap": "wrap", "gap": "14px", "paddingTop": "18px"}},
                    _ToggleChip("Git & .gitignore", init_git, set_init_git),
                    _ToggleChip(".env from example", init_dotenv, set_init_dotenv),
                    _ToggleChip(".vscode settings", init_vscode, set_init_vscode),
                    _ToggleChip("Install packages", init_env, set_init_env),
                    _ToggleChip("Prefer uv", use_uv, set_use_uv),
                ),
            ),
        ),
    )


@component
def _ToggleChip(label: str, active: bool, setter):
    return html.button(
        {
            "type": "button",
            "className": "ak-btn",
            "on_click": lambda _e: setter(not active),
            "style": {
                "padding": "6px 12px",
                "borderRadius": "8px",
                "fontSize": "12.5px",
                "border": f"1px solid {'#10B981' if active else '#242838'}",
                "backgroundColor": "rgba(16,185,129,0.12)" if active else "#090A0F",
                "color": "#10B981" if active else "#94A3B8",
            },
        },
        f"{'✓ ' if active else ''}{label}",
    )
