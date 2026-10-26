#!/usr/bin/env bash
set -euo pipefail

VERSION="${1:-0.1.3}"
DIST_DIR="${2:-dist}"
OUTPUT_DIR="${3:-output}"

echo "========================================"
echo "Building Linux Packages for adevkit v${VERSION}"
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

# 2. Package tar.gz standalone archive with both triggers
TARBALL_NAME="devkit-v${VERSION}-linux-x64.tar.gz"
echo "[+] Creating standalone tarball: ${OUTPUT_DIR}/${TARBALL_NAME}"
tar -czf "${OUTPUT_DIR}/${TARBALL_NAME}" -C "${DIST_DIR}" adevkit devkit

# 3. Build Debian package (.deb)
if command -v dpkg-deb >/dev/null 2>&1; then
    DEB_DIR="deb_pkg_build"
    rm -rf "${DEB_DIR}"
    mkdir -p "${DEB_DIR}/DEBIAN"
    mkdir -p "${DEB_DIR}/usr/local/bin"

    cp "${DIST_DIR}/adevkit" "${DEB_DIR}/usr/local/bin/adevkit"
    ln -sf "adevkit" "${DEB_DIR}/usr/local/bin/devkit"
    chmod 755 "${DEB_DIR}/usr/local/bin/adevkit"

    cat <<EOF > "${DEB_DIR}/DEBIAN/control"
Package: adevkit
Version: ${VERSION}
Section: utils
Priority: optional
Architecture: amd64
Maintainer: Aayush Srivastava <contact@aayushsrivastava.com>
Homepage: https://aayushsrivastava.com
Description: adevkit (Aayush's DevKit)
 Single-command project initialization with Agentic skills, AI agents, and environments.
EOF

    DEB_NAME="adevkit_${VERSION}_amd64.deb"
    echo "[+] Building Debian package: ${OUTPUT_DIR}/${DEB_NAME}"
    dpkg-deb --build --root-owner-group "${DEB_DIR}" "${OUTPUT_DIR}/${DEB_NAME}"
    rm -rf "${DEB_DIR}"
fi

echo "[+] Linux build complete."
