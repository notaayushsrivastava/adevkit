"""Backward-compatible facade for adevkit.core.scaffold.env_setup."""
import sys
from ..core.scaffold import env_setup as _mod
sys.modules[__name__] = _mod
