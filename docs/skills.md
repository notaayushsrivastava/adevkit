# Agent Skills

`adevkit` bundles curated agent skills for offline use and supports `skills.sh`-style installation from GitHub repositories, URLs, or local directories.

## List Available Skills

```bash
adevkit skills list
```

## Install Skills

```bash
# Install from embedded catalog into current project (.agents/skills/)
adevkit skills add vercel-react-best-practices

# Install from GitHub shorthand into global store (~/.adevkit/skills/)
adevkit skills add owner/repo --global
```

## Create & Manage Custom Skills

```bash
adevkit skills create team-standards --desc "Repository coding conventions" --global
adevkit skills remove team-standards --global
adevkit skills update
```
