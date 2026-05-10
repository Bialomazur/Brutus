from brutus.attacker.util import IP_TEMPLATE


class IPCommand:
    def execute(self, window, command: str, context: dict) -> None:
        ip = context.get("ip", "")
        window.Output.addItem(IP_TEMPLATE.format(ip=ip))
