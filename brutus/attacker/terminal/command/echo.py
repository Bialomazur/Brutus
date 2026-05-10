class EchoCommand:
    def execute(self, window, command: str, context: dict) -> None:
        parts = command.split(" ", 1)
        window.Output.addItem(parts[1] if len(parts) > 1 else "")
        window.Input.clear()
