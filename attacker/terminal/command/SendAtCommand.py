from attacker.terminal.command.Command import Command
from attacker.util import *


class SendAtCommand(Command):
    """Expect pattern '<id>@<payload>' and send payload to that connection."""
    def execute(self, window, command: str, context: dict):
        connections = context.get("connections", {})
        try:
            receiver_id = int(command.split("@")[0])
            payload = command.split("@", 1)[1]
            receiver = connections[receiver_id]
            receiver.send(payload.encode("utf-8"))
            window.Input.clear()
        except Exception:
            window.Output.addItem(ERROR_CLIENT_NOT_FOUND)

