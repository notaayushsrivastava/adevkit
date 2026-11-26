"""PyWebView + ReactPy desktop launcher for adevkit Studio."""

import os
import socket
import sys
import threading
from pathlib import Path
import uvicorn
import webview
from reactpy.backend.starlette import configure
from starlette.applications import Starlette

from .app import DevKitApp
from .bridge import DevKitBridge


_ASSETS_DIR = Path(__file__).resolve().parent / "assets"


class _CompatStarlette(Starlette):
    """Compatibility shim for Starlette >=1.0 where add_websocket_route moved to router."""

    def add_websocket_route(self, path, route, name=None):
        return self.router.add_websocket_route(path, route, name=name)


def create_gui_app(bridge: DevKitBridge) -> Starlette:
    """Create and configure the Starlette + ReactPy ASGI application."""
    app = _CompatStarlette()
    configure(app, lambda: DevKitApp(bridge=bridge))
    return app


def get_app_icon_path() -> str | None:
    """Return path to the bundled app icon (.ico on Windows, .png elsewhere)."""
    ico = _ASSETS_DIR / "icon.ico"
    png = _ASSETS_DIR / "icon.png"
    if sys.platform == "win32" and ico.exists():
        return str(ico)
    if png.exists():
        return str(png)
    return None


def _find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return int(s.getsockname()[1])


def launch_gui(debug: bool = False):
    """Start local ReactPy server, open PyWebView window, and exit cleanly on close."""
    bridge = DevKitBridge()
    app = create_gui_app(bridge)

    port = _find_free_port()
    server_config = uvicorn.Config(app, host="127.0.0.1", port=port, log_level="warning")
    server = uvicorn.Server(server_config)

    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()

    window = webview.create_window(
        title="adevkit Studio",
        url=f"http://127.0.0.1:{port}",
        width=1200,
        height=780,
        min_size=(960, 620),
        background_color="#090A0F",
    )
    bridge.attach_window(window)

    def _on_closed():
        server.should_exit = True

    window.events.closed += _on_closed

    try:
        webview.start(debug=debug, icon=get_app_icon_path())
    finally:
        server.should_exit = True
        thread.join(timeout=1.0)
        os._exit(0)
