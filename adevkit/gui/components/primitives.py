"""Compound and explicit-variant UI primitives matching the ui.html design system."""

from typing import Optional, Any
from reactpy import component, html

from .icons import ICON_FOLDER, ICON_COPY


_BADGE_STYLES = {
    "rust": ("#DEA584", "rgba(222,165,132,0.12)", "rgba(222,165,132,0.3)"),
    "node": ("#22C55E", "rgba(34,197,94,0.12)", "rgba(34,197,94,0.3)"),
    "python": ("#38BDF8", "rgba(56,189,248,0.12)", "rgba(56,189,248,0.3)"),
    "success": ("#10B981", "rgba(16,185,129,0.12)", "rgba(16,185,129,0.3)"),
    "warning": ("#F59E0B", "rgba(245,158,11,0.12)", "rgba(245,158,11,0.3)"),
    "danger": ("#EF4444", "rgba(239,68,68,0.12)", "rgba(239,68,68,0.3)"),
    "dev": ("#F59E0B", "rgba(245,158,11,0.12)", "transparent"),
    "neutral": ("#94A3B8", "rgba(148,163,184,0.12)", "transparent"),
}


@component
def Badge(label: str, variant: str = "neutral"):
    fg, bg, bd = _BADGE_STYLES.get(variant, _BADGE_STYLES["neutral"])
    return html.span(
        {
            "style": {
                "display": "inline-flex",
                "alignItems": "center",
                "fontSize": "11.5px",
                "fontWeight": "600",
                "padding": "3px 8px",
                "borderRadius": "6px",
                "color": fg,
                "backgroundColor": bg,
                "border": f"1px solid {bd}",
                "whiteSpace": "nowrap",
            }
        },
        label,
    )


@component
def PrimaryButton(label: str, on_click=None, disabled: bool = False, icon=None, size: str = "md"):
    return _ButtonBase(label=label, on_click=on_click, disabled=disabled, icon=icon, size=size, variant="primary")


@component
def SecondaryButton(label: str, on_click=None, disabled: bool = False, icon=None, size: str = "md"):
    return _ButtonBase(label=label, on_click=on_click, disabled=disabled, icon=icon, size=size, variant="secondary")


@component
def GhostButton(label: str, on_click=None, disabled: bool = False, icon=None, size: str = "md"):
    return _ButtonBase(label=label, on_click=on_click, disabled=disabled, icon=icon, size=size, variant="ghost")


@component
def DangerButton(label: str, on_click=None, disabled: bool = False, icon=None, size: str = "md"):
    return _ButtonBase(label=label, on_click=on_click, disabled=disabled, icon=icon, size=size, variant="danger")


@component
def _ButtonBase(label: str, on_click, disabled: bool, icon: Any, size: str, variant: str):
    height = "28px" if size == "sm" else "36px"
    padding = "0 10px" if size == "sm" else "0 14px"
    font_size = "12.5px" if size == "sm" else "13.5px"

    if variant == "primary":
        style = {
            "backgroundColor": "#38BDF8",
            "color": "#090A0F",
            "border": "1px solid #38BDF8",
            "fontWeight": "600",
        }
    elif variant == "danger":
        style = {
            "backgroundColor": "transparent",
            "color": "#F87171",
            "border": "1px solid rgba(239,68,68,0.4)",
            "fontWeight": "500",
        }
    elif variant == "ghost":
        style = {
            "backgroundColor": "transparent",
            "color": "#94A3B8",
            "border": "1px solid transparent",
            "fontWeight": "500",
        }
    else:
        style = {
            "backgroundColor": "#1A1D28",
            "color": "#F1F5F9",
            "border": "1px solid #3B4259",
            "fontWeight": "500",
        }

    style.update(
        {
            "display": "inline-flex",
            "alignItems": "center",
            "justifyContent": "center",
            "gap": "6px",
            "height": height,
            "padding": padding,
            "borderRadius": "8px",
            "fontSize": font_size,
            "whiteSpace": "nowrap",
        }
    )

    children = [icon, label] if icon is not None else [label]
    return html.button(
        {"type": "button", "className": "ak-btn", "disabled": disabled, "on_click": on_click, "style": style},
        *children,
    )


@component
def CardRoot(*children, selected: bool = False, interactive: bool = False, style: Optional[dict] = None):
    cls = "ak-card"
    if interactive:
        cls += " ak-card-interactive"
    if selected:
        cls += " ak-card-selected"
    merged = {"padding": "16px", "display": "flex", "flexDirection": "column", "gap": "12px"}
    if style:
        merged.update(style)
    return html.div({"className": cls, "style": merged}, *children)


