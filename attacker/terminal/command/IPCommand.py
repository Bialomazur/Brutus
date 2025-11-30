from attacker.terminal.command.Command import Command
from attacker.util import *


class IPCommand(Command):
    def execute(self, window, command: str, context: dict):
        ip = context.get("ip", "")
        window.Output.addItem(IP_TEMPLATE.format(ip=ip))

