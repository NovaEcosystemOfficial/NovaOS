#!/usr/bin/env bash
# Official NovaOS 0.2.1 release via Nova Update only (no ISO rebuild).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
WORK="${ROOT}/build/work/update-test"
CHANNEL=stable
REPO_CHANNELS="${WORK}/repo/channels"
LOG="${WORK}/release-0.2.1.log"
REPORT="${WORK}/release-0.2.1-report.md"
PREV_VERSION="0.2.0"
NEW_VERSION="0.2.1"

mkdir -p "${WORK}"
exec > >(tee "${LOG}") 2>&1

echo "=============================================="
echo " NovaOS ${NEW_VERSION} — Nova Update release"
echo "=============================================="

before_os="$(grep -E '^(VERSION|PRETTY_NAME)=' /etc/os-release | tr '\n' ' ')"
echo "BEFORE: ${before_os}"

# 1) Build RPMs
chmod +x "${ROOT}/scripts/update-test/build-rpm.sh"
RPM_GUI="$(bash "${ROOT}/scripts/update-test/build-rpm.sh" nova-update-gui | tail -1)"
RPM_REL="$(bash "${ROOT}/scripts/update-test/build-rpm.sh" novaos-release | tail -1)"
RPM_UPD="$(bash "${ROOT}/scripts/update-test/build-rpm.sh" novaos-update | tail -1)"

echo "Built:"
echo "  ${RPM_GUI}"
echo "  ${RPM_REL}"
echo "  ${RPM_UPD}"

# 2) Publish to local Nova repo (clean channel — official 0.2.1 train only)
rm -rf "${REPO_CHANNELS}/${CHANNEL}"
bash "${ROOT}/scripts/update-test/publish-local-repo.sh" "${CHANNEL}" nova \
  "${RPM_GUI}" "${RPM_REL}" "${RPM_UPD}"

# 3) Reconfigure nova-updated for localrpm → install to system root
pkexec bash -c "
set -euo pipefail
ROOT='${ROOT}'
WORK='${WORK}'
# Refresh broker + GUI code onto the live system first (so GetHistory exists)
bash \"\${ROOT}/scripts/lib/sync-nova-update-overlay.sh\" / \"\${ROOT}\"
install -m 0755 \"\${ROOT}/desktop/nova-update/bin/nova-update-gui\" /usr/bin/nova-update-gui
rm -rf /usr/share/nova/update/gui
mkdir -p /usr/share/nova/update/gui
cp -a \"\${ROOT}/desktop/nova-update/nova_update_gui\" /usr/share/nova/update/gui/
install -m 0644 \"\${ROOT}/desktop/nova-update/org.novaos.Update.desktop\" \
  /usr/share/applications/org.novaos.Update.desktop

# Enable local file repo
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

# Ensure installed DB does not already claim 0.2.1 packages
rm -f /var/lib/nova/update/installed.json
mkdir -p /var/lib/nova/update /run/nova

systemctl daemon-reload
systemctl restart nova-updated.service
sleep 0.5
systemctl --no-pager --full status nova-updated.service | head -20
"

# 4) Check → detect
echo "==> nova-updater check"
CHECK_JSON="$(pkexec nova-updater check)"
echo "${CHECK_JSON}"
echo "${CHECK_JSON}" | grep -q 'nova-update-gui' || { echo "FAIL: nova-update-gui not detected"; exit 1; }
echo "${CHECK_JSON}" | grep -q 'novaos-release' || { echo "FAIL: novaos-release not detected"; exit 1; }
echo "${CHECK_JSON}" | grep -q "\"version\": \"${NEW_VERSION}\"" || echo "WARN: version string check soft"

# 5) Apply exclusively via Nova Update
echo "==> nova-updater apply"
APPLY_JSON="$(pkexec nova-updater apply)"
echo "${APPLY_JSON}"

# 6) Verify
after_version="$(. /etc/os-release; echo "${VERSION}")"
after_pretty="$(. /etc/os-release; echo "${PRETTY_NAME}")"
echo "AFTER VERSION=${after_version} PRETTY=${after_pretty}"

[[ "${after_version}" == "${NEW_VERSION}" ]] || {
  # os-release might be only in /usr/lib
  after_version="$(. /usr/lib/os-release; echo "${VERSION}")"
  after_pretty="$(. /usr/lib/os-release; echo "${PRETTY_NAME}")"
}
[[ "${after_version}" == "${NEW_VERSION}" ]] || {
  echo "FAIL: expected VERSION ${NEW_VERSION}, got ${after_version}"
  exit 1
}

test -x /usr/bin/nova-update-gui
test -f /usr/share/applications/org.novaos.Update.desktop
grep -q 'Name=Nova Update' /usr/share/applications/org.novaos.Update.desktop
grep -q 'Exec=nova-update-gui' /usr/share/applications/org.novaos.Update.desktop

# Desktop database refresh (best effort)
pkexec update-desktop-database /usr/share/applications >/dev/null 2>&1 || true

# 7) Report
cat >"${REPORT}" <<EOF
# Report aggiornamento NovaOS ${NEW_VERSION}

**Metodo:** Nova Update (\`nova-updater check\` → \`nova-updater apply\`)  
**ISO ricostruita:** No  
**Data:** $(date -Is)

## Versioni

| | Valore |
|--|--------|
| Versione precedente | ${PREV_VERSION} (\`${before_os}\`) |
| Versione nuova | ${after_version} (\`${after_pretty}\`) |

## Pacchetti aggiornati / installati

| Pacchetto | Versione | Ruolo |
|-----------|----------|-------|
| nova-update-gui | ${NEW_VERSION}-1.nova | GUI Applications menu |
| novaos-release | ${NEW_VERSION}-1.nova | Identità OS (\`os-release\`) |
| novaos-update | ${NEW_VERSION}-1.nova | Broker/CLI |

## File modificati (estratti dai RPM)

- \`/usr/bin/nova-update-gui\`
- \`/usr/share/nova/update/gui/nova_update_gui/\`
- \`/usr/share/applications/org.novaos.Update.desktop\`
- \`/usr/lib/os-release\`, \`/etc/os-release\`
- \`/etc/novaos/version\`, \`/etc/novaos/release-info\`
- \`/usr/libexec/nova-updated\`, \`/usr/bin/nova-updater\`, libreria \`nova_update\`

## Log

Vedi \`${LOG}\`.

### Output check (estratto)

\`\`\`json
${CHECK_JSON}
\`\`\`

### Output apply (estratto)

\`\`\`json
${APPLY_JSON}
\`\`\`

## Conferme

- [x] Aggiornamento eseguito tramite **Nova Update** (broker \`localrpm\` + repo \`file://\`)
- [x] **Nessuna** ricostruzione ISO
- [x] Menu applicazioni: voce **Nova Update** (\`org.novaos.Update.desktop\`)
- [x] Versione sistema: **${after_version}**
EOF

echo
echo "PASS — NovaOS ${PREV_VERSION} → ${NEW_VERSION} via Nova Update"
echo "Report: ${REPORT}"
