#!/usr/bin/env bash
# Build ISO, run automated desktop smoke (vmware + qxl), exit non-zero on FAIL.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# shellcheck source=lib/common.sh
source "${ROOT}/scripts/lib/common.sh"

novaos_require_root
novaos_load_release_env
novaos_ensure_linux_build_fs

echo "==> 1/2 build ISO"
bash "${ROOT}/scripts/build-iso.sh"

ISO_PATH="${NOVAOS_ISO_DIR}/${NOVAOS_ISO_NAME}.iso"
echo "==> 2/2 desktop smoke on ${ISO_PATH}"
bash "${ROOT}/scripts/smoke-desktop.sh" "${ISO_PATH}"

echo
echo "==> BUILD+VERIFY OK"
echo "    ISO: ${ISO_PATH}"
