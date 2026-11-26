"""Application state models and ReactPy context for adevkit Studio."""

from dataclasses import dataclass, field
from typing import List, Tuple, Optional
from reactpy import create_context


@dataclass
class GenerationJob:
    status: str = "idle"  # idle | running | success | error
    project_name: str = ""
    target_dir: str = ""
    logs: List[Tuple[str, str, str]] = field(default_factory=list)  # (tag, text, tone)


@dataclass
class ToastMessage:
    text: str
    tone: str = "info"  # info | success | warning | danger


# Shared context providing {route, navigate, bridge, job, set_job, notify}
AppContext = create_context(None)
