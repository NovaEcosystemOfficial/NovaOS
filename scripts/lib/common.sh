#!/usr/bin/env bash
# Shared paths and helpers for NovaOS build scripts.
# shellcheck shell=bash

NOVAOS_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
export NOVAOS_ROOT

# Optional local overrides (copy from configs/bootstrap/env.sh.example)
if [[ -f "${NOVAOS_ROOT}/configs/bootstrap/env.sh" ]]; then
  # shellcheck disable=SC1091
  source "${NOVAOS_ROOT}/configs/bootstrap/env.sh"
fi

export NOVAOS_BUILD_DIR="${NOVAOS_BUILD_DIR:-${NOVAOS_ROOT}/build}"
export NOVAOS_ISO_DIR="${NOVAOS_ISO_DIR:-${NOVAOS_ROOT}/iso}"
export NOVAOS_CONFIG_DIR="${NOVAOS_CONFIG_DIR:-${NOVAOS_ROOT}/configs}"

# KIWI needs a real Linux filesystem for workdirs (loop mounts, chmod, xattrs).
# Auto-relocate when the repo lives on drvfs/9p/NTFS (typical WSL /mnt/* case).
novaos_ensure_linux_build_fs() {
  local fstype
  fstype="$(findmnt -n -o FSTYPE --target "${NOVAOS_BUILD_DIR}" 2>/dev/null || true)"
  case "${fstype}" in
    9p|drvfs|fuse*|vfat|ntfs|ntfs3|cifs|smb3)
      local relocated="/var/tmp/novaos-build"
      echo "WARN: NOVAOS_BUILD_DIR is on ${fstype}; relocating work to ${relocated}" >&2
      export NOVAOS_BUILD_DIR="${relocated}"
      mkdir -p "${NOVAOS_BUILD_DIR}/cache" "${NOVAOS_BUILD_DIR}/work" "${NOVAOS_BUILD_DIR}/logs"
      ;;
  esac
}

novaos_load_release_env() {
  local env_file="${NOVAOS_CONFIG_DIR}/fedora/release.env"
  if [[ ! -f "${env_file}" ]]; then
    echo "ERROR: missing ${env_file}" >&2
    return 1
  fi
  # shellcheck disable=SC1090
  set -a
  # shellcheck disable=SC1091
  source "${env_file}"
  set +a

  local required=(FEDORA_VERSION FEDORA_ARCH NOVAOS_VERSION NOVAOS_PROFILE NOVAOS_ISO_NAME NOVAOS_MILESTONE)
  local k
  for k in "${required[@]}"; do
    if [[ -z "${!k:-}" ]]; then
      echo "ERROR: ${env_file} missing required variable: ${k}" >&2
      return 1
    fi
  done

  # Keep aliases consistent after load
  export NOVAOS_KIWI_PROFILE="${NOVAOS_PROFILE}"
}

novaos_require_root() {
  if [[ "${EUID}" -ne 0 ]]; then
    echo "ERROR: this command must run as root (KIWI / image build)." >&2
    echo "Try: sudo ${0}" >&2
    exit 1
  fi
}

novaos_require_cmd() {
  local c
  for c in "$@"; do
    if ! command -v "${c}" >/dev/null 2>&1; then
      echo "ERROR: required command not found: ${c}" >&2
      echo "Run: sudo scripts/setup-build-host.sh" >&2
      exit 1
    fi
  done
}

novaos_timestamp() {
  date -u +%Y%m%dT%H%M%SZ
}

novaos_kiwi_bin() {
  if command -v kiwi-ng >/dev/null 2>&1; then
    printf '%s\n' "kiwi-ng"
  elif command -v kiwi >/dev/null 2>&1; then
    printf '%s\n' "kiwi"
  else
    return 1
  fi
}
