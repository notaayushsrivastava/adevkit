#!/usr/bin/env bash
set -euo pipefail

VERSION="${1:-0.1.2}"
DIST_DIR="${2:-dist}"
OUTPUT_DIR="${3:-output}"
ARCH="${4:-$(uname -m)}"

echo "========================================"
echo "Building macOS Packages for adevkit v${VERSION} (${ARCH})"
echo "========================================"

mkdir -p "${OUTPUT_DIR}"

BINARY_PATH="${DIST_DIR}/devkit"
if [ ! -f "${BINARY_PATH}" ]; then
    echo "Error: Binary not found at ${BINARY_PATH}" >&2
    exit 1
fi

chmod +x "${BINARY_PATH}"

# 1. Package tar.gz standalone archive
TARBALL_NAME="devkit-v${VERSION}-macos-${ARCH}.tar.gz"
echo "[+] Creating standalone tarball: ${OUTPUT_DIR}/${TARBALL_NAME}"
tar -czf "${OUTPUT_DIR}/${TARBALL_NAME}" -C "${DIST_DIR}" devkit

# 2. Build Apple Installer Package (.pkg)
if command -v pkgbuild >/dev/null 2>&1; then
    PKG_ROOT="pkg_root"
    rm -rf "${PKG_ROOT}"
    mkdir -p "${PKG_ROOT}/usr/local/bin"

    cp "${BINARY_PATH}" "${PKG_ROOT}/usr/local/bin/devkit"
    chmod 755 "${PKG_ROOT}/usr/local/bin/devkit"

    PKG_NAME="AayushsDevKit-v${VERSION}-macos.pkg"
    echo "[+] Building Apple PKG package: ${OUTPUT_DIR}/${PKG_NAME}"
    pkgbuild --root "${PKG_ROOT}" \
             --identifier "com.aayush.adevkit" \
             --version "${VERSION}" \
             --install-location "/" \
             "${OUTPUT_DIR}/${PKG_NAME}"

    rm -rf "${PKG_ROOT}"
fi

echo "[+] macOS build complete."
