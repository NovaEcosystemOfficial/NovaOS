"""Unix-socket client for nova-platformd (nova-platform-python)."""

from __future__ import annotations

import os
import socket
from pathlib import Path
from typing import Any

from .protocol import decode_line, encode, request

DEFAULT_SOCKET = Path("/run/nova/platform.sock")


class PlatformClient:
    def __init__(self, socket_path: Path | None = None) -> None:
        env = os.environ.get("NOVA_PLATFORM_SOCKET")
        self.socket_path = Path(env) if env else Path(socket_path or DEFAULT_SOCKET)
        self._id = 0

    def call(self, method: str, params: dict[str, Any] | None = None) -> Any:
        self._id += 1
        payload = request(method, params, req_id=self._id)
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as sock:
            sock.settimeout(30)
            sock.connect(str(self.socket_path))
            sock.sendall(encode(payload))
            sock.shutdown(socket.SHUT_WR)
            buf = b""
            while not buf.endswith(b"\n"):
                chunk = sock.recv(65536)
                if not chunk:
                    break
                buf += chunk
        if not buf:
            raise RuntimeError("empty response from nova-platformd")
        msg = decode_line(buf.splitlines()[0])
        if msg.get("error"):
            raise RuntimeError(str(msg["error"]))
        return msg.get("result")
