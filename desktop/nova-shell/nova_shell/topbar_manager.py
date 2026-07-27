"""TopBarManager — fixed panel with workspace struts (Vision 2.0).

The bar is never an overlay: it reserves the top of the work area via
``_NET_WM_STRUT`` / ``_NET_WM_STRUT_PARTIAL`` so maximized windows and close
buttons stay below the chrome. Edge-reveal / auto-hide are intentionally gone.
"""

from __future__ import annotations

import ctypes
from ctypes import c_char_p, c_int, c_ulong, c_void_p
from typing import Callable

import gi

gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
from gi.repository import Gdk, GLib, Gtk  # noqa: E402

# X11
PropModeReplace = 0
XA_CARDINAL = 6


def _x11() -> ctypes.CDLL | None:
    try:
        lib = ctypes.CDLL("libX11.so.6")
    except OSError:
        return None
    lib.XOpenDisplay.argtypes = [c_char_p]
    lib.XOpenDisplay.restype = c_void_p
    lib.XCloseDisplay.argtypes = [c_void_p]
    lib.XCloseDisplay.restype = c_int
    lib.XInternAtom.argtypes = [c_void_p, c_char_p, c_int]
    lib.XInternAtom.restype = c_ulong
    lib.XChangeProperty.argtypes = [
        c_void_p,
        c_ulong,
        c_ulong,
        c_ulong,
        c_int,
        c_int,
        c_void_p,
        c_int,
    ]
    lib.XChangeProperty.restype = c_int
    lib.XFlush.argtypes = [c_void_p]
    lib.XFlush.restype = c_int
    return lib


class TopBarManager:
    """Positions the top bar and publishes EWMH struts so the WM shrinks workarea."""

    def __init__(
        self,
        bar: Gtk.Window,
        *,
        bar_height: int,
        on_geometry: Callable[[], None] | None = None,
    ) -> None:
        self._bar = bar
        self._bar_height = max(28, int(bar_height))
        self._on_geometry = on_geometry
        self._poll_id = 0
        self._geo = self._monitor_geo()
        self._xlib = _x11()

        self._bar.set_type_hint(Gdk.WindowTypeHint.DOCK)
        self._bar.set_decorated(False)
        self._bar.set_skip_taskbar_hint(True)
        self._bar.set_skip_pager_hint(True)
        self._bar.set_accept_focus(False)
        self._bar.stick()
        # DOCK + strut: participate in workarea; do not float over clients.
        self._bar.set_keep_above(False)

        self._bar.connect("realize", lambda *_: GLib.idle_add(self.apply))
        self._bar.connect("map-event", lambda *_a: self.apply() or False)
        self._bar.connect("configure-event", self._on_configure)

        self.place()
        self._poll_id = GLib.timeout_add(2000, self._poll)

    @property
    def height(self) -> int:
        return self._bar_height

    def place(self) -> None:
        self._geo = self._monitor_geo()
        geo = self._geo
        self._bar.set_size_request(geo.width, self._bar_height)
        self._bar.resize(geo.width, self._bar_height)
        self._bar.move(geo.x, geo.y)
        if self._on_geometry:
            self._on_geometry()

    def apply(self) -> bool:
        """Re-assert geometry + struts (safe to call often)."""
        self.place()
        self._set_struts()
        self.set_blur_behind()
        return False

    def destroy(self) -> None:
        if self._poll_id:
            GLib.source_remove(self._poll_id)
            self._poll_id = 0
        self._clear_struts()

    # --- API compatibility (Vision 2.0: bar never hides) ---

    def notify_menu_open(self) -> None:
        return

    def notify_menu_close(self) -> None:
        return

    def request_show(self) -> None:
        self.apply()

    def request_hide(self) -> None:
        return

    def _monitor_geo(self):
        screen = self._bar.get_screen()
        monitor = screen.get_primary_monitor()
        return screen.get_monitor_geometry(monitor)

    def _on_configure(self, *_a) -> bool:
        geo = self._monitor_geo()
        if self._bar.get_window() is not None:
            x, y = self._bar.get_position()
            if x != geo.x or y != geo.y:
                self._bar.move(geo.x, geo.y)
        return False

    def _poll(self) -> bool:
        geo = self._monitor_geo()
        if (
            geo.x != self._geo.x
            or geo.y != self._geo.y
            or geo.width != self._geo.width
            or geo.height != self._geo.height
        ):
            self.apply()
        else:
            self._set_struts()
        return True

    def _window_xid(self) -> int | None:
        gdk_win = self._bar.get_window()
        if gdk_win is None:
            return None
        try:
            gi.require_version("GdkX11", "3.0")
            from gi.repository import GdkX11  # noqa: WPS433
        except (ValueError, ImportError):
            return None
        if not isinstance(gdk_win, GdkX11.X11Window):
            return None
        return int(gdk_win.get_xid())

    def _set_struts(self) -> None:
        xid = self._window_xid()
        if xid is None or self._xlib is None:
            return
        geo = self._geo
        top = self._bar_height
        strut = (c_ulong * 4)(0, 0, top, 0)
        # left, right, top, bottom, left_start_y, left_end_y, right_start_y, right_end_y,
        # top_start_x, top_end_x, bottom_start_x, bottom_end_x
        partial = (c_ulong * 12)(
            0,
            0,
            top,
            0,
            0,
            0,
            0,
            0,
            geo.x,
            max(geo.x, geo.x + geo.width - 1),
            0,
            0,
        )
        self._xchange(xid, b"_NET_WM_STRUT", strut, 4)
        self._xchange(xid, b"_NET_WM_STRUT_PARTIAL", partial, 12)

    def _clear_struts(self) -> None:
        xid = self._window_xid()
        if xid is None or self._xlib is None:
            return
        self._xchange(xid, b"_NET_WM_STRUT", (c_ulong * 4)(0, 0, 0, 0), 4)
        self._xchange(xid, b"_NET_WM_STRUT_PARTIAL", (c_ulong * 12)(*([0] * 12)), 12)

    def set_blur_behind(self, xid: int | None = None) -> None:
        """Enable KWin blur behind the bar (glassmorphism)."""
        if xid is None:
            xid = self._window_xid()
        if xid is None or self._xlib is None:
            return
        geo = self._geo
        # Region relative to window: x, y, width, height
        region = (c_ulong * 4)(0, 0, max(1, geo.width), self._bar_height)
        self._xchange(xid, b"_KDE_NET_WM_BLUR_BEHIND_REGION", region, 4)

    def _xchange(self, xid: int, name: bytes, data, nelements: int) -> None:
        lib = self._xlib
        assert lib is not None
        dpy = lib.XOpenDisplay(None)
        if not dpy:
            return
        try:
            atom = lib.XInternAtom(dpy, name, 0)
            lib.XChangeProperty(
                dpy,
                c_ulong(xid),
                c_ulong(atom),
                c_ulong(XA_CARDINAL),
                32,
                PropModeReplace,
                ctypes.cast(data, c_void_p),
                nelements,
            )
            lib.XFlush(dpy)
        finally:
            lib.XCloseDisplay(dpy)
