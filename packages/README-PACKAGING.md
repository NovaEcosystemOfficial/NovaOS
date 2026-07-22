# Linee guida packaging NovaOS

## Principi

1. Un componente installabile → un RPM (o set chiaro di RPM).  
2. File in path FHS documentati (`docs/boot-foundation/04-File-System.md`).  
3. Nessuna dipendenza da Ollama/AI nei pacchetti M0.1.  
4. Spec file in `SPECS/` o accanto alle fonti del pacchetto — decidere uno stile e mantenerlo.  
5. Firma pacchetti: obbligatoria prima di release pubbliche (dopo M0.1 interno).

## Build pacchetto (futuro)

```text
scripts/build-package.sh novaos-branding
  → RPM in build/work/rpms o packages/out (da definire)
  → inclusione nella ricetta KIWI
```

## Review checklist

- [ ] License dichiarata  
- [ ] File list esplicita  
- [ ] Nessun segreto  
- [ ] Allineamento Design System / boot-foundation  
