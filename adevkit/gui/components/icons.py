"""Hoisted static SVG icons matching ui.html."""

from reactpy import svg


def BrandLogo(size: int = 30):
    return svg.svg(
        {"width": str(size), "height": str(size), "viewBox": "0 0 48 48", "role": "img", "aria-label": "adevkit"},
        svg.rect({"x": "0.5", "y": "0.5", "width": "47", "height": "47", "rx": "12", "fill": "#090A0F", "stroke": "#3B4259"}),
        svg.path({"d": "M15 16l10 8-10 8", "fill": "none", "stroke": "#38BDF8", "stroke-width": "4", "stroke-linecap": "round", "stroke-linejoin": "round"}),
        svg.path({"d": "M28 33h9", "stroke": "#F1F5F9", "stroke-width": "4", "stroke-linecap": "round"}),
    )


def _icon(path_d: str, size: int = 16, stroke_width: str = "1.75"):
    return svg.svg(
        {
            "width": str(size),
            "height": str(size),
            "viewBox": "0 0 24 24",
            "fill": "none",
            "stroke": "currentColor",
            "stroke-width": stroke_width,
            "stroke-linecap": "round",
            "stroke-linejoin": "round",
            "aria-hidden": "true",
            "style": {"flex": "none"},
        },
        svg.path({"d": path_d}),
    )


ICON_PLUS = _icon("M12 5v14M5 12h14")
ICON_TERMINAL = _icon("M4 17l6-6-6-6M12 19h8")
ICON_PACKAGE = _icon("M16.5 9.4l-9-5.19M21 16V8a2 2 0 00-1-1.73l-7-4a2 2 0 00-2 0l-7 4A2 2 0 003 8v8a2 2 0 001 1.73l7 4a2 2 0 002 0l7-4A2 2 0 0021 16zM3.27 6.96L12 12.01l8.73-5.05M12 22.08V12")
ICON_SPARKLES = _icon("M12 3l1.8 4.2L18 9l-4.2 1.8L12 15l-1.8-4.2L6 9l4.2-1.8L12 3zM5 17l.9 2.1L8 20l-2.1.9L5 23l-.9-2.1L2 20l2.1-.9L5 17zM19 15l.9 2.1L22 18l-2.1.9L19 21l-.9-2.1L16 18l2.1-.9L19 15z")
ICON_LAYERS = _icon("M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5")
ICON_SHIELD = _icon("M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z")
ICON_ACTIVITY = _icon("M22 12h-4l-3 9L9 3l-3 9H2")
ICON_CHECK = _icon("M5 12l5 5 9-10", size=14, stroke_width="2.4")
ICON_FOLDER = _icon("M22 19a2 2 0 01-2 2H4a2 2 0 01-2-2V5a2 2 0 012-2h5l2 3h9a2 2 0 012 2z", size=15)
ICON_COPY = _icon("M9 9h11v11H9zM5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1", size=14)
ICON_CHEVRON_LEFT = _icon("M15 18l-6-6 6-6", size=15)
ICON_CHEVRON_RIGHT = _icon("M9 18l6-6-6-6", size=15)
ICON_REFRESH = _icon("M23 4v6h-6M1 20v-6h6M3.51 9a9 9 0 0114.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0020.49 15", size=14)
