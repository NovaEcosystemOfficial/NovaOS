#!/usr/bin/env bash
# Install Nova Center onto the live host (overlay + optional Nova Update apply).
# Usage: sudo bash scripts/install-nova-center-host.sh
#    or: pkexec bash /home/fabio/NovaOS/scripts/install-nova-center-host.sh
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WORK="${ROOT}/build/work/update-test"
CHANNEL=stable
REPO_CHANNELS="${WORK}/repo/channels"
SRC="${ROOT}/desktop/nova-center"

if [[ "$(id -u)" -ne 0 ]]; then
  echo "Re-exec with root…" >&2
  exec pkexec bash "$0" "$@"
fi

echo "==> Installing Nova Center files"
install -m 0755 "${SRC}/bin/nova-center" /usr/bin/nova-center
rm -rf /usr/share/nova/center
mkdir -p /usr/share/nova/center
cp -a "${SRC}/nova_center" /usr/share/nova/center/
find /usr/share/nova/center -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true
install -m 0644 "${SRC}/org.novaos.Center.desktop" /usr/share/applications/org.novaos.Center.desktop
update-desktop-database /usr/share/applications >/dev/null 2>&1 || true

# If RPM already built, also register via localrpm when broker is present
RPM="$(find "${WORK}/rpmbuild/RPMS" -name 'nova-center-*.rpm' 2>/dev/null | sort | tail -1 || true)"
if [[ -n "${RPM}" && -f "${RPM}" ]]; then
  echo "==> Publishing ${RPM} to local stable repo"
  bash "${ROOT}/scripts/update-test/publish-local-repo.sh" "${CHANNEL}" nova "${RPM}" || true

  cat >/etc/yum.repos.d/novaos-stable-local.repo <<EOF
[novaos-stable-local]
name=NovaOS local update-test repo (stable)
baseurl=file://${REPO_CHANNELS}/stable
enabled=1
gpgcheck=0
metadata_expire=30
priority=5
EOF

  mkdir -p /etc/systemd/system/nova-updated.service.d
  cat >/etc/systemd/system/nova-updated.service.d/10-localrpm.conf <<EOF
[Service]
Environment=NOVA_UPDATE_BACKEND=localrpm
Environment=NOVA_UPDATE_LOCAL_REPO=${REPO_CHANNELS}
Environment=NOVA_UPDATE_INSTALL_ROOT=/
Environment=NOVA_UPDATE_SIGNATURE_POLICY=warn
EOF

  python3 - <<'PY'
import json
from pathlib import Path
p = Path("/var/lib/nova-update/installed.json")
p.parent.mkdir(parents=True, exist_ok=True)
data = {}
if p.is_file():
    try:
        data = json.loads(p.read_text())
    except json.JSONDecodeError:
        data = {}
if not isinstance(data, dict):
    data = {}
data["nova-center"] = {
    "version": "0.2.2",
    "release": "1.nova",
    "arch": "noarch",
    "nevra": "nova-center-0.2.2-1.nova.noarch",
    "rpm": "nova-center-0.2.2-1.nova.noarch.rpm",
}
p.write_text(json.dumps(data, indent=2) + "\n")
PY

  if systemctl is-system-running >/dev/null 2>&1 || [[ -d /run/systemd/system ]]; then
    systemctl daemon-reload || true
    systemctl restart nova-updated.service || true
  fi
fi

echo "PASS — Nova Center installed"
echo "  /usr/bin/nova-center"
echo "  /usr/share/applications/org.novaos.Center.desktop"
command -v nova-center
nova-center --help 2>/dev/null || true
DISPLAY= nova-center >/tmp/nova-center-smoke.json 2>/tmp/nova-center-smoke.err || true
grep -q 'center.v1' /tmp/nova-center-smoke.json && echo "PASS — center.v1 snapshot OK"
