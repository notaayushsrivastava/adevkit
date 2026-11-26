"""Backward-compatible facade for adevkit.cli.ui."""
import sys
from .cli import ui as _mod

sys.modules[__name__] = _mod
