#!/usr/bin/env bash
# P0 stability gate for NovaOS Foundation 0.1 (no product features).
# Exit 0 only if all automated P0 checks PASS.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# shellcheck source=lib/common.sh
source "${ROOT}/scripts/lib/common.sh"

novaos_load_release_env
novaos_require_root "$@"

ISO_PATH="${1:-${NOVAOS_ISO_DIR}/${NOVAOS_ISO_NAME}.iso}"
if [[ ! -f "${ISO_PATH}" ]]; then
  ISO_PATH="${NOVAOS_ISO_DIR}/latest/novaos-current.iso"
fi
if [[ ! -f "${ISO_PATH}" ]]; then
  echo "ERROR: ISO not found" >&2
  exit 1
fi

REPORT_DIR="${NOVAOS_BUILD_DIR}/logs/p0-gate-$(novaos_timestamp)"
mkdir -p "${REPORT_DIR}"
REPORT="${REPORT_DIR}/P0-GATE.md"
fail=0

pass() { echo "| $1 | PASS | $2 |" | tee -a "${REPORT}.rows"; }
fail_row() { echo "| $1 | FAIL | $2 |" | tee -a "${REPORT}.rows"; fail=1; }
skip_row() { echo "| $1 | SKIP | $2 |" | tee -a "${REPORT}.rows"; }

rm -f "${REPORT}.rows"
echo "==> P0 gate on ${ISO_PATH}"
echo "    report: ${REPORT}"

# --- P0-S1 / integrity ---
if [[ -f "${ISO_PATH}.sha256" ]] || [[ -f "${NOVAOS_ISO_DIR}/${NOVAOS_ISO_NAME}.iso.sha256" ]]; then
  SUM_FILE="${ISO_PATH}.sha256"
  [[ -f "${SUM_FILE}" ]] || SUM_FILE="${NOVAOS_ISO_DIR}/${NOVAOS_ISO_NAME}.iso.sha256"
  if (cd "$(dirname "${SUM_FILE}")" && sha256sum -c "$(basename "${SUM_FILE}")" >/dev/null 2>&1) \
    || sha256sum -c "${SUM_FILE}" >/dev/null 2>&1; then
    pass "P0-INT" "ISO SHA256 OK (${SUM_FILE})"
  else
    # Checksum file may point at releases/ path — verify hash of ISO_PATH directly
    expected="$(awk '{print $1}' "${SUM_FILE}" | head -n1)"
    actual="$(sha256sum "${ISO_PATH}" | awk '{print $1}')"
    if [[ "${expected}" == "${actual}" ]]; then
      pass "P0-INT" "ISO SHA256 matches ${expected}"
    else
      fail_row "P0-INT" "SHA256 mismatch expected=${expected} actual=${actual}"
    fi
  fi
else
  fail_row "P0-INT" "missing .sha256 sidecar"
fi

# --- Static image checks (M5/M6/M7/M8 prerequisites + ISSUE-001 regression) ---
MNT_ISO="${REPORT_DIR}/mnt-iso"
MNT_SQ="${REPORT_DIR}/mnt-squash"
MNT_ROOT="${REPORT_DIR}/mnt-rootfs"
mkdir -p "${MNT_ISO}" "${MNT_SQ}" "${MNT_ROOT}"
cleanup_mnt() {
  umount -l "${MNT_ROOT}" 2>/dev/null || true
  umount -l "${MNT_SQ}" 2>/dev/null || true
  umount -l "${MNT_ISO}" 2>/dev/null || true
}
trap cleanup_mnt EXIT

cp -f "${ISO_PATH}" "${REPORT_DIR}/inspect.iso"
mount -o loop,ro "${REPORT_DIR}/inspect.iso" "${MNT_ISO}"
mount -o loop,ro "${MNT_ISO}/LiveOS/squashfs.img" "${MNT_SQ}"
mount -o loop,ro "${MNT_SQ}/LiveOS/rootfs.img" "${MNT_ROOT}"
R="${MNT_ROOT}"

