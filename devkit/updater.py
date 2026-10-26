import os
import sys
import json
import time
import threading
import urllib.request
import urllib.error
from pathlib import Path
from typing import Optional, Dict, Any, Tuple

from . import __version__
from .config import UPDATE_CACHE_FILE, ensure_user_dirs

CACHE_TTL_SECONDS = 86400  # 24 hours
PYPI_API_URL = "https://pypi.org/pypi/adevkit/json"
GITHUB_RELEASES_URL = "https://api.github.com/repos/notaayushsrivastava/adevkit/releases/latest"


def detect_installation_type() -> str:
    """
    Detect whether DevKit is running as an MSI/frozen executable or as a Python package.
    Can be overridden via DEVKIT_INSTALL_TYPE environment variable ('msi' or 'python').
    """
    env_override = os.environ.get("DEVKIT_INSTALL_TYPE", "").strip().lower()
    if env_override in ("msi", "binary", "exe"):
        return "msi"
    if env_override in ("python", "pip", "pypi"):
        return "python"

    if getattr(sys, "frozen", False):
        return "msi"
    return "python"


def parse_semver(version_str: str) -> Tuple[int, ...]:
    """Parse a semantic version string into a comparable tuple of integers."""
    import re
    cleaned = version_str.lstrip("v").strip()
    # Extract numeric components
    match = re.match(r"^(\d+)(?:\.(\d+))?(?:\.(\d+))?", cleaned)
    if match:
        parts = [int(p) if p is not None else 0 for p in match.groups()]
        return tuple(parts)
    return (0, 0, 0)


def is_newer_version(candidate_version: str, current_version: str) -> bool:
    """Check if candidate_version is strictly newer than current_version."""
    try:
        from packaging import version
        return version.parse(candidate_version.lstrip("v")) > version.parse(current_version.lstrip("v"))
    except Exception:
        return parse_semver(candidate_version) > parse_semver(current_version)


def check_pypi_update(current_version: str = __version__, timeout: float = 2.0) -> Optional[Dict[str, Any]]:
    """
    Check PyPI for the latest version of adevkit.
    """
    try:
        req = urllib.request.Request(
            PYPI_API_URL,
            headers={"User-Agent": f"adevkit-updater/{current_version}"},
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            if resp.status == 200:
                data = json.loads(resp.read().decode("utf-8"))
                latest_version = data.get("info", {}).get("version", "").strip()
                if latest_version:
                    has_update = is_newer_version(latest_version, current_version)
                    project_url = data.get("info", {}).get("project_url") or "https://pypi.org/project/adevkit/"
                    return {
                        "install_type": "python",
                        "current_version": current_version,
                        "latest_version": latest_version,
                        "update_available": has_update,
                        "update_command": "pip install --upgrade adevkit",
                        "url": project_url,
                    }
    except Exception:
        pass
    return None


def check_msi_update(current_version: str = __version__, timeout: float = 2.0) -> Optional[Dict[str, Any]]:
    """
    Check GitHub Releases for the latest Windows MSI / executable release.
    """
    try:
        req = urllib.request.Request(
            GITHUB_RELEASES_URL,
            headers={
                "User-Agent": f"adevkit-updater/{current_version}",
                "Accept": "application/vnd.github.v3+json",
            },
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            if resp.status == 200:
                data = json.loads(resp.read().decode("utf-8"))
                tag_name = data.get("tag_name", "").strip().lstrip("v")
                if tag_name:
                    has_update = is_newer_version(tag_name, current_version)
                    
                    # Search for MSI asset
                    msi_download_url = None
                    for asset in data.get("assets", []):
                        name = asset.get("name", "")
                        if name.endswith(".msi"):
                            msi_download_url = asset.get("browser_download_url")
                            break

                    release_url = data.get("html_url") or "https://github.com/notaayushsrivastava/adevkit/releases/latest"
                    download_url = msi_download_url or release_url
                    
                    return {
                        "install_type": "msi",
                        "current_version": current_version,
                        "latest_version": tag_name,
                        "update_available": has_update,
                        "update_command": f"Download MSI installer: {download_url}",
                        "url": download_url,
                        "release_page": release_url,
                    }
    except Exception:
        pass
    return None


def load_cached_update(max_age_seconds: int = CACHE_TTL_SECONDS) -> Optional[Dict[str, Any]]:
    """Load cached update metadata if it is still fresh."""
    try:
        if not UPDATE_CACHE_FILE.exists():
            return None
        with open(UPDATE_CACHE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        timestamp = data.get("timestamp", 0)
        if (time.time() - timestamp) <= max_age_seconds:
            return data
    except Exception:
        pass
    return None


def save_cached_update(data: Dict[str, Any]):
    """Persist update check metadata to cache file."""
    try:
        ensure_user_dirs()
        payload = dict(data)
        payload["timestamp"] = time.time()
        with open(UPDATE_CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)
    except Exception:
        pass


def check_for_updates(
    force: bool = False,
    mode: Optional[str] = None,
    current_version: str = __version__,
    timeout: float = 2.0,
) -> Optional[Dict[str, Any]]:
    """
    Check for updates for the active or specified installation mode.
    Uses cached result unless force=True or cache is stale.
    """
    target_mode = mode or detect_installation_type()

    if not force:
        cached = load_cached_update()
        if cached and cached.get("install_type") == target_mode:
            # Re-verify update_available against current_version
            cached_latest = cached.get("latest_version", "")
            cached["update_available"] = is_newer_version(cached_latest, current_version)
            return cached

    if target_mode == "msi":
        res = check_msi_update(current_version=current_version, timeout=timeout)
    else:
        res = check_pypi_update(current_version=current_version, timeout=timeout)

    if res:
        save_cached_update(res)
    return res


def trigger_background_check(mode: Optional[str] = None):
    """
    Check if cache has expired; if so, trigger a background daemon thread
    to update the cache without blocking CLI execution.
    """
    cached = load_cached_update()
    if cached is None:
        def _worker():
            try:
                check_for_updates(force=True, mode=mode, timeout=3.0)
            except Exception:
                pass

        t = threading.Thread(target=_worker, daemon=True)
        t.start()


def notify_update_if_available(console_obj=None, auto_check_background: bool = True):
    """
    Print an update banner if a newer version is known to be available.
    Triggers a background check if cache is expired.
    """
    if auto_check_background:
        trigger_background_check()

    cached = load_cached_update(max_age_seconds=CACHE_TTL_SECONDS * 7)
    if not cached:
        return

    latest_ver = cached.get("latest_version")
    if not latest_ver or not is_newer_version(latest_ver, __version__):
        return

    install_type = cached.get("install_type", "python")
    up_cmd = cached.get("update_command", "")
    url = cached.get("url", "")

    if console_obj is None:
        from .ui import console
        console_obj = console

    from rich.panel import Panel
    from rich.text import Text

    text = Text()
    text.append(f"A new version of Aayush's DevKit is available: ", style="white")
    text.append(f"v{__version__}", style="yellow")
    text.append(" -> ", style="dim")
    text.append(f"v{latest_ver}\n", style="bold green")

    if install_type == "python":
        text.append("To upgrade via pip, run:\n", style="dim")
        text.append(f"  {up_cmd}", style="bold cyan")
    else:
        text.append("Download latest Windows MSI installer:\n", style="dim")
        text.append(f"  {url}", style="bold cyan")

    panel = Panel(
        text,
        title="[bold yellow][i] Update Available[/bold yellow]",
        border_style="yellow",
        padding=(0, 2),
    )
    console_obj.print(panel)
    console_obj.print()
