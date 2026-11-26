"""Live Generation terminal output view matching ui.html."""

import subprocess
import sys
from reactpy import component, html, use_context

from ...state import AppContext
from ..primitives import (
    Badge,
    SecondaryButton,
    PrimaryButton,
    SectionHeader,
    TerminalWindow,
    TerminalLine,
)
from ..icons import ICON_CHEVRON_LEFT, ICON_FOLDER


@component
def LiveGenerationView():
    ctx = use_context(AppContext)
    job = ctx["job"]
    navigate = ctx["navigate"]
    notify = ctx["notify"]

    status_badge = {
        "idle": Badge("Ready", "neutral"),
        "running": Badge("Scaffolding...", "python"),
        "success": Badge("Completed", "success"),
        "error": Badge("Failed", "danger"),
    }.get(job.status, Badge("Ready", "neutral"))

    def handle_open_folder(_event):
        if not job.target_dir:
            return
        try:
            if sys.platform == "win32":
                subprocess.Popen(["explorer", job.target_dir])
            elif sys.platform == "darwin":
                subprocess.Popen(["open", job.target_dir])
            else:
                subprocess.Popen(["xdg-open", job.target_dir])
        except Exception as exc:
            notify(f"Could not open folder: {exc}", "warning")

    def handle_copy(_event):
        notify("Copied terminal log to session buffer.", "info")

    return html.div(
        {"style": {"display": "flex", "flexDirection": "column", "gap": "20px", "maxWidth": "1100px"}},
        SectionHeader(
            "Live generation",
            f"Target: {job.target_dir or 'No active project run yet'}",
            right=html.div(
                {"style": {"display": "flex", "alignItems": "center", "gap": "10px"}},
                status_badge,
                SecondaryButton(
                    "Back to New Project",
                    on_click=lambda _e: navigate("new_project", direction="nav-back"),
                    icon=ICON_CHEVRON_LEFT,
                ),
                PrimaryButton(
                    "Open Folder",
                    on_click=handle_open_folder,
                    disabled=not bool(job.target_dir),
                    icon=ICON_FOLDER,
                ),
            ),
        ),
        TerminalWindow(
            f"adevkit · generate {job.project_name}".strip(),
            job.status,
            handle_copy,
            *[
                TerminalLine(tag=tag, text=text, tone=tone)
                for idx, (tag, text, tone) in enumerate(
                    job.logs or [("$", "Start a project from New Project to stream generation logs.", "neutral")]
                )
            ],
        ),
    )
