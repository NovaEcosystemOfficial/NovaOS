# `vm/`

Ambiente e configurazioni per **test in macchina virtuale** delle ISO NovaOS.

## Scopo (Sprint 5)

Preparare un posto standard per:

- parametri QEMU/KVM di riferimento;
- note sul firmware UEFI (OVMF);
- script di lancio collegati a `scripts/run-vm.sh`;
- dischi di prova (non versionati).

## Motivazione

Validare ogni ISO in VM **prima** del flash USB sul PC di sviluppo riduce il ciclo di feedback (docs/boot-foundation/09-Testing-Strategy.md Tier 0–1).

## Struttura

```text
vm/
├── README.md
├── qemu/             # parametri e snippet di launch
├── disks/            # dischi qcow2 di test (gitignored content)
└── notes/            # appunti su reference VM
```

## Requisiti host

- Fedora host consigliato
- `qemu-kvm`, `edk2-ovmf`
- ISO in `iso/releases` o `iso/latest`

## Stato Sprint 5

Infrastruttura documentata + template parametri. Nessuna VM automatica obbligatoria finché non esiste ISO.
