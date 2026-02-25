from src.attacker.terminal.command.Command import Command


class HelpCommand(Command):
    def execute(self, window, command: str, context: dict):
        from src.attacker.terminal.command.Command import COMMANDS
        
        # Filter out hidden or alias commands if necessary, 
        # but for now, let's just show all distinct handlers.
        unique_handlers = {}
        for key, handler in COMMANDS.items():
            handler_name = str(handler)
            if handler_name not in unique_handlers:
                unique_handlers[handler_name] = []
            unique_handlers[handler_name].append(key)

        help_text = "Available commands:\n"
        for handler_name, keys in sorted(unique_handlers.items()):
            # Join keys and present them
            help_text += f" - {', '.join(keys)} -> {handler_name}\n"
        
        window.Output.addItem(help_text)
        window.Input.clear()
