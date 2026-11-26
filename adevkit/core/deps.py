import re
import sys
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Any

from .utils.system import (
    which_tool,
    detect_cargo,
    detect_node_package_manager,
    detect_uv,
    run_command,
)


def detect_project_type(cwd: Optional[Path] = None) -> str:
    """
    Detect the project ecosystem based on manifest files present in cwd.
    Returns 'rust', 'node', 'python', or 'unknown'.
    """
    path = Path(cwd) if cwd else Path.cwd()

    if (path / "Cargo.toml").is_file():
        return "rust"
    if (path / "package.json").is_file():
        return "node"
    if (path / "pyproject.toml").is_file() or (path / "requirements.txt").is_file():
        return "python"

    return "unknown"


def add_dependencies(
    packages: List[str], dev: bool = False, cwd: Optional[Path] = None
) -> Tuple[bool, str]:
    """
    Add/install one or more packages into the project in cwd.
    Automatically detects Rust (Cargo), JavaScript (npm/pnpm/yarn/bun), or Python (uv/pip).
    """
    path = Path(cwd) if cwd else Path.cwd()
    if not packages:
        return False, "No package names provided."

    cleaned_pkgs = [p.strip() for p in packages if p.strip()]
    if not cleaned_pkgs:
        return False, "No valid package names provided."

    eco = detect_project_type(path)

    if eco == "rust":
        cargo = detect_cargo()
        if not cargo:
            return False, "Cargo is not installed or not in system PATH."
        cmd = [cargo, "add"]
        if dev:
            cmd.append("--dev")
        cmd.extend(cleaned_pkgs)
        code, out, err = run_command(cmd, cwd=path)
        if code != 0:
            return False, f"cargo add failed: {err or out}"
        dev_label = " (dev)" if dev else ""
        return True, f"Added Rust dependencies{dev_label}: {', '.join(cleaned_pkgs)}"

    elif eco == "node":
        pm = detect_node_package_manager()
        pm_bin = which_tool(pm)
        if not pm_bin:
            return False, f"Node package manager '{pm}' is not found in PATH."

        if pm == "npm":
            cmd = [pm, "install", "-D" if dev else "--save"] + cleaned_pkgs
        elif pm == "bun":
            cmd = [pm, "add", "-d" if dev else ""] + cleaned_pkgs
            cmd = [c for c in cmd if c]
        else:  # pnpm, yarn
            cmd = [pm, "add", "-D" if dev else ""] + cleaned_pkgs
            cmd = [c for c in cmd if c]

        code, out, err = run_command(cmd, cwd=path)
        if code != 0:
            return False, f"{pm} add failed: {err or out}"
        dev_label = " (dev)" if dev else ""
        return True, f"Added JavaScript dependencies{dev_label} via {pm}: {', '.join(cleaned_pkgs)}"

    elif eco == "python":
        uv_bin = detect_uv()
        if uv_bin and (path / "pyproject.toml").is_file():
            cmd = [uv_bin, "add"]
            if dev:
                cmd.append("--dev")
            cmd.extend(cleaned_pkgs)
            code, out, err = run_command(cmd, cwd=path)
            if code == 0:
                dev_label = " (dev)" if dev else ""
                return True, f"Added Python dependencies{dev_label} via uv: {', '.join(cleaned_pkgs)}"

        # Pip fallback
        venv_pip = path / ".venv" / ("Scripts" / "pip.exe" if sys.platform == "win32" else "bin" / "pip")
        pip_cmd = str(venv_pip) if venv_pip.is_file() else which_tool("pip") or sys.executable
        if not pip_cmd:
            return False, "Neither uv nor pip was found."

        cmd = [pip_cmd, "install"] + cleaned_pkgs if pip_cmd != sys.executable else [pip_cmd, "-m", "pip", "install"] + cleaned_pkgs
        code, out, err = run_command(cmd, cwd=path)
        if code != 0:
            return False, f"pip install failed: {err or out}"

        # Update requirements.txt if present
        req_file = path / ("requirements-dev.txt" if dev and (path / "requirements-dev.txt").exists() else "requirements.txt")
        if req_file.exists():
            try:
                existing = req_file.read_text(encoding="utf-8").splitlines()
                existing_names = {re.split(r"[><=~;]", line.strip())[0].strip().lower() for line in existing if line.strip() and not line.startswith("#")}
                to_append = [p for p in cleaned_pkgs if re.split(r"[><=~;]", p)[0].strip().lower() not in existing_names]
                if to_append:
                    with open(req_file, "a", encoding="utf-8") as f:
                        for p in to_append:
                            f.write(f"\n{p}")
            except Exception:
                pass

        dev_label = " (dev)" if dev else ""
        return True, f"Installed Python dependencies{dev_label} via pip: {', '.join(cleaned_pkgs)}"

    return False, "No supported project manifest found (looked for Cargo.toml, package.json, pyproject.toml, requirements.txt)."


