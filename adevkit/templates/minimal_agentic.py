from typing import List
from .base import BaseTemplate

class MinimalAgenticTemplate(BaseTemplate):
    id = "minimal_agentic"
    name = "Minimal Agentic Repo (Blank starter + Agent Skills)"
    short_name = "Minimal Agentic Starter"
    description = "Clean, stack-agnostic blank repository primed for AI pair programming with AGENTS.md, PRD.md, and skills."
    category = "Agentic / Starter"
    has_node = False
    has_python = False

    def scaffold(self) -> List[str]:
        files_created = []

        readme = """# {{PROJECT_NAME}}

Welcome to **{{PROJECT_NAME}}**, created with **Aayush's DevKit**.

## Overview
This repository is configured with an agentic architecture optimized for pair-programming with AI assistants (Antigravity, Cursor, Claude Code, Gemini CLI).

## Key Files
- `AGENTS.md`: Agent instructions, coding guidelines, and rules.
- `PRD.md`: Product Requirements Document and project scope.
- `skills-lock.json`: Active agent skills installed in `.agents/skills/`.

## Getting Started
Begin by reviewing `PRD.md` and outlining your core domain tasks.
"""
        self.write_file("README.md", readme)
        files_created.append("README.md")

        return files_created
