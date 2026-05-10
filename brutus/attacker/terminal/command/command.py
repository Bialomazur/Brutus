from abc import ABC

from brutus.attacker.terminal.command.echo import EchoCommand
from brutus.attacker.terminal.command.ip import IPCommand
from brutus.attacker.terminal.command.quit import QuitCommand
from brutus.attacker.terminal.command.send_at import SendAtCommand
from brutus.attacker.terminal.command.show_clients import ShowClientsCommand
from brutus.attacker.terminal.command.show_header import ShowHeaderCommand

COMMANDS: dict = {
    "ip": IPCommand(),
    "clear": ShowHeaderCommand(),
    "quit": QuitCommand(),
    "exit": QuitCommand(),
    "echo ": EchoCommand(),
    "show_clients": ShowClientsCommand(),
    "show clients": ShowClientsCommand(),
    "sc": ShowClientsCommand(),
    "@": SendAtCommand(),
}


class Command(ABC):
    ERROR_MESSAGE_PREFIX = "[Error]"

    def execute(self, window, command: str, context: dict) -> None:
        raise NotImplementedError

    def error(self, window, message: str) -> None:
        window.Output.addItem(f"{self.ERROR_MESSAGE_PREFIX} {message}")

    def __str__(self) -> str:
        return self.__class__.__name__

    def __repr__(self) -> str:
        return f"<Command: {self.__class__.__name__}>"


def dispatch(command_str: str, window, context: dict) -> bool:
    """Execute the matching command; return True if handled."""
    if "@" in command_str:
        handler = COMMANDS.get("@")
        if handler:
            handler.execute(window, command_str, context)
            return True

    for key, handler in COMMANDS.items():
        if key.endswith(" ") and command_str.startswith(key):
            handler.execute(window, command_str, context)
            return True

    handler = COMMANDS.get(command_str)
    if handler:
        handler.execute(window, command_str, context)
        return True

    return False
