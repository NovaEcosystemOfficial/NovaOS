#!/usr/bin/env bash
# Boot NovaOS ISO headless in QEMU and collect desktop smoke markers from serial.
# Emulates VirtualBox-like (vmware SVGA) and VMware/QEMU (qxl) display paths.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# shellcheck source=lib/common.sh
source "${ROOT}/scripts/lib/common.sh"

novaos_load_release_env
novaos_require_cmd qemu-system-x86_64

ISO_PATH="${1:-${NOVAOS_ISO_DIR}/${NOVAOS_ISO_NAME}.iso}"
if [[ ! -f "${ISO_PATH}" ]]; then
  ISO_PATH="${NOVAOS_ISO_DIR}/latest/novaos-current.iso"
fi
if [[ ! -f "${ISO_PATH}" ]]; then
  echo "ERROR: ISO not found" >&2
  exit 1
fi

RAM_MB="${NOVAOS_VM_RAM:-4096}"
CPUS="${NOVAOS_VM_CPUS:-2}"
TIMEOUT_SEC="${NOVAOS_SMOKE_TIMEOUT:-480}"
OUT_DIR="${NOVAOS_BUILD_DIR}/logs/smoke-$(novaos_timestamp)"
mkdir -p "${OUT_DIR}"

OVMF_CODE=""
for candidate in \
  /usr/share/edk2/ovmf/OVMF_CODE.fd \
  /usr/share/edk2/ovmf/OVMF_CODE.secboot.fd \
  /usr/share/OVMF/OVMF_CODE.fd \
  /usr/share/OVMF/OVMF_CODE.secboot.fd \
  /usr/share/qemu/OVMF.fd; do
  if [[ -f "${candidate}" ]]; then
    OVMF_CODE="${candidate}"
    break
  fi
done
if [[ -z "${OVMF_CODE}" ]]; then
  echo "ERROR: OVMF firmware not found" >&2
  exit 1
fi

KVM_ARGS=()
if [[ -e /dev/kvm && -r /dev/kvm ]]; then
  KVM_ARGS=(-enable-kvm -cpu host)
else
  echo "WARN: /dev/kvm unavailable — TCG (slow)" >&2
  KVM_ARGS=(-cpu max)
fi

run_one() {
  local name=$1
  shift
  local serial="${OUT_DIR}/${name}.serial.log"
  local qemu_log="${OUT_DIR}/${name}.qemu.log"
  local disk="${OUT_DIR}/${name}.qcow2"
  rm -f "${serial}" "${qemu_log}" "${disk}"
  qemu-img create -f qcow2 "${disk}" 8G >/dev/null

  local vnc_display=$((20 + RANDOM % 40))
  echo "==> smoke[${name}] iso=${ISO_PATH}"
  echo "    serial=${serial}"
  echo "    vnc=127.0.0.1:$((5900 + vnc_display))"

  # VNC (not -display none) so logind sees a graphical seat and SDDM autologin runs.
  timeout --signal=KILL "${TIMEOUT_SEC}" qemu-system-x86_64 \
    "${KVM_ARGS[@]}" \
    -m "${RAM_MB}" \
    -smp "${CPUS}" \
    -drive if=pflash,format=raw,readonly=on,file="${OVMF_CODE}" \
    -drive file="${disk}",if=virtio,format=qcow2 \
    -cdrom "${ISO_PATH}" \
    -boot order=d \
    -vga none \
    -vnc "127.0.0.1:${vnc_display}" \
    -serial file:"${serial}" \
    -device virtio-net-pci,netdev=n0 \
    -netdev user,id=n0 \
    -usb -device usb-tablet \
    -name "NovaOS-smoke-${name}" \
    "$@" >"${qemu_log}" 2>&1 || true

  if ! grep -q "NOVAOS_SMOKE_END" "${serial}" 2>/dev/null; then
    echo "ERROR: smoke[${name}] no NOVAOS_SMOKE_END within ${TIMEOUT_SEC}s" >&2
    echo "---- serial tail ----" >&2
    tail -n 80 "${serial}" 2>/dev/null || true
    return 1
  fi

  local result
  result="$(grep -E 'NOVAOS_SMOKE_RESULT ' "${serial}" | tail -n1 || true)"
  echo "    ${result}"
  mkdir -p "${OUT_DIR}/${name}"
  # Extract report block if present
  if grep -q "NOVAOS_SMOKE_REPORT_BEGIN" "${serial}"; then
    python3 - "${serial}" "${OUT_DIR}/${name}/verify-report.txt" <<'PY' || true
import re, sys
text = open(sys.argv[1], "rb").read().decode("utf-8", "replace").replace("\r", "")
lines, inside = [], False
for line in text.splitlines():
    clean = re.sub(r"^\[[0-9.]+\]\s+novaos-desktop-verify\[\d+\]:\s*", "", line)
    if "NOVAOS_SMOKE_REPORT_BEGIN" in clean:
        inside = True
        continue
    if "NOVAOS_SMOKE_REPORT_END" in clean:
        inside = False
        continue
    if inside:
        lines.append(clean)
open(sys.argv[2], "w", encoding="utf-8").write("\n".join(lines) + "\n")
PY
  fi
  cp -f "${serial}" "${OUT_DIR}/${name}/serial.log"

  if grep -q "NOVAOS_SMOKE_RESULT PASS" "${serial}"; then
    echo "OK: smoke[${name}] PASS"
    return 0
  fi

  echo "ERROR: smoke[${name}] FAIL" >&2
  if [[ -f "${OUT_DIR}/${name}/verify-report.txt" ]]; then
    echo "---- verify-report ----" >&2
    tail -n 100 "${OUT_DIR}/${name}/verify-report.txt" >&2 || true
  else
    echo "---- serial tail ----" >&2
    tail -n 100 "${serial}" >&2 || true
  fi
  return 1
}

