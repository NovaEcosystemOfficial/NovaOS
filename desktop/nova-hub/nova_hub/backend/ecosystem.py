"""Ecosystem app catalog (placeholders until apps ship)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class EcosystemApp:
    id: str
    name: str
    tagline: str
    command: str | None  # None = coming soon
    available: bool


ECOSYSTEM: tuple[EcosystemApp, ...] = (
    EcosystemApp("novadocs", "NovaDocs", "Documenti e knowledge base", None, False),
    EcosystemApp("novapromo", "NovaPromo", "Campagne e promozione", None, False),
    EcosystemApp("novastudio", "NovaStudio", "Creazione contenuti", None, False),
    EcosystemApp("novabeauty", "NovaBeauty", "Design e brand kit", None, False),
    EcosystemApp("novacloud", "NovaCloud", "Sync e storage Nova", None, False),
    EcosystemApp("novasky", "NovaSky", "Connettività e edge", None, False),
    EcosystemApp("novaos", "NovaOS", "Sistema e identità", "nova-center", True),
    EcosystemApp("ryuk", "Ryuk", "Assistente di sistema", None, False),
)


def catalog() -> list[dict]:
    return [
        {
            "id": a.id,
            "name": a.name,
            "tagline": a.tagline,
            "command": a.command,
            "available": a.available,
            "status": "disponibile" if a.available else "prossimamente",
        }
        for a in ECOSYSTEM
    ]
