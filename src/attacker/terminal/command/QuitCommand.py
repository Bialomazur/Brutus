from src.attacker.terminal.command.Command import Command


class QuitCommand(Command):
    def execute(self, window, command: str, context: dict):
        window.hide()

