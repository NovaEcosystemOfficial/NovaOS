#!/usr/bin/env bash
# Ensure system group "nova" exists and add interactive users to it.
# Safe to re-run. Used by post-install, host install, and image config.
# shellcheck shell=bash
set -euo pipefail

ensure_nova_group() {
  if command -v systemd-sysusers >/dev/null 2>&1; then
    if [[ -f /usr/lib/sysusers.d/nova.conf ]]; then
      systemd-sysusers nova.conf >/dev/null 2>&1 || true
    fi
  fi
  if ! getent group nova >/dev/null 2>&1; then
    groupadd -r nova
  fi
}

# Add a single user to group nova (idempotent).
add_user_to_nova_group() {
  local user="${1:?user required}"
  if ! id -u "${user}" >/dev/null 2>&1; then
    return 0
  fi
  if id -nG "${user}" 2>/dev/null | tr ' ' '\n' | grep -qx nova; then
    return 0
  fi
  usermod -aG nova "${user}"
}

# Add all human login accounts (UID >= 1000, < 65534) plus common live users.
add_login_users_to_nova_group() {
  ensure_nova_group
  local user uid
  while IFS=: read -r user _ uid _; do
    if [[ "${uid}" -ge 1000 && "${uid}" -lt 65534 ]]; then
      add_user_to_nova_group "${user}"
    fi
  done < <(getent passwd)
  # Live/demo account may already exist with reserved name
  if id -u nova >/dev/null 2>&1; then
    # user named "nova" is distinct from group "nova"
    add_user_to_nova_group nova || true
  fi
}

# When sourced, only define helpers. When executed, apply.
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  add_login_users_to_nova_group
  echo "PASS — group nova ready; login users membership updated"
  getent group nova || true
fi
