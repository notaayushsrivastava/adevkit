"""Backward-compatible facade for adevkit.core.prompts."""
import sys
from .core import prompts as _mod

sys.modules[__name__] = _mod
