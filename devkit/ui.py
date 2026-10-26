import sys
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table

console = Console()

BANNER_ART = r"""
   ___                 _        _         ___          _  ___ _   
  / _ \               | |      ( )       |   \        | |/ (_) |  
 / /_\ \__ _ _   _ _   _| |__    |/ ___    | |) |_____ _| ' / _| |_ 
 |  _  / _` | | | | | | | '_ \     / __|   |  _/ _ \ \ / /  < | | __|
 | | | | (_| | |_| | |_| | | | |    \__ \   | | |  __/\ V /| . \| | |_ 
 \_| |_/\__,_|\__, |\__,_|_| |_|    |___/   |___/\___| \_/ |_|\_\_|\__|
               __/ |                                                    
              |___/                                                     
"""

def print_banner():
    """Display the Aayush's DevKit branding banner."""
    text = Text(BANNER_ART, style="bold cyan")
    panel = Panel(
        text,
        title="[bold yellow]Aayush's DevKit[/bold yellow]",
        subtitle="[bold white]Single-Command Project Scaffolding & Agentic Environment Setup[/bold white]",
        border_style="bright_blue",
        padding=(0, 2),
    )
    console.print(panel)
    console.print()

def success(message: str):
    console.print(f"[bold green][+][/bold green] {message}")

def info(message: str):
    console.print(f"[bold cyan][i][/bold cyan] {message}")

def warning(message: str):
    console.print(f"[bold yellow][!][/bold yellow] {message}")

def error(message: str):
    console.print(f"[bold red][x][/bold red] {message}")

def section(title: str):
    console.print(f"\n[bold magenta]─── {title} ───[/bold magenta]\n")

def print_summary_table(project_name: str, target_dir: str, template: str, skills: list[str], prd_mode: str):
    """Print an aesthetic summary table of the project to be created."""
    table = Table(title="Project Initialization Summary", border_style="cyan")
    table.add_column("Property", style="bold yellow", width=22)
    table.add_column("Value", style="white")

    table.add_row("Project Name", project_name)
    table.add_row("Target Directory", target_dir)
    table.add_row("Template", template)
    table.add_row("Skills Selected", ", ".join(skills) if skills else "None")
    table.add_row("PRD Mode", prd_mode)

    console.print(table)
    console.print()
