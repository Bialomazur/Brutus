from attacker.util import *
from attacker.terminal.command.Command import Command


class ShowClientsCommand(Command):
    def execute(self, window, command: str, context: dict):
        connections = context.get("connections", {})
        locator = context.get("locator")
        # If no clients connected, print a friendly message instead of an empty table
        if not connections:
            window.Output.addItem(NO_CLIENTS_TEMPLATE)
            window.Input.clear()
            return

        active_connections = "\n".join(
            CLIENT_ROW_TEMPLATE.format(
                id=key,
                addr=connections[key].addr,
                location=locator.get_location(connections[key].addr[0])
            )
            for key in connections.keys()
        )
        window.Output.addItem(f"{CLIENT_HEADER}{active_connections}")
        window.Input.clear()

