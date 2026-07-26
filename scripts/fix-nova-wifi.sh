#!/usr/bin/env bash
# Sprint 17 — repair Wi-Fi stack on a live NovaOS host (NetworkManager + wpa_supplicant).
# No chmod 777 / no GUI-as-root. Requires root (pkexec/sudo).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [[ "$(id -u)" -ne 0 ]]; then
  exec pkexec bash "$0" "$@"
fi

echo "==> Restoring usrmerge (/usr/sbin → bin) so wpa_supplicant can start"
# shellcheck source=lib/ensure-usrmerge.sh
source "${ROOT}/scripts/lib/ensure-usrmerge.sh"
ensure_usrmerge /

if [[ ! -x /usr/sbin/wpa_supplicant && ! -x /usr/bin/wpa_supplicant ]]; then
  echo "FAIL: wpa_supplicant binary missing — install package wpa_supplicant" >&2
  exit 1
fi
test -x /usr/sbin/wpa_supplicant

echo "==> Installing NetworkManager Wi-Fi policy"
install -d /etc/NetworkManager/conf.d
install -m 0644 "${ROOT}/configs/network/20-novaos-wifi.conf" \
  /etc/NetworkManager/conf.d/20-novaos-wifi.conf

echo "==> Unblocking radio + ensuring Wi-Fi enabled"
rfkill unblock wifi 2>/dev/null || true
rfkill unblock wlan 2>/dev/null || true

systemctl reset-failed wpa_supplicant.service 2>/dev/null || true
systemctl restart NetworkManager.service
# Give NM time to D-Bus activate wpa_supplicant
sleep 2
systemctl start wpa_supplicant.service 2>/dev/null || true
sleep 1

nmcli radio wifi on || true
nmcli general reload 2>/dev/null || true

echo "==> Status"
stat -c '%N' /usr/sbin
systemctl is-active NetworkManager.service
systemctl is-active wpa_supplicant.service || systemctl status wpa_supplicant.service --no-pager | head -15 || true
nmcli -t radio
nmcli -t device status

WIFI_DEV="$(nmcli -t -f DEVICE,TYPE device status | awk -F: '$2=="wifi"{print $1; exit}')"
if [[ -z "${WIFI_DEV}" ]]; then
  echo "WARN: no Wi-Fi device visible to NetworkManager" >&2
else
  STATE="$(nmcli -t -f DEVICE,STATE device status | awk -F: -v d="${WIFI_DEV}" '$1==d{print $2}')"
  echo "Wi-Fi device ${WIFI_DEV} state=${STATE}"
  if [[ "${STATE}" == "unavailable" ]]; then
    echo "FAIL: Wi-Fi still unavailable after wpa_supplicant fix" >&2
    journalctl -b -u wpa_supplicant -u NetworkManager --no-pager -n 30 >&2 || true
    exit 1
  fi
  nmcli device wifi rescan 2>/dev/null || true
  sleep 2
  echo "==> Scan (top 8)"
  nmcli -t -f IN-USE,SSID,SIGNAL,SECURITY device wifi list ifname "${WIFI_DEV}" 2>/dev/null | head -8 || true
fi

# Ensure saved Wi-Fi connections autoconnect
while IFS=: read -r name uuid typ; do
  [[ "${typ}" == "802-11-wireless" ]] || continue
  nmcli connection modify "${uuid}" connection.autoconnect yes connection.autoconnect-priority 0 2>/dev/null || true
  echo "    autoconnect enabled: ${name}"
done < <(nmcli -t -f NAME,UUID,TYPE connection show)

echo "PASS — Wi-Fi foundation repaired (NetworkManager + wpa_supplicant)"
