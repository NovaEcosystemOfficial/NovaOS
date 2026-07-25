#!/usr/bin/env bash
# Installability gate: static installer checks + ISO rootfs presence of Calamares.
# Does not perform a full guided install (see qa/INSTALL-CHECKLIST.md).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# shellcheck source=lib/common.sh
source "${ROOT}/scripts/lib/common.sh"

novaos_load_release_env
novaos_require_root "$@"

bash "${ROOT}/scripts/validate-installer.sh"

ISO_PATH="${1:-${NOVAOS_ISO_DIR}/${NOVAOS_ISO_NAME}.iso}"
if [[ ! -f "${ISO_PATH}" ]]; then
  ISO_PATH="${NOVAOS_ISO_DIR}/latest/novaos-current.iso"
fi
if [[ ! -f "${ISO_PATH}" ]]; then
  echo "ERROR: ISO not found (build with: sudo make iso)" >&2
  exit 1
fi

REPORT_DIR="${NOVAOS_BUILD_DIR}/logs/install-gate-$(novaos_timestamp)"
mkdir -p "${REPORT_DIR}"
MNT_ISO="${REPORT_DIR}/mnt-iso"
MNT_SQ="${REPORT_DIR}/mnt-squash"
MNT_ROOT="${REPORT_DIR}/mnt-rootfs"
mkdir -p "${MNT_ISO}" "${MNT_SQ}" "${MNT_ROOT}"
cleanup() {
  umount -l "${MNT_ROOT}" 2>/dev/null || true
  umount -l "${MNT_SQ}" 2>/dev/null || true
  umount -l "${MNT_ISO}" 2>/dev/null || true
}
trap cleanup EXIT

echo "==> install-gate inspecting ${ISO_PATH}"
mount -o loop,ro "${ISO_PATH}" "${MNT_ISO}"
mount -o loop,ro "${MNT_ISO}/LiveOS/squashfs.img" "${MNT_SQ}"
mount -o loop,ro "${MNT_SQ}/LiveOS/rootfs.img" "${MNT_ROOT}"
R="${MNT_ROOT}"
fail=0

check() {
  local name=$1 cond=$2 detail=$3
  if eval "${cond}"; then
    echo "PASS: ${name} — ${detail}"
  else
    echo "FAIL: ${name} — ${detail}" >&2
    fail=1
  fi
}

check "CALAMARES_BIN" "[[ -x '${R}/usr/bin/calamares' ]]" "calamares binary"
check "SETTINGS" "[[ -f '${R}/etc/calamares/settings.conf' ]]" "NovaOS settings"
check "BRANDING" "[[ -f '${R}/etc/calamares/branding/novaos/branding.desc' ]]" "novaos branding"
check "POSTINSTALL" "[[ -x '${R}/usr/sbin/novaos-post-install.sh' ]]" "post-install script"
check "DESKTOP" "[[ -f '${R}/usr/share/applications/novaos-installer.desktop' ]]" "desktop launcher"
check "OS_PROBER" "[[ -x '${R}/usr/bin/os-prober' ]] || [[ -x '${R}/usr/sbin/os-prober' ]]" "os-prober"
check "GIT" "[[ -x '${R}/usr/bin/git' ]]" "git"
check "GCC" "[[ -x '${R}/usr/bin/gcc' ]]" "gcc"
check "MAKE" "[[ -x '${R}/usr/bin/make' ]]" "make"
check "LIVE_MARKER" "grep -q 'mode=live' '${R}/etc/novaos/install-state'" "live install-state"

# Live regression: SDDM + Plasma still present
check "SDDM" "[[ -x '${R}/usr/bin/sddm' ]]" "sddm"
check "PLASMA" "[[ -x '${R}/usr/bin/startplasma-x11' ]]" "startplasma-x11"

echo
if [[ "${fail}" -ne 0 ]]; then
  echo "install-gate: FAILED"
  exit 1
fi
echo "install-gate: PASSED — ISO contains installer stack"
echo "Manual dual-boot / reboot tests: qa/INSTALL-CHECKLIST.md"
exit 0
