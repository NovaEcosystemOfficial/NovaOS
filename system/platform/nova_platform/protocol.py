"""JSON Lines protocol for platform.v1 over a Unix socket."""

from __future__ import annotations

import json
from typing import Any

API = "platform.v1"


def encode(obj: dict[str, Any]) -> bytes:
    return (json.dumps(obj, ensure_ascii=False, separators=(",", ":")) + "\n").encode(
        "utf-8"
    )


def decode_line(line: bytes | str) -> dict[str, Any]:
    if isinstance(line, bytes):
        line = line.decode("utf-8")
    data = json.loads(line)
    if not isinstance(data, dict):
        raise ValueError("protocol message must be a JSON object")
    return data


def request(method: str, params: dict[str, Any] | None = None, req_id: int = 1) -> dict[str, Any]:
    return {"api": API, "id": req_id, "method": method, "params": params or {}}


def response(req_id: Any, result: Any = None, error: str | None = None) -> dict[str, Any]:
    msg: dict[str, Any] = {"api": API, "id": req_id}
    if error:
        msg["error"] = error
    else:
        msg["result"] = result
    return msg
