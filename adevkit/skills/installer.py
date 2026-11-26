"""Backward-compatible facade for adevkit.core.skills.installer."""
import sys
from ..core.skills import installer as _mod
sys.modules[__name__] = _mod
