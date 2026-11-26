"""Vault & Settings view matching ui.html."""

from reactpy import component, html, use_context, use_state

from ...state import AppContext
from ..primitives import (
    Badge,
    CardRoot,
    CardHeader,
    DangerButton,
    PrimaryButton,
    SecondaryButton,
    SectionHeader,
)
from ..icons import ICON_PLUS


@component
def VaultSettingsView():
    ctx = use_context(AppContext)
    bridge = ctx["bridge"]
    notify = ctx["notify"]

    reveal, set_reveal = use_state(False)
    vault_state, set_vault_state = use_state(lambda: bridge.get_vault_state(reveal=False))
    new_key, set_new_key = use_state("")
    new_val, set_new_val = use_state("")

    agents_map = bridge.get_supported_agents()
    selected_agents, set_selected_agents = use_state(vault_state["default_agents"])
    python_pm, set_python_pm = use_state(vault_state["python_pm"])
    node_pm, set_node_pm = use_state(vault_state["node_pm"])

    def reload_vault(next_reveal: bool):
        set_reveal(next_reveal)
        set_vault_state(bridge.get_vault_state(reveal=next_reveal))

    def handle_store(_event):
        if not new_key.strip():
            return
        bridge.set_vault_item(new_key.strip(), new_val)
        notify(f"Stored '{new_key.strip()}' in secure vault.", "success")
        set_new_key("")
        set_new_val("")
        reload_vault(reveal)

    def handle_delete(key: str):
        if bridge.delete_vault_item(key):
            notify(f"Deleted '{key}' from vault.", "success")
            reload_vault(reveal)

    def toggle_agent(aid: str):
        if aid in selected_agents:
            set_selected_agents([a for a in selected_agents if a != aid])
        else:
            set_selected_agents([*selected_agents, aid])

    def handle_save_prefs(_event):
        bridge.update_preferences(selected_agents, python_pm, node_pm)
        notify("Updated toolchain and default AI agent preferences.", "success")

    backend_variant = "success" if "DPAPI" in vault_state["backend"] else "neutral"
    configs = vault_state.get("configs", {})

    return html.div(
        {"style": {"display": "flex", "flexDirection": "column", "gap": "20px", "maxWidth": "1100px"}},
        SectionHeader(
            "Vault & settings",
            "Encrypted secret storage and global toolchain preferences.",
            right=html.div(
                {"style": {"display": "flex", "alignItems": "center", "gap": "10px"}},
                Badge(vault_state["backend"], backend_variant),
                SecondaryButton(
                    "Hide secrets" if reveal else "Reveal secrets",
                    on_click=lambda _e: reload_vault(not reveal),
                ),
            ),
        ),
        # Toolchain Preferences
        CardRoot(
            CardHeader(
                "Toolchain Preferences",
                subtitle="Global defaults for project initialization & package management",
                badge=PrimaryButton("Save Preferences", on_click=handle_save_prefs, size="sm"),
            ),
            html.div(
                {"style": {"display": "grid", "gridTemplateColumns": "1fr 1fr 1.6fr", "gap": "16px"}},
                html.div(
                    {"style": {"display": "flex", "flexDirection": "column", "gap": "6px"}},
                    html.label({"style": {"fontSize": "11px", "color": "#7B8AA0", "textTransform": "uppercase", "fontWeight": "600"}}, "Python PM"),
                    html.select(
                        {"className": "ak-input", "value": python_pm, "on_change": lambda e: set_python_pm(e["target"]["value"])},
                        html.option({"value": "auto"}, "Auto-detect (uv if available)"),
                        html.option({"value": "uv"}, "uv"),
                        html.option({"value": "pip"}, "pip / venv"),
                    ),
                ),
                html.div(
                    {"style": {"display": "flex", "flexDirection": "column", "gap": "6px"}},
                    html.label({"style": {"fontSize": "11px", "color": "#7B8AA0", "textTransform": "uppercase", "fontWeight": "600"}}, "Node PM"),
                    html.select(
                        {"className": "ak-input", "value": node_pm, "on_change": lambda e: set_node_pm(e["target"]["value"])},
                        html.option({"value": "auto"}, "Auto-detect"),
                        html.option({"value": "bun"}, "bun"),
                        html.option({"value": "pnpm"}, "pnpm"),
                        html.option({"value": "yarn"}, "yarn"),
                        html.option({"value": "npm"}, "npm"),
                    ),
                ),
                html.div(
                    {"style": {"display": "flex", "flexDirection": "column", "gap": "6px"}},
                    html.label({"style": {"fontSize": "11px", "color": "#7B8AA0", "textTransform": "uppercase", "fontWeight": "600"}}, "Default AI Agents"),
                    html.div(
                        {"style": {"display": "flex", "flexWrap": "wrap", "gap": "6px"}},
                        *[
                            html.button(
                                {
                                    "key": aid,
                                    "type": "button",
                                    "className": "ak-btn",
                                    "on_click": lambda _e, a=aid: toggle_agent(a),
                                    "style": {
                                        "padding": "5px 10px",
                                        "borderRadius": "6px",
                                        "fontSize": "12px",
                                        "border": f"1px solid {'#38BDF8' if aid in selected_agents else '#242838'}",
                                        "backgroundColor": "#1A1D28" if aid in selected_agents else "#090A0F",
                                        "color": "#F1F5F9" if aid in selected_agents else "#94A3B8",
                                    },
                                },
                                meta["name"] if isinstance(meta, dict) else aid,
                            )
                            for aid, meta in agents_map.items()
                        ],
                    ),
                ),
            ),
        ),
        # Add Secret Form
        CardRoot(
            html.div(
                {"style": {"display": "grid", "gridTemplateColumns": "1fr 1.6fr auto", "gap": "12px", "alignItems": "end"}},
                html.div(
                    {"style": {"display": "flex", "flexDirection": "column", "gap": "6px"}},
                    html.label({"style": {"fontSize": "11px", "color": "#7B8AA0", "textTransform": "uppercase", "fontWeight": "600"}}, "Key"),
                    html.input(
                        {
                            "type": "text",
                            "className": "ak-input ak-input-mono",
                            "placeholder": "anthropic_api_key",
                            "value": new_key,
                            "on_change": lambda e: set_new_key(e["target"]["value"]),
                        }
                    ),
                ),
                html.div(
                    {"style": {"display": "flex", "flexDirection": "column", "gap": "6px"}},
                    html.label({"style": {"fontSize": "11px", "color": "#7B8AA0", "textTransform": "uppercase", "fontWeight": "600"}}, "Value"),
                    html.input(
                        {
                            "type": "password",
                            "className": "ak-input ak-input-mono",
                            "placeholder": "sk-ant-...",
                            "value": new_val,
                            "on_change": lambda e: set_new_val(e["target"]["value"]),
                        }
                    ),
                ),
                PrimaryButton("Store in Vault", on_click=handle_store, disabled=not new_key.strip(), icon=ICON_PLUS),
            ),
        ),
        # Vault Keys Table
        html.div(
            {"style": {"background": "#12141C", "border": "1px solid #242838", "borderRadius": "12px", "overflow": "hidden"}},
            html.div(
                {"style": {"display": "grid", "gridTemplateColumns": "260px 1fr 100px", "height": "40px", "alignItems": "center", "padding": "0 20px", "borderBottom": "1px solid #242838", "fontSize": "11px", "fontWeight": "600", "letterSpacing": "0.08em", "textTransform": "uppercase", "color": "#7B8AA0"}},
                html.span("Key"),
                html.span("Value"),
                html.span({"style": {"textAlign": "right"}}, "Action"),
            ),
            *(
                [
                    html.div(
                        {
                            "key": k,
                            "style": {"display": "grid", "gridTemplateColumns": "260px 1fr 100px", "height": "44px", "alignItems": "center", "padding": "0 20px", "borderBottom": "1px solid #242838", "fontSize": "13px"},
                        },
                        html.span({"style": {"fontFamily": "var(--font-mono)", "color": "#38BDF8"}}, k),
                        html.span({"style": {"fontFamily": "var(--font-mono)", "color": "#94A3B8", "overflow": "hidden", "textOverflow": "ellipsis", "whiteSpace": "nowrap"}}, str(v)),
                        html.span(
                            {"style": {"textAlign": "right"}},
                            DangerButton("Delete", size="sm", on_click=lambda _e, key_name=k: handle_delete(key_name)),
                        ),
                    )
                    for k, v in configs.items()
                ]
                if configs
                else [
                    html.div(
                        {"style": {"padding": "24px 20px", "textAlign": "center", "color": "#7B8AA0", "fontSize": "13px"}},
                        "No entries stored in ~/.adevkit/vault.json yet.",
                    )
                ]
            ),
        ),
    )
