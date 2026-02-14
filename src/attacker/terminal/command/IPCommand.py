from src.attacker.terminal.command.Command import Command
from src.attacker.util import IP_TEMPLATE


class IPCommand(Command):
    def execute(self, window, command: str, context: dict):
        ip = context.get("ip", "")
        window.Output.addItem(IP_TEMPLATE.format(ip=ip))

