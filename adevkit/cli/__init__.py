"""Modular CLI package for adevkit."""

from .main import app, main
from .commands.init import init

__all__ = ["app", "main", "init"]
