#!/usr/bin/env bash
# Apply nova-updated socket ACL fix on the live host (group nova, 0660).
# Requires root (pkexec/sudo). No chmod 777, no GUI-as-root.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [[ "$(id -u)" -ne 0 ]]; then
  exec pkexec bash "$0" "$@"
fi

echo "==> Syncing Nova Update overlay (daemon + units + sysusers)"
bash "${ROOT}/scripts/lib/sync-nova-update-overlay.sh" / "${ROOT}"

# shellcheck source=lib/ensure-nova-group.sh
source "${ROOT}/scripts/lib/ensure-nova-group.sh"
add_login_users_to_nova_group

echo "==> Reloading systemd units"
systemctl daemon-reload
systemctl enable nova-updated.socket
systemctl enable nova-updated.service

# Stop service first so it releases any self-bound socket, then start socket unit.
systemctl stop nova-updated.service 2>/dev/null || true
rm -f /run/nova/update.sock
systemctl restart nova-updated.socket
systemctl restart nova-updated.service
sleep 0.8

echo "==> Socket status"
stat -c '%U:%G %a %n' /run/nova/update.sock
OWNER_MODE="$(stat -c '%U:%G %a' /run/nova/update.sock)"
[[ "${OWNER_MODE}" == "root:nova 660" ]] || {
  echo "FAIL: expected root:nova 660, got ${OWNER_MODE}" >&2
  exit 1
}
getent group nova
systemctl --no-pager --full is-active nova-updated.socket
systemctl --no-pager --full is-active nova-updated.service

USER_NAME="$(getent passwd | awk -F: '$3>=1000 && $3<65534 {print $1; exit}')"
[[ -n "${USER_NAME}" ]] || { echo "FAIL: no interactive user" >&2; exit 1; }

echo "==> Client connect as ${USER_NAME} via group nova (sg)"
CLIENT_SCRIPT="$(mktemp)"
chmod 644 "${CLIENT_SCRIPT}"
cat >"${CLIENT_SCRIPT}" <<'PY'
import json
import socket
import sys

s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
s.settimeout(5)
try:
    s.connect("/run/nova/update.sock")
except PermissionError as exc:
    print(f"FAIL permission denied: {exc}", file=sys.stderr)
    sys.exit(1)
s.sendall(b'{"api":"system.update.v1","id":1,"method":"GetStatus","params":{}}\n')
s.shutdown(socket.SHUT_WR)
buf = b""
while not buf.endswith(b"\n"):
    chunk = s.recv(4096)
    if not chunk:
        break
    buf += chunk
s.close()
msg = json.loads(buf.decode())
if msg.get("error"):
    print("FAIL", msg, file=sys.stderr)
    sys.exit(1)
result = msg.get("result") or {}
print("PASS — GetStatus OK")
print(f"    channel={result.get('channel')} backend={result.get('backend')}")
PY
chmod 644 "${CLIENT_SCRIPT}"
runuser -u "${USER_NAME}" -- sg nova -c "python3 ${CLIENT_SCRIPT}"
rm -f "${CLIENT_SCRIPT}"

# Negative check: without group nova, connect must fail (proves we didn't chmod world-writable)
echo "==> Negative check: credentials without group nova must be denied"
NEG="$(mktemp)"
chmod 644 "${NEG}"
cat >"${NEG}" <<'PY'
import socket
import sys

s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
try:
    s.connect("/run/nova/update.sock")
except PermissionError:
    print("PASS — permission denied without group nova (expected)")
    sys.exit(0)
s.close()
print("FAIL — connect succeeded without group nova (socket too open?)", file=sys.stderr)
sys.exit(1)
PY
FABIO_UID="$(id -u "${USER_NAME}")"
FABIO_GID="$(id -g "${USER_NAME}")"
if command -v setpriv >/dev/null 2>&1; then
  setpriv --reuid="${FABIO_UID}" --regid="${FABIO_GID}" --clear-groups -- python3 "${NEG}"
else
  echo "WARN: setpriv missing — skip negative ACL check"
fi
rm -f "${NEG}"

if command -v nova-center >/dev/null 2>&1; then
  echo "==> Nova Center bridge as ${USER_NAME}"
  runuser -u "${USER_NAME}" -- sg nova -c 'DISPLAY= nova-center' \
    >/tmp/nova-center-socket-test.json 2>/tmp/nova-center-socket-test.err || true
  if grep -q '"service": "attivo"' /tmp/nova-center-socket-test.json \
    && ! grep -q 'permission denied' /tmp/nova-center-socket-test.json \
    && ! grep -q '"error": "permesso negato' /tmp/nova-center-socket-test.json; then
    echo "PASS — Nova Center updates bridge OK"
  else
    echo "FAIL — Nova Center still cannot reach broker" >&2
    python3 -c 'import json;print(json.load(open("/tmp/nova-center-socket-test.json"))["updates"])' >&2 || true
    exit 1
  fi
fi

# Broker still works as root / service
nova-updater status >/tmp/nova-updater-status.json
grep -q '"api"' /tmp/nova-updater-status.json || grep -q channel /tmp/nova-updater-status.json \
  || { echo "FAIL: nova-updater status"; cat /tmp/nova-updater-status.json; exit 1; }
echo "PASS — nova-updater status OK"

echo
echo "NOTE: log out/in (or newgrp nova) so the graphical session inherits group nova."
echo "PASS — socket is root:nova 0660; no sudo required for group members."
