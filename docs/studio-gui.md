# adevkit Studio (Desktop GUI)

Launch the ReactPy + PyWebView desktop interface:

```bash
adevkit gui
```

> If you installed a headless CLI-only environment and see a missing dependency prompt, run `pip install "adevkit[gui]"`.

## Studio Views

1. **New project**: Interactive form with native OS folder picker, 12+ template cards, AI agent & skill selection, and workspace toggles.
2. **Live generation**: Real-time streaming terminal log of project scaffolding with one-click folder launch.
3. **Dependencies**: Auto-detects Rust, Node.js, or Python manifests; add/remove packages with `--dev` support.
4. **Skills hub**: Search and filter bundled or custom skills; install to a project or globally.
5. **Template studio**: Snapshot local folders into reusable custom templates and manage starters.
6. **Vault & settings**: View DPAPI/POSIX encryption status, manage secrets, and set Python/Node PM defaults.
7. **Diagnostics**: Live environment status for Python, `uv`, Cargo/`rustc`, Node PMs, Git, and update checks.
