"""Backward-compatible facade for adevkit.core.templates.custom."""
import sys
from ..core.templates import custom as _mod
sys.modules[__name__] = _mod
