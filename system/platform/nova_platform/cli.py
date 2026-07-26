"""nova-platformctl — CLI for platform.v1."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .client import PlatformClient
from .config import PlatformConfig


def _print(obj) -> None:
    print(json.dumps(obj, indent=2, ensure_ascii=False, default=str))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Nova Platform control (nova-platformctl)")
    parser.add_argument("--socket", type=Path, default=None)
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("ping", help="ping platform daemon")
    sub.add_parser("health", help="JSON health report (services, sockets, version, errors)")
    sub.add_parser("version", help="platform + OS version")
    sub.add_parser("hostname", help="hostname")
    sub.add_parser("uptime", help="uptime")
    sub.add_parser("session", help="session info")
    sub.add_parser("network", help="network status")
    sub.add_parser("system-info", help="full system info")
    sub.add_parser("services", help="monitored Nova services")
    call = sub.add_parser("call", help="raw method call")
    call.add_argument("method")
    call.add_argument("--params", default="{}", help="JSON object params")

    args = parser.parse_args(argv)
    cfg = PlatformConfig.load()
    sock = args.socket or cfg.socket_path
    client = PlatformClient(sock)

    try:
        if args.cmd == "ping":
            _print(client.call("ping"))
        elif args.cmd == "health":
            _print(client.call("health"))
        elif args.cmd == "version":
            _print(client.call("get-version"))
        elif args.cmd == "hostname":
            _print(client.call("get-hostname"))
        elif args.cmd == "uptime":
            _print(client.call("get-uptime"))
        elif args.cmd == "session":
            _print(client.call("get-session"))
        elif args.cmd == "network":
            _print(client.call("get-network"))
        elif args.cmd == "system-info":
            _print(client.call("get-system-info"))
        elif args.cmd == "services":
            _print(client.call("get-services"))
        elif args.cmd == "call":
            params = json.loads(args.params)
            if not isinstance(params, dict):
                raise SystemExit("--params must be a JSON object")
            _print(client.call(args.method, params))
        else:
            parser.error(f"unknown command {args.cmd}")
            return 2
    except Exception as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
