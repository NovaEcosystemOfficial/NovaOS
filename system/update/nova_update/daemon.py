"""nova-updated — Update Broker daemon."""

from __future__ import annotations

import argparse
import grp
import logging
import os
import pwd
import signal
import socket
import sys
import threading
from pathlib import Path

from .broker import UpdateBroker
from .config import UpdateConfig
from .protocol import decode_line, encode

log = logging.getLogger("nova-updated")

# systemd passes listening fds starting at SD_LISTEN_FDS_START.
_SD_LISTEN_FDS_START = 3
_NOVA_GROUP = "nova"


def _systemd_listen_sockets() -> list[socket.socket]:
    """Adopt listening sockets from systemd socket activation (LISTEN_FDS)."""
    listen_pid = os.environ.get("LISTEN_PID")
    listen_fds = os.environ.get("LISTEN_FDS")
    if not listen_pid or not listen_fds:
        return []
    try:
        if int(listen_pid) != os.getpid():
            return []
        count = int(listen_fds)
    except ValueError:
        return []
    if count < 1:
        return []

    socks: list[socket.socket] = []
    for offset in range(count):
        fd = _SD_LISTEN_FDS_START + offset
        try:
            os.set_inheritable(fd, False)
        except OSError:
            pass
        socks.append(socket.socket(fileno=fd))

    # Avoid leaking activation env to child processes.
    os.environ.pop("LISTEN_PID", None)
    os.environ.pop("LISTEN_FDS", None)
    os.environ.pop("LISTEN_FDNAMES", None)
    return socks


def _secure_socket_perms(path: Path) -> None:
    """Ensure root:nova 0660 for self-bound sockets (dev / non-activation)."""
    try:
        os.chmod(path, 0o660)
    except OSError as exc:
        log.warning("chmod %s failed: %s", path, exc)
    try:
        gid = grp.getgrnam(_NOVA_GROUP).gr_gid
    except KeyError:
        log.warning("group %r missing — socket stays root-only until sysusers runs", _NOVA_GROUP)
        return
    try:
        uid = pwd.getpwnam("root").pw_uid
    except KeyError:
        uid = 0
    try:
        os.chown(path, uid, gid)
    except OSError as exc:
        log.warning("chown %s root:%s failed: %s", path, _NOVA_GROUP, exc)


class BrokerServer:
    def __init__(self, broker: UpdateBroker, socket_path: Path) -> None:
        self.broker = broker
        self.socket_path = socket_path
        self._stop = threading.Event()
        self._server: socket.socket | None = None
        self._socket_activated = False

    def start(self) -> None:
        inherited = _systemd_listen_sockets()
        if inherited:
            self._socket_activated = True
            server = inherited[0]
            for extra in inherited[1:]:
                try:
                    extra.close()
                except OSError:
                    pass
            log.info(
                "listening via systemd socket activation on %s (backend=%s)",
                self.socket_path,
                self.broker.backend.name,
            )
        else:
            self._socket_activated = False
            self.socket_path.parent.mkdir(parents=True, exist_ok=True)
            if self.socket_path.exists():
                self.socket_path.unlink()
            server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            server.bind(str(self.socket_path))
            _secure_socket_perms(self.socket_path)
            server.listen(8)
            log.info(
                "listening on %s (backend=%s, self-bound root:%s 0660)",
                self.socket_path,
                self.broker.backend.name,
                _NOVA_GROUP,
            )

        server.settimeout(1.0)
        self._server = server
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
            except Exception:
                log.exception("client handler error")
                conn.sendall(encode({"api": "system.update.v1", "error": "internal error"}))

    def stop(self) -> None:
        self._stop.set()
        if self._server is not None:
            try:
                self._server.close()
            except OSError:
                pass
            self._server = None
        # systemd owns the path under socket activation — never unlink it.
        if self._socket_activated:
            return
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
