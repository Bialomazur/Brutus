import socket
import threading
import time
from typing import Optional


class TCPClient:
    # Default send/recv chunk size
    DEFAULT_CHUNK = 4096

    def __init__(self, host: str, port: int, timeout: Optional[float] = None) -> None:
        # Host/port for the remote server
        self.host = host
        self.port = port
        self.timeout = timeout

        # Socket and running flag
        self.sock: Optional[socket.socket] = None
        self.running = False
        self._lock = threading.Lock()

    def connect(self) -> None:
        """Establish a TCP connection to the configured host/port."""
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
        """Send all bytes; on failure close the socket and stop the client."""
        try:
            if not self.sock:
                raise RuntimeError("socket not connected")
            self.sock.sendall(data)
        except Exception:
            # best-effort close on any send error
            try:
                self.close()
            except Exception:
                pass
            raise

    def close(self) -> None:
        """Shutdown and close the socket and mark the client as stopped."""
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
        """Override in subclasses with the client loop logic."""
        raise NotImplementedError("Subclasses must implement run()")

