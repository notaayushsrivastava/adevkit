import shutil
import sys
from pathlib import Path
from typing import Tuple, Optional
from ..utils.system import detect_node_package_manager, which_tool, run_command

def setup_python_environment(target_dir: Path) -> Tuple[bool, str]:
    """Create .venv and install requirements if present."""
    target_dir = Path(target_dir)
    python_exe = sys.executable

    # 1. Create .venv
    venv_dir = target_dir / ".venv"
    if not venv_dir.exists():
        code, out, err = run_command([python_exe, "-m", "venv", ".venv"], cwd=target_dir)
        if code != 0:
            return False, f"Failed to create virtual environment: {err}"

    # 2. Determine pip path
    if sys.platform == "win32":
        pip_path = venv_dir / "Scripts" / "pip.exe"
    else:
        pip_path = venv_dir / "bin" / "pip"

    req_file = target_dir / "requirements.txt"
    if req_file.exists() and pip_path.exists():
        code, out, err = run_command([str(pip_path), "install", "-r", "requirements.txt"], cwd=target_dir)
        if code != 0:
            return False, f"Failed to install requirements: {err}"

    return True, "Python virtual environment and requirements configured."

def setup_node_environment(target_dir: Path) -> Tuple[bool, str]:
    """Detect package manager and install node modules."""
    target_dir = Path(target_dir)
    pkg_json = target_dir / "package.json"
    if not pkg_json.exists():
        return True, "No package.json found; skipping Node dependencies."

    pm = detect_node_package_manager()
    pm_bin = which_tool(pm)
    if not pm_bin:
        return False, f"No Node.js package manager found in PATH (tried bun, pnpm, yarn, npm)."

    code, out, err = run_command([pm, "install"], cwd=target_dir)
    if code != 0:
        return False, f"Failed to install node modules via {pm}: {err}"

    return True, f"Installed node modules via {pm}."

def setup_dotenv_file(target_dir: Path) -> bool:
    """Copy .env.example to .env if .env doesn't exist yet."""
    target_dir = Path(target_dir)
    env_example = target_dir / ".env.example"
    env_file = target_dir / ".env"
    if env_example.exists() and not env_file.exists():
        shutil.copy2(env_example, env_file)
        return True
    return False
