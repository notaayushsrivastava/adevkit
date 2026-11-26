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
    """
    Detect the best available Node.js package manager in order of preference.
    Respects user's configured preference from vault if installed.
    """
    try:
        from ..vault import get_preferred_node_pm
        pref = get_preferred_node_pm()
        if pref and which_tool(pref):
            return pref
    except Exception:
        pass

    for pm in ["bun", "pnpm", "yarn", "npm"]:
        if which_tool(pm):
            return pm
    return "npm"

def detect_cargo() -> Optional[str]:
    """Detect if cargo (Rust package manager) is installed and available in PATH."""
    return which_tool("cargo")

def detect_rustc() -> Optional[str]:
    """Detect if rustc (Rust compiler) is installed and available in PATH."""
    return which_tool("rustc")

def get_rustc_version() -> Optional[str]:
    """Return the rustc version string (e.g. 'rustc 1.85.0') if available."""
    rustc = detect_rustc()
    if not rustc:
        return None
    code, out, _ = run_command([rustc, "--version"])
    if code == 0 and out.strip():
        return out.strip().split("\n")[0]
    return None

def detect_git() -> bool:
    """Check if git is installed and available in PATH."""
    return which_tool("git") is not None

def detect_uv() -> Optional[str]:
    """Detect if uv (Astral fast Python manager) is installed and available in PATH."""
    return which_tool("uv")

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
