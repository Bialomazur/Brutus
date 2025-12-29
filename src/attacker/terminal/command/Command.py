from abc import ABC

from src.attacker.terminal.command.ShowHeaderCommand import ShowHeaderCommand
from src.attacker.terminal.command.ShowClientsCommand import ShowClientsCommand
from src.attacker.terminal.command.EchoCommand import EchoCommand
from src.attacker.terminal.command.QuitCommand import QuitCommand
from src.attacker.terminal.command.IPCommand import IPCommand
from src.attacker.terminal.command.SendAtCommand import SendAtCommand


class Command(ABC):
    """Base command interface: implement execute(window, command, context)."""
    def execute(self, window, command: str, context: dict):
        raise NotImplementedError

    def __str__(self):
        return self.__class__.__name__

    def __repr__(self):
        return f"<Command: {self.__class__.__name__}>"

    def __len__(self):
        return 1


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
        handler = COMMAND.get("@")
        if handler:
            handler.execute(window, command_str, context)
            return True

    # Prefix matches first (e.g. "echo ")
    for key, handler in COMMAND.items():
        if key.endswith(" "):
            if command_str.startswith(key):
                handler.execute(window, command_str, context)
                return True

    # Exact matches
    handler = COMMAND.get(command_str)
    if handler:
        handler.execute(window, command_str, context)
        return True

    return False
