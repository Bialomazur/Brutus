from attacker.service.Service import Service
import pyaudio
import threading
from pynput.keyboard import Key, Listener

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 4096


class AudioService(Service):
    """Service that accepts a single TCP connection and plays incoming audio to the local output device."""

    def __init__(self, host: str, port: int):
        super().__init__(host, port)
        self._pyaudio = None
        self._stream = None
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
        """Accept connection and stream audio data until stopped."""
        try:
            self.setup_socket()
            self.accept_connection()
            if not self.conn:
                return

            self._pyaudio = pyaudio.PyAudio()
            self._stream = self._pyaudio.open(format=FORMAT,
                                              channels=CHANNELS,
                                              rate=RATE,
                                              output=True,
                                              frames_per_buffer=CHUNK)

            # start keyboard listener in background so esc can stop streaming
            self._start_keyboard_listener()

            while self.running:
                try:
                    data = self.conn.recv(CHUNK)
                    if not data:
                        break
                    self._stream.write(data)
                except Exception:
                    break
        finally:
            # cleanup resources
            try:
                if self._stream:
                    self._stream.stop_stream()
                    self._stream.close()
            except Exception:
                pass
            try:
                if self._pyaudio:
                    self._pyaudio.terminate()
            except Exception:
                pass
            try:
                if self.conn:
                    self.conn.close()
            except Exception:
                pass
            self.conn = None
