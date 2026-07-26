"""Unix-socket client for nova-updated."""

from __future__ import annotations

import socket
from pathlib import Path
from typing import Any

from .protocol import decode_line, encode, request


class UpdateClient:
    def __init__(self, socket_path: Path) -> None:
        self.socket_path = Path(socket_path)
        self._id = 0

    def call(self, method: str, params: dict[str, Any] | None = None) -> Any:
        self._id += 1
        payload = request(method, params, req_id=self._id)
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as sock:
            sock.settimeout(120)
            sock.connect(str(self.socket_path))
            sock.sendall(encode(payload))
            sock.shutdown(socket.SHUT_WR)
            buf = b""
            while not buf.endswith(b"\n"):
                chunk = sock.recv(4096)
                if not chunk:
                    break
                buf += chunk
        if not buf:
            raise RuntimeError("empty response from nova-updated")
        msg = decode_line(buf.splitlines()[0])
        if msg.get("error"):
            raise RuntimeError(str(msg["error"]))
        return msg.get("result")
