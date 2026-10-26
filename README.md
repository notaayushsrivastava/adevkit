```text
 █████╗  █████╗ ██╗   ██╗██╗   ██╗███████╗██╗  ██╗███████╗    ██████╗ ███████╗██╗   ██╗██╗  ██╗██╗████████╗
██╔══██╗██╔══██╗╚██╗ ██╔╝██║   ██║██╔════╝██║  ██║██╔════╝    ██╔══██╗██╔════╝██║   ██║██║ ██╔╝██║╚══██╔══╝
███████║███████║ ╚████╔╝ ██║   ██║███████╗███████║███████╗    ██║  ██║█████╗  ██║   ██║█████╔╝ ██║   ██║   
██╔══██║██╔══██║  ╚██╔╝  ██║   ██║╚════██║██╔══██║╚════██║    ██║  ██║██╔══╝  ╚██╗ ██╔╝██╔═██╗ ██║   ██║   
██║  ██║██║  ██║   ██║   ╚██████╔╝███████║██║  ██║███████║    ██████╔╝███████╗ ╚████╔╝ ██║  ██╗██║   ██║   
╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝    ╚═════╝ ╚══════╝╚═╝  ╚═╝╚══════╝    ╚═════╝ ╚══════╝  ╚═══╝  ╚═╝  ╚═╝╚═╝   ╚═╝   
```

# adevkit (Aayush's DevKit)

> **One-Command Project Scaffolding with Agentic Skills, AI Assistant Guidelines & Environment Setup**  
> Developed and published by **[Aayush Srivastava](https://aayushsrivastava.com)**

[![Build & Release](https://github.com/notaayushsrivastava/adevkit/actions/workflows/release.yml/badge.svg)](https://github.com/notaayushsrivastava/adevkit/actions/workflows/release.yml)
[![PyPI Version](https://img.shields.io/pypi/v/adevkit.svg?color=blue)](https://pypi.org/project/adevkit/)
[![Python Versions](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://pypi.org/project/adevkit/)
[![GitHub Release](https://img.shields.io/github/v/release/notaayushsrivastava/adevkit?color=brightgreen&label=release)](https://github.com/notaayushsrivastava/adevkit/releases/latest)
[![WinGet Package](https://img.shields.io/badge/winget-notaayushsrivastava.adevkit-0078D4?logo=windows&logoColor=white)](https://github.com/microsoft/winget-pkgs)
[![APT Repository](https://img.shields.io/badge/apt-repository-A81D33?logo=debian&logoColor=white)](https://notaayushsrivastava.github.io/adevkit)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Author](https://img.shields.io/badge/Author-Aayush%20Srivastava-111827?logo=google-chrome&logoColor=white)](https://aayushsrivastava.com)

**adevkit** (Aayush's DevKit) is a fast, interactive developer toolkit CLI designed to initialize production-ready projects in seconds. It handles everything: asking project names, generating tailored codebases, selecting target AI coding assistants (Antigravity, Cursor, Claude Code, GitHub Copilot, Windsurf, Aider), auto-installing curated and custom AI agent skills (like `skills.sh`), creating comprehensive specifications, securely storing API credentials (with Windows DPAPI encryption), and setting up isolated Python virtual environments, Git, Node packages, and VSCode settings.

---

## Features

- **Interactive Terminal UI**: Built with `Typer`, `Rich`, and `InquirerPy` featuring branded ASCII art, arrow-key navigation, live progress spinners, and status tables.
- **10 Built-In Project Starters**:
  1. `nextjs`: Full-Stack Next.js 14/15 App Router, React 19, TypeScript, Tailwind CSS, Lucide Icons, and shadcn-ready layout.
  2. `saas_fullstack`: Production-grade SaaS starter with Next.js 15, Prisma ORM, Stripe subscriptions, and Auth.
  3. `design_system`: Tokenized UI component library with Framer Motion, accessible primitives, and interactive showcase.
  4. `content_site`: Blazing-fast content and marketing website with Astro 4, Tailwind Typography, and zero JS by default.
  5. `python_fastapi`: Modern async Python backend with FastAPI, Pydantic v2, Typer CLI, and automated `.venv` & pytest.
  6. `ai_agents_python`: Asynchronous multi-agent framework starter with state graphs, memory, and FastAPI endpoints.
  7. `vite_react`: Ultra-fast Frontend SPA with Vite 5, React 18, TypeScript, and Tailwind CSS.
  8. `minimal_agentic`: Clean blank repository with agent tools, `AGENTS.md`, and `PRD.md` ready for AI pair programming.
  9. `expo_mobile`: Cross-platform mobile starter with React Native, Expo SDK, and TypeScript.
  10. `expo_fullstack`: Monorepo with Expo React Native mobile `frontend/` and selectable `backend/` (FastAPI or Node.js Hono).
- **Custom Template Engine**:
  - `adevkit template save <NAME>`: Snapshot any existing directory or repo into reusable custom templates saved in `~/.adevkit/templates/`.
  - `adevkit template list`: View all built-in and custom templates.
  - `adevkit template delete <NAME>`: Cleanly remove saved templates.
- **42 Embedded Curated Agent Skills**:
  - Direct, 100% offline access to all curated skills with automatic `.agents/skills/` population and valid `skills-lock.json` generation.
  - Sourced from top engineering leaders:
    - **`pbakaus/impeccable`**: Design craftsmanship, typography hierarchy, spacing & layout polish.
    - **`Leonxlnx/taste-skill` (`design-taste-frontend`)**: Aesthetic taste, anti-generic UI, distinctive art direction & color harmony.
    - **`DietrichGebert/ponytail`**: `ponytail`, `ponytail-audit`, `ponytail-review`, `ponytail-debt`, `ponytail-gain`, `ponytail-help`.
    - **`vercel-labs/agent-skills`**: `vercel-react-best-practices`, `vercel-composition-patterns`, `vercel-optimize`, `deploy-to-vercel`, `vercel-react-view-transitions`.
    - **`nextlevelbuilder/ui-ux-pro-max-skill`**: `ui-ux-pro-max`, `design`, `design-system`, `ui-styling`, `brand`, `banner-design`, `slides`.
    - **`emilkowalski/skills`**: `emil-design-eng`, `animate`, `animate-expo`, `animation-performance`, `apple-design`, `break-ui`, `improve-animations`, `mobile-native`.
- **Automated Environment Setup**:
  - **Python**: Automated `.venv` creation and dependency installation via **`uv`** (Astral's ultra-fast Python manager) or standard `venv`/`pip`. Configurable per-project via `--uv`/`--no-uv` or globally via `adevkit config set-python-pm uv`.
  - **Node.js**: Automatically detects `bun`, `pnpm`, `yarn`, or `npm` and installs `node_modules`.
  - **Git**: Initializes repository and crafts stack-tailored `.gitignore`.
  - **Environment**: Copies `.env.example` to `.env` without overwriting.
  - **VSCode**: Scaffolds `.vscode/settings.json` and `.vscode/extensions.json`.
- **Intelligent Documentation**:
  - **`AGENTS.md`**: Injects tailored guidelines for AI assistants (Antigravity, Cursor, Claude Code, Gemini CLI), including anti-generic design rules and Vercel Server Component patterns when relevant skills are selected.
  - **`PRD.md`**: Guided prompt wizard, standardized comprehensive starter, or path-based import.
  - **`README.md` Templates**: Choose from 4 built-in styles (`modern`, `minimal`, `enterprise`, `agentic`) or create and save reusable custom templates in `~/.adevkit/readmes/` with dynamic placeholder interpolation.
- **Automatic Multi-Channel Update Checker**:
  - Automatically identifies whether running as a Python package (`adevkit` via PyPI) or native Windows MSI installer (via GitHub Releases).
  - Background, non-blocking check with 24-hour smart caching in `~/.aayush-devkit/update_cache.json`.
  - Manual check command via `adevkit check-update` (`--type python`, `--type msi`, or `--type all`).

---

## Quick Start

### 1. Install via PyPI (All Platforms)
```bash
pip install --upgrade adevkit
```
Now run `adevkit` anywhere in your terminal (shorthand `devkit` is also supported):
```bash
adevkit init
```

### 2. Universal 1-Line Installer (Linux & macOS)
```bash
curl -fsSL https://raw.githubusercontent.com/notaayushsrivastava/adevkit/main/installer/install.sh | bash
```

### 3. Native Platform Installers
- **Windows (WinGet)**: Install and update directly via Windows Package Manager:
  ```powershell
  winget install notaayushsrivastava.adevkit
  ```
- **Windows (Direct MSI)**: Download and run [`AayushsDevKit-v0.1.4-x64.msi`](https://github.com/notaayushsrivastava/adevkit/releases). It automatically configures `adevkit` (and alias `devkit`) in your system `PATH`.
- **macOS**: Download and run [`AayushsDevKit-v0.1.4-macos.pkg`](https://github.com/notaayushsrivastava/adevkit/releases) (or extract `devkit-v0.1.4-macos-arm64.tar.gz`).
- **Linux (Debian/Ubuntu)**: Download [`notaayushsrivastava.adevkit_0.1.4_amd64.deb`](https://github.com/notaayushsrivastava/adevkit/releases) and run `sudo dpkg -i notaayushsrivastava.adevkit_0.1.4_amd64.deb` (or extract `devkit-v0.1.4-linux-x64.tar.gz`).
- **APT repository (Debian/Ubuntu)**: Configure the repository once, then install and update with APT:
  ```bash
  curl -fsSL https://raw.githubusercontent.com/notaayushsrivastava/adevkit/main/installer/install-apt.sh | bash
  ```
  This adds the signed APT source and installs `notaayushsrivastava.adevkit`. Future updates are available through:
  ```bash
  sudo apt update
  sudo apt install notaayushsrivastava.adevkit
  ```

The APT repository is published to GitHub Pages by the release workflow. Repository
maintainers must enable Pages for the `gh-pages` branch and add an
`APT_GPG_PRIVATE_KEY` Actions secret containing the ASCII-armored private key used
to sign repository metadata. Generate a dedicated key with:
```bash
gpg --quick-generate-key "adevkit APT repository" rsa3072 sign 2y
gpg --armor --export-secret-keys "adevkit APT repository" > apt-private-key.asc
```
Keep `apt-private-key.asc` private; only the generated public key is published.

WinGet submissions to the Windows Package Manager Community Repository (`microsoft/winget-pkgs`)
are automated by `.github/workflows/winget-submission.yml`. Repository maintainers
should configure a `WINGET_TOKEN` Actions secret (a Classic GitHub Personal Access Token
with `public_repo` and `workflow` scopes) and fork `microsoft/winget-pkgs` to allow
automated pull request generation. Manifests are generated and validated via
`.\installer\build_winget_manifest.ps1`.

### 4. Run Directly from Source
```powershell
python app.py
```
Or with Windows command script:
```powershell
.\adevkit.cmd
```

---

## Commands

### Initialize a New Project
```powershell
# Interactive wizard
adevkit init

# Specify name and target directory
adevkit init my-saas -t saas_fullstack

# Non-interactive / CI mode
adevkit init my-app -t nextjs -s ponytail -s impeccable -s design-taste-frontend --yes
```

### Manage Custom Templates
```powershell
# Snapshot current folder as a reusable template
adevkit template save my-starter --desc "Company internal microservice"

# Snapshot specific folder
adevkit template save my-starter --path "C:\path\to\project"

# List all available templates (built-in and custom)
adevkit template list

# Delete a custom template
adevkit template delete my-starter
```

### Manage Agent Skills (skills.sh compatible)
```powershell
# List curated and user-added custom skills
adevkit skills list

# Install a skill from the curated catalog into current project
adevkit skills add impeccable

# Install any skill from GitHub repo or shorthand (like skills.sh)
adevkit skills add owner/repo
adevkit skills add https://github.com/owner/repo/tree/main/path/to/skill

# Install a skill from a local folder or raw SKILL.md URL
adevkit skills add ./my-local-skill
adevkit skills add https://example.com/SKILL.md

# Install globally to ~/.adevkit/skills/ (available in every project)
adevkit skills add ./team-standards --global

# Scaffold a brand new custom skill template
adevkit skills create my-custom-skill --desc "Custom guidelines"

# Remove a custom skill
adevkit skills remove my-custom-skill --global
```

### Customizable README Templates
```powershell
# List available built-in and user-custom README templates
adevkit readme list

# Save a custom reusable README template
adevkit readme save my-org-readme --path ./my-template.md

# Preview a README template
adevkit readme show enterprise

# Generate or regenerate README for any folder
adevkit readme generate --style enterprise --target ./my-project

# Delete a custom README template
adevkit readme delete my-org-readme
```

### Secure Configuration & AI Agent Defaults
```powershell
# View configured settings (secrets are masked by default)
adevkit config list

# Store API keys securely (Windows DPAPI / POSIX host encryption)
adevkit config set anthropic_api_key "sk-ant-..."
adevkit config set openai_api_key "sk-proj-..."

# Configure global default AI coding assistants for project scaffolding
adevkit config set-agents antigravity cursor claude copilot

# Retrieve a value (optionally reveal unmasked secret)
adevkit config get anthropic_api_key --reveal

# Delete a configuration key
adevkit config delete openai_api_key
```

### Check for Updates
```powershell
# Check for updates for active installation channel (PyPI adevkit or GitHub MSI)
adevkit check-update

# Force check specific channel or both
adevkit check-update --type python
adevkit check-update --type msi
adevkit check-update --type all
```

### System Diagnostics
```powershell
adevkit info
```

---

## Running Tests

The test suite covers all 10 templates, custom template snapshots, skills installation, lockfile verification, and environment setup:

```powershell
.\.venv\Scripts\pytest.exe tests/ -v
```

---

## Author & Publisher

Developed and maintained by **[Aayush Srivastava](https://aayushsrivastava.com)**.
- **Website**: [aayushsrivastava.com](https://aayushsrivastava.com)
- **GitHub**: [@notaayushsrivastava](https://github.com/notaayushsrivastava)

---

## License

MIT License (c) 2026-Present [Aayush Srivastava](https://aayushsrivastava.com). All rights reserved.