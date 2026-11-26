"""Backward-compatible facade for adevkit.core.skills.catalog."""
import sys
from ..core.skills import catalog as _mod
sys.modules[__name__] = _mod
