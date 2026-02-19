import socket
import os
import threading
import asyncio
import requests
import json

from src.attacker.terminal.command.Command import dispatch as command_dispatch
from src.attacker.terminal.server.Server import Server
from src.attacker.terminal.Terminal import Terminal
from src.attacker.util import VERSION, UNKNOWN_COMMAND_TEMPLATE

""" constants """
CURRENT_FOLDER = os.path.dirname(os.path.realpath(__file__))
HOST = socket.gethostname()
PORT = 8080

""" globals """
ip = ""
connections = {}
window = None


def start_server_in_background(window):
    try:
        # pass the shared connections dict into Server
        server = Server(HOST, PORT, window, connections)
        
        # Create a new event loop for the background thread
        def run_server():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(server.start())
                print("Server running!")
                loop.run_until_complete(server.serve_forever())
            except Exception as e:
                print(f"Server error: {e}")
            finally:
                loop.close()
        
        t = threading.Thread(target=run_server, daemon=True)
        t.start()
    except Exception as e:
        print(f"Failed to start server: {e}")

def main():
    global ip, window
    window = Terminal()

    # try to obtain public IP; non-fatal
    try:
        r = requests.get('https://api.ipify.org?format=json', timeout=15)
        content = r.content.decode("Cp1252")
        content = json.loads(content)
        ip = content.get("ip", "")
    except Exception:
        print("Could not retrieve public IP!")

    # Prepare context for command handlers and render header using Command objects
    context = {
        "connections": connections,
        "ip": ip,
        "version": VERSION,
    }

    # Use the OO command subsystem to show the header
    command_dispatch("clear", window, context)

    # Start server in background
    start_server_in_background(window)

    # Main terminal input loop (runs in main thread)
    try:
        while True:
            try:
                command = input("> ").strip()
            except (EOFError, KeyboardInterrupt):
                print("")  # newline for cleanliness
                break

            if not command:
                continue

            # update context each loop in case connections/ip change
            context.update({
                "connections": connections,
                "ip": ip,
            })

            handled = command_dispatch(command, window, context)
            if not handled:
                window.Output.addItem(UNKNOWN_COMMAND_TEMPLATE.format(command=command))
    finally:
        print("Shutting down.")
        try:
            for c in list(connections.values()):
                try:
                    c.close()
                except Exception:
                    pass
        except Exception:
            pass


if __name__ == "__main__":
    main()
