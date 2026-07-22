# 04 — Icons

**NovaOS Design System — Iconografia**  
**Sprint:** 2 — Identità visiva  
**Stato:** Specifica ufficiale (pre-glyph set)

---

## 1. Scopo

Definire linguaggio, griglia, pesi e metafore delle icone di NovaOS / Nova Shell. Nessun file SVG in questo sprint: solo regole che guideranno il set **Nova Icons**.

---

## 2. Filosofia

1. **Segni, non illustrazioni** — icone UI essenziali; niente mascotte.
2. **Una sola famiglia** — stroke coerente in tutto il sistema.
3. **Metafore universali + metafore Nova** — dove serve differenziazione (AI, Shell).
4. **Riconoscibilità a 16px** — se non legge a 16, non è pronta.
5. **Non Fluent, non SF Symbols, non Breeze clonate** — ispirazione ok, copia no.

---

## 3. Griglia e geometria

| Parametro | Valore |
|-----------|--------|
| Canvas live | 24×24 unit (design) |
| Optical padding | 2 unit per lato tipici |
| Keyline shapes | square / circle / rect orizzontale secondo metafora |
| Corner radius icone | 2 unit (non 0 a lama; non round-full) |
| Stroke (regular) | 1.75 unit @24 |
| Stroke (micro 16) | 1.5 unit ottico |
| Terminali | Rounded caps / joins leggermente arrotondati |
| Angoli preferiti | 45° / 90°; diagonali controllate |

### Dimensioni d’uso

| Token | px | Uso |
|-------|-----|-----|
| `icon.xs` | 12 | Indicatori densi (raro) |
| `icon.sm` | 16 | Menu, titlebar, status |
| `icon.md` | 20 | Bottoni toolbar |
| `icon.lg` | 24 | Launcher grid, settings rows |
| `icon.xl` | 32 | Empty state |
| `icon.app` | 48 / 64 / 128 / 256 / 512 | App icon raster |

---

## 4. Pesi e varianti

| Variante | Uso |
|----------|-----|
| **Outline** | Default UI chrome |
| **Solid** | Selezionato, toggle on, status filled |
| **Duotone controllato** | Solo mark AI / Nova: outline + fill `signal` al 20–40% |

Mai più di due toni. Mai gradienti dentro l’icona UI.

---

## 5. Colore delle icone

| Contesto | Colore |
|----------|--------|
| Default | `text` / `steel` corrente del tema |
| Active / selected | `stellar.500` (azione) oppure testo primary |
| AI correlato | `signal.400/500` |
| Danger | `state.danger` |
| Disabled | opacità 40% |

Le icone **non** portano il brand purple; seguono i token colore.

---

## 6. Metafore distintive Nova

| Concetto | Metafora Nova | Evitare |
|----------|---------------|---------|
| Launcher di sistema | **Nova Core** — nucleo + anello | Logo Windows, griglia 3×3 generica unica firma |
| NovaAI | Alone / nodo luminoso stilizzato | Testa robot, sparkles cliché a 4 punte Apple |
| Control Center | Slider + raggio | Ingranaggio unico per tutto |
| Notifiche | Campana geometrica semplificata | Bollini cartoon |
| Rete | Onde corte angolari | Globe generico se c’è meglio |
| Cloud Nova | Forma cloud con taglio netto | Icloud clone |

---

## 7. App icon system

- Forma contenitore: **squircle soft Nova** con raggio proprietario (non iOS, non mask Windows).
- Raggio proporzionale: ~22% del lato a 128px (da calibrare in asset phase).
- Fondale app: tinta da palette dominio, ma bordo/ombra secondo token unificati.
- Glyph centrato, safe area 80%.
- Ombra: **una** sola, soft, Y+2 blur 8 opacità bassa — non stack Material.

---

## 8. Cursore e status glyphs

- Cursori: precisi, hotspot documentati; variante “busy” con alone `signal` minimo (non beachball, non clessidra XP).
- Tray: preferire monochromi template; badge numerico con raggio 6px max.

---

## 9. Accessibilità

- Non usare solo l’icona per azioni distruttive: sempre label in menu.
- Contrasto glyph/fondo ≥ 3:1 per icone informative.
- Alt text / accessible name obbligatori dove non c’è label visibile.

---

## 10. Processo di evoluzione

1. Core set shell (~80 glyph) prima del resto.
2. Settings set.
3. File manager / system.
4. Ecosystem apps ereditano stile, aggiungono metafore di dominio in PR di design review.

---

## 11. Motivazione

Uno stroke 1.75 su griglia 24 bilancia nitidezza HiDPI e personalità. Il duotone limitato al solo AI evita il look “icon pack marketplace”. Il rifiuto esplicito di Fluent/SF/Breeze protegge il riconoscimento a colpo d’occhio.
