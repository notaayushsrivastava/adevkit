#!/usr/bin/env bash
# Universal Installer for adevkit (Aayush's DevKit) on Linux and macOS
# Usage: curl -fsSL https://raw.githubusercontent.com/notaayushsrivastava/adevkit/main/installer/install.sh | bash

set -euo pipefail

REPO="notaayushsrivastava/adevkit"
INSTALL_DIR="/usr/local/bin"

if [ ! -w "${INSTALL_DIR}" ]; then
    INSTALL_DIR="${HOME}/.local/bin"
    mkdir -p "${INSTALL_DIR}"
fi

echo "========================================="
echo " Installing adevkit (Aayush's DevKit)    "
echo "========================================="

OS="$(uname -s)"
ARCH="$(uname -m)"

case "${OS}" in
    Linux*)
        PLATFORM="linux"
        ;;
    Darwin*)
        PLATFORM="macos"
        ;;
    *)
        echo "Error: Unsupported operating system ${OS}. Please use pip install adevkit or Windows MSI." >&2
        exit 1
        ;;
esac

case "${ARCH}" in
    x86_64|amd64)
        ARCH_TAG="x64"
        ;;
    arm64|aarch64)
        ARCH_TAG="arm64"
        ;;
    *)
        ARCH_TAG="${ARCH}"
        ;;
esac

echo "[*] Detected OS: ${PLATFORM}, Architecture: ${ARCH_TAG}"

# Get latest release tag
LATEST_TAG=$(curl -s "https://api.github.com/repos/${REPO}/releases/latest" | grep '"tag_name":' | sed -E 's/.*"([^"]+)".*/\1/')
if [ -z "${LATEST_TAG}" ]; then
    LATEST_TAG="v0.1.4"
fi

VERSION="${LATEST_TAG#v}"
TARBALL_NAME="devkit-v${VERSION}-${PLATFORM}-${ARCH_TAG}.tar.gz"
# Fallback to x64 if arm64 not found or vice versa
DOWNLOAD_URL="https://github.com/${REPO}/releases/download/${LATEST_TAG}/${TARBALL_NAME}"

TMP_DIR=$(mktemp -d)
trap 'rm -rf "${TMP_DIR}"' EXIT

echo "[*] Downloading ${TARBALL_NAME}..."
if ! curl -fsSL "${DOWNLOAD_URL}" -o "${TMP_DIR}/${TARBALL_NAME}"; then
    # Try alternative architecture fallback if needed
    if [ "${ARCH_TAG}" = "arm64" ]; then
        TARBALL_NAME="devkit-v${VERSION}-${PLATFORM}-x64.tar.gz"
        DOWNLOAD_URL="https://github.com/${REPO}/releases/download/${LATEST_TAG}/${TARBALL_NAME}"
        echo "[*] Trying fallback: ${TARBALL_NAME}..."
        curl -fsSL "${DOWNLOAD_URL}" -o "${TMP_DIR}/${TARBALL_NAME}"
    else
        echo "Error: Failed to download release from ${DOWNLOAD_URL}" >&2
        exit 1
    fi
fi

echo "[*] Extracting..."
tar -xzf "${TMP_DIR}/${TARBALL_NAME}" -C "${TMP_DIR}"

if [ -f "${TMP_DIR}/adevkit" ]; then
    PRIMARY_BIN="${TMP_DIR}/adevkit"
elif [ -f "${TMP_DIR}/devkit" ]; then
    PRIMARY_BIN="${TMP_DIR}/devkit"
else
    echo "Error: Neither adevkit nor devkit executable found in archive." >&2
    exit 1
fi

chmod +x "${PRIMARY_BIN}"

echo "[*] Installing triggers to ${INSTALL_DIR} (adevkit and devkit)..."
if [ -w "${INSTALL_DIR}" ]; then
    cp "${PRIMARY_BIN}" "${INSTALL_DIR}/adevkit"
    ln -sf "adevkit" "${INSTALL_DIR}/devkit" 2>/dev/null || cp "${PRIMARY_BIN}" "${INSTALL_DIR}/devkit"
else
    sudo cp "${PRIMARY_BIN}" "${INSTALL_DIR}/adevkit"
    sudo ln -sf "adevkit" "${INSTALL_DIR}/devkit" 2>/dev/null || sudo cp "${PRIMARY_BIN}" "${INSTALL_DIR}/devkit"
fi

if [[ ":$PATH:" != *":${INSTALL_DIR}:"* ]]; then
    echo "[!] Warning: ${INSTALL_DIR} is not in your current PATH."
    echo "    Add it to your ~/.bashrc or ~/.zshrc:"
    echo "    export PATH=\"${INSTALL_DIR}:\$PATH\""
fi

echo "[+] adevkit v${VERSION} installed successfully! (Both 'adevkit' and 'devkit' commands available)"
"${INSTALL_DIR}/adevkit" info || true
