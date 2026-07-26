"""Wizard state model."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class WelcomeState:
    hostname: str = ""
    theme_id: str = "nova-light"
    hostname_applied: bool = False
    hostname_error: str = ""
    links_seen: bool = False
