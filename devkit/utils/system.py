import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional, List, Tuple

def which_tool(tool_name: str) -> Optional[str]:
    """Find the executable path for a tool, handling Windows .cmd / .exe extensions."""
    path = shutil.which(tool_name)
    if path:
        return path
    if sys.platform == "win32":
        for ext in [".cmd", ".bat", ".exe"]:
            path = shutil.which(f"{tool_name}{ext}")
            if path:
                return path
    return None

def detect_node_package_manager() -> str:
    """Detect the best available Node.js package manager in order of preference."""
    for pm in ["bun", "pnpm", "yarn", "npm"]:
        if which_tool(pm):
            return pm
    return "npm"

def detect_git() -> bool:
    """Check if git is installed and available in PATH."""
    return which_tool("git") is not None

def detect_python() -> str:
    """Return the currently executing python interpreter path."""
    return sys.executable

def run_command(cmd: List[str], cwd: Optional[Path] = None, timeout: int = 300) -> Tuple[int, str, str]:
    """Execute a system command synchronously and return (exit_code, stdout, stderr)."""
    try:
        proc = subprocess.run(
            cmd,
            cwd=str(cwd) if cwd else None,
            capture_output=True,
            text=True,
            timeout=timeout,
            shell=(sys.platform == "win32" and not cmd[0].endswith(".exe")),
        )
        return proc.returncode, proc.stdout, proc.stderr
    except Exception as e:
        return -1, "", str(e)
