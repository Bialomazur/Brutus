from src.attacker.terminal.command.Command import Command
from src.attacker.util import HEADER_TEMPLATE


class ShowHeaderCommand(Command):
    def execute(self, window, command: str, context: dict):
        window.Output.clear()
        window.Input.clear()
        version = context.get("version", "")
        ip = context.get("ip", "")
        window.Output.addItem(HEADER_TEMPLATE.format(version=version, ip=ip))

