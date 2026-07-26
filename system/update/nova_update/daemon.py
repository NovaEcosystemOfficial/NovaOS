"""nova-updated — Update Broker daemon."""

from __future__ import annotations

import argparse
import logging
import os
import signal
import socket
import sys
import threading
from pathlib import Path

from .broker import UpdateBroker
from .config import UpdateConfig
from .protocol import decode_line, encode

log = logging.getLogger("nova-updated")


class BrokerServer:
    def __init__(self, broker: UpdateBroker, socket_path: Path) -> None:
        self.broker = broker
        self.socket_path = socket_path
        self._stop = threading.Event()
        self._server: socket.socket | None = None

    def start(self) -> None:
        self.socket_path.parent.mkdir(parents=True, exist_ok=True)
        if self.socket_path.exists():
            self.socket_path.unlink()
        server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        server.bind(str(self.socket_path))
        try:
            os.chmod(self.socket_path, 0o660)
        except OSError:
            pass
        server.listen(8)
        server.settimeout(1.0)
        self._server = server
        log.info("listening on %s (backend=%s)", self.socket_path, self.broker.backend.name)
        while not self._stop.is_set():
            try:
                conn, _ = server.accept()
            except socket.timeout:
                continue
            except OSError:
                break
            threading.Thread(target=self._handle, args=(conn,), daemon=True).start()

    def _handle(self, conn: socket.socket) -> None:
        with conn:
            try:
                data = b""
                while not data.endswith(b"\n"):
                    chunk = conn.recv(4096)
                    if not chunk:
                        break
                    data += chunk
                if not data:
                    return
                message = decode_line(data.splitlines()[0])
                reply = self.broker.dispatch(message)
                conn.sendall(encode(reply))
            except Exception as exc:
                log.exception("client handler error")
                conn.sendall(encode({"api": "system.update.v1", "error": str(exc)}))

    def stop(self) -> None:
        self._stop.set()
        if self._server is not None:
            try:
                self._server.close()
            except OSError:
                pass
        if self.socket_path.exists():
            try:
                self.socket_path.unlink()
            except OSError:
                pass


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="NovaOS Update Broker (nova-updated)")
    parser.add_argument("--config", type=Path, default=None, help="path to nova-update.conf")
    parser.add_argument(
        "--backend",
        choices=("auto", "dnf", "mock", "localrpm"),
        default=None,
        help="override backend",
    )
    parser.add_argument("--socket", type=Path, default=None, help="override Unix socket path")
    parser.add_argument("--foreground", action="store_true", help="run in foreground (default)")
    parser.add_argument("--verbose", "-v", action="store_true")
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    config = UpdateConfig.load(args.config)
    if args.backend:
        config.backend = args.backend
    if args.socket:
        config.socket_path = args.socket

    broker = UpdateBroker(config)
    server = BrokerServer(broker, config.socket_path)

    def _shutdown(*_args) -> None:
        log.info("shutting down")
        server.stop()

    signal.signal(signal.SIGINT, _shutdown)
    signal.signal(signal.SIGTERM, _shutdown)

    try:
        server.start()
    except Exception:
        server.stop()
        raise
    return 0


if __name__ == "__main__":
    sys.exit(main())
