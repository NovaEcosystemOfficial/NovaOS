#!/usr/bin/env bash
# Stage Nova Welcome + shared helpers into a KIWI/root overlay.
# shellcheck shell=bash
set -euo pipefail

ROOT_OVERLAY="${1:?usage: sync-nova-welcome-overlay.sh <root-overlay> [novaos-root]}"
NOVAOS_ROOT="${2:-}"
if [[ -z "${NOVAOS_ROOT}" ]]; then
  NOVAOS_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
fi

WELCOME_SRC="${NOVAOS_ROOT}/desktop/nova-welcome"
SHARED_SRC="${NOVAOS_ROOT}/desktop/nova-shared"

echo "==> Syncing Nova Welcome into ${ROOT_OVERLAY}"
mkdir -p \
  "${ROOT_OVERLAY}/usr/bin" \
  "${ROOT_OVERLAY}/usr/share/nova/welcome" \
  "${ROOT_OVERLAY}/usr/share/nova/shared" \
  "${ROOT_OVERLAY}/usr/share/applications" \
  "${ROOT_OVERLAY}/etc/xdg/autostart" \
  "${ROOT_OVERLAY}/etc/skel/.config/autostart" \
  "${ROOT_OVERLAY}/usr/share/doc/nova-welcome"

rm -rf "${ROOT_OVERLAY}/usr/share/nova/welcome/nova_welcome"
rm -rf "${ROOT_OVERLAY}/usr/share/nova/shared/nova_shared"
cp -a "${WELCOME_SRC}/nova_welcome" "${ROOT_OVERLAY}/usr/share/nova/welcome/"
cp -a "${SHARED_SRC}/nova_shared" "${ROOT_OVERLAY}/usr/share/nova/shared/"
find "${ROOT_OVERLAY}/usr/share/nova" -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true

install -m 0755 "${WELCOME_SRC}/bin/nova-welcome" "${ROOT_OVERLAY}/usr/bin/nova-welcome"
install -m 0644 "${WELCOME_SRC}/org.novaos.Welcome.desktop" \
  "${ROOT_OVERLAY}/usr/share/applications/org.novaos.Welcome.desktop"
install -m 0644 "${WELCOME_SRC}/org.novaos.Welcome.autostart.desktop" \
  "${ROOT_OVERLAY}/etc/xdg/autostart/org.novaos.Welcome.desktop"
install -m 0644 "${WELCOME_SRC}/org.novaos.Welcome.autostart.desktop" \
  "${ROOT_OVERLAY}/etc/skel/.config/autostart/org.novaos.Welcome.desktop"
install -m 0644 "${WELCOME_SRC}/README.md" \
  "${ROOT_OVERLAY}/usr/share/doc/nova-welcome/README.md"

echo "    installed: nova-welcome + nova_shared + xdg autostart"
