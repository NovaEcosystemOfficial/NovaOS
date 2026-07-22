#!/usr/bin/env bash
# Replace stock QEMU example — use scripts/run-vm.sh instead.
exec "$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)/scripts/run-vm.sh" "$@"
