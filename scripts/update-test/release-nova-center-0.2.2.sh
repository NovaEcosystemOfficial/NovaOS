#!/usr/bin/env bash
# Ship Nova Center (0.2.2) via Nova Update — no ISO rebuild.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
WORK="${ROOT}/build/work/update-test"
CHANNEL=stable
REPO_CHANNELS="${WORK}/repo/channels"
LOG="${WORK}/release-nova-center-0.2.2.log"
REPORT="${ROOT}/docs/releases/0.2.2-nova-center.md"
PKG_VERSION="0.2.2"

mkdir -p "${WORK}"
exec > >(tee "${LOG}") 2>&1

echo "=============================================="
echo " Nova Center ${PKG_VERSION} — Nova Update ship"
echo "=============================================="

# 1) Build RPM
chmod +x "${ROOT}/scripts/update-test/build-rpm.sh"
RPM_CENTER="$(bash "${ROOT}/scripts/update-test/build-rpm.sh" nova-center "${PKG_VERSION}" | tee /dev/stderr | tail -1)"
echo "Built: ${RPM_CENTER}"
[[ -f "${RPM_CENTER}" ]] || { echo "FAIL: rpm missing"; exit 1; }

# 2) Publish into local stable channel (nova class) — keep existing packages
bash "${ROOT}/scripts/update-test/publish-local-repo.sh" "${CHANNEL}" nova "${RPM_CENTER}"

# 3) Ensure localrpm backend + repo on host
pkexec bash -c "
set -euo pipefail
ROOT='${ROOT}'
WORK='${WORK}'
REPO_CHANNELS='${REPO_CHANNELS}'

cat >/etc/yum.repos.d/novaos-stable-local.repo <<EOF
[novaos-stable-local]
name=NovaOS local update-test repo (stable)
baseurl=file://\${REPO_CHANNELS}/stable
enabled=1
gpgcheck=0
metadata_expire=30
priority=5
EOF

mkdir -p /etc/systemd/system/nova-updated.service.d
cat >/etc/systemd/system/nova-updated.service.d/10-localrpm.conf <<EOF
[Service]
Environment=NOVA_UPDATE_BACKEND=localrpm
Environment=NOVA_UPDATE_LOCAL_REPO=\${REPO_CHANNELS}
Environment=NOVA_UPDATE_INSTALL_ROOT=/
Environment=NOVA_UPDATE_SIGNATURE_POLICY=warn
EOF

# Clear installed marker for this package so check sees it as pending
python3 - <<'PY'
import json
from pathlib import Path
p = Path('/var/lib/nova-update/installed.json')
if p.is_file():
    data = json.loads(p.read_text())
    if isinstance(data, dict):
        data.pop('nova-center', None)
        p.write_text(json.dumps(data, indent=2) + '\n')
PY

systemctl daemon-reload
systemctl restart nova-updated.service
sleep 0.8
systemctl --no-pager --full status nova-updated.service | head -25
"

# 4) Check → Apply via Nova Update
echo "==> nova-updater check"
CHECK_JSON="$(pkexec nova-updater check)"
echo "${CHECK_JSON}"
echo "${CHECK_JSON}" | grep -q 'nova-center' || { echo "FAIL: nova-center not detected"; exit 1; }

echo "==> nova-updater apply"
APPLY_JSON="$(pkexec nova-updater apply)"
echo "${APPLY_JSON}"

# 5) Verify install
test -x /usr/bin/nova-center
test -f /usr/share/applications/org.novaos.Center.desktop
test -d /usr/share/nova/center/nova_center
grep -q 'Name=Nova Center' /usr/share/applications/org.novaos.Center.desktop
grep -q 'Exec=nova-center' /usr/share/applications/org.novaos.Center.desktop
pkexec update-desktop-database /usr/share/applications >/dev/null 2>&1 || true

# Live data smoke (headless JSON)
SMOKE="$(DISPLAY= /usr/bin/nova-center 2>/dev/null || true)"
echo "${SMOKE}" | grep -q '"api": "center.v1"' || { echo "FAIL: center.v1 snapshot"; exit 1; }
echo "${SMOKE}" | grep -q 'novaos_version' || { echo "FAIL: no novaos_version"; exit 1; }

# 6) Report
cat >"${REPORT}" <<EOF
# Report Nova Center ${PKG_VERSION}

| Campo | Valore |
|-------|--------|
| Pacchetto | \`nova-center\` ${PKG_VERSION} |
| Canale | ${CHANNEL} |
| Metodo | Nova Update (\`localrpm\`) — **senza rebuild ISO** |
| Host | \$(hostname) |
| NovaOS | \$(. /etc/os-release 2>/dev/null; echo "\${PRETTY_NAME:-\${NAME}} \${VERSION}") |

## Verifiche

- [x] RPM costruito e pubblicato su repo locale stable
- [x] \`nova-updater check\` rileva \`nova-center\`
- [x] \`nova-updater apply\` installa il pacchetto
- [x] \`/usr/bin/nova-center\` presente
- [x] Launcher \`org.novaos.Center.desktop\` nel menu Applicazioni
- [x] Snapshot \`center.v1\` con dati reali

Log: \`${LOG}\`
EOF

# Expand hostname/version in report
HOSTNAME_V="$(hostname)"
OS_V="$(. /etc/os-release; echo "${PRETTY_NAME} ${VERSION}")"
sed -i \
  -e "s/\$(hostname)/${HOSTNAME_V}/" \
  -e "s|\$(. /etc/os-release 2>/dev/null; echo \"\${PRETTY_NAME:-\${NAME}} \${VERSION}\")|${OS_V}|" \
  "${REPORT}"

echo "PASS — Nova Center ${PKG_VERSION} installed via Nova Update"
echo "Report: ${REPORT}"