analyze_and_hint() {
  local report=$1
  [[ -f "${report}" ]] || return 0
  echo "==> Auto-analysis hints"
  if grep -qiE 'VBoxDRMClient|VERR_INVALID_PARAMETER' "${report}"; then
    echo "HINT: VirtualBox DRM client still active — stub/mask VBoxDRMClient"
  fi
  if grep -qiE 'DISPLAY is empty|no-display' "${report}"; then
    echo "HINT: SDDM did not hand off X session — check getty@tty1 / sddm X11 config"
  fi
  if grep -qiE 'DBUS_SESSION_BUS_ADDRESS|<empty>' "${report}" && grep -qi 'startplasma' "${report}"; then
    echo "HINT: missing session bus — ensure dbus-run-session wrapper"
  fi
  if grep -qiE 'Cannot open virtual console|vt[0-9]|plymouth' "${report}"; then
    echo "HINT: VT/plymouth conflict — keep plymouth.enable=0 and mask getty@tty1"
  fi
  if grep -qiE 'llvmpipe|swrast|GLX|EGL' "${report}"; then
    echo "HINT: GL path issue — keep LIBGL_ALWAYS_SOFTWARE=1 / KWIN_COMPOSE=N"
  fi
  if grep -qiE 'Permission denied|/dev/dri' "${report}"; then
    echo "HINT: missing video/render group membership for nova"
  fi
  if grep -qiE 'xinitrc-ran' "${report}" && ! grep -qiE 'novaos-plasma-x11 invoke|======== novaos session' "${report}"; then
    echo "HINT: Xsession aborted after xinitrc.d (check sourced scripts for bare exit — e.g. 98vboxadd-xclient.sh)"
  fi
}

echo "==> NovaOS desktop smoke"
echo "    out: ${OUT_DIR}"
echo

fail=0
# NOTE: QEMU's vmware-svga often fails with modern vmwgfx ("unsupported hypervisor"),
# leaving no DRM seat. Use virtio-vga as the software-GL / modesetting stand-in for
# VirtualBox(VMSVGA 3D-off) and VMware guest paths; keep qxl as second GPU path.
if ! run_one "virtio" -device virtio-vga; then
  fail=1
  analyze_and_hint "${OUT_DIR}/virtio/verify-report.txt"
fi

# QEMU/QXL path (SPICE-style / some hypervisors)
if ! run_one "qxl" -device qxl-vga; then
  fail=1
  analyze_and_hint "${OUT_DIR}/qxl/verify-report.txt"
fi

echo
if [[ "${fail}" -eq 0 ]]; then
  echo "PASS: desktop smoke (virtio + qxl)"
  echo "${OUT_DIR}" > "${NOVAOS_BUILD_DIR}/logs/smoke-latest.txt"
  exit 0
fi

echo "FAIL: desktop smoke — see ${OUT_DIR}" >&2
echo "${OUT_DIR}" > "${NOVAOS_BUILD_DIR}/logs/smoke-latest.txt"
exit 1
