#!/usr/bin/env bash
set -euo pipefail

VERSION="${1:-0.1.2}"
DIST_DIR="${2:-dist}"
OUTPUT_DIR="${3:-output}"

echo "========================================"
echo "Building Linux Packages for adevkit v${VERSION}"
echo "========================================"

mkdir -p "${OUTPUT_DIR}"

# 1. Verify dist binary exists
BINARY_PATH="${DIST_DIR}/devkit"
if [ ! -f "${BINARY_PATH}" ]; then
    echo "Error: Binary not found at ${BINARY_PATH}" >&2
    exit 1
fi

chmod +x "${BINARY_PATH}"

# 2. Package tar.gz standalone archive
TARBALL_NAME="devkit-v${VERSION}-linux-x64.tar.gz"
echo "[+] Creating standalone tarball: ${OUTPUT_DIR}/${TARBALL_NAME}"
tar -czf "${OUTPUT_DIR}/${TARBALL_NAME}" -C "${DIST_DIR}" devkit

# 3. Build Debian package (.deb)
if command -v dpkg-deb >/dev/null 2>&1; then
    DEB_DIR="deb_pkg_build"
    rm -rf "${DEB_DIR}"
    mkdir -p "${DEB_DIR}/DEBIAN"
    mkdir -p "${DEB_DIR}/usr/local/bin"

    cp "${BINARY_PATH}" "${DEB_DIR}/usr/local/bin/devkit"
    chmod 755 "${DEB_DIR}/usr/local/bin/devkit"

    cat <<EOF > "${DEB_DIR}/DEBIAN/control"
Package: adevkit
Version: ${VERSION}
Section: utils
Priority: optional
Architecture: amd64
Maintainer: Aayush Srivastava <aayush@example.com>
Homepage: https://github.com/notaayushsrivastava/adevkit
Description: adevkit (Aayush's DevKit)
 Single-command project initialization with Agentic skills, AI agents, and environments.
EOF

    DEB_NAME="adevkit_${VERSION}_amd64.deb"
    echo "[+] Building Debian package: ${OUTPUT_DIR}/${DEB_NAME}"
    dpkg-deb --build --root-owner-group "${DEB_DIR}" "${OUTPUT_DIR}/${DEB_NAME}"
    rm -rf "${DEB_DIR}"
fi

echo "[+] Linux build complete."
