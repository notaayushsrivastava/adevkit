"""Backward-compatible facade for adevkit.core.skills.custom."""
import sys
from ..core.skills import custom as _mod
sys.modules[__name__] = _mod
