# adevkit Documentation

**adevkit** (Aayush's DevKit) is a single-command project scaffolding CLI and desktop Studio GUI designed for AI-assisted engineering workflows.

```bash
pip install adevkit
adevkit init my-project
```

## Capabilities

- **12 Built-In Templates**: Next.js 15, SaaS Fullstack, FastAPI, AI Agents, Rust CLI, Rust Axum, Expo Mobile, Expo Fullstack, Astro, Vite React, Design System, and Minimal Agentic.
- **Multi-Agent Context**: Generates tailored `AGENTS.md`, `PRD.md`, and native rules for Antigravity, Cursor, Claude Code, GitHub Copilot, Windsurf, and Aider.
- **Bundled Agent Skills**: Offline-ready skills catalog (`skills.sh` compatible) with lockfile tracking.
- **Cross-Ecosystem Dependencies**: Unified `adevkit add` / `adevkit remove` / `adevkit deps list` for Rust (`cargo`), JavaScript (`bun`, `pnpm`, `yarn`, `npm`), and Python (`uv`, `pip`).
- **Encrypted Vault**: Windows DPAPI and POSIX salted encryption for API keys and toolchain defaults.
- **Studio Desktop GUI**: ReactPy + PyWebView desktop application via `adevkit gui`.

```{toctree}
:maxdepth: 2
:caption: Getting Started

installation
quickstart
studio-gui
```

```{toctree}
:maxdepth: 2
:caption: Core Workflows

templates
skills
dependencies
vault
```

```{toctree}
:maxdepth: 2
:caption: Reference

cli-reference
```
