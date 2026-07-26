"""nova-updater — CLI for Nova Update Broker."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from .client import UpdateClient
from .config import UpdateConfig


def _client() -> UpdateClient:
    cfg = UpdateConfig.load()
    sock = os.environ.get("NOVA_UPDATE_SOCKET")
    return UpdateClient(Path(sock) if sock else cfg.socket_path)


def _print(data) -> None:
    print(json.dumps(data, indent=2, ensure_ascii=False))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="nova-updater",
        description="NovaOS update client (talks to nova-updated)",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("ping", help="ping the update broker")
    sub.add_parser("status", help="show broker status")
    sub.add_parser("check", help="check for updates")
    sub.add_parser("apply", help="apply pending updates")
    sub.add_parser("progress", help="show progress")
    sub.add_parser("verify", help="verify signature policy against pending updates")
    sub.add_parser("history", help="show update history")
    sub.add_parser("system", help="show NovaOS version and service status")

    ch = sub.add_parser("channel", help="get or set update channel")
    ch_sub = ch.add_subparsers(dest="channel_cmd", required=True)
    ch_sub.add_parser("get", help="show active channel")
    ch_set = ch_sub.add_parser("set", help="set active channel")
    ch_set.add_argument(
        "name",
        choices=("stable", "beta", "developer", "nightly", "dev"),
        help="channel id (dev is an alias of developer)",
    )
    ch_sub.add_parser("list", help="list channels")

    args = parser.parse_args(argv)
    client = _client()

    try:
        if args.cmd == "ping":
            _print(client.call("Ping"))
        elif args.cmd == "status":
            _print(client.call("GetStatus"))
        elif args.cmd == "check":
            _print(client.call("Check"))
        elif args.cmd == "apply":
            _print(client.call("Apply"))
        elif args.cmd == "progress":
            _print(client.call("GetProgress"))
        elif args.cmd == "verify":
            _print(client.call("VerifySignatures"))
        elif args.cmd == "history":
            _print(client.call("GetHistory"))
        elif args.cmd == "system":
            _print(client.call("GetSystemInfo"))
        elif args.cmd == "channel":
            if args.channel_cmd in ("get", "list"):
                _print(client.call("GetChannel"))
            elif args.channel_cmd == "set":
                _print(client.call("SetChannel", {"channel": args.name}))
        else:
            parser.error(f"unknown command {args.cmd}")
            return 2
    except FileNotFoundError:
        print(
            "error: cannot connect to nova-updated "
            f"(socket missing: {_client().socket_path})",
            file=sys.stderr,
        )
        return 1
    except ConnectionRefusedError:
        print("error: nova-updated is not running", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
