"""nova-platformd — Platform Service daemon."""

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
import time
from pathlib import Path

from .config import PlatformConfig
from .logging_setup import get_logger, setup_logging
from .monitor import collect_services
from .protocol import decode_line, encode
from .service import PlatformService

log = logging.getLogger("nova-platformd")
plog = get_logger("platform")

_SD_LISTEN_FDS_START = 3
_NOVA_GROUP = "nova"


def _systemd_listen_sockets() -> list[socket.socket]:
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
    os.environ.pop("LISTEN_PID", None)
    os.environ.pop("LISTEN_FDS", None)
    os.environ.pop("LISTEN_FDNAMES", None)
    return socks


def _secure_socket_perms(path: Path) -> None:
    try:
        os.chmod(path, 0o660)
    except OSError as exc:
        log.warning("chmod %s failed: %s", path, exc)
    try:
        gid = grp.getgrnam(_NOVA_GROUP).gr_gid
    except KeyError:
        log.warning("group %r missing", _NOVA_GROUP)
        return
    try:
        uid = pwd.getpwnam("root").pw_uid
    except KeyError:
        uid = 0
    try:
        os.chown(path, uid, gid)
    except OSError as exc:
        log.warning("chown failed: %s", exc)


class PlatformServer:
    def __init__(self, service: PlatformService, socket_path: Path, monitor_interval: int) -> None:
        self.service = service
        self.socket_path = socket_path
        self.monitor_interval = max(15, monitor_interval)
        self._stop = threading.Event()
        self._server: socket.socket | None = None
        self._socket_activated = False

    def start(self) -> None:
        threading.Thread(target=self._monitor_loop, daemon=True).start()
        inherited = _systemd_listen_sockets()
        if inherited:
            self._socket_activated = True
            server = inherited[0]
            for extra in inherited[1:]:
                try:
                    extra.close()
                except OSError:
                    pass
            plog.info("listening via systemd activation on %s", self.socket_path)
        else:
            self._socket_activated = False
            self.socket_path.parent.mkdir(parents=True, exist_ok=True)
            if self.socket_path.exists():
                self.socket_path.unlink()
            server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            server.bind(str(self.socket_path))
            _secure_socket_perms(self.socket_path)
            server.listen(16)
            plog.info("listening on %s (self-bound root:%s 0660)", self.socket_path, _NOVA_GROUP)

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

    def _monitor_loop(self) -> None:
        while not self._stop.is_set():
            try:
                collect_services()
            except Exception:
                plog.exception("monitor tick failed")
            self._stop.wait(self.monitor_interval)

    def _handle(self, conn: socket.socket) -> None:
        with conn:
            try:
                data = b""
                while not data.endswith(b"\n"):
                    chunk = conn.recv(65536)
                    if not chunk:
                        break
                    data += chunk
                if not data:
                    return
                message = decode_line(data.splitlines()[0])
                reply = self.service.dispatch(message)
                conn.sendall(encode(reply))
            except Exception:
                plog.exception("client handler error")
                conn.sendall(encode({"api": "platform.v1", "error": "internal error"}))

    def stop(self) -> None:
        self._stop.set()
        if self._server is not None:
            try:
                self._server.close()
            except OSError:
                pass
            self._server = None
        if self._socket_activated:
            return
        if self.socket_path.exists():
            try:
                self.socket_path.unlink()
            except OSError:
                pass


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="NovaOS Platform Service (nova-platformd)")
    parser.add_argument("--config", type=Path, default=None)
    parser.add_argument("--socket", type=Path, default=None)
    parser.add_argument("--foreground", action="store_true")
    parser.add_argument("--verbose", "-v", action="store_true")
    args = parser.parse_args(argv)

    config = PlatformConfig.load(args.config)
    if args.socket:
        config.socket_path = args.socket

    setup_logging(config.log_dir, verbose=args.verbose)
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        force=False,
    )

    try:
        config.state_dir.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        log.warning("cannot create state_dir %s: %s", config.state_dir, exc)
    try:
        config.log_dir.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        log.warning("cannot create log_dir %s: %s", config.log_dir, exc)
    service = PlatformService()
    server = PlatformServer(service, config.socket_path, config.monitor_interval_sec)

    def _shutdown(*_a) -> None:
        plog.info("shutting down")
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
    raise SystemExit(main())
