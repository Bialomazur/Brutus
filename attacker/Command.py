import os
import time

# String templates and helpers for consistent output formatting
HEADER_TEMPLATE = "{version:<40}{ip}"
CLIENT_HEADER = "ID\t\t       Address\t\t\t   Location\n\n"
CLIENT_ROW_TEMPLATE = "{id}\t\t{addr}\t\t{location}"
IP_TEMPLATE = "Current IP: {ip}"
ERROR_CLIENT_NOT_FOUND = "[ ! ] ERROR Client not found."
TIME_FMT = "%H:%M:%S"


def ts():
    """Return current timestamp string according to TIME_FMT."""
    return time.strftime(TIME_FMT)


class Command:
    """Base command interface: implement execute(window, command, context)."""
    def execute(self, window, command: str, context: dict):
        raise NotImplementedError


class ShowHeaderCommand(Command):
    def execute(self, window, command: str, context: dict):
        window.Output.clear()
        window.Input.clear()
        version = context.get("version", "")
        ip = context.get("ip", "")
        window.Output.addItem(HEADER_TEMPLATE.format(version=version, ip=ip))


class ShowClientsCommand(Command):
    def execute(self, window, command: str, context: dict):
        connections = context.get("connections", {})
        locator = context.get("locator")
        active_connections = "\n".join(
            CLIENT_ROW_TEMPLATE.format(
                id=key,
                addr=connections[key].addr,
                location=locator.get_location(connections[key].addr[0])
            )
            for key in connections.keys()
        ) if connections else ""
        window.Output.addItem(f"{CLIENT_HEADER}{active_connections}")
        window.Input.clear()


class EchoCommand(Command):
    def execute(self, window, command: str, context: dict):
        parts = command.split(" ", 1)
        output_text = parts[1] if len(parts) > 1 else ""
        window.Output.addItem(output_text)
        window.Input.clear()


class QuitCommand(Command):
    def execute(self, window, command: str, context: dict):
        window.hide()


class IPCommand(Command):
    def execute(self, window, command: str, context: dict):
        ip = context.get("ip", "")
        window.Output.addItem(IP_TEMPLATE.format(ip=ip))


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


COMMANDS = {
    "ip": IPCommand(),
    "clear": ShowHeaderCommand(),
    "quit": QuitCommand(),
    "exit": QuitCommand(),
    "echo ": EchoCommand(),            # prefix: "echo <text>"
    "show_clients": ShowClientsCommand(),
    "show clients": ShowClientsCommand(),
    "sc": ShowClientsCommand(),
    "@": SendAtCommand(),              # special handler for "<id>@<cmd>"
}


def dispatch(command_str: str, window, context: dict) -> bool:
    """
    Find the matching command in COMMANDS and execute it.
    Returns True if a command was executed, False otherwise.
    Rules:
     - If '@' in command_str => use the '@' handler if present.
     - Check prefix-keys first (keys ending with a space).
     - Check exact keys.
    """
    if "@" in command_str:
        handler = COMMANDS.get("@")
        if handler:
            handler.execute(window, command_str, context)
            return True

    # Prefix matches first (e.g. "echo ")
    for key, handler in COMMANDS.items():
        if key.endswith(" "):
            if command_str.startswith(key):
                handler.execute(window, command_str, context)
                return True

    # Exact matches
    handler = COMMANDS.get(command_str)
    if handler:
        handler.execute(window, command_str, context)
        return True

    return False
