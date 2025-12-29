from src.attacker.terminal.command.Command import Command


class IPCommand(Command):
    def execute(self, window, command: str, context: dict):
        ip = context.get("ip", "")
        window.Output.addItem(IP_TEMPLATE.format(ip=ip))

