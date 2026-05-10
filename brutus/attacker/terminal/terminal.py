import sys


class Terminal:
    class OutputList:
        def addItem(self, text: str) -> None:
            print(text)

        def clear(self) -> None:
            try:
                print("\033[H\033[J", end="", flush=True)
            except Exception:
                print("\n" * 5)

    class InputHelper:
        def clear(self) -> None:
            pass

    def __init__(self) -> None:
        self.Output = Terminal.OutputList()
        self.Input = Terminal.InputHelper()

    def hide(self) -> None:
        print("Exiting...")
        sys.exit(0)
