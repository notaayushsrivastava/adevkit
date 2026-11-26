import sys
import typer

# Windows consoles may use a legacy code page (for example cp1252) that cannot
# encode Unicode symbols used by Rich/Typer. Force UTF-8 output where supported.
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        try:
            _stream.reconfigure(encoding="utf-8", errors="replace")
        except (OSError, ValueError):
            pass

from ..core.updater import notify_update_if_available
from .commands.init import init
from .commands.templates import template_app
from .commands.skills import skills_app
from .commands.readme import readme_app
from .commands.config import config_app
from .commands.deps import deps_app, deps_add_cmd, deps_remove_cmd
from .commands.updater import check_update_command
from .commands.info import system_info
from .commands.gui import launch_gui_command

app = typer.Typer(
    name="adevkit",
    help="adevkit (Aayush's DevKit) - Single-command project initialization with Agentic skills, AI agents, and environments.",
    add_completion=False,
)

app.add_typer(template_app, name="template")
app.add_typer(skills_app, name="skills")
app.add_typer(config_app, name="config")
app.add_typer(readme_app, name="readme")
app.add_typer(deps_app, name="deps")


@app.callback(invoke_without_command=True)
def main_entry(ctx: typer.Context):
    """If no subcommand is passed, default to interactive init."""
    notify_update_if_available()
    if ctx.invoked_subcommand is None:
        init()


app.command(name="init")(init)
app.command(name="add")(deps_add_cmd)
app.command(name="remove")(deps_remove_cmd)
app.command(name="check-update")(check_update_command)
app.command(name="info")(system_info)
app.command(name="gui")(launch_gui_command)


def main():
    """Main CLI entrypoint."""
    app()


if __name__ == "__main__":
    main()
