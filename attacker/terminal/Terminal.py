import sys

class TerminalWindow:
    class OutputList:
        def addItem(self, text: str):
            print(text)

        def clear(self):
            try:
                print("\033[H\033[J", end="")
            except Exception:
                print("\n" * 5)

    class InputHelper:
        def clear(self):
            pass

    def __init__(self):
        self.Output = TerminalWindow.OutputList()
        self.Input = TerminalWindow.InputHelper()

    def hide(self):
        print("Exiting...")
        sys.exit(0)

