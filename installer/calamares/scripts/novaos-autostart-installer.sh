#!/bin/sh
# SPDX-License-Identifier: MIT
# Launch Calamares once on Live sessions after Plasma is up.
# Installed systems remove this via novaos-post-install.sh / install-state.
set -eu

STATE="${NOVAOS_INSTALL_STATE:-/etc/novaos/install-state}"
MARKER="${HOME}/.config/novaos/installer-autostarted"

# Only on live media
if [ ! -f "${STATE}" ] || ! grep -q '^mode=live$' "${STATE}" 2>/dev/null; then
  exit 0
fi

mkdir -p "${HOME}/.config/novaos"
if [ -f "${MARKER}" ]; then
  exit 0
fi

# Wait for Plasma/session bus so kdesu/polkit dialogs work.
i=0
while [ "${i}" -lt 60 ]; do
  if [ -n "${XDG_RUNTIME_DIR:-}" ] && [ -S "${XDG_RUNTIME_DIR}/bus" ]; then
    break
  fi
  i=$((i + 1))
  sleep 1
done
sleep 3

touch "${MARKER}"

# Live sudoers allows passwordless calamares for the demo wheel user.
if command -v sudo >/dev/null 2>&1; then
  exec sudo -n -E /usr/bin/calamares
fi
if command -v kdesu >/dev/null 2>&1; then
  exec kdesu -t -- /usr/bin/calamares
fi
exec /usr/bin/calamares
