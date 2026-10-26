#!/usr/bin/env bash
set -euo pipefail

VERSION="${1:-0.1.3}"
DIST_DIR="${2:-dist}"
OUTPUT_DIR="${3:-output}"
ARCH="${4:-$(uname -m)}"

echo "========================================"
echo "Building macOS Packages for adevkit v${VERSION} (${ARCH})"
echo "========================================"

mkdir -p "${OUTPUT_DIR}"

# 1. Verify dist binary exists and ensure both adevkit and devkit triggers exist
if [ -f "${DIST_DIR}/adevkit" ]; then
    BINARY_PATH="${DIST_DIR}/adevkit"
    cp -f "${DIST_DIR}/adevkit" "${DIST_DIR}/devkit"
elif [ -f "${DIST_DIR}/devkit" ]; then
    BINARY_PATH="${DIST_DIR}/devkit"
    cp -f "${DIST_DIR}/devkit" "${DIST_DIR}/adevkit"
else
    echo "Error: Neither adevkit nor devkit binary found in ${DIST_DIR}" >&2
    exit 1
fi

chmod +x "${DIST_DIR}/adevkit" "${DIST_DIR}/devkit"

# 1. Package tar.gz standalone archive with both triggers
TARBALL_NAME="devkit-v${VERSION}-macos-${ARCH}.tar.gz"
echo "[+] Creating standalone tarball: ${OUTPUT_DIR}/${TARBALL_NAME}"
tar -czf "${OUTPUT_DIR}/${TARBALL_NAME}" -C "${DIST_DIR}" adevkit devkit

# 2. Build Apple Installer Package (.pkg)
if command -v pkgbuild >/dev/null 2>&1; then
    PKG_ROOT="pkg_root"
    rm -rf "${PKG_ROOT}"
    mkdir -p "${PKG_ROOT}/usr/local/bin"

    cp "${DIST_DIR}/adevkit" "${PKG_ROOT}/usr/local/bin/adevkit"
    ln -sf "adevkit" "${PKG_ROOT}/usr/local/bin/devkit"
    chmod 755 "${PKG_ROOT}/usr/local/bin/adevkit"

    PKG_NAME="AayushsDevKit-v${VERSION}-macos.pkg"
    echo "[+] Building Apple PKG package: ${OUTPUT_DIR}/${PKG_NAME}"
    pkgbuild --root "${PKG_ROOT}" \
             --identifier "com.aayushsrivastava.adevkit" \
             --version "${VERSION}" \
             --install-location "/" \
             "${OUTPUT_DIR}/${PKG_NAME}"

    rm -rf "${PKG_ROOT}"
fi

echo "[+] macOS build complete."
