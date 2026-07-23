#!/usr/bin/env bash
# Verifica presenza dei file critici per la build ISO NovaOS
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
required_dirs=(
  build configs assets iso packages scripts vm tools
  configs/fedora configs/kiwi configs/kiwi/novaos-m01
)
required_files=(
  configs/kiwi/novaos-m01/appliance.kiwi
  configs/kiwi/novaos-m01/config.sh
  configs/kiwi/novaos-m01/iso-esp-excludes.yaml
  configs/kiwi/novaos-m01/PUBLIC_DEMO_CREDENTIALS.txt
  configs/fedora/release.env
  configs/bootstrap/host-packages.txt
  scripts/build-iso.sh
  scripts/setup-build-host.sh
  scripts/check-env.sh
  scripts/run-vm.sh
  scripts/validate-pipeline.sh
  scripts/lib/common.sh
  Makefile
  SECURITY.md
)

echo "lint-workspace: ${ROOT}"
err=0
for p in "${required_dirs[@]}"; do
  if [[ ! -d "${ROOT}/${p}" ]]; then
    echo "MISSING DIR: ${p}"
    err=1
  fi
done
for p in "${required_files[@]}"; do
  if [[ ! -f "${ROOT}/${p}" ]]; then
    echo "MISSING FILE: ${p}"
    err=1
  fi
done

if [[ "${err}" -ne 0 ]]; then
  echo "FAIL"
  exit 1
fi
echo "PASS — build infrastructure OK"
exit 0