if [[ -x "${R}/usr/bin/konsole" ]]; then
  pass "P0-M5" "konsole present (${R}/usr/bin/konsole)"
else
  fail_row "P0-M5" "konsole binary missing"
fi

if [[ -x "${R}/usr/bin/systemsettings" ]] || [[ -x "${R}/usr/bin/systemsettings6" ]]; then
  pass "P0-M6" "systemsettings present"
else
  fail_row "P0-M6" "systemsettings binary missing"
fi

if [[ -x "${R}/usr/bin/systemctl" ]] && grep -q 'poweroff\|reboot' "${R}/usr/lib/systemd/system/poweroff.target" 2>/dev/null \
  || [[ -f "${R}/usr/lib/systemd/system/poweroff.target" && -f "${R}/usr/lib/systemd/system/reboot.target" ]]; then
  pass "P0-M7" "systemd poweroff.target present"
  pass "P0-M8" "systemd reboot.target present"
else
  fail_row "P0-M7" "poweroff.target missing"
  fail_row "P0-M8" "reboot.target missing"
fi

# ISSUE-001 regression: sourced xinitrc must not bare-exit
VBOX_XC="${R}/etc/X11/xinit/xinitrc.d/98vboxadd-xclient.sh"
if [[ -f "${VBOX_XC}" ]] && grep -qE '^[[:space:]]*exit([[:space:]]|$)' "${VBOX_XC}"; then
  fail_row "P0-R-ISSUE001" "98vboxadd-xclient.sh still contains bare exit"
else
  pass "P0-R-ISSUE001" "no bare exit in 98vboxadd-xclient.sh (or file absent)"
fi

if [[ -x "${R}/usr/bin/startplasma-x11" && -x "${R}/usr/bin/sddm" ]]; then
  pass "P0-STACK" "sddm + startplasma-x11 present"
else
  fail_row "P0-STACK" "sddm/startplasma-x11 missing"
fi

cleanup_mnt
trap - EXIT

# --- Runtime smoke (S1/S2/S3 desktop stay-up) ---
echo "==> runtime smoke-desktop.sh"
if bash "${ROOT}/scripts/smoke-desktop.sh" "${ISO_PATH}" | tee "${REPORT_DIR}/smoke.stdout"; then
  pass "P0-S1" "QEMU boot / smoke completed"
  pass "P0-S2" "graphical session stayed up (smoke PASS)"
  pass "P0-S3" "desktop session verified (kwin/plasmashell)"
  pass "P0-R1" "smoke virtio+qxl both PASS (multi-boot GPU paths)"
else
  fail_row "P0-S1" "smoke-desktop failed — see ${REPORT_DIR}/smoke.stdout"
  fail_row "P0-S2" "smoke-desktop failed"
  fail_row "P0-S3" "smoke-desktop failed"
  fail_row "P0-R1" "smoke-desktop failed"
fi

SMOKE_DIR="$(cat "${NOVAOS_BUILD_DIR}/logs/smoke-latest.txt" 2>/dev/null || true)"
{
  echo "# NovaOS Foundation 0.1 — P0 Gate Report"
  echo
  echo "- Date: $(date -Is)"
  echo "- ISO: \`${ISO_PATH}\`"
  echo "- Smoke dir: \`${SMOKE_DIR:-n/a}\`"
  echo
  echo "| ID | Result | Notes |"
  echo "|----|--------|-------|"
  cat "${REPORT}.rows"
  echo
  if [[ "${fail}" -eq 0 ]]; then
    echo "**GATE: PASS** — Foundation 0.1 P0 automated checks green."
  else
    echo "**GATE: FAIL** — do not tag/release."
  fi
} > "${REPORT}"

echo
cat "${REPORT}"
echo "${REPORT}" > "${NOVAOS_BUILD_DIR}/logs/p0-gate-latest.txt"
exit "${fail}"
