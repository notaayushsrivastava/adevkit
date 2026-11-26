"""Design system tokens, base styles, and compositor-only animations for adevkit Studio."""

DESIGN_SYSTEM_CSS = """
:root {
  --bg-canvas: #090A0F;
  --bg-surface: #12141C;
  --bg-elevated: #1A1D28;
  --border-subtle: #242838;
  --border-active: #3B4259;
  --text-primary: #F1F5F9;
  --text-secondary: #94A3B8;
  --text-muted: #7B8AA0;
  --accent-primary: #38BDF8;
  --accent-primary-deep: #0284C7;
  --accent-success: #10B981;
  --accent-warning: #F59E0B;
  --accent-danger: #EF4444;
  --accent-rust: #DEA584;
  --accent-node: #22C55E;
  --accent-python: #38BDF8;
  --ease-out: cubic-bezier(0.23, 1, 0.32, 1);
  --ease-in-out: cubic-bezier(0.77, 0, 0.175, 1);
  --ease-drawer: cubic-bezier(0.32, 0.72, 0, 1);
  --font-ui: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  --font-mono: 'JetBrains Mono', 'Fira Code', Menlo, Consolas, monospace;
}

* { box-sizing: border-box; }
html, body {
  margin: 0;
  padding: 0;
  background: var(--bg-canvas);
  color: var(--text-primary);
  font-family: var(--font-ui);
  font-size: 14px;
  line-height: 1.5;
  -webkit-font-smoothing: antialiased;
}

::-webkit-scrollbar { width: 8px; height: 8px; }
::-webkit-scrollbar-track { background: var(--bg-canvas); }
::-webkit-scrollbar-thumb { background: var(--border-subtle); border-radius: 999px; }
::-webkit-scrollbar-thumb:hover { background: var(--border-active); }

/* Sidebar navigation items: fast color + tactile press */
.ak-nav {
  transition: background-color 150ms ease, color 150ms ease, transform 100ms var(--ease-out);
}
.ak-nav:active {
  transform: scale(0.98);
}

/* Buttons: instant pointer-down feedback (Apple Design) */
.ak-btn {
  transition: transform 100ms var(--ease-out), background-color 150ms ease, border-color 150ms ease, opacity 150ms ease;
  cursor: pointer;
  font-family: var(--font-ui);
}
.ak-btn:active:not(:disabled) {
  transform: scale(0.97);
}
.ak-btn:disabled { opacity: 0.45; cursor: not-allowed; }

/* Cards: explicit properties only (never transition: all) */
.ak-card {
  background: var(--bg-surface);
  border: 1px solid var(--border-subtle);
  border-radius: 12px;
  transition: border-color 150ms ease, background-color 150ms ease, transform 150ms var(--ease-out);
}
.ak-card-interactive:active {
  transform: scale(0.99);
}
.ak-card-selected {
  border-color: var(--accent-primary) !important;
  background: var(--bg-elevated) !important;
}

/* Hover gating for pointer devices only */
@media (hover: hover) and (pointer: fine) {
  .ak-nav:hover {
    background: var(--bg-elevated) !important;
    color: var(--text-primary) !important;
  }
  .ak-btn:hover:not(:disabled) {
    filter: brightness(1.08);
  }
  .ak-card-interactive:hover {
    border-color: var(--border-active);
    background: var(--bg-elevated);
  }
}

.ak-input {
  width: 100%;
  height: 36px;
  padding: 0 12px;
  border-radius: 8px;
  border: 1px solid var(--border-subtle);
  background: var(--bg-canvas);
  color: var(--text-primary);
  font-family: var(--font-ui);
  font-size: 13.5px;
  outline: none;
  transition: border-color 150ms ease;
}
.ak-input:focus {
  border-color: var(--accent-primary);
}
.ak-input-mono {
  font-family: var(--font-mono);
  font-size: 13px;
}

.ak-virtual-row {
  content-visibility: auto;
  contain-intrinsic-size: auto 44px;
}

/* Compositor-only animations (transform + opacity) */
@keyframes ak-spin {
  to { transform: rotate(360deg); }
}
.ak-spinner {
  width: 14px;
  height: 14px;
  border-radius: 999px;
  border: 2px solid var(--border-subtle);
  border-top-color: var(--accent-primary);
  animation: ak-spin 800ms linear infinite;
  display: inline-block;
  flex: none;
}

@keyframes ak-panel-enter {
  from {
    opacity: 0;
    transform: translateY(6px) scale(0.994);
  }
  to {
    opacity: 1;
    transform: none;
  }
}
.ak-main-panel {
  view-transition-name: main-panel;
  animation: ak-panel-enter 190ms var(--ease-out) both;
}

@keyframes ak-toast-enter {
  from {
    opacity: 0;
    transform: translateY(-4px) scale(0.97);
  }
  to {
    opacity: 1;
    transform: none;
  }
}
.ak-toast {
  animation: ak-toast-enter 180ms var(--ease-out) both;
}

@keyframes ak-log-enter {
  from {
    opacity: 0;
    transform: translateY(3px);
  }
  to {
    opacity: 1;
    transform: none;
  }
}
.ak-log-line {
  animation: ak-log-enter 140ms var(--ease-out) both;
}

/* View Transitions */
@keyframes ak-fade-in { from { opacity: 0; } }
@keyframes ak-fade-out { to { opacity: 0; } }
@keyframes ak-slide-in-right { from { opacity: 0; transform: translateX(18px); } }
@keyframes ak-slide-out-left { to { opacity: 0; transform: translateX(-18px); } }
@keyframes ak-slide-in-left { from { opacity: 0; transform: translateX(-18px); } }
@keyframes ak-slide-out-right { to { opacity: 0; transform: translateX(18px); } }

::view-transition-old(main-panel) {
  animation: 140ms var(--ease-out) both ak-fade-out;
}
::view-transition-new(main-panel) {
  animation: 180ms var(--ease-out) both ak-fade-in;
}

html[data-transition="nav-forward"]::view-transition-old(main-panel) {
  animation: 150ms var(--ease-out) both ak-slide-out-left;
}
html[data-transition="nav-forward"]::view-transition-new(main-panel) {
  animation: 200ms var(--ease-drawer) both ak-slide-in-right;
}

html[data-transition="nav-back"]::view-transition-old(main-panel) {
  animation: 150ms var(--ease-out) both ak-slide-out-right;
}
html[data-transition="nav-back"]::view-transition-new(main-panel) {
  animation: 200ms var(--ease-drawer) both ak-slide-in-left;
}

@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.001ms !important;
    transition-duration: 0.001ms !important;
  }
  ::view-transition-group(*),
  ::view-transition-old(*),
  ::view-transition-new(*) {
    animation: none !important;
  }
}
"""

VIEW_TRANSITION_SCRIPT = """
window.__adevkitNavigate = function(direction) {
  if (direction) {
    document.documentElement.setAttribute('data-transition', direction);
  } else {
    document.documentElement.removeAttribute('data-transition');
  }
};
"""
