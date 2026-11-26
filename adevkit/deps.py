"""Backward-compatible facade for adevkit.core.deps."""
import sys
from .core import deps as _mod

sys.modules[__name__] = _mod
