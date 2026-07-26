# `scripts/`

Official build/test entrypoints for NovaOS.

| Script | Purpose |
|--------|---------|
| `validate-pipeline.sh` | Static checks (no root) |
| `validate-update.sh` | Nova Update foundation + image overlay smoke (no root) |
| `setup-build-host.sh` | Install KIWI, QEMU, OVMF (root) |
| `check-env.sh` | Validate tools + description on build host |
| `build-iso.sh` | Build live ISO with KIWI (root); syncs Calamares + Nova Update |
| `run-vm.sh` | Boot ISO in QEMU/UEFI |
| `sha256-iso.sh` | Checksum helper |
| `clean-build.sh` | Remove `build/work` (+ optional cache) |
| `lib/common.sh` | Shared paths/helpers |
| `lib/sync-nova-update-overlay.sh` | Stage update broker/CLI/repos/GUI into KIWI `root/` |
| `install-nova-update-host.sh` | Install Nova Update on the running host (no ISO) |
| `update-test/` | Local RPM repo e2e (build/publish/check/apply) |

```bash
make validate
make validate-update
make test-update
sudo make setup
make check
sudo make iso
make vm
```
