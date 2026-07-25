#!/usr/bin/env bash
# Full 0.2 installable release build (requires root + ~80GB free Linux FS).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT}"

echo "==> NovaOS 0.2 installable release"
make validate
make validate-installer
sudo bash ./scripts/setup-build-host.sh
bash ./scripts/check-env.sh
sudo bash ./scripts/build-iso.sh
sudo bash ./scripts/qa-p0-gate.sh
sudo bash ./scripts/qa-install-gate.sh

# shellcheck source=lib/common.sh
source "${ROOT}/scripts/lib/common.sh"
novaos_load_release_env

echo
echo "==> Release artifacts"
ls -lh "${NOVAOS_ISO_DIR}/${NOVAOS_ISO_NAME}.iso" \
       "${NOVAOS_ISO_DIR}/${NOVAOS_ISO_NAME}.iso.sha256" \
       "${NOVAOS_ISO_DIR}/latest/novaos-current.iso" 2>/dev/null || true
echo "Manual HW/dual-boot: qa/INSTALL-CHECKLIST.md"
