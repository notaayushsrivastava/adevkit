"""Backward-compatible facade for adevkit.core.scaffold.agent_configs."""
import sys
from ..core.scaffold import agent_configs as _mod
sys.modules[__name__] = _mod
