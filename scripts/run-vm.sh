#!/usr/bin/env bash
# Boot the latest (or given) NovaOS ISO in QEMU/KVM with UEFI.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# shellcheck source=lib/common.sh
source "${ROOT}/scripts/lib/common.sh"

novaos_require_cmd qemu-system-x86_64

ISO_PATH="${1:-${NOVAOS_ISO_DIR}/latest/novaos-current.iso}"
RAM_MB="${NOVAOS_VM_RAM:-4096}"
CPUS="${NOVAOS_VM_CPUS:-2}"
DISK="${NOVAOS_VM_DISK:-${NOVAOS_ROOT}/vm/disks/test-m01.qcow2}"

if [[ ! -f "${ISO_PATH}" ]]; then
  echo "ERROR: ISO not found: ${ISO_PATH}" >&2
  echo "Build first: sudo scripts/build-iso.sh" >&2
  exit 1
fi

# Locate OVMF firmware
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
  echo "ERROR: OVMF firmware not found. Install edk2-ovmf." >&2
  exit 1
fi

mkdir -p "$(dirname "${DISK}")"
if [[ ! -f "${DISK}" ]]; then
  novaos_require_cmd qemu-img
  qemu-img create -f qcow2 "${DISK}" 40G
  echo "Created disk ${DISK}"
fi

KVM_ARGS=()
if [[ -e /dev/kvm && -r /dev/kvm ]]; then
  KVM_ARGS=(-enable-kvm -cpu host)
else
  echo "WARN: /dev/kvm not available — using TCG (slow)" >&2
  KVM_ARGS=(-cpu max)
fi

echo "==> QEMU NovaOS"
echo "    iso:  ${ISO_PATH}"
echo "    disk: ${DISK}"
echo "    ovmf: ${OVMF_CODE}"
echo "    ram:  ${RAM_MB}M cpus: ${CPUS}"
echo "    login: nova / novaos"
echo

exec qemu-system-x86_64 \
  "${KVM_ARGS[@]}" \
  -m "${RAM_MB}" \
  -smp "${CPUS}" \
  -drive if=pflash,format=raw,readonly=on,file="${OVMF_CODE}" \
  -drive file="${DISK}",if=virtio,format=qcow2 \
  -cdrom "${ISO_PATH}" \
  -boot order=d \
  -device virtio-vga \
  -device virtio-net-pci,netdev=n0 \
  -netdev user,id=n0 \
  -usb -device usb-tablet \
  -name "NovaOS-0.1"
