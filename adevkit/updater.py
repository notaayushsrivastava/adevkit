"""Backward-compatible facade for adevkit.core.updater."""
import sys
from .core import updater as _mod

sys.modules[__name__] = _mod
