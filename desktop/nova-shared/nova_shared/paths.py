"""Nova user/config paths — shared by Welcome and Center."""

from __future__ import annotations

from pathlib import Path

# Canonical Nova Identity assets (Sprint 20+)
NOVA_ASSETS = Path("/usr/share/nova/assets")
NOVA_LOGO_PNG = NOVA_ASSETS / "logo" / "novaos.png"
NOVA_LOGO_SVG = NOVA_ASSETS / "logo" / "novaos.svg"
NOVA_PALETTE = NOVA_ASSETS / "palette" / "novaos.json"
NOVA_TOKENS_CSS = NOVA_ASSETS / "fonts" / "novaos-tokens.css"


def nova_config_dir() -> Path:
    return Path.home() / ".config" / "nova"


def ensure_nova_config_dir() -> Path:
    base = nova_config_dir()
    base.mkdir(parents=True, exist_ok=True)
    return base


def welcome_completed_marker() -> Path:
    return nova_config_dir() / "welcome-completed"


def theme_pref_path() -> Path:
    return nova_config_dir() / "theme"


def is_welcome_completed() -> bool:
    return welcome_completed_marker().is_file()


def mark_welcome_completed() -> None:
    path = ensure_nova_config_dir() / "welcome-completed"
    path.write_text("completed\n", encoding="utf-8")


def read_theme_id(default: str = "nova-light") -> str:
    path = theme_pref_path()
    if not path.is_file():
        return default
    value = path.read_text(encoding="utf-8").strip()
    return value or default


def write_theme_id(theme_id: str) -> None:
    ensure_nova_config_dir()
    theme_pref_path().write_text(theme_id.strip() + "\n", encoding="utf-8")


def logo_png() -> Path | None:
    if NOVA_LOGO_PNG.is_file():
        return NOVA_LOGO_PNG
    pix = Path("/usr/share/pixmaps/novaos.png")
    return pix if pix.is_file() else None
