import os
import sys
from pathlib import Path

# Base user directory for adevkit (Aayush's DevKit) settings, templates & skills
PRIMARY_DEVKIT_DIR = Path.home() / ".adevkit"
LEGACY_DEVKIT_DIR = Path.home() / ".aayush-devkit"

if PRIMARY_DEVKIT_DIR.exists():
    USER_DEVKIT_DIR = PRIMARY_DEVKIT_DIR
elif LEGACY_DEVKIT_DIR.exists():
    USER_DEVKIT_DIR = LEGACY_DEVKIT_DIR
else:
    USER_DEVKIT_DIR = PRIMARY_DEVKIT_DIR

USER_TEMPLATES_DIR = USER_DEVKIT_DIR / "templates"
USER_SKILLS_DIR = USER_DEVKIT_DIR / "skills"
USER_README_DIR = USER_DEVKIT_DIR / "readmes"
USER_CONFIG_FILE = USER_DEVKIT_DIR / "config.json"
VAULT_FILE = USER_DEVKIT_DIR / "vault.json"
UPDATE_CACHE_FILE = USER_DEVKIT_DIR / "update_cache.json"

# Package directory containing embedded default skills/templates
if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
    PACKAGE_ROOT = Path(sys._MEIPASS) / "adevkit"
else:
    PACKAGE_ROOT = Path(__file__).parent.resolve()

EMBEDDED_SKILLS_DIR = PACKAGE_ROOT / "skills" / "embedded"

def ensure_user_dirs():
    """Ensure ~/.adevkit and subdirectories exist."""
    USER_DEVKIT_DIR.mkdir(parents=True, exist_ok=True)
    USER_TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)
    USER_SKILLS_DIR.mkdir(parents=True, exist_ok=True)
    USER_README_DIR.mkdir(parents=True, exist_ok=True)
