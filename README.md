# ⚡ Aayush's DevKit ⚡

> **One-Command Project Scaffolding with Agentic Skills & Environment Setup**

**Aayush's DevKit** is a fast, interactive developer toolkit CLI designed to initialize production-ready projects in seconds. It handles everything: asking project names, generating tailored codebases, auto-installing curated AI agent skills, creating comprehensive `AGENTS.md` and `PRD.md` documentation, and setting up isolated Python virtual environments, Git, Node packages, and VSCode settings.

---

## 🚀 Features

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
  - `devkit template save <NAME>`: Snapshot any existing directory or repo into reusable custom templates saved in `~/.aayush-devkit/templates/`.
  - `devkit template list`: View all built-in and custom templates.
  - `devkit template delete <NAME>`: Cleanly remove saved templates.
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
  - **Python**: Creates `.venv` using active Python interpreter, installs `requirements.txt`.
  - **Node.js**: Automatically detects `bun`, `pnpm`, `yarn`, or `npm` and installs `node_modules`.
  - **Git**: Initializes repository and crafts stack-tailored `.gitignore`.
  - **Environment**: Copies `.env.example` to `.env` without overwriting.
  - **VSCode**: Scaffolds `.vscode/settings.json` and `.vscode/extensions.json`.
- **Intelligent Documentation**:
  - **`AGENTS.md`**: Injects tailored guidelines for AI assistants (Antigravity, Cursor, Claude Code, Gemini CLI), including anti-generic design rules and Vercel Server Component patterns when relevant skills are selected.
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
devkit init my-saas -t saas_fullstack

# Non-interactive / CI mode
devkit init my-app -t nextjs -s ponytail -s impeccable -s design-taste-frontend --yes
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
devkit skills add impeccable

# Sync and reload skills catalog
devkit skills update
```

### System Diagnostics
```powershell
devkit info
```

---

## 🧪 Running Tests

The test suite covers all 10 templates, custom template snapshots, skills installation, lockfile verification, and environment setup:

```powershell
.\.venv\Scripts\pytest.exe tests/ -v
```

---

## 📄 License
MIT © Aayush
