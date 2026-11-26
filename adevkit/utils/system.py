"""Backward-compatible facade for adevkit.core.utils.system."""
import sys
from ..core.utils import system as _mod
sys.modules[__name__] = _mod
