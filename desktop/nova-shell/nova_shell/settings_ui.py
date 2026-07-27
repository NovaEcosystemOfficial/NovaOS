"""Impostazioni Nova — top bar visibility (shell-local, not Center)."""

from __future__ import annotations

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk  # noqa: E402

from .prefs import TopBarMode, mode_label
from .topbar_manager import TopBarManager


class TopBarSettingsDialog(Gtk.Dialog):
    def __init__(self, parent: Gtk.Window | None, manager: TopBarManager) -> None:
        super().__init__(title="Impostazioni Nova — Barra superiore", parent=parent, flags=0)
        self.set_modal(True)
        self.set_default_size(420, 260)
        self._manager = manager
        self.add_button("Chiudi", Gtk.ResponseType.CLOSE)

        box = self.get_content_area()
        box.set_spacing(12)
        box.set_border_width(16)

        title = Gtk.Label(label="Barra superiore Nova", xalign=0)
        title.set_markup("<b>Barra superiore Nova</b>")
        box.pack_start(title, False, False, 0)

        hint = Gtk.Label(
            label="Scegli come la Horizon Bar interagisce con le finestre.",
            xalign=0,
        )
        hint.set_line_wrap(True)
        box.pack_start(hint, False, False, 0)

        self._group: Gtk.RadioButton | None = None
        self._buttons: dict[TopBarMode, Gtk.RadioButton] = {}
        for mode in (
            TopBarMode.ALWAYS_VISIBLE,
            TopBarMode.AUTO_HIDE,
            TopBarMode.HIDE_MAXIMIZED,
        ):
            btn = Gtk.RadioButton.new_with_label_from_widget(
                self._group, mode_label(mode)
            )
            if self._group is None:
                self._group = btn
            if mode == manager.mode:
                btn.set_active(True)
            btn.connect("toggled", self._on_toggle, mode)
            self._buttons[mode] = btn
            box.pack_start(btn, False, False, 0)

        tip = Gtk.Label(
            label="Default: Nascondi automaticamente. Il menu Launcher "
            "riapre sempre la barra.",
            xalign=0,
        )
        tip.set_line_wrap(True)
        box.pack_start(tip, False, False, 0)
        self.show_all()

    def _on_toggle(self, btn: Gtk.RadioButton, mode: TopBarMode) -> None:
        if btn.get_active():
            self._manager.set_mode(mode)
