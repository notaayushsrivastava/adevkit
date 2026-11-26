# Installation

## Python (`pip`)

### Default (CLI + Studio GUI)
Installs both the CLI and the ReactPy + PyWebView desktop Studio (`adevkit gui`):

```bash
pip install adevkit
```

### Explicit Extras
```bash
# Explicit GUI extras
pip install "adevkit[gui]"

# Minimal / headless environments
pip install "adevkit[cli]"
```

## Native OS Packages

### Windows (WinGet)
```powershell
winget install notaayushsrivastava.adevkit
```

### Debian / Ubuntu (APT)
```bash
sudo apt update && sudo apt install adevkit
```

### macOS (PKG)
Download the latest `.pkg` installer from [GitHub Releases](https://github.com/notaayushsrivastava/adevkit/releases/latest) or install via `curl`:

```bash
curl -LO https://github.com/notaayushsrivastava/adevkit/releases/latest/download/adevkit-macos.pkg
sudo installer -pkg adevkit-macos.pkg -target /
```

## Verify Installation

```bash
adevkit info
```
