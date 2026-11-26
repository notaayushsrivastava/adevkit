# Dependency Management

`adevkit` automatically detects your project's manifest (`Cargo.toml`, `package.json`, `pyproject.toml`, or `requirements.txt`) and delegates to the appropriate package manager.

## Add Dependencies

```bash
# Rust (Cargo)
adevkit add serde tokio

# JavaScript / TypeScript (bun, pnpm, yarn, or npm)
adevkit add zod lucide-react
adevkit add vitest --dev

# Python (uv or pip)
adevkit add fastapi uvicorn
```

## Remove & List Dependencies

```bash
adevkit remove zod
adevkit deps list
```

## Preferred Package Managers

Configure your global default Python or Node.js package manager:

```bash
adevkit config set-python-pm uv      # or pip
adevkit config set-node-pm pnpm      # bun, pnpm, yarn, or npm
```
