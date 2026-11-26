# Vault & Settings

`adevkit` stores global settings and API credentials in `~/.adevkit/vault.json`.

- **Windows**: Sensitive keys (`*_key`, `*_token`, `*_secret`, `*_password`) are encrypted using Windows DPAPI (`CryptProtectData`).
- **macOS & Linux**: Sensitive keys are encrypted using a salted user-and-machine derived key.

## Manage Secrets

```bash
adevkit config set anthropic_api_key sk-ant-...
adevkit config get anthropic_api_key          # masked by default
adevkit config get anthropic_api_key --reveal # decrypted output
adevkit config list
adevkit config delete anthropic_api_key
```

## Default AI Agents & Toolchains

```bash
adevkit config set-agents antigravity cursor claude
adevkit config set-python-pm uv
adevkit config set-node-pm pnpm
```
