# CLI Reference

## Top-Level Commands

| Command | Description |
| --- | --- |
| `adevkit init [DIR]` | Initialize a new project interactively or with flags |
| `adevkit gui` | Launch the adevkit Studio desktop GUI |
| `adevkit add <PKGS...>` | Add dependencies (`--dev` for dev dependencies) |
| `adevkit remove <PKGS...>` | Remove dependencies from current project |
| `adevkit info` | Display environment diagnostics and detected tooling |
| `adevkit check-update` | Check PyPI / GitHub Releases for updates |

## Subcommand Groups

- `adevkit template {list, save, delete}`
- `adevkit skills {list, add, create, remove, update}`
- `adevkit deps {add, remove, list}`
- `adevkit config {list, set, get, delete, set-agents, set-python-pm, get-python-pm, set-node-pm, get-node-pm}`
- `adevkit readme {list, save, show, delete, generate}`
