import cv2
import pickle
import struct
import sys
import time
from Client import Client

HOST = __import__("socket").gethostname()
PORT = 8081
RECV_CHUNK = 4096


class WebcamClient(Client):
    """Webcam client that captures frames and streams them to a remote server."""

    def __init__(self, host: str, port: int):
        super().__init__(host, port)
        self.cap = None
        # size of packed length header; use native long size as original code
        self.payload_size = struct.calcsize("L")

    def run(self) -> None:
        """Connect to server and stream serialized frames until stopped or failure."""
        try:
            self.connect()
        except Exception:
            return

        try:
            self.cap = cv2.VideoCapture(0)
            while self.running:
                try:
                    ret, frame = self.cap.read()
                    if not ret:
                        time.sleep(0.05)
                        continue
                    data = pickle.dumps(frame)
                    message_size = struct.pack("L", len(data))
                    # send header + payload
                    self.sendall(message_size + data)
                except Exception:
                    break
        finally:
            try:
                if self.cap:
                    self.cap.release()
            except Exception:
                pass
            self.close()
            # preserve original behavior of exiting after streaming stops
            try:
                sys.exit(0)
            except SystemExit:
                pass


if __name__ == "__main__":
    wc = WebcamClient(HOST, PORT)
    try:
        wc.run()
    except KeyboardInterrupt:
        wc.close()
