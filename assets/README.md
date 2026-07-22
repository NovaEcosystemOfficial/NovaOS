# `assets/`

Asset di sistema e di branding **sorgente** usati nelle immagini NovaOS (non codice).

## Scopo (Sprint 5)

Preparare l’alberatura dove il team depositerà logo, wallpaper, temi greeter/splash e risorse statiche, in conformità al Design System.

## Motivazione

Gli asset devono essere:

- versionabili (file sorgente non enormi);
- referenziabili dalle ricette KIWI / pacchetti `novaos-branding`;
- distinti da `branding/` root (identità di progetto) se serve una copia “da installare nel rootfs”.

`branding/` alla root resta la **fonte di verità creativa**; `assets/` è la **vista da packaging** verso l’immagine.

## Struttura

```text
assets/
├── README.md
├── branding/       # logo, mark, lockup pronti al packaging
├── plymouth/       # tema splash (file theme — futuri)
├── sddm/           # tema login (futuri)
├── wallpapers/     # sfondi Nova Shell iniziale
├── icons/          # icone di sistema / app stub
└── sounds/         # opzionale M0.1+ (Design System 08)
```

## Regole

- Niente binari ISO qui.
- Preferire SVG + PNG export documentati.
- Licenze/asset di terzi: solo con clearance.

## Stato Sprint 5

Struttura creata. Placeholder README nelle sottocartelle. Nessun tema SDDM/Shell implementato.
