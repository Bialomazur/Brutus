class QuitCommand:
    def execute(self, window, command: str, context: dict) -> None:
        window.hide()
