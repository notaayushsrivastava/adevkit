"""Sphinx configuration for adevkit documentation."""

project = "adevkit"
copyright = "2026, Aayush Srivastava"
author = "Aayush Srivastava"
release = "0.1.5"

extensions = [
    "myst_parser",
    "sphinx_copybutton",
]

myst_enable_extensions = [
    "colon_fence",
    "deflist",
    "tasklist",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

html_theme = "furo"
html_title = "adevkit Documentation"
html_favicon = "../web/assets/favicon.svg"

html_theme_options = {
    "light_css_variables": {
        "color-brand-primary": "#0284C7",
        "color-brand-content": "#0284C7",
    },
    "dark_css_variables": {
        "color-brand-primary": "#38BDF8",
        "color-brand-content": "#38BDF8",
        "color-background-primary": "#090A0F",
        "color-background-secondary": "#12141C",
        "color-background-hover": "#1A1D28",
        "color-background-border": "#242838",
    },
    "source_repository": "https://github.com/notaayushsrivastava/adevkit",
    "source_branch": "main",
    "source_directory": "docs/",
}
