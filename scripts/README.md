# `scripts/`

Official build/test entrypoints for NovaOS.

| Script | Purpose |
|--------|---------|
| `validate-pipeline.sh` | Static checks (no root) |
| `setup-build-host.sh` | Install KIWI, QEMU, OVMF (root) |
| `check-env.sh` | Validate tools + description on build host |
| `build-iso.sh` | Build live ISO with KIWI (root) |
| `run-vm.sh` | Boot ISO in QEMU/UEFI |
| `sha256-iso.sh` | Checksum helper |
| `clean-build.sh` | Remove `build/work` (+ optional cache) |
| `lib/common.sh` | Shared paths/helpers |

```bash
make validate
sudo make setup
make check
sudo make iso
make vm
```
