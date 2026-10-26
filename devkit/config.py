import os
import sys
from pathlib import Path

# Base user directory for global Aayush's DevKit settings & custom templates
USER_DEVKIT_DIR = Path.home() / ".aayush-devkit"
USER_TEMPLATES_DIR = USER_DEVKIT_DIR / "templates"
USER_CONFIG_FILE = USER_DEVKIT_DIR / "config.json"
UPDATE_CACHE_FILE = USER_DEVKIT_DIR / "update_cache.json"

# Package directory containing embedded default skills/templates
if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
    PACKAGE_ROOT = Path(sys._MEIPASS) / "devkit"
else:
    PACKAGE_ROOT = Path(__file__).parent.resolve()

EMBEDDED_SKILLS_DIR = PACKAGE_ROOT / "skills" / "embedded"

def ensure_user_dirs():
    """Ensure ~/.aayush-devkit and custom templates directories exist."""
    USER_DEVKIT_DIR.mkdir(parents=True, exist_ok=True)
    USER_TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)
