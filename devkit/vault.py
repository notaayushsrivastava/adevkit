import os
import sys
import json
import base64
import hashlib
from pathlib import Path
from typing import Any, Dict, Optional, List

from .config import VAULT_FILE, ensure_user_dirs

SENSITIVE_KEYWORDS = {
    "key", "token", "secret", "password", "credential", "auth", "api_key"
}


def _is_sensitive_key(key: str) -> bool:
    """Check if key name implies sensitive data that should be encrypted."""
    import re
    tokens = set(re.split(r"[_\-\s]+", key.lower()))
    if any(tok in {"key", "token", "secret", "password", "credential", "apikey", "pass"} for tok in tokens):
        return True
    if any(sub in key.lower() for sub in ["api_key", "auth_token", "access_token", "private_key"]):
        return True
    return False


def _encrypt_data(plaintext: str) -> Dict[str, Any]:
    """
    Encrypt a secret string using Windows DPAPI if on Windows,
    or a salted host-bound key derivation on POSIX platforms.
    """
    if sys.platform == "win32":
        try:
            import ctypes
            from ctypes import wintypes

            class DATA_BLOB(ctypes.Structure):
                _fields_ = [
                    ("cbData", wintypes.DWORD),
                    ("pbData", ctypes.POINTER(ctypes.c_byte)),
                ]

            raw_bytes = plaintext.encode("utf-8")
            in_blob = DATA_BLOB(len(raw_bytes), ctypes.cast(raw_bytes, ctypes.POINTER(ctypes.c_byte)))
            out_blob = DATA_BLOB()

            if ctypes.windll.crypt32.CryptProtectData(
                ctypes.byref(in_blob),
                "adevkit_secret",
                None,
                None,
                None,
                0x01,  # CRYPTPROTECT_UI_FORBIDDEN
                ctypes.byref(out_blob),
            ):
                encrypted_bytes = ctypes.string_at(out_blob.pbData, out_blob.cbData)
                ctypes.windll.kernel32.LocalFree(out_blob.pbData)
                b64_cipher = base64.b64encode(encrypted_bytes).decode("ascii")
                return {"_enc": True, "_mech": "dpapi", "data": b64_cipher}
        except Exception:
            pass

    # POSIX / Fallback encryption with machine/user salt
    salt = hashlib.sha256(f"{os.getlogin()}_{Path.home()}".encode("utf-8", errors="ignore")).digest()
    data_bytes = plaintext.encode("utf-8")
    xor_bytes = bytes([b ^ salt[i % len(salt)] for i, b in enumerate(data_bytes)])
    return {"_enc": True, "_mech": "salted", "data": base64.b64encode(xor_bytes).decode("ascii")}


def _decrypt_data(payload: Dict[str, Any]) -> str:
    """Decrypt a payload dictionary created by _encrypt_data."""
    if not isinstance(payload, dict) or not payload.get("_enc"):
        return str(payload)

    mech = payload.get("_mech")
    b64_data = payload.get("data", "")
    cipher_bytes = base64.b64decode(b64_data)

    if mech == "dpapi" and sys.platform == "win32":
        try:
            import ctypes
            from ctypes import wintypes

            class DATA_BLOB(ctypes.Structure):
                _fields_ = [
                    ("cbData", wintypes.DWORD),
                    ("pbData", ctypes.POINTER(ctypes.c_byte)),
                ]

            in_blob = DATA_BLOB(len(cipher_bytes), ctypes.cast(cipher_bytes, ctypes.POINTER(ctypes.c_byte)))
            out_blob = DATA_BLOB()

            if ctypes.windll.crypt32.CryptUnprotectData(
                ctypes.byref(in_blob),
                None,
                None,
                None,
                None,
                0x01,  # CRYPTPROTECT_UI_FORBIDDEN
                ctypes.byref(out_blob),
            ):
                plain_bytes = ctypes.string_at(out_blob.pbData, out_blob.cbData)
                ctypes.windll.kernel32.LocalFree(out_blob.pbData)
                return plain_bytes.decode("utf-8")
        except Exception:
            pass

    # Fallback decryption
    salt = hashlib.sha256(f"{os.getlogin()}_{Path.home()}".encode("utf-8", errors="ignore")).digest()
    plain_bytes = bytes([b ^ salt[i % len(salt)] for i, b in enumerate(cipher_bytes)])
    return plain_bytes.decode("utf-8", errors="ignore")


def _read_vault() -> Dict[str, Any]:
    """Read the raw vault file contents."""
    if not VAULT_FILE.exists():
        return {}
    try:
        with open(VAULT_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _write_vault(data: Dict[str, Any]):
    """Write the raw vault file contents with strict file permissions."""
    ensure_user_dirs()
    temp_file = VAULT_FILE.with_suffix(".tmp")
    with open(temp_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    # Restrict permissions on POSIX
    if sys.platform != "win32":
        try:
            os.chmod(temp_file, 0o600)
        except Exception:
            pass

    temp_file.replace(VAULT_FILE)


def get_config(key: str, default: Any = None) -> Any:
    """Retrieve a configuration value from the vault, decrypting if encrypted."""
    vault = _read_vault()
    if key not in vault:
        return default
    val = vault[key]
    if isinstance(val, dict) and val.get("_enc"):
        return _decrypt_data(val)
    return val


def set_config(key: str, value: Any, secret: Optional[bool] = None) -> None:
    """
    Store a configuration key-value pair.
    Automatically encrypts if secret=True or if the key name indicates a sensitive secret.
    """
    vault = _read_vault()
    should_encrypt = secret if secret is not None else _is_sensitive_key(key)

    if should_encrypt and isinstance(value, str):
        vault[key] = _encrypt_data(value)
    else:
        vault[key] = value

    _write_vault(vault)


def delete_config(key: str) -> bool:
    """Remove a configuration key from the vault."""
    vault = _read_vault()
    if key in vault:
        del vault[key]
        _write_vault(vault)
        return True
    return False


def list_configs(reveal_secrets: bool = False) -> Dict[str, Any]:
    """
    Return all configuration items.
    If reveal_secrets is False, masks sensitive values for safe display.
    """
    vault = _read_vault()
    result = {}
    for k, v in vault.items():
        if isinstance(v, dict) and v.get("_enc"):
            if reveal_secrets:
                result[k] = _decrypt_data(v)
            else:
                raw_plain = _decrypt_data(v)
                if len(raw_plain) > 8:
                    result[k] = f"{raw_plain[:4]}...{raw_plain[-4:]} [encrypted]"
                else:
                    result[k] = "*** [encrypted]"
        else:
            result[k] = v
    return result


def get_default_agents() -> List[str]:
    """Get the user's default preferred AI agents for new projects."""
    agents = get_config("default_agents")
    if isinstance(agents, list) and agents:
        return [str(a).strip().lower() for a in agents]
    return ["antigravity", "cursor", "claude"]


def set_default_agents(agents: List[str]) -> None:
    """Persist the user's default preferred AI agents."""
    cleaned = [str(a).strip().lower() for a in agents if str(a).strip()]
    set_config("default_agents", cleaned, secret=False)
