# Contributing to adevkit

Thank you for your interest in contributing to **adevkit**! We welcome bug reports, feature proposals, new project templates, agent skills, Studio GUI improvements, and documentation updates.

## Code of Conduct
All contributors and maintainers are expected to abide by our [Code of Conduct](CODE_OF_CONDUCT.md).

---

## Architecture Overview

```text
adevkit/
├── core/        # Headless business logic (templates, skills, deps, vault, scaffold, updater)
├── cli/         # Modular Typer CLI commands & Rich terminal UI
└── gui/         # ReactPy + PyWebView desktop Studio (`adevkit gui`)
web/             # Vercel static landing page
docs/            # Sphinx + Furo Read the Docs documentation
tests/           # Pytest suite
```

---

## Local Development Setup

1. **Fork and clone** the repository:
   ```bash
   git clone https://github.com/notaayushsrivastava/adevkit.git
   cd adevkit
   ```
2. **Create a virtual environment** and install in editable mode with GUI & test dependencies:
   ```bash
   python -m venv .venv
   # Windows:
   .\.venv\Scripts\activate
   # macOS / Linux:
   source .venv/bin/activate

   pip install -e ".[gui]"
   pip install pytest
   ```
3. **Run the test suite**:
   ```bash
   pytest -v
   ```

---

## Common Contribution Workflows

### Adding a Built-In Template
1. Create a template class under `adevkit/core/templates/` inheriting from `BaseTemplate`.
2. Register it in `adevkit/core/templates/__init__.py` (`BUILTIN_TEMPLATES`).
3. Add recommended skills in `adevkit/core/skills/catalog.py`.
4. Add scaffolding tests under `tests/`.

### Adding a Curated Agent Skill
1. Place the skill directory containing `SKILL.md` under `adevkit/core/skills/embedded/<skill-id>/`.
2. Index it in `adevkit/core/skills/catalog.py`.
3. Verify skill installation with `tests/test_skills.py`.

### Working on the Studio GUI (`adevkit/gui/`)
- Follow the design tokens in `adevkit/gui/styles.py`.
- Keep all `reactpy` and `pywebview` imports isolated inside `adevkit/gui/` so `adevkit[cli]` remains headless-safe.
- Test rendering via `tests/test_architecture_and_gui.py` and visually verify with `python -m adevkit gui`.

---

## Pull Request Process
1. Create a feature branch from `main` (e.g., `feat/my-template` or `fix/vault-edge-case`).
2. Keep changes focused and include unit tests in `tests/`.
3. Ensure `pytest -v` passes completely.
4. Open a Pull Request using the PR template and link any related issue.
