import socket
import threading
from abc import ABC
from typing import Optional


class Service(ABC):
    """Base class for network-backed services that accept one connection and run in a background thread."""

    def __init__(self, host: str, port: int, backlog: int = 1, reuse_addr: bool = True) -> None:
        self.host = host
        self.port = port
        self.backlog = backlog
        self.reuse_addr = reuse_addr

        self.server_socket: Optional[socket.socket] = None
        self.conn: Optional[socket.socket] = None
        self.addr = None

        self._thread: Optional[threading.Thread] = None
        self.running = False

    def setup_socket(self) -> None:
        """Create, bind and listen on the server socket."""
        if self.server_socket:
            return
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if self.reuse_addr:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((self.host, self.port))
        s.listen(self.backlog)
        self.server_socket = s

    def accept_connection(self) -> None:
        """Accept a single connection and store it on self.conn."""
        if not self.server_socket:
            self.setup_socket()
        self.conn, self.addr = self.server_socket.accept()

    def start(self, daemon: bool = True) -> None:
        """Start the service's run loop in a background thread."""
        if self.running:
            return
        self.running = True
        self._thread = threading.Thread(target=self.run_wrapper, daemon=daemon)
        self._thread.start()

    def run_wrapper(self) -> None:
        """Wrapper to ensure proper cleanup after run() finishes or raises."""
        try:
            self.run()
        finally:
            self.stop()

    def run(self) -> None:
        """Override in subclasses with the service's logic."""
        raise NotImplementedError("Subclasses must implement run().")

    def stop(self) -> None:
        """Stop the service and close sockets."""
        self.running = False
        try:
            if self.conn:
                try:
                    self.conn.shutdown(socket.SHUT_RDWR)
                except Exception:
                    pass
                try:
                    self.conn.close()
                except Exception:
                    pass
                self.conn = None
        finally:
            if self.server_socket:
                try:
                    self.server_socket.close()
                except Exception:
                    pass
                self.server_socket = None

