"""Impostazioni Nova — top bar (Vision 2.0: fixed strut, no hide modes)."""

from __future__ import annotations

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk  # noqa: E402

from .topbar_manager import TopBarManager


class TopBarSettingsDialog(Gtk.Dialog):
    def __init__(self, parent: Gtk.Window | None, manager: TopBarManager) -> None:
        super().__init__(title="Impostazioni Nova — Barra superiore", parent=parent, flags=0)
        self.set_modal(True)
        self.set_default_size(420, 200)
        self._manager = manager
        self.add_button("Chiudi", Gtk.ResponseType.CLOSE)

        box = self.get_content_area()
        box.set_spacing(12)
        box.set_border_width(16)

        title = Gtk.Label(xalign=0)
        title.set_markup("<b>Barra superiore Nova</b>")
        box.pack_start(title, False, False, 0)

        body = Gtk.Label(
            label=(
                "Vision 2.0: la barra è un pannello fisso che riserva lo spazio "
                "in alto (strut). Non è un overlay e non si nasconde al bordo. "
                "Le finestre massimizzate restano sotto la barra; la X di "
                "chiusura resta sempre cliccabile."
            ),
            xalign=0,
        )
        body.set_line_wrap(True)
        box.pack_start(body, False, False, 0)

        tip = Gtk.Label(
            label=f"Altezza riservata: {manager.height}px",
            xalign=0,
        )
        tip.get_style_context().add_class("dim-label")
        box.pack_start(tip, False, False, 0)
        self.show_all()
