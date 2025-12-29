from src.attacker.terminal.command.Command import Command


class EchoCommand(Command):
    def execute(self, window, command: str, context: dict):
        parts = command.split(" ", 1)
        output_text = parts[1] if len(parts) > 1 else ""
        window.Output.addItem(output_text)
        window.Input.clear()

