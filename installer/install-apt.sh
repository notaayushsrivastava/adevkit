#!/usr/bin/env bash
set -euo pipefail

REPOSITORY="https://notaayushsrivastava.github.io/adevkit"
KEYRING="/usr/share/keyrings/adevkit-archive-keyring.gpg"
SOURCES_FILE="/etc/apt/sources.list.d/adevkit.list"

case "$(id -u)" in
    0) SUDO="" ;;
    *) SUDO="sudo" ;;
esac

tmp_key="$(mktemp)"
trap 'rm -f "${tmp_key}"' EXIT
curl --fail --silent --show-error --location \
    "${REPOSITORY}/adevkit-archive-keyring.gpg" \
    --output "${tmp_key}"

${SUDO} install -Dm644 "${tmp_key}" "${KEYRING}"
printf 'deb [arch=amd64 signed-by=%s] %s stable main\n' "${KEYRING}" "${REPOSITORY}" | ${SUDO} tee "${SOURCES_FILE}" >/dev/null

${SUDO} apt-get update
${SUDO} apt-get install -y notaayushsrivastava.adevkit
