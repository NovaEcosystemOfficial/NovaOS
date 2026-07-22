#!/usr/bin/env bash
# Validate that this machine can build and test NovaOS images.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# shellcheck source=lib/common.sh
source "${ROOT}/scripts/lib/common.sh"

novaos_load_release_env

err=0
warn() { echo "WARN: $*" >&2; }
fail() { echo "FAIL: $*" >&2; err=1; }
ok() { echo "OK: $*"; }

echo "NovaOS check-env"
echo "  root=${NOVAOS_ROOT}"
echo "  fedora=${FEDORA_VERSION}/${FEDORA_ARCH}"
echo "  novaos=${NOVAOS_VERSION} profile=${NOVAOS_PROFILE}"
echo "  iso_name=${NOVAOS_ISO_NAME}"
echo

for d in build configs assets iso packages scripts vm tools \
  configs/kiwi/"${NOVAOS_PROFILE}" configs/fedora configs/bootstrap \
  build/cache build/work build/logs iso/releases iso/latest; do
  if [[ -d "${NOVAOS_ROOT}/${d}" ]]; then
    ok "dir ${d}"
  else
    fail "missing dir ${d}"
  fi
done

DESC="configs/kiwi/${NOVAOS_PROFILE}"
for f in \
  "${DESC}/appliance.kiwi" \
  "${DESC}/config.sh" \
  "${DESC}/iso-esp-excludes.yaml" \
  configs/fedora/release.env \
  configs/bootstrap/host-packages.txt \
  scripts/build-iso.sh \
  scripts/setup-build-host.sh \
  scripts/run-vm.sh \
  scripts/sha256-iso.sh \
  scripts/clean-build.sh \
  scripts/lib/common.sh \
  Makefile; do
  if [[ -f "${NOVAOS_ROOT}/${f}" ]]; then
    ok "file ${f}"
  else
    fail "missing file ${f}"
  fi
done

chmod +x \
  "${NOVAOS_ROOT}/${DESC}/config.sh" \
  "${NOVAOS_ROOT}/scripts/"*.sh \
  "${NOVAOS_ROOT}/tools/lint/"*.sh \
  2>/dev/null || true

if [[ -x "${NOVAOS_ROOT}/${DESC}/config.sh" ]]; then
  ok "config.sh executable"
else
  warn "config.sh not marked executable (build-iso will chmod +x)"
fi

# Cross-reference: appliance must mention esp excludes file
if grep -q 'iso-esp-excludes.yaml' "${NOVAOS_ROOT}/${DESC}/appliance.kiwi"; then
  ok "appliance.kiwi references iso-esp-excludes.yaml"
else
  fail "appliance.kiwi missing iso-esp-excludes.yaml reference"
fi

if command -v kiwi-ng >/dev/null 2>&1 || command -v kiwi >/dev/null 2>&1; then
  ok "kiwi present ($(novaos_kiwi_bin))"
else
  fail "kiwi-ng not installed — run sudo scripts/setup-build-host.sh"
fi

if command -v qemu-system-x86_64 >/dev/null 2>&1; then
  ok "qemu-system-x86_64"
else
  warn "qemu-system-x86_64 missing (needed for scripts/run-vm.sh)"
fi

if command -v python3 >/dev/null 2>&1; then
  ok "python3"
else
  fail "python3 required by build-iso.sh"
fi

if [[ "${EUID}" -eq 0 ]]; then
  ok "running as root (required for build-iso)"
else
  warn "not root — build-iso.sh will require sudo"
fi

if command -v xmllint >/dev/null 2>&1; then
  if xmllint --noout "${NOVAOS_ROOT}/${DESC}/appliance.kiwi"; then
    ok "appliance.kiwi well-formed XML"
  else
    fail "appliance.kiwi XML invalid"
  fi
else
  warn "xmllint not installed — skip XML check (libxml2)"
fi

# OVMF for VM tests
ovmf=0
for candidate in \
  /usr/share/edk2/ovmf/OVMF_CODE.fd \
  /usr/share/edk2/ovmf/OVMF_CODE.secboot.fd \
  /usr/share/OVMF/OVMF_CODE.fd \
  /usr/share/qemu/OVMF.fd; do
  if [[ -f "${candidate}" ]]; then
    ok "OVMF ${candidate}"
    ovmf=1
    break
  fi
done
if [[ "${ovmf}" -eq 0 ]]; then
  warn "OVMF firmware not found (install edk2-ovmf for run-vm)"
fi

echo
if [[ "${err}" -ne 0 ]]; then
  echo "check-env: FAILED"
  exit 1
fi
echo "check-env: PASSED"
exit 0
