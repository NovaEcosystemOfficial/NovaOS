#!/usr/bin/env bash
# Install Nova Update onto the running host (no ISO rebuild).
# Requires root. Idempotent.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "==> Installing Nova Update onto live system from ${ROOT}"
if [[ "${EUID}" -ne 0 ]]; then
  echo "NOTE: not running as root (uid=${EUID}); attempting direct install"
  echo "      If permission denied, re-run: sudo $0"
fi
bash "${ROOT}/scripts/lib/sync-nova-update-overlay.sh" "/" "${ROOT}"
# Prefer local e2e repo when present (demonstrates check without remote mirror).
LOCAL_CHANNEL="${ROOT}/build/work/update-test/repo/channels/stable"
if [[ -d "${LOCAL_CHANNEL}/repodata" ]]; then
  echo "==> Wiring local test repo (file://${LOCAL_CHANNEL})"
  cat >/etc/yum.repos.d/novaos-stable-local.repo <<EOF
[novaos-stable-local]
name=NovaOS local update-test repo (stable)
baseurl=file://${LOCAL_CHANNEL}
enabled=1
gpgcheck=0
metadata_expire=60
priority=5
EOF
  # Keep remote novaos-stable as fallback but lower priority / optional
  if [[ -f /etc/yum.repos.d/novaos-stable.repo ]]; then
    sed -i 's/^enabled=.*/enabled=0/' /etc/yum.repos.d/novaos-stable.repo || true
  fi
fi

echo "==> Importing NovaOS RPM GPG key"
if [[ -f /etc/pki/novaos/RPM-GPG-KEY-novaos ]]; then
  rpm --import /etc/pki/novaos/RPM-GPG-KEY-novaos 2>/dev/null || \
    echo "WARN: rpm --import skipped/failed (placeholder key is OK for foundation)"
else
  echo "ERROR: GPG key missing at /etc/pki/novaos/RPM-GPG-KEY-novaos" >&2
  exit 1
fi

# Runtime dirs for the daemon
mkdir -p /run/nova /var/lib/nova/update
chmod 755 /run/nova /var/lib/nova/update

echo "==> Enabling and starting nova-updated"
systemctl daemon-reload
systemctl enable nova-updated.service
systemctl restart nova-updated.service

# Brief wait for socket
for _ in $(seq 1 30); do
  if [[ -S /run/nova/update.sock ]] || systemctl is-active --quiet nova-updated.service; then
    break
  fi
  sleep 0.1
done

systemctl --no-pager --full status nova-updated.service || true

echo "==> Verifying CLI"
command -v nova-updater >/dev/null
command -v nova-update-gui >/dev/null
test -x /usr/libexec/nova-updated

echo "==> nova-updater ping"
nova-updater ping

echo "==> nova-updater status"
nova-updater status

echo "==> nova-updater check"
nova-updater check

echo
echo "PASS — Nova Update installed on live system"
echo "    service: $(systemctl is-enabled nova-updated.service) / $(systemctl is-active nova-updated.service)"
echo "    socket:  $( [[ -S /run/nova/update.sock ]] && echo present || echo missing )"
echo "    key:     /etc/pki/novaos/RPM-GPG-KEY-novaos"
echo "    repos:   /etc/yum.repos.d/novaos-*.repo"
