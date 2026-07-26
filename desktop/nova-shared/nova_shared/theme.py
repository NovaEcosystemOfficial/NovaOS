"""Theme registry — prepared for future Nova Shell themes."""

from __future__ import annotations

from dataclasses import dataclass

from .paths import read_theme_id, write_theme_id


@dataclass(frozen=True)
class ThemeInfo:
    id: str
    label: str
    description: str


# Extensible catalog; Welcome / Center / Shell share the same IDs.
THEMES: tuple[ThemeInfo, ...] = (
    ThemeInfo(
        id="nova-dark",
        label="Nova Dark",
        description="Interfaccia scura, ideale per lunghe sessioni",
    ),
    ThemeInfo(
        id="nova-light",
        label="Nova Light",
        description="Interfaccia chiara, leggibile in ambienti luminosi",
    ),
)


def list_themes() -> list[ThemeInfo]:
    return list(THEMES)


def get_theme(theme_id: str) -> ThemeInfo | None:
    for theme in THEMES:
        if theme.id == theme_id:
            return theme
    return None


def apply_theme_preference(theme_id: str) -> ThemeInfo:
    """Persist theme choice. Plasma/Shell look-and-feel hooks land later."""
    info = get_theme(theme_id) or THEMES[1]
    write_theme_id(info.id)
    return info


def current_theme() -> ThemeInfo:
    return get_theme(read_theme_id()) or THEMES[1]
