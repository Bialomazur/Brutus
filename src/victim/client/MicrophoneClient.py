import pyaudio
import time
from TCPClient import TCPClient


FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 4096

HOST = __import__("socket").gethostname()
PORT = 8082


class MicrophoneTCPClient(TCPClient):
    """Microphone client that streams captured audio to a remote server."""

    def __init__(self, host: str, port: int):
        super().__init__(host, port)
        self._pyaudio = None
        self._stream = None

    def _callback(self, in_data, frame_count, time_info, status):
        """PyAudio stream callback: send audio frames to the server."""
        try:
            # send raw audio bytes to remote
            self.sendall(in_data)
            return (None, pyaudio.paContinue)
        except Exception:
            # on error stop streaming
            return (None, pyaudio.paComplete)

    def run(self) -> None:
        """Connect to server, open audio input stream and keep running until stopped."""
        try:
            self.connect()
        except Exception:
            return

        try:
            self._pyaudio = pyaudio.PyAudio()
            self._stream = self._pyaudio.open(format=FORMAT,
                                              channels=CHANNELS,
                                              rate=RATE,
                                              input=True,
                                              frames_per_buffer=CHUNK,
                                              stream_callback=self._callback)
            self._stream.start_stream()

            # keep alive while stream is active and client running
            while self.running and self._stream.is_active():
                time.sleep(0.1)
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
            self.close()