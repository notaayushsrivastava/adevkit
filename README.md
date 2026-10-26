# ⚡ Aayush's DevKit ⚡

> **One-Command Project Scaffolding with Agentic Skills & Environment Setup**

**Aayush's DevKit** is a fast, interactive developer toolkit CLI designed to initialize production-ready projects in seconds. It handles everything: asking project names, generating tailored codebases, auto-installing curated AI agent skills, creating comprehensive `AGENTS.md` and `PRD.md` documentation, and setting up isolated Python virtual environments, Git, Node packages, and VSCode settings.

---

## 🚀 Features

- **Interactive Terminal UI**: Built with `Typer`, `Rich`, and `InquirerPy` featuring branded ASCII art, arrow-key navigation, live progress spinners, and status tables.
- **5 Built-In Project Starters**:
  1. `nextjs`: Full-Stack Next.js 14/15 App Router, React 19, TypeScript, Tailwind CSS, Lucide Icons, and shadcn-ready layout.
  2. `python_fastapi`: Modern async Python backend with FastAPI, Pydantic v2, Typer CLI, and automated `.venv` & pytest.
  3. `vite_react`: Ultra-fast Frontend SPA with Vite 5, React 18, TypeScript, and Tailwind CSS.
  4. `minimal_agentic`: Clean blank repository with agent tools, `AGENTS.md`, and `PRD.md` ready for AI pair programming.
  5. `expo_mobile`: Cross-platform mobile starter with React Native, Expo SDK, and TypeScript.
- **Custom Template Engine**:
  - `devkit template save <NAME>`: Snapshot any existing directory or repo into reusable custom templates saved in `~/.aayush-devkit/templates/`.
  - `devkit template list`: View all built-in and custom templates.
  - `devkit template delete <NAME>`: Cleanly remove saved templates.
- **Agentic Skills Integration**:
  - Embeds curated agent skills directly into `.agents/skills/` and generates compliant `skills-lock.json` with sha256 checksums.
  - Built-in skills include:
    - **Ponytail Suite**: `ponytail`, `ponytail-audit`, `ponytail-review`, `ponytail-debt` (lazy senior dev mode).
    - **Modern Web**: HTML5/CSS standards, container queries, view transitions, and accessibility.
    - **Chrome DevTools**: Browser automation, DOM/CSS debugging, and performance profiling.
    - **Gemini API Dev**: Text/multimodal prompts, structured outputs, streaming, and tool calling.
- **Automated Environment Setup**:
  - **Python**: Creates `.venv` using active Python interpreter, installs `requirements.txt`.
  - **Node.js**: Automatically detects `bun`, `pnpm`, `yarn`, or `npm` and installs `node_modules`.
  - **Git**: Initializes repository and crafts stack-tailored `.gitignore`.
  - **Environment**: Copies `.env.example` to `.env` without overwriting.
  - **VSCode**: Scaffolds `.vscode/settings.json` and `.vscode/extensions.json`.
- **Intelligent Documentation**:
  - **`AGENTS.md`**: Pre-configured architectural guidelines, dev/build/test commands, and rules for AI assistants (Antigravity, Cursor, Claude Code, Gemini CLI).
  - **`PRD.md`**: Guided prompt wizard, standardized comprehensive starter, or path-based import.

---

## 📦 Quick Start

### 1. Run Directly
```powershell
python app.py
```
Or with Windows command script:
```powershell
.\devkit.cmd
```

### 2. Global Installation
Install globally in editable mode:
```powershell
pip install -e .
```
Now run `devkit` from any folder in your terminal:
```powershell
devkit init
```

---

## 🛠 Commands

### Initialize a New Project
```powershell
# Interactive wizard
devkit init

# Specify name and target directory
devkit init my-api -t python_fastapi

# Non-interactive / CI mode
devkit init my-app -t nextjs -s ponytail -s modern-web-guidance --yes
```

### Manage Custom Templates
```powershell
# Snapshot current folder as a reusable template
devkit template save my-starter --desc "Company internal microservice"

# Snapshot specific folder
devkit template save my-starter --path "C:\path\to\project"

# List all available templates (built-in and custom)
devkit template list

# Delete a custom template
devkit template delete my-starter
```

### Manage Agent Skills
```powershell
# List curated skill catalog
devkit skills list

# Install a skill into the current project
devkit skills add modern-web-guidance
```

### System Diagnostics
```powershell
devkit info
```

---

## 🧪 Running Tests

The test suite covers template scaffolding, custom template snapshots, skills installation, lockfile verification, and environment setup:

```powershell
.\.venv\Scripts\pytest.exe tests/ -v
```

---

## 📄 License
MIT © Aayush
