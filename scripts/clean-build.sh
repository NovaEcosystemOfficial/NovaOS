#!/usr/bin/env bash
# Remove KIWI work trees and optionally package cache.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# shellcheck source=lib/common.sh
source "${ROOT}/scripts/lib/common.sh"

CLEAN_CACHE=0
FORCE=0
for arg in "$@"; do
  case "${arg}" in
    --cache) CLEAN_CACHE=1 ;;
    --yes|-y) FORCE=1 ;;
    -h|--help)
      echo "Usage: $0 [--yes] [--cache]"
      echo "  --yes    do not ask for confirmation"
      echo "  --cache  also delete build/cache"
      exit 0
      ;;
  esac
done

WORK="${NOVAOS_BUILD_DIR}/work"
LOGS="${NOVAOS_BUILD_DIR}/logs"
CACHE="${NOVAOS_BUILD_DIR}/cache"

echo "Will remove contents of:"
echo "  ${WORK}"
echo "  ${LOGS}"
if [[ "${CLEAN_CACHE}" -eq 1 ]]; then
  echo "  ${CACHE}"
fi

if [[ "${FORCE}" -ne 1 ]]; then
  read -r -p "Continue? [y/N] " ans
  [[ "${ans}" == "y" || "${ans}" == "Y" ]] || exit 0
fi

mkdir -p "${WORK}" "${LOGS}" "${CACHE}"
# Keep directory placeholders
find "${WORK}" -mindepth 1 -maxdepth 1 -exec rm -rf {} +
find "${LOGS}" -mindepth 1 -maxdepth 1 -exec rm -rf {} +
if [[ "${CLEAN_CACHE}" -eq 1 ]]; then
  find "${CACHE}" -mindepth 1 -maxdepth 1 -exec rm -rf {} +
fi

echo "clean-build: done"
