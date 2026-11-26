"""Backward-compatible facade for adevkit.core.vault."""
import sys
from .core import vault as _mod

sys.modules[__name__] = _mod