def remove_dependencies(
    packages: List[str], cwd: Optional[Path] = None
) -> Tuple[bool, str]:
    """
    Remove one or more packages from the project in cwd.
    """
    path = Path(cwd) if cwd else Path.cwd()
    if not packages:
        return False, "No package names provided."

    cleaned_pkgs = [p.strip() for p in packages if p.strip()]
    if not cleaned_pkgs:
        return False, "No valid package names provided."

    eco = detect_project_type(path)

    if eco == "rust":
        cargo = detect_cargo()
        if not cargo:
            return False, "Cargo is not installed or not in system PATH."
        cmd = [cargo, "remove"] + cleaned_pkgs
        code, out, err = run_command(cmd, cwd=path)
        if code != 0:
            return False, f"cargo remove failed: {err or out}"
        return True, f"Removed Rust dependencies: {', '.join(cleaned_pkgs)}"

    elif eco == "node":
        pm = detect_node_package_manager()
        pm_bin = which_tool(pm)
        if not pm_bin:
            return False, f"Node package manager '{pm}' is not found in PATH."

        cmd = [pm, "uninstall" if pm == "npm" else "remove"] + cleaned_pkgs
        code, out, err = run_command(cmd, cwd=path)
        if code != 0:
            return False, f"{pm} remove failed: {err or out}"
        return True, f"Removed JavaScript dependencies via {pm}: {', '.join(cleaned_pkgs)}"

    elif eco == "python":
        uv_bin = detect_uv()
        if uv_bin and (path / "pyproject.toml").is_file():
            cmd = [uv_bin, "remove"] + cleaned_pkgs
            code, out, err = run_command(cmd, cwd=path)
            if code == 0:
                return True, f"Removed Python dependencies via uv: {', '.join(cleaned_pkgs)}"

        venv_pip = path / ".venv" / ("Scripts" / "pip.exe" if sys.platform == "win32" else "bin" / "pip")
        pip_cmd = str(venv_pip) if venv_pip.is_file() else which_tool("pip") or sys.executable

        cmd = [pip_cmd, "uninstall", "-y"] + cleaned_pkgs if pip_cmd != sys.executable else [pip_cmd, "-m", "pip", "uninstall", "-y"] + cleaned_pkgs
        code, out, err = run_command(cmd, cwd=path)
        if code != 0:
            return False, f"pip uninstall failed: {err or out}"

        # Clean from requirements.txt if present
        req_file = path / "requirements.txt"
        if req_file.exists():
            try:
                names_to_remove = {p.lower() for p in cleaned_pkgs}
                lines = req_file.read_text(encoding="utf-8").splitlines()
                kept = []
                for line in lines:
                    raw = re.split(r"[><=~;]", line.strip())[0].strip().lower()
                    if raw not in names_to_remove:
                        kept.append(line)
                req_file.write_text("\n".join(kept) + "\n", encoding="utf-8")
            except Exception:
                pass

        return True, f"Uninstalled Python dependencies via pip: {', '.join(cleaned_pkgs)}"

    return False, "No supported project manifest found (looked for Cargo.toml, package.json, pyproject.toml, requirements.txt)."


def list_dependencies(cwd: Optional[Path] = None) -> Dict[str, Any]:
    """
    List installed/configured dependencies and dev-dependencies in cwd.
    """
    path = Path(cwd) if cwd else Path.cwd()
    eco = detect_project_type(path)

    result: Dict[str, Any] = {
        "ecosystem": eco,
        "manifest": None,
        "dependencies": [],
        "dev_dependencies": [],
    }

    if eco == "rust":
        cargo_path = path / "Cargo.toml"
        result["manifest"] = str(cargo_path)
        if cargo_path.exists():
            content = cargo_path.read_text(encoding="utf-8")
            current_section = None
            for raw_line in content.splitlines():
                line = raw_line.strip()
                if line.startswith("[") and line.endswith("]"):
                    sec = line[1:-1].strip()
                    if sec in ("dependencies", "dev-dependencies"):
                        current_section = sec
                    else:
                        current_section = None
                    continue

                if current_section and "=" in line and not line.startswith("#"):
                    pkg_name = line.split("=", 1)[0].strip()
                    spec = line.split("=", 1)[1].strip()
                    item = {"name": pkg_name, "version": spec.strip('"\'')}
                    if current_section == "dependencies":
                        result["dependencies"].append(item)
                    elif current_section == "dev-dependencies":
                        result["dev_dependencies"].append(item)

    elif eco == "node":
        import json
        pkg_path = path / "package.json"
        result["manifest"] = str(pkg_path)
        if pkg_path.exists():
            try:
                data = json.loads(pkg_path.read_text(encoding="utf-8"))
                deps = data.get("dependencies", {})
                for k, v in deps.items():
                    result["dependencies"].append({"name": k, "version": str(v)})
                dev_deps = data.get("devDependencies", {})
                for k, v in dev_deps.items():
                    result["dev_dependencies"].append({"name": k, "version": str(v)})
            except Exception:
                pass

    elif eco == "python":
        req_path = path / "requirements.txt"
        if req_path.exists():
            result["manifest"] = str(req_path)
            for line in req_path.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line and not line.startswith("#"):
                    result["dependencies"].append({"name": line, "version": ""})

    return result
