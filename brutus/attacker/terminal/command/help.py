class HelpCommand:
    def execute(self, window, command: str, context: dict) -> None:
        from brutus.attacker.terminal.command.command import COMMANDS

        seen: dict[str, list[str]] = {}
        for key, handler in COMMANDS.items():
            name = type(handler).__name__
            seen.setdefault(name, []).append(key.strip())

        lines = ["Available commands:"]
        for name, keys in sorted(seen.items()):
            lines.append(f"  {', '.join(keys):30} {name}")
        window.Output.addItem("\n".join(lines))
        window.Input.clear()
