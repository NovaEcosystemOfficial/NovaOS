#!/usr/bin/env bash
# Compute SHA256 for an ISO artifact.
set -euo pipefail

TARGET="${1:-}"
if [[ -z "${TARGET}" ]]; then
  echo "Usage: $0 <path-to.iso>" >&2
  exit 2
fi
if [[ ! -f "${TARGET}" ]]; then
  echo "ERROR: file not found: ${TARGET}" >&2
  exit 1
fi

if command -v sha256sum >/dev/null 2>&1; then
  sha256sum "${TARGET}" | tee "${TARGET}.sha256"
elif command -v shasum >/dev/null 2>&1; then
  shasum -a 256 "${TARGET}" | tee "${TARGET}.sha256"
else
  echo "ERROR: need sha256sum or shasum" >&2
  exit 1
fi
