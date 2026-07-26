#!/usr/bin/env bash
# Static validation of the NovaOS Calamares installer tree (no root).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
err=0
pass() { echo "PASS: $*"; }
fail() { echo "FAIL: $*" >&2; err=1; }

echo "==> validate-installer (static)"
SRC="${ROOT}/installer/calamares"

[[ -d "${SRC}" ]] && pass "installer/calamares exists" || fail "installer/calamares missing"

required=(
  settings.conf
  modules/welcome.conf
  modules/partition.conf
  modules/users.conf
  modules/unpackfs.conf
  modules/removeuser.conf
  modules/displaymanager.conf
  modules/grubcfg.conf
  modules/bootloader.conf
  modules/services-systemd.conf
  modules/shellprocess-postinstall.conf
  modules/finished.conf
  scripts/novaos-post-install.sh
  desktop/novaos-installer.desktop
  branding/novaos/branding.desc
  branding/novaos/show.qml
  branding/novaos/logo.png
  branding/novaos/welcome.png
)
for f in "${required[@]}"; do
  if [[ -f "${SRC}/${f}" ]]; then
    pass "${f}"
  else
    fail "missing ${f}"
  fi
done

if grep -q 'branding: novaos' "${SRC}/settings.conf"; then
  pass "settings branding=novaos"
else
  fail "settings.conf must set branding: novaos"
fi

if grep -q 'initialPartitioningChoice: none' "${SRC}/modules/partition.conf"; then
  pass "partition: no default erase"
else
  fail "partition must default to none (explicit dual-boot safety)"
fi

if grep -q 'GRUB_DISABLE_OS_PROBER' "${SRC}/modules/grubcfg.conf"; then
  pass "grubcfg enables os-prober knobs"
else
  fail "grubcfg missing OS_PROBER setting"
fi

if grep -q '/run/rootfsbase' "${SRC}/modules/unpackfs.conf"; then
  pass "unpackfs uses KIWI LiveOS /run/rootfsbase"
else
  fail "unpackfs must use /run/rootfsbase"
fi

if grep -q 'username: nova' "${SRC}/modules/removeuser.conf"; then
  pass "removeuser targets demo account nova"
else
  fail "removeuser must remove demo user nova"
fi

if grep -q 'calamares' "${ROOT}/configs/kiwi/novaos-m01/appliance.kiwi"; then
  pass "appliance.kiwi includes calamares"
else
  fail "appliance.kiwi missing calamares package"
fi

if grep -q 'os-prober' "${ROOT}/configs/kiwi/novaos-m01/appliance.kiwi"; then
  pass "appliance.kiwi includes os-prober"
else
  fail "appliance.kiwi missing os-prober"
fi

for needle in git gcc make cmake; do
  if grep -q "<package name=\"${needle}\"/>" "${ROOT}/configs/kiwi/novaos-m01/appliance.kiwi"; then
    pass "devtools package ${needle}"
  else
    fail "missing devtools package ${needle}"
  fi
done

if grep -q 'Syncing Calamares' "${ROOT}/scripts/build-iso.sh"; then
  pass "build-iso syncs installer tree"
else
  fail "build-iso.sh must sync installer/calamares"
fi

if grep -q 'sync-nova-update-overlay' "${ROOT}/scripts/build-iso.sh"; then
  pass "build-iso syncs Nova Update overlay"
else
  fail "build-iso.sh must sync Nova Update into root overlay"
fi

if grep -q 'nova-updated.service' "${SRC}/modules/services-systemd.conf"; then
  pass "services-systemd enables nova-updated"
else
  fail "services-systemd.conf must enable nova-updated.service"
fi

if grep -q 'nova-updated.socket' "${SRC}/modules/services-systemd.conf"; then
  pass "services-systemd enables nova-updated.socket"
else
  fail "services-systemd.conf must enable nova-updated.socket"
fi

if grep -q 'name: nova' "${SRC}/modules/users.conf"; then
  pass "Calamares users defaultGroups includes nova"
else
  fail "users.conf must add installer account to group nova"
fi

if grep -q 'systemctl enable nova-updated' "${SRC}/scripts/novaos-post-install.sh"; then
  pass "post-install enables nova-updated"
else
  fail "novaos-post-install.sh must enable nova-updated"
fi

if grep -q 'usermod -aG nova' "${SRC}/scripts/novaos-post-install.sh"; then
  pass "post-install adds users to group nova"
else
  fail "post-install must usermod -aG nova for login users"
fi

if grep -q 'systemctl enable nova-updated' "${ROOT}/configs/kiwi/novaos-m01/config.sh"; then
  pass "config.sh enables nova-updated"
else
  fail "config.sh must enable nova-updated.service"
fi

if grep -q 'wpa_supplicant' "${ROOT}/configs/kiwi/novaos-m01/appliance.kiwi" \
  && grep -q 'linux-firmware' "${ROOT}/configs/kiwi/novaos-m01/appliance.kiwi"; then
  pass "appliance.kiwi includes Wi-Fi stack packages"
else
  fail "appliance.kiwi must include wpa_supplicant and linux-firmware"
fi

if grep -q 'novaos-post-install.sh' "${SRC}/modules/shellprocess-postinstall.conf" \
  && grep -q '/usr/bin/novaos-post-install.sh' "${SRC}/modules/shellprocess-postinstall.conf"; then
  pass "post-install invoked from /usr/bin (usrmerge-safe)"
else
  fail "shellprocess must call /usr/bin/novaos-post-install.sh"
fi

if [[ -f "${ROOT}/configs/network/20-novaos-wifi.conf" ]]; then
  pass "NetworkManager Wi-Fi policy present"
else
  fail "missing configs/network/20-novaos-wifi.conf"
fi

echo
if [[ "${err}" -ne 0 ]]; then
  echo "validate-installer: FAILED"
  exit 1
fi
echo "validate-installer: PASSED"
exit 0
