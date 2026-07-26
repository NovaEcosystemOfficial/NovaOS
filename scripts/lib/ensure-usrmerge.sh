#!/usr/bin/env bash
# Ensure Fedora-style usrmerge: /usr/sbin → bin (and /sbin → usr/sbin).
# Critical for wpa_supplicant: unit ExecStart=/usr/sbin/wpa_supplicant while
# the binary ships in /usr/bin. Creating a real /usr/sbin directory (e.g. via
# overlay mkdir or naive rpm2cpio|cpio) breaks Wi-Fi.
# shellcheck shell=bash
set -euo pipefail

ensure_usrmerge() {
  local root="${1:-/}"
  root="${root%/}"
  [[ -z "${root}" ]] && root="/"

  local sbin="${root}/usr/sbin"
  local bin="${root}/usr/bin"

  mkdir -p "${bin}"

  if [[ -L "${sbin}" ]]; then
    local target
    target="$(readlink "${sbin}")"
    if [[ "${target}" == "bin" || "${target}" == "/usr/bin" || "${target}" == "../bin" ]]; then
      return 0
    fi
  fi

  if [[ -d "${sbin}" && ! -L "${sbin}" ]]; then
    local f base
    shopt -s nullglob
    for f in "${sbin}"/* "${sbin}"/.[!.]* "${sbin}"/..?*; do
      [[ -e "${f}" ]] || continue
      base="$(basename "${f}")"
      if [[ -e "${bin}/${base}" || -L "${bin}/${base}" ]]; then
        # Prefer the usrmerge location; drop duplicate under real sbin.
        rm -rf "${f}"
      else
        mv "${f}" "${bin}/${base}"
      fi
    done
    shopt -u nullglob
    rmdir "${sbin}" 2>/dev/null || rm -rf "${sbin}"
  elif [[ -e "${sbin}" && ! -d "${sbin}" ]]; then
    rm -f "${sbin}"
  fi

  ln -sfn bin "${sbin}"

  # Classic symlinks at root (when operating on live /)
  if [[ "${root}" == "/" ]]; then
    if [[ ! -L /sbin ]]; then
      rm -rf /sbin
      ln -sfn usr/sbin /sbin
    fi
    if [[ ! -L /bin ]]; then
      # Never replace a real /bin with content — only fix if missing/wrong
      if [[ ! -e /bin ]]; then
        ln -sfn usr/bin /bin
      fi
    fi
    chmod 755 /usr 2>/dev/null || true
  fi
}

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  ensure_usrmerge "${1:-/}"
  echo "PASS — usrmerge OK ($(readlink -f /usr/sbin 2>/dev/null || readlink /usr/sbin))"
  ls -ld /usr/sbin /usr/bin/wpa_supplicant 2>/dev/null || true
fi
