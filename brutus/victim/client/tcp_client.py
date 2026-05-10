import socket
import threading
from typing import Optional


class TCPClient:
    DEFAULT_CHUNK = 4096

    def __init__(self, host: str, port: int, timeout: Optional[float] = None) -> None:
        self.host = host
        self.port = port
        self.timeout = timeout
        self.sock: Optional[socket.socket] = None
        self.running = False
        self._lock = threading.Lock()

    def connect(self) -> None:
        with self._lock:
            if self.sock:
                return
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            if self.timeout is not None:
                s.settimeout(self.timeout)
            s.connect((self.host, self.port))
            self.sock = s
            self.running = True

    def sendall(self, data: bytes) -> None:
        try:
            if not self.sock:
                raise RuntimeError("not connected")
            self.sock.sendall(data)
        except Exception:
            try:
                self.close()
            except Exception:
                pass
            raise

    def close(self) -> None:
        with self._lock:
            self.running = False
            if self.sock:
                try:
                    self.sock.shutdown(socket.SHUT_RDWR)
                except Exception:
                    pass
                try:
                    self.sock.close()
                except Exception:
                    pass
                self.sock = None

    def run(self) -> None:
        raise NotImplementedError
