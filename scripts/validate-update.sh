#!/usr/bin/env bash
# Offline validation for Sprint 15 — Nova Update Foundation
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# shellcheck source=lib/common.sh
source "${ROOT}/scripts/lib/common.sh"

SOCK="$(mktemp -u /tmp/nova-update-XXXXXX.sock)"
STATE="$(mktemp -d /tmp/nova-update-state-XXXXXX)"
PID=""

cleanup() {
  if [[ -n "${PID}" ]] && kill -0 "${PID}" 2>/dev/null; then
    kill "${PID}" 2>/dev/null || true
    wait "${PID}" 2>/dev/null || true
  fi
  rm -f "${SOCK}"
  rm -rf "${STATE}"
}
trap cleanup EXIT

err=0
pass() { echo "PASS: $*"; }
fail() { echo "FAIL: $*"; err=1; }

# --- Static layout ---
required=(
  docs/platform/11-Nova-Update.md
  docs/adr/ADR-009-Nova-Update-Agent.md
  system/update/bin/nova-updated
  system/update/bin/nova-updater
  system/update/bin/nova-update-gui
  system/update/nova_update/broker.py
  system/update/systemd/nova-updated.service
  system/update/systemd/nova-updated.socket
  system/update/sysusers.d/nova.conf
  system/update/systemd/80-novaos-update.preset
  system/update/conf/nova-update.conf
  shell/nova-updater/nova-updater
  desktop/nova-update/org.novaos.Update.desktop
  desktop/nova-update/qml/NovaUpdate/Main.qml
  packages/SPECS/novaos-update.spec
  packages/repo/README.md
  packages/repo/conf/novaos-stable.repo
  packages/repo/conf/novaos-beta.repo
  packages/repo/conf/novaos-developer.repo
  packages/repo/conf/novaos-nightly.repo
  packages/repo/keys/RPM-GPG-KEY-novaos
  scripts/lib/sync-nova-update-overlay.sh
)

for rel in "${required[@]}"; do
  if [[ -e "${ROOT}/${rel}" ]]; then
    pass "exists ${rel}"
  else
    fail "missing ${rel}"
  fi
done

for ch in stable beta developer nightly; do
  for cls in os nova apps; do
    d="${ROOT}/packages/repo/channels/${ch}/${cls}/x86_64"
    if [[ -d "${d}" ]]; then
      pass "repo channel ${ch}/${cls}"
    else
      fail "repo channel missing ${ch}/${cls}"
    fi
  done
done

# --- Image overlay staging (same path as build-iso.sh) ---
OVERLAY="$(mktemp -d /tmp/nova-update-overlay-XXXXXX)"
bash "${ROOT}/scripts/lib/sync-nova-update-overlay.sh" "${OVERLAY}" "${ROOT}"
overlay_required=(
  usr/libexec/nova-updated
  usr/bin/nova-updater
  usr/bin/nova-update-gui
  usr/lib/nova/update/nova_update/broker.py
  etc/nova/update/nova-update.conf
  usr/lib/systemd/system/nova-updated.service
  usr/lib/systemd/system/nova-updated.socket
  usr/lib/sysusers.d/nova.conf
  usr/lib/systemd/system-preset/80-novaos-update.preset
  etc/yum.repos.d/novaos-stable.repo
  etc/pki/novaos/RPM-GPG-KEY-novaos
  usr/share/applications/org.novaos.Update.desktop
)
for rel in "${overlay_required[@]}"; do
  if [[ -e "${OVERLAY}/${rel}" ]]; then
    pass "overlay ${rel}"
  else
    fail "overlay missing ${rel}"
  fi
done
if grep -q 'gpgkey=file:///etc/pki/novaos/RPM-GPG-KEY-novaos' \
  "${OVERLAY}/etc/yum.repos.d/novaos-stable.repo"; then
  pass "overlay repo gpgkey path"
else
  fail "overlay repo gpgkey path mismatch"
fi
if grep -q '^Exec=nova-update-gui' "${OVERLAY}/usr/share/applications/org.novaos.Update.desktop"; then
  pass "desktop launches nova-update-gui"
else
  fail "desktop must Exec=nova-update-gui"
fi
if grep -q 'enable nova-updated.socket' \
  "${OVERLAY}/usr/lib/systemd/system-preset/80-novaos-update.preset" \
  && grep -q 'enable nova-updated.service' \
  "${OVERLAY}/usr/lib/systemd/system-preset/80-novaos-update.preset"; then
  pass "systemd preset enables nova-updated socket+service"
else
  fail "preset must enable nova-updated.socket and nova-updated.service"
fi
if grep -q 'SocketGroup=nova' "${OVERLAY}/usr/lib/systemd/system/nova-updated.socket" \
  && grep -q 'SocketMode=0660' "${OVERLAY}/usr/lib/systemd/system/nova-updated.socket"; then
  pass "socket unit root:nova 0660"
else
  fail "nova-updated.socket must set SocketGroup=nova SocketMode=0660"
fi
if grep -q '^g nova' "${OVERLAY}/usr/lib/sysusers.d/nova.conf"; then
  pass "sysusers defines group nova"
else
  fail "sysusers.d/nova.conf must define group nova"
fi
rm -rf "${OVERLAY}"

# --- Runtime smoke (mock backend) ---
export NOVA_UPDATE_SOCKET="${SOCK}"
export NOVA_UPDATE_STATE_DIR="${STATE}"
export NOVA_UPDATE_BACKEND=mock

"${ROOT}/system/update/bin/nova-updated" --backend mock --socket "${SOCK}" --foreground >/tmp/nova-updated-validate.log 2>&1 &
PID=$!

# Wait for socket
for _ in $(seq 1 50); do
  [[ -S "${SOCK}" ]] && break
  sleep 0.1
done
if [[ ! -S "${SOCK}" ]]; then
  fail "daemon did not create socket (see /tmp/nova-updated-validate.log)"
  cat /tmp/nova-updated-validate.log >&2 || true
  exit 1
fi
pass "nova-updated listening"

CLI=("${ROOT}/shell/nova-updater/nova-updater")

if "${CLI[@]}" ping | grep -q '"pong": true'; then
  pass "ping"
else
  fail "ping"
fi

if "${CLI[@]}" channel set developer | grep -q '"channel": "developer"'; then
  pass "channel set developer"
else
  fail "channel set developer"
fi

# alias dev → developer
if "${CLI[@]}" channel set dev | grep -q '"channel": "developer"'; then
  pass "channel alias dev"
else
  fail "channel alias dev"
fi

if "${CLI[@]}" channel set nightly >/dev/null && "${CLI[@]}" check | grep -q novaos-update; then
  pass "check nightly"
else
  fail "check nightly"
fi

if "${CLI[@]}" apply | grep -q '"reboot_required"'; then
  pass "apply"
else
  fail "apply"
fi

if "${CLI[@]}" verify | grep -q '"policy"'; then
  pass "verify signatures hook"
else
  fail "verify signatures hook"
fi

if "${CLI[@]}" status | grep -q '"api": "system.update.v1"'; then
  pass "status api version"
else
  fail "status api version"
fi

if [[ "${err}" -ne 0 ]]; then
  echo "FAIL — Nova Update foundation validation"
  exit 1
fi
echo "PASS — Nova Update foundation OK"
exit 0
