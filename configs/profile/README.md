# `configs/profile/`

Profili nominati di prodotto/immagine.

## Motivazione

Una sola repo, più profili:

| Profilo | Uso |
|---------|-----|
| `m01` | Milestone 0.1 — ISO foundation boot |
| `dev` | Extra tool di debug (futuro) |
| `atomic` | Futuro rpm-ostree (non ora) |

I profili collegano `configs/fedora` + `configs/kiwi` + flag script senza duplicare tutto.

## Stato Sprint 5

Profilo `m01` documentato come target attivo.
