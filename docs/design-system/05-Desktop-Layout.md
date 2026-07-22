# 05 — Desktop Layout

**NovaOS Design System — Nova Shell**  
**Sprint:** 2 — Identità visiva  
**Stato:** Specifica di layout ufficiale

---

## 1. Scopo

Definire l’architettura spaziale di **Nova Shell**, il desktop ufficiale di NovaOS e cuore dell’esperienza utente. Questo documento fissa regioni, componenti e comportamenti di layout — non codice e non mockup bitmap.

---

## 2. Dichiarazione

> **Nova Shell** è l’ambiente desktop di NovaOS. Non si presenta come Plasma, non imita Windows, non imita macOS. È un prodotto con geografia propria.

Upstream tecnico (es. stack di sessione) può esistere sotto il cofano; **l’utente vede solo Nova Shell**.

---

## 3. Filosofia dello spazio

1. **Orizzonte, non molo** — la UI di sistema vive su un asse orizzontale basso *asimmetrico*, non su un dock centrato.
2. **Vuoto produttivo** — il desktop è superficie di lavoro, non bacheca di widget.
3. **Tre profondità** — wallpaper → finestre → chrome flottante (glass).
4. **AI a portata, non al centro scenico permanente** — invocabile, non un pannello fisso invasivo.
5. **Una composizione** — ogni regione ha un mestiere.

---

## 4. Geometria globale

### 4.1 Unità e spacing

| Token | Valore | Uso |
|-------|--------|-----|
| `space.1` | 4px | micro |
| `space.2` | 8px | stretto |
| `space.3` | 12px | default interno |
| `space.4` | 16px | padding pannello |
| `space.5` | 24px | sezioni |
| `space.6` | 32px | respiro maggiore |
| `space.7` | 48px | hero / onboarding |

### 4.2 Raggi

| Token | Valore | Uso |
|-------|--------|-----|
| `radius.sm` | 6px | chip, input piccoli |
| `radius.md` | 10px | bottoni, menu |
| `radius.lg` | 14px | pannelli glass, finestre |
| `radius.xl` | 20px | launcher, control center |
| `radius.sheet` | 16px | notification center |

**Motivazione:** raggi medi distintivi; evitano lo squircle Apple e il quasi-quadrato classico Win32, senza pill `9999px`.

### 4.3 Margini sicuri desktop

- Distanza chrome flottante dai bordi schermo: **12px** (edge inset).
- Gap tra Horizon Bar e finestre massimizzate: gestito da strut/reserved area **48px** (altezza bar) + inset.

---

## 5. Regioni di Nova Shell

