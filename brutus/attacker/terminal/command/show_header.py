from brutus.attacker.util import HEADER_TEMPLATE


class ShowHeaderCommand:
    def execute(self, window, command: str, context: dict) -> None:
        window.Output.clear()
        window.Input.clear()
        version = context.get("version", "")
        ip = context.get("ip", "")
        window.Output.addItem(HEADER_TEMPLATE.format(version=version, ip=ip))
