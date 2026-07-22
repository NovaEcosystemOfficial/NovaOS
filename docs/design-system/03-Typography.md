# 03 — Typography

**NovaOS Design System — Tipografia**  
**Sprint:** 2 — Identità visiva  
**Stato:** Specifica ufficiale

---

## 1. Scopo

Definire la voce tipografica di NovaOS e Nova Shell: famiglie, scale, pesi, tracking, uso su UI di sistema. La tipografia è il segnale di brand più forte dopo il colore.

---

## 2. Filosofia tipografica

1. **Espressiva ma leggibile** — carattere proprio, mai a scapito dell’UI densa.
2. **Una famiglia UI + una mono** — niente zoo di font.
3. **Niente default anonimi come identità** — Inter, Roboto, Arial, system-ui non sono il volto di Nova.
4. **Gerarchia per peso e size, non per decorazione** — pochi italic, niente outline.
5. **Numeri tabulari** dove servono (panel sistema, monitor risorse).

### Motivazione

Un OS AI-First deve sembrare progettato, non “tema con font di sistema”. La leggibilità a 11–13px è non negoziabile; il display serve a boot, onboarding e momenti di brand.

---

## 3. Famiglie ufficiali

### 3.1 Nova Sans (UI / brand sans)

| Aspetto | Specifica |
|---------|-----------|
| **Ruolo** | Interfaccia, titoli UI, shell, app native |
| **Carattere** | Sans geometrica umanistica, aperture aperte, terminali netti |
| **Personalità** | Precisa, contemporanea, calda quanto basta |
| **Pesi** | Regular 400, Medium 500, Semibold 600, Bold 700 |
| **Italic** | Solo se necessario (citazioni rare); UI preferisce roman |

**Interim open-source (fino a font proprietario):**  
Licenza OFL, metricamente vicina alla direzione: **Outfit** *oppure* **Manrope** come candidato primario di prototipo; decisione finale di file in `branding/fonts/` in fase asset.

> Il nome prodotto resta **Nova Sans**. I file interim sono un ponte, non il brand name.

### 3.2 Nova Display (momenti di marca)

| Aspetto | Specifica |
|---------|-----------|
| **Ruolo** | Boot title, hero installer, empty state di sistema, about |
| **Carattere** | Display sans con leggerissimo contrasto / letterform più distintiva |
| **Pesi** | Medium 500, Semibold 600 |
| **Uso** | Mai per body lunghi; mai sotto 20px |

**Interim:** stesso file di Nova Sans in peso Semibold con tracking dedicato, *oppure* taglio display dedicato quando disponibile.

### 3.3 Nova Mono

| Aspetto | Specifica |
|---------|-----------|
| **Ruolo** | Shell testuale, log, codice, path, hash |
| **Carattere** | Mono leggibile, chiaro a piccole size |
| **Interim** | **IBM Plex Mono** o **JetBrains Mono** (valutare licenza/distribuzione) |

---

## 4. Scale tipografica (type scale)

Unità in **px** a densità di riferimento 1x (100% scaling). Su HiDPI scala proporzionale.

| Token | Size | Line height | Uso tipico |
|-------|------|-------------|------------|
| `type.display.lg` | 40 | 48 | Boot, hero rari |
| `type.display.md` | 32 | 40 | Onboarding step title |
| `type.title.lg` | 24 | 32 | Titoli pagina settings |
| `type.title.md` | 20 | 28 | Sezioni pannello |
| `type.title.sm` | 16 | 24 | Titoli card/lista |
| `type.body.lg` | 15 | 24 | Body comodo |
| `type.body.md` | 13 | 20 | Body UI default Nova Shell |
| `type.body.sm` | 12 | 16 | Secondary, meta |
| `type.caption` | 11 | 14 | Timestamp, hint |
| `type.micro` | 10 | 12 | Solo badge tecnici; evitare |

**Default shell:** `type.body.md` 13/20 — bilancia densità e calma.

---

## 5. Pesi e gerarchia

| Livello | Peso | Tracking |
|---------|------|----------|
| Display | 600 | -0.02em |
| Title | 600 | -0.01em |
| Body | 400 | 0 |
| Label / emphasis | 500 | 0 |
| Button | 500–600 | 0.01em |
| Overline / section mark | 500 | 0.06em (uppercase raro; preferire sentence case) |

**Sentence case** ovunque in italiano UI. Uppercase solo per micro-label di sistema se indispensabile.

---

## 6. Regole di composizione

- Max ~70–80 caratteri per riga nei dialoghi di sistema.
- Titoli non truncati con ellissi se evitabile; preferire wrap a 2 righe.
- Non giustificare il testo UI.
- Link: peso 500 + colore `signal` o `stellar` a seconda del contesto (AI vs azione).
- Non sottolineare titoli; underline solo link focus/hover se necessario all’a11y.

---

## 7. Tipografia in Nova Shell

| Elemento | Token |
|----------|-------|
| Clock / status | `body.sm` Medium, tabular nums |
| Launcher search | `title.sm` / `body.lg` |
| Notifica titolo | `title.sm` Semibold |
| Notifica body | `body.md` |
| Menu contestuale | `body.md` |
| Finestra titlebar | `body.md` Medium |
| NovaAI prompt | `body.lg` |

---

## 8. Localizzazione

- Supporto obbligatorio: latino completo (italiano/inglese prioritari).
- Fallback stack documentato in implementazione: `Nova Sans`, interim, poi Noto Sans per glyph mancanti.
- Mai “scimmiottare” letterspacing tipico Apple o Segoe Windows.

---

## 9. Accessibilità

- Zoom OS fino a 125–150% senza clip critici.
- Dynamic Type-like: rispettare scaling utente.
- Focus ring non sostituito dal solo bold.

---

## 10. Motivazione delle scelte

Si evita Inter/Roboto perché sono la “non-identità” del web 2018–2024.  
Outfit/Manrope (interim) offrono geometricità contemporanea senza sembrare Material o SF Pro.  
La scala parte da 13px body per un desktop produttivo, non da 16px “mobile-first” che rende la shell scarsa.
