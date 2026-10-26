#!/usr/bin/env bash
set -euo pipefail

VERSION="${1:?Usage: build_apt_repo.sh VERSION PACKAGE_DIR OUTPUT_DIR}"
PACKAGE_DIR="${2:?Usage: build_apt_repo.sh VERSION PACKAGE_DIR OUTPUT_DIR}"
OUTPUT_DIR="${3:?Usage: build_apt_repo.sh VERSION PACKAGE_DIR OUTPUT_DIR}"

: "${APT_GPG_PRIVATE_KEY:?APT_GPG_PRIVATE_KEY must contain the repository signing key}"

command -v apt-ftparchive >/dev/null 2>&1 || {
    echo "Error: apt-ftparchive is required (install apt-utils)." >&2
    exit 1
}
command -v gpg >/dev/null 2>&1 || {
    echo "Error: gpg is required." >&2
    exit 1
}

rm -rf "${OUTPUT_DIR}"
mkdir -p \
    "${OUTPUT_DIR}/pool/main/n/notaayushsrivastava.adevkit" \
    "${OUTPUT_DIR}/dists/stable/main/binary-amd64"

if [ -f "${PACKAGE_DIR}/notaayushsrivastava.adevkit_${VERSION}_amd64.deb" ]; then
    DEB_SRC="${PACKAGE_DIR}/notaayushsrivastava.adevkit_${VERSION}_amd64.deb"
elif [ -f "${PACKAGE_DIR}/adevkit_${VERSION}_amd64.deb" ]; then
    DEB_SRC="${PACKAGE_DIR}/adevkit_${VERSION}_amd64.deb"
else
    echo "Error: Could not find debian package for version ${VERSION} in ${PACKAGE_DIR}" >&2
    exit 1
fi

cp "${DEB_SRC}" \
    "${OUTPUT_DIR}/pool/main/n/notaayushsrivastava.adevkit/"

# Generate index paths relative to the repository root. Absolute paths here
# leak "apt-repo/" (or a runner path) into each Filename field, causing APT
# to request a URL that does not exist on GitHub Pages.
(
    cd "${OUTPUT_DIR}"
    apt-ftparchive packages "pool" \
        > "dists/stable/main/binary-amd64/Packages"
)
gzip -9kf "${OUTPUT_DIR}/dists/stable/main/binary-amd64/Packages"

cat > "${OUTPUT_DIR}/apt-ftparchive.conf" <<EOF
APT::FTPArchive::Release::Origin "notaayushsrivastava.adevkit";
APT::FTPArchive::Release::Label "notaayushsrivastava.adevkit";
APT::FTPArchive::Release::Suite "stable";
APT::FTPArchive::Release::Codename "stable";
APT::FTPArchive::Release::Architectures "amd64";
APT::FTPArchive::Release::Components "main";
EOF
# Write the generated Release outside the indexed directory first. Redirecting
# directly to dists/stable/Release causes apt-ftparchive to hash that file while
# it is still being written, producing a self-referential checksum entry.
RELEASE_TMP="${OUTPUT_DIR}/Release.tmp"
apt-ftparchive -c "${OUTPUT_DIR}/apt-ftparchive.conf" \
    release "${OUTPUT_DIR}/dists/stable" \
    > "${RELEASE_TMP}"
mv "${RELEASE_TMP}" "${OUTPUT_DIR}/dists/stable/Release"
rm "${OUTPUT_DIR}/apt-ftparchive.conf"

# Fail the build if an index path would resolve outside this published repository.
PACKAGES_INDEX="${OUTPUT_DIR}/dists/stable/main/binary-amd64/Packages"
while IFS= read -r package_path; do
    if [ ! -f "${OUTPUT_DIR}/${package_path}" ]; then
        echo "Error: Packages index references missing file: ${package_path}" >&2
        exit 1
    fi
done < <(awk '/^Filename: / { print $2 }' "${PACKAGES_INDEX}")

if grep -Eq '^[[:xdigit:]]+[[:space:]]+[0-9]+[[:space:]]+Release$' "${OUTPUT_DIR}/dists/stable/Release"; then
    echo "Error: Release metadata contains a self-referential Release checksum." >&2
    exit 1
fi

GNUPGHOME="$(mktemp -d)"
trap 'rm -rf "${GNUPGHOME}"' EXIT
chmod 700 "${GNUPGHOME}"
printf '%s\n' "${APT_GPG_PRIVATE_KEY}" | gpg --batch --import
KEY_ID="$(gpg --batch --list-secret-keys --with-colons | awk -F: '$1 == "sec" { print $5; exit }')"
gpg --batch --yes --local-user "${KEY_ID}" --armor \
    --output "${OUTPUT_DIR}/dists/stable/InRelease" \
    --clearsign "${OUTPUT_DIR}/dists/stable/Release"
gpg --batch --yes --local-user "${KEY_ID}" \
    --output "${OUTPUT_DIR}/dists/stable/Release.gpg" \
    --detach-sign "${OUTPUT_DIR}/dists/stable/Release"
gpg --batch --export "${KEY_ID}" \
    > "${OUTPUT_DIR}/adevkit-archive-keyring.gpg"
