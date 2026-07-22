# `vm/qemu/`

Parametri di riferimento per QEMU/KVM.

## Target smoke (Tier 0)

| Parametro | Valore consigliato |
|-----------|-------------------|
| RAM | 4096 MB (8192 meglio) |
| CPU | host / 2+ cores |
| Firmware | OVMF (UEFI) |
| GPU | virtio / std |
| ISO | path da `iso/` |

## File

- `launch.example.sh` — esempio di riga di comando (non entrypoint ufficiale; usare `scripts/run-vm.sh`)

## Motivazione

Un comando “golden” evita che ogni developer inventi flag diversi e dichiari falsi positivi/negativi.
