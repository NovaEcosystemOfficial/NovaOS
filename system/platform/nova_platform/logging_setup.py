"""Logging setup for /var/log/nova/{platform,update,services}.log."""

from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


def setup_logging(log_dir: Path, *, verbose: bool = False) -> None:
    log_dir.mkdir(parents=True, exist_ok=True)
    level = logging.DEBUG if verbose else logging.INFO
    fmt = logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")

    root = logging.getLogger()
    root.setLevel(level)
    # Avoid duplicate handlers on reload
    if not any(isinstance(h, RotatingFileHandler) for h in root.handlers):
        sh = logging.StreamHandler()
        sh.setFormatter(fmt)
        root.addHandler(sh)

    for name, filename in (
        ("nova.platform", "platform.log"),
        ("nova.update", "update.log"),
        ("nova.services", "services.log"),
    ):
        logger = logging.getLogger(name)
        logger.setLevel(level)
        logger.propagate = False
        if any(isinstance(h, RotatingFileHandler) for h in logger.handlers):
            continue
        fh = RotatingFileHandler(
            log_dir / filename,
            maxBytes=2_000_000,
            backupCount=3,
            encoding="utf-8",
        )
        fh.setFormatter(fmt)
        logger.addHandler(fh)
        # Also mirror to stderr for journald
        if not any(isinstance(h, logging.StreamHandler) for h in logger.handlers):
            eh = logging.StreamHandler()
            eh.setFormatter(fmt)
            logger.addHandler(eh)


def get_logger(channel: str) -> logging.Logger:
    """channel: platform | update | services"""
    return logging.getLogger(f"nova.{channel}")
