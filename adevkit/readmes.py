"""Backward-compatible facade for adevkit.core.readmes."""
import sys
from .core import readmes as _mod

sys.modules[__name__] = _mod
