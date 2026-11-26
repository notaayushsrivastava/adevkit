import typer
from rich.panel import Panel

from ..ui import console


def launch_gui_command(
    debug: bool = typer.Option(False, "--debug", help="Enable PyWebView developer tools and debug logging"),
):
    """Launch the adevkit desktop GUI (ReactPy + PyWebView)."""
    try:
        from ...gui.launcher import launch_gui
    except ImportError as exc:
        panel = Panel(
            "[bold red]GUI dependencies are not installed.[/bold red]\n\n"
            "You appear to be running a headless/CLI-only installation of adevkit.\n"
            "To install the desktop UI kit, run:\n\n"
            "  [bold cyan]pip install \"adevkit\\[gui]\"[/bold cyan]\n\n"
            f"[dim]Missing dependency detail: {exc}[/dim]",
            title="adevkit GUI",
            border_style="red",
        )
        console.print(panel)
        raise typer.Exit(1)

    launch_gui(debug=debug)
