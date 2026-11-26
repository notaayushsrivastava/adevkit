# Project Templates

## Built-In Starters (12)

| Template ID | Stack | Description |
| --- | --- | --- |
| `nextjs` | JS / TS | Next.js 15 App Router, React 19, TypeScript, Tailwind CSS |
| `saas_fullstack` | JS / TS | Next.js 15, Prisma ORM, Stripe subscriptions, Auth |
| `design_system` | JS / TS | Tokenized UI component library with Framer Motion |
| `content_site` | JS / TS | Astro 4 marketing/content site with Tailwind Typography |
| `vite_react` | JS / TS | Vite 5 + React + TypeScript + Tailwind SPA |
| `expo_mobile` | JS / TS | React Native + Expo SDK + TypeScript |
| `expo_fullstack` | Fullstack | Expo mobile frontend + FastAPI or Node Hono backend |
| `python_fastapi` | Python | Async FastAPI, Pydantic v2, Typer CLI, pytest |
| `ai_agents_python` | Python | Multi-agent state graphs, memory, FastAPI endpoints |
| `rust_cli` | Rust | Clap v4 derive, Tokio async runtime, Anyhow, tracing |
| `rust_axum` | Rust | Axum 0.7, Tokio, Tower-HTTP CORS/Trace, Serde JSON |
| `minimal_agentic` | Universal | Clean workspace with `AGENTS.md`, `PRD.md`, and skills |

## Custom Templates

Snapshot any local folder into a reusable template stored in `~/.adevkit/templates/`:

```bash
adevkit template save client-portal --path ./my-portal --desc "Standard client starter"
adevkit template list
adevkit template delete client-portal
```
