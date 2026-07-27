"""TopBarManager — auto-hide / edge reveal / maximized awareness.

Modular controller so notifications, Ryuk, global search and quick controls
can hook into show/hide later without rewriting the Horizon Bar UI.
"""

from __future__ import annotations

from typing import Callable

import gi

gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
from gi.repository import Gdk, GLib, Gtk  # noqa: E402

from .prefs import TopBarMode, load_mode, save_mode

SHOW_MS = 180
HIDE_DELAY_MS = 500
FRAME_MS = 16
SENSOR_HEIGHT = 3
EDGE_PX = 2


def _try_has_maximized() -> bool:
    """Best-effort: any maximized window on the active workspace (Wnck)."""
    try:
        gi.require_version("Wnck", "3.0")
        from gi.repository import Wnck  # type: ignore
    except (ValueError, ImportError):
        return False
    try:
        screen = Wnck.Screen.get_default()
        if screen is None:
            return False
        screen.force_update()
        for win in screen.get_windows() or []:
            if win.is_skip_tasklist() or win.is_skip_pager():
                continue
            if win.get_window_type() != Wnck.WindowType.NORMAL:
                continue
            if win.is_maximized():
                return True
        return False
    except Exception:  # noqa: BLE001
        return False


class TopBarManager:
    """Owns visibility policy and slide animation for the top bar window."""

    def __init__(
        self,
        bar: Gtk.Window,
        *,
        bar_height: int,
        on_mode_changed: Callable[[TopBarMode], None] | None = None,
    ) -> None:
        self._bar = bar
        self._bar_height = max(bar_height, 24)
        self._on_mode_changed = on_mode_changed
        self._mode = load_mode()
        self._visible = True
        self._animating = False
        self._anim_id = 0
        self._hide_id = 0
        self._poll_id = 0
        self._pointer_on_bar = False
        self._menu_open = False
        self._progress = 0.0 if self._mode == TopBarMode.AUTO_HIDE else 1.0  # 0=hidden
        self._geo = self._monitor_geo()

        # Hot-edge sensor (always present; only interactive when bar hidden)
        self._sensor = Gtk.Window(type=Gtk.WindowType.TOPLEVEL)
        self._sensor.set_decorated(False)
        self._sensor.set_skip_taskbar_hint(True)
        self._sensor.set_skip_pager_hint(True)
        self._sensor.set_keep_above(True)
        self._sensor.set_accept_focus(False)
        self._sensor.set_type_hint(Gdk.WindowTypeHint.DOCK)
        self._sensor.set_name("nova-topbar-sensor")
        self._sensor.set_opacity(0.01)
        sensor_box = Gtk.EventBox()
        sensor_box.set_size_request(-1, SENSOR_HEIGHT)
        sensor_box.set_visible_window(True)
        self._sensor.add(sensor_box)
        sensor_box.connect("enter-notify-event", self._on_sensor_enter)
        self._sensor.connect("enter-notify-event", self._on_sensor_enter)

        self._bar.add_events(
            Gdk.EventMask.ENTER_NOTIFY_MASK
            | Gdk.EventMask.LEAVE_NOTIFY_MASK
            | Gdk.EventMask.POINTER_MOTION_MASK
        )
        self._bar.connect("enter-notify-event", self._on_bar_enter)
        self._bar.connect("leave-notify-event", self._on_bar_leave)

        self._apply_window_hints()
        self._place_windows(immediate=True)
        self._sensor.show_all()
        self._poll_id = GLib.timeout_add(250, self._poll)
        self.recompute(force=True)

    @property
    def mode(self) -> TopBarMode:
        return self._mode

    @property
    def is_shown(self) -> bool:
        return self._progress > 0.85

    def set_mode(self, mode: TopBarMode) -> None:
        if mode == self._mode:
            return
        self._mode = mode
        save_mode(mode)
        self._apply_window_hints()
        if self._on_mode_changed:
            self._on_mode_changed(mode)
        self.recompute(force=True)

    def notify_menu_open(self) -> None:
        """Menus / launcher / settings force the bar visible."""
        self._menu_open = True
        self._cancel_hide()
        self._animate_to(1.0)

    def notify_menu_close(self) -> None:
        self._menu_open = False
        self.recompute()

    def request_show(self) -> None:
        self._cancel_hide()
        self._animate_to(1.0)

    def request_hide(self) -> None:
        if self._menu_open or self._mode == TopBarMode.ALWAYS_VISIBLE:
            return
        self._animate_to(0.0)

    def destroy(self) -> None:
        if self._poll_id:
            GLib.source_remove(self._poll_id)
            self._poll_id = 0
        self._cancel_hide()
        self._cancel_anim()
        try:
            self._sensor.destroy()
        except Exception:  # noqa: BLE001
            pass

    def _apply_window_hints(self) -> None:
        # Never reserve struts that shrink the work area permanently while
        # auto-hiding — that would fight maximized windows.
        if self._mode == TopBarMode.ALWAYS_VISIBLE:
            self._bar.set_type_hint(Gdk.WindowTypeHint.DOCK)
        else:
            self._bar.set_type_hint(Gdk.WindowTypeHint.UTILITY)
        self._bar.set_keep_above(True)

    def _monitor_geo(self):
        screen = self._bar.get_screen()
        monitor = screen.get_primary_monitor()
        return screen.get_monitor_geometry(monitor)

    def _place_windows(self, *, immediate: bool = False) -> None:
        self._geo = self._monitor_geo()
        geo = self._geo
        self._bar.resize(geo.width, self._bar_height)
        self._sensor.resize(geo.width, SENSOR_HEIGHT)
        self._sensor.move(geo.x, geo.y)
        if immediate:
            y = self._y_for_progress(self._progress)
            self._bar.move(geo.x, y)

    def _y_for_progress(self, progress: float) -> int:
        # progress 0 → fully above screen; 1 → flush with top
        hidden_y = self._geo.y - self._bar_height + EDGE_PX
        shown_y = self._geo.y
        return int(hidden_y + (shown_y - hidden_y) * max(0.0, min(1.0, progress)))

    def _on_sensor_enter(self, *_a) -> bool:
        if self._mode == TopBarMode.ALWAYS_VISIBLE:
            return False
        self.request_show()
        return False

    def _on_bar_enter(self, _w, event) -> bool:
        if event.detail == Gdk.NotifyType.INFERIOR:
            return False
        self._pointer_on_bar = True
        self._cancel_hide()
        if self._mode != TopBarMode.ALWAYS_VISIBLE:
            self.request_show()
        return False

    def _on_bar_leave(self, _w, event) -> bool:
        if event.detail == Gdk.NotifyType.INFERIOR:
            return False
        self._pointer_on_bar = False
        self._schedule_hide()
        return False

    def _schedule_hide(self) -> None:
        self._cancel_hide()
        if self._menu_open or self._mode == TopBarMode.ALWAYS_VISIBLE:
            return
        self._hide_id = GLib.timeout_add(HIDE_DELAY_MS, self._hide_timeout)

    def _hide_timeout(self) -> bool:
        self._hide_id = 0
        if self._pointer_on_bar or self._menu_open:
            return False
        if self._should_stay_visible():
            return False
        self._animate_to(0.0)
        return False

    def _cancel_hide(self) -> None:
        if self._hide_id:
            GLib.source_remove(self._hide_id)
            self._hide_id = 0

    def _cancel_anim(self) -> None:
        if self._anim_id:
            GLib.source_remove(self._anim_id)
            self._anim_id = 0
        self._animating = False

    def _desired_progress(self) -> float:
        if self._menu_open or self._pointer_on_bar:
            return 1.0
        if self._mode == TopBarMode.ALWAYS_VISIBLE:
            return 1.0
        if self._mode == TopBarMode.HIDE_MAXIMIZED:
            return 0.0 if _try_has_maximized() else 1.0
        # AUTO_HIDE
        return 0.0

    def _should_stay_visible(self) -> bool:
        return self._desired_progress() >= 1.0

    def recompute(self, *, force: bool = False) -> None:
        self._place_windows(immediate=False)
        want = self._desired_progress()
        if force:
            self._cancel_anim()
            self._progress = want
            self._bar.move(self._geo.x, self._y_for_progress(self._progress))
            self._bar.set_opacity(0.0 if want < 0.01 else 1.0)
            self._update_sensor_visibility()
            return
        self._animate_to(want)

    def _animate_to(self, target: float) -> None:
        target = max(0.0, min(1.0, target))
        self._anim_target = target
        if abs(target - self._progress) < 0.01 and not self._animating:
            self._progress = target
            self._bar.move(self._geo.x, self._y_for_progress(self._progress))
            self._bar.set_opacity(0.0 if target < 0.01 else 1.0)
            self._update_sensor_visibility()
            return
        if self._animating:
            return
        self._animating = True
        self._anim_id = GLib.timeout_add(FRAME_MS, self._anim_frame)

    def _anim_frame(self) -> bool:
        target = getattr(self, "_anim_target", self._progress)
        remaining = target - self._progress
        if abs(remaining) < 0.02:
            self._progress = target
            self._bar.move(self._geo.x, self._y_for_progress(self._progress))
            self._animating = False
            self._anim_id = 0
            self._update_sensor_visibility()
            self._bar.set_opacity(0.0 if self._progress < 0.01 else 1.0)
            return False
        # Ease-out ~180ms without flicker
        self._progress += remaining * 0.28
        self._bar.move(self._geo.x, self._y_for_progress(self._progress))
        self._bar.set_opacity(max(0.0, min(1.0, self._progress)))
        return True

    def _update_sensor_visibility(self) -> None:
        # Sensor only needed when bar can hide
        if self._mode == TopBarMode.ALWAYS_VISIBLE or self._progress > 0.5:
            self._sensor.hide()
        else:
            self._sensor.show_all()
            self._sensor.set_keep_above(True)

    def _poll(self) -> bool:
        # Track maximized state + monitor geometry changes
        geo = self._monitor_geo()
        if (
            geo.x != self._geo.x
            or geo.y != self._geo.y
            or geo.width != self._geo.width
            or geo.height != self._geo.height
        ):
            self._place_windows(immediate=True)
        if self._mode == TopBarMode.HIDE_MAXIMIZED and not self._menu_open and not self._pointer_on_bar:
            self.recompute()
        return True
