#!/usr/bin/env bash
# Stage Nova Update into a KIWI root/ overlay (or any rootfs prefix).
# Used by build-iso.sh so live + installed systems ship update stack by default.
# shellcheck shell=bash
set -euo pipefail

# Args: ROOT_OVERLAY [NOVAOS_ROOT]
ROOT_OVERLAY="${1:?usage: sync-nova-update-overlay.sh <root-overlay> [novaos-root]}"
NOVAOS_ROOT="${2:-}"

if [[ -z "${NOVAOS_ROOT}" ]]; then
  NOVAOS_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
fi

UPDATE_SRC="${NOVAOS_ROOT}/system/update"
REPO_SRC="${NOVAOS_ROOT}/packages/repo"
DESKTOP_SRC="${NOVAOS_ROOT}/desktop/nova-update"

if [[ ! -d "${UPDATE_SRC}/nova_update" ]]; then
  echo "ERROR: Nova Update sources missing at ${UPDATE_SRC}" >&2
  return 1 2>/dev/null || exit 1
fi

echo "==> Syncing Nova Update into ${ROOT_OVERLAY}"

mkdir -p \
  "${ROOT_OVERLAY}/usr/lib/nova/update" \
  "${ROOT_OVERLAY}/usr/libexec" \
  "${ROOT_OVERLAY}/usr/bin" \
  "${ROOT_OVERLAY}/etc/nova/update" \
  "${ROOT_OVERLAY}/usr/lib/systemd/system" \
  "${ROOT_OVERLAY}/usr/lib/systemd/system-preset" \
  "${ROOT_OVERLAY}/usr/lib/sysusers.d" \
  "${ROOT_OVERLAY}/etc/yum.repos.d" \
  "${ROOT_OVERLAY}/etc/pki/novaos" \
  "${ROOT_OVERLAY}/usr/share/applications" \
  "${ROOT_OVERLAY}/usr/share/nova/update/ui" \
  "${ROOT_OVERLAY}/usr/share/doc/novaos-update" \
  "${ROOT_OVERLAY}/var/lib/nova/update"

# Python library
rm -rf "${ROOT_OVERLAY}/usr/lib/nova/update/nova_update"
cp -a "${UPDATE_SRC}/nova_update" "${ROOT_OVERLAY}/usr/lib/nova/update/nova_update"

# Binaries on PATH / libexec
install -m 0755 "${UPDATE_SRC}/bin/nova-updated" "${ROOT_OVERLAY}/usr/libexec/nova-updated"
install -m 0755 "${UPDATE_SRC}/bin/nova-updater" "${ROOT_OVERLAY}/usr/bin/nova-updater"
# Prefer real GTK GUI when present in desktop/
if [[ -x "${NOVAOS_ROOT}/desktop/nova-update/bin/nova-update-gui" ]]; then
  install -m 0755 "${NOVAOS_ROOT}/desktop/nova-update/bin/nova-update-gui" \
    "${ROOT_OVERLAY}/usr/bin/nova-update-gui"
  mkdir -p "${ROOT_OVERLAY}/usr/share/nova/update/gui"
  rm -rf "${ROOT_OVERLAY}/usr/share/nova/update/gui/nova_update_gui"
  cp -a "${NOVAOS_ROOT}/desktop/nova-update/nova_update_gui" \
    "${ROOT_OVERLAY}/usr/share/nova/update/gui/"
else
  install -m 0755 "${UPDATE_SRC}/bin/nova-update-gui" "${ROOT_OVERLAY}/usr/bin/nova-update-gui"
fi

# Config + unit + socket + preset + sysusers (enable by default)
install -m 0644 "${UPDATE_SRC}/conf/nova-update.conf" \
  "${ROOT_OVERLAY}/etc/nova/update/nova-update.conf"
install -m 0644 "${UPDATE_SRC}/systemd/nova-updated.service" \
  "${ROOT_OVERLAY}/usr/lib/systemd/system/nova-updated.service"
install -m 0644 "${UPDATE_SRC}/systemd/nova-updated.socket" \
  "${ROOT_OVERLAY}/usr/lib/systemd/system/nova-updated.socket"
install -m 0644 "${UPDATE_SRC}/systemd/80-novaos-update.preset" \
  "${ROOT_OVERLAY}/usr/lib/systemd/system-preset/80-novaos-update.preset"
install -m 0644 "${UPDATE_SRC}/sysusers.d/nova.conf" \
  "${ROOT_OVERLAY}/usr/lib/sysusers.d/nova.conf"

# DNF repo channel files
install -m 0644 "${REPO_SRC}/conf/"*.repo "${ROOT_OVERLAY}/etc/yum.repos.d/"

# GPG key at the path referenced by novaos-*.repo
if [[ -f "${REPO_SRC}/keys/RPM-GPG-KEY-novaos" ]]; then
  install -m 0644 "${REPO_SRC}/keys/RPM-GPG-KEY-novaos" \
    "${ROOT_OVERLAY}/etc/pki/novaos/RPM-GPG-KEY-novaos"
else
  install -m 0644 "${REPO_SRC}/keys/novaos-rpm-placeholder.gpg" \
    "${ROOT_OVERLAY}/etc/pki/novaos/RPM-GPG-KEY-novaos"
fi

# Applications menu + QML foundation
install -m 0644 "${DESKTOP_SRC}/org.novaos.Update.desktop" \
  "${ROOT_OVERLAY}/usr/share/applications/org.novaos.Update.desktop"
mkdir -p "${ROOT_OVERLAY}/usr/share/nova/update/ui"
if [[ -d "${DESKTOP_SRC}/qml" ]]; then
  cp -a "${DESKTOP_SRC}/qml/." "${ROOT_OVERLAY}/usr/share/nova/update/ui/"
fi
install -m 0644 "${UPDATE_SRC}/README.md" \
  "${ROOT_OVERLAY}/usr/share/doc/novaos-update/README.md"

# Ensure stable channel enabled, others disabled (defaults already in .repo files)
# Harden permissions on repos/keys
chmod 644 "${ROOT_OVERLAY}/etc/yum.repos.d/novaos-"*.repo
chmod 644 "${ROOT_OVERLAY}/etc/pki/novaos/RPM-GPG-KEY-novaos"

echo "    installed: nova-updated (+socket), nova-updater, nova-update-gui"
echo "    group:     sysusers nova → /run/nova/update.sock root:nova 0660"
echo "    repos:     $(ls -1 "${ROOT_OVERLAY}/etc/yum.repos.d/novaos-"*.repo | wc -l) channel files"
echo "    key:       /etc/pki/novaos/RPM-GPG-KEY-novaos"
echo "    desktop:   org.novaos.Update.desktop"