```text
┌─────────────────────────────────────────────────────────────┐
│  Stage (wallpaper + finestre)                               │
│                                                             │
│                                                             │
│                                                             │
│  [Notification Center / Control / AI — overlay on demand]   │
│                                                             │
│  ┌─────────────── Horizon Bar (floating) ───────────────┐   │
│  │ Core │ Pins ……… Focus ……… Status │ Pulse │ Tray │Clock│   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### 5.1 Stage

- Wallpaper di sistema a piena area.
- Icone desktop: **disabilitate di default** (attivabili); preferenza file manager / launcher.
- Widget sparsi: **non previsti** nella v1 di prodotto (anti-KDE “plasmoid festival”).

### 5.2 Horizon Bar — chrome primario

Barra flottante inferiore, **non a tutta larghezza sticky come taskbar Windows**, ma **isola orizzontale** con larghezza massima e margini laterali.

| Parametro | Valore |
|-----------|--------|
| Altezza | 48px |
| Larghezza | `min(1120px, 100vw - 24px)` su desktop; su ultrawide non stirata edge-to-edge |
| Posizione | Bottom center ottico, ma contenuto **asimmetrico** (sinistra pesante su brand/app, destra su sistema) |
| Materiale | Nova Glass (`blur.glass`, bordo `glass.border`) |
| Ombra | Y+8 blur 24 opacità 18% — **una** ombra |

**Perché non taskbar Windows:** niente strip full-bleed attaccata al bordo con Start+cerca+task view cloni.  
**Perché non dock macOS:** niente icon stack centrato con magnify; niente solo-app senza status.

#### Segmenti Horizon Bar (da sinistra a destra)

1. **Nova Core** — bottone launcher (mark nucleo+anello).  
2. **Pins** — app fissate (icon.sm/md), max consigliato 7.  
3. **Focus Strip** — finestre aperte come **capsule testo+icona** (non solo icone tipo Win11, non solo mirror dock). Mostra titolo truncato dell’app in focus group.  
4. **Spacer flessibile**.  
5. **Pulse** — entry NovaAI (dot `signal` quando attivo).  
6. **Tray** — indicatori sistema compatti.  
7. **Quick** — rete/audio/power in forma ridotta (aprono Control Center).  
8. **Clock** — orario; click apre calendario/agenda sobria.

### 5.3 Nova Core → Launcher

Nome UI: **Launcher** (non Start, non Activities, non Spotlight clone).

| Parametro | Specifica |
|-----------|-----------|
| Forma | Pannello glass `radius.xl`, larghezza 640–720px, altezza max ~70vh |
| Apertura | Origine dal Core; animazione scale+fade (vedi `06-Animations.md`) |
| Struttura | Search top → **Suggestions** (AI-assisted, opzionali) → **Apps grid** → **Places** |
| Grid | 6 colonne, icon 48 + label `caption`/`body.sm` |
| Search | Sempre focus all’apertura; shortcut sistema dedicato |

Niente “tile live” tipo Windows. Niente categorie a colonna stile menu classico come default.

### 5.4 Notification Center

| Parametro | Specifica |
|-----------|-----------|
| Edge | **Destra**, sheet verticale |
| Larghezza | 380px |
| Materiale | Glass strong |
| Sezioni | In alto *NovaAI brief* (compact, dismissible) → lista notifiche → clear |

Notifiche come card leggere (`radius.md`), stripe sinistra semantica (AI=`signal`, danger=`danger`, default=`steel`).

**Non** un Action Center Windows clone (toggles misti + notifiche nella stessa pila confusionaria): i toggle vivono nel Control Center.

### 5.5 Control Center

| Parametro | Specifica |
|-----------|-----------|
| Apertura | Da Quick / shortcut |
| Forma | Pannello floating sopra Horizon Bar a destra, 360px |
| Contenuto | Rete, Audio, Luminosità, Bluetooth, Modalità (Focus/Silent), Night, Energia, tile *NovaAI mode* (Locale/Cloud/Off) |
| Layout | Griglia 2 colonne di tile `radius.lg`, slider full-width sotto |

### 5.6 NovaAI Surface

Tre livelli (progressivi):

1. **Pulse compact** in bar (stato).  
2. **Inline suggest** in launcher/search.  
3. **NovaAI Stage** — pannello laterale sinistro 420px *on demand* (non sempre aperto): chat/context di sistema, azioni con conferma.

Mai un assistente bubble stile consumer chat app al centro del desktop come UI permanente.

### 5.7 Menu contestuali

- `radius.md`, padding `space.2`, item height 32px.
- Separatori 1px `glass.border`.
- Icone a sinistra opzionali; shortcut a destra in `muted`.
- Niente ombre multiple; fade+slide 2–4px.

### 5.8 Finestre

| Elemento | Specifica Nova |
|----------|----------------|
| Titlebar height | 40px |
| Controls posizione | **Destra** (close/maximize/minimize) — geometria circolare 12px hit 28px |
| Controls stile | Monochrome → hover tinge; close hover `danger` soft — **non** traffic lights RGB |
| Bound radius | `radius.lg` su floating; square quando tiled/maximized secondo policy |
| Focus | Bordo 1px `stellar` a 35% opacità **o** titlebar text weight up — niente glow 20px |
| Shadow | Una, Y+12 blur 32 opacità 22% inactive più bassa |

**Motivazione anti-macOS:** niente semafori a sinistra.  
**Motivazione anti-Windows:** niente titlebar generica “grigia flat” senza carattere; capsule Focus Strip diverse dalle thumbnail Win.

### 5.9 Tiling e layout finestre

- Snap zone con overlay glass leggero e label.
- Corner snap supportato.
- Nessuna animazione elastica esagerata.

---

## 6. Densità e display

| Modo | Note |
|------|------|
| Comfort (default) | Valori di questo doc |
| Compact | Altezze -4px, body 12px — power user |
| Ultrawide | Horizon Bar non supera 1120px; resta centrata |

Multi-monitor: Horizon Bar sul monitor primario di default; opzione “bar su tutti”.

---

## 7. Temi chiaro/scuro sul layout

Il layout **non cambia geografia** tra temi: cambiano solo token colore/materiale (`02-Color-Palette.md`). La riconoscibilità di Nova Shell è strutturale.

---

## 8. Cosa Nova Shell non è (checklist anti-clone)

| Pattern vietato | Origine tipica |
|-----------------|----------------|
| Taskbar full-width attaccata al bordo con Start | Windows |
| Dock centrato con magnification | macOS |
| Pannello default + widget dump | KDE stock |
| Global menu bar top stile Apple | macOS |
| Traffici luci | macOS |
| Search bar forever-on in taskbar | Windows 11 |

---

## 9. Motivazione complessiva

La Horizon Bar a isola + Focus Strip testuale + Core/Pulse separati crea una silhouette unica. L’utente riconosce Nova dalla **geografia**, non solo dal wallpaper. Notification e Control separati rispettano “un compito per superficie”. NovaAI è capacità di sistema a strati, non una app chat incollata.
