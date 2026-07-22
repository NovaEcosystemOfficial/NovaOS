#!/usr/bin/env bash
# Install host dependencies required to build NovaOS images with KIWI NG.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# shellcheck source=lib/common.sh
source "${ROOT}/scripts/lib/common.sh"

novaos_require_root
novaos_load_release_env
novaos_require_cmd dnf

PKG_LIST="${NOVAOS_CONFIG_DIR}/bootstrap/host-packages.txt"
if [[ ! -f "${PKG_LIST}" ]]; then
  echo "ERROR: missing ${PKG_LIST}" >&2
  exit 1
fi

mapfile -t PACKAGES < <(grep -vE '^\s*(#|$)' "${PKG_LIST}")
if [[ "${#PACKAGES[@]}" -eq 0 ]]; then
  echo "ERROR: no packages listed in ${PKG_LIST}" >&2
  exit 1
fi

echo "==> Resolving host packages"
installable=()
missing=()
for p in "${PACKAGES[@]}"; do
  if rpm -q "${p}" >/dev/null 2>&1; then
    echo "    already installed: ${p}"
    installable+=("${p}")
  elif dnf list --available "${p}" >/dev/null 2>&1; then
    echo "    available: ${p}"
    installable+=("${p}")
  else
    echo "    MISSING in repos: ${p}"
    missing+=("${p}")
  fi
done

if [[ "${#missing[@]}" -gt 0 ]]; then
  echo "ERROR: host packages not found in DNF repos:" >&2
  printf '  - %s\n' "${missing[@]}" >&2
  echo "Update configs/bootstrap/host-packages.txt for this Fedora release." >&2
  exit 1
fi

echo "==> Installing build-host packages via dnf"
dnf install -y "${installable[@]}"

echo "==> Ensuring build directories exist"
mkdir -p \
  "${NOVAOS_BUILD_DIR}/cache" \
  "${NOVAOS_BUILD_DIR}/work" \
  "${NOVAOS_BUILD_DIR}/logs" \
  "${NOVAOS_ISO_DIR}/releases" \
  "${NOVAOS_ISO_DIR}/latest"

echo "==> Host tool versions"
if KIWI_BIN="$(novaos_kiwi_bin)"; then
  "${KIWI_BIN}" --version || true
else
  echo "ERROR: kiwi-ng still not on PATH after install" >&2
  exit 1
fi
command -v qemu-system-x86_64 >/dev/null && qemu-system-x86_64 --version | head -n1 || true
command -v python3 >/dev/null && python3 --version || true

echo "==> setup-build-host complete"
echo "Next: scripts/check-env.sh && sudo scripts/build-iso.sh"