@component
def CardHeader(title: str, subtitle: Optional[str] = None, badge=None):
    return html.div(
        {"style": {"display": "flex", "justifyContent": "space-between", "alignItems": "flex-start", "gap": "12px"}},
        html.div(
            html.div({"style": {"fontSize": "15px", "fontWeight": "600", "color": "#F1F5F9"}}, title),
            html.div(
                {"style": {"fontFamily": "var(--font-mono)", "fontSize": "12px", "color": "#7B8AA0", "marginTop": "2px"}},
                subtitle,
            )
            if subtitle
            else None,
        ),
        badge,
    )


@component
def CardBody(*children):
    return html.div({"style": {"fontSize": "13px", "lineHeight": "1.5", "color": "#94A3B8"}}, *children)


@component
def SectionHeader(title: str, subtitle: str = "", right=None):
    return html.div(
        {"style": {"display": "flex", "justifyContent": "space-between", "alignItems": "flex-end", "gap": "16px", "marginBottom": "16px"}},
        html.div(
            html.h2({"style": {"margin": 0, "fontSize": "22px", "fontWeight": "600", "letterSpacing": "-0.01em", "color": "#F1F5F9"}}, title),
            html.p({"style": {"margin": "4px 0 0", "fontSize": "13.5px", "color": "#94A3B8"}}, subtitle) if subtitle else None,
        ),
        right,
    )


@component
def PathInput(label: str, value: str, on_change, on_browse=None, placeholder: str = ""):
    return html.div(
        {"style": {"display": "flex", "flexDirection": "column", "gap": "6px"}},
        html.label(
            {"style": {"fontSize": "11px", "fontWeight": "600", "letterSpacing": "0.08em", "textTransform": "uppercase", "color": "#7B8AA0"}},
            label,
        ),
        html.div(
            {"style": {"display": "flex", "gap": "8px"}},
            html.input(
                {
                    "type": "text",
                    "className": "ak-input ak-input-mono",
                    "value": value,
                    "placeholder": placeholder,
                    "on_change": lambda e: on_change(e["target"]["value"]),
                }
            ),
            SecondaryButton("Browse...", on_click=on_browse, icon=ICON_FOLDER) if on_browse else None,
        ),
    )


@component
def TerminalLine(tag: str, text: str, tone: str = "neutral"):
    tag_colors = {
        "success": "#10B981",
        "warning": "#F59E0B",
        "danger": "#EF4444",
        "neutral": "#7B8AA0",
    }
    tc = "#F1F5F9" if tag == "$" else "#94A3B8"
    return html.div(
        {"className": "ak-log-line", "style": {"display": "flex", "gap": "12px", "alignItems": "baseline"}},
        html.span({"style": {"color": tag_colors.get(tone, "#7B8AA0"), "width": "54px", "flex": "none"}}, tag),
        html.span({"style": {"color": tc, "wordBreak": "break-word"}}, text),
    )


@component
def TerminalWindow(title: str, status: str = "idle", on_copy=None, *children):
    return html.div(
        {"style": {"background": "#090A0F", "border": "1px solid #242838", "borderRadius": "12px", "overflow": "hidden", "display": "flex", "flexDirection": "column"}},
        html.div(
            {"style": {"display": "flex", "alignItems": "center", "justifyContent": "space-between", "height": "40px", "padding": "0 16px", "borderBottom": "1px solid #242838", "background": "#12141C"}},
            html.span({"style": {"fontFamily": "var(--font-mono)", "fontSize": "12px", "color": "#94A3B8"}}, title),
            GhostButton("Copy", on_click=on_copy, icon=ICON_COPY, size="sm") if on_copy else None,
        ),
        html.div(
            {"style": {"padding": "16px", "fontFamily": "var(--font-mono)", "fontSize": "12.5px", "lineHeight": "1.75", "display": "flex", "flexDirection": "column", "minHeight": "320px", "maxHeight": "460px", "overflowY": "auto"}},
            *children,
            html.div(
                {"style": {"display": "flex", "gap": "12px", "alignItems": "center", "marginTop": "6px"}},
                html.span({"className": "ak-spinner"}),
                html.span({"style": {"color": "#94A3B8"}}, "Running operation..."),
            )
            if status == "running"
            else None,
        ),
    )
