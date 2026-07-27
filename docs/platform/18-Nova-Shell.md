# Nova Shell Foundation

**Top Bar 3.0** · Pacchetto `nova-shell` 0.3.0 · API `shell.v1`

## 1. Top Bar 3.0

| Regola | Comportamento |
|--------|----------------|
| Visivo | Glassmorphism leggero (RGBA + blur KWin), ~36px, wordmark Nova |
| Strut | `_NET_WM_STRUT` / `_NET_WM_STRUT_PARTIAL` — ridimensiona il workspace |
| No overlay | Mai sopra le finestre |
| No Plasma panel | `nova-hide-plasma-panels` + layout LfF senza `defaultPanel` |
| Layout | Logo+Nova · centro libero · Notifiche · Rete · Audio · Batteria* · Ora |
| Control Center | Icone a destra → hook `open_control_center(section=…)` (flyout stub) |

\*Batteria solo se presente. CPU/RAM/Disco **non** sono in barra.

## 2. Architettura

```text
nova-shell (GTK3)
   ├─► Top Bar 3.0 (glass DOCK + strut + blur)
   ├─► plasma_panels.hide → qdbus plasmashell evaluateScript
   ├─► control_center.open_* → flyout (futuro Control Center)
   ├─► platform.v1
   └─► shell.search.v1 / shell.dock.v1
```

## 3. CLI

```bash
nova-shell
nova-shell --json
nova-shell --hide-plasma-panels
nova-hide-plasma-panels
```

## 4. Distribuzione

Solo **Nova Update** stable. Dopo `apply`: logout/login.
