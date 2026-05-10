"""asyncio TCP server — accepts victim connections."""

import asyncio
import pathlib

from brutus.attacker.terminal.server.connection import Connection
from brutus.attacker.util import CONNECTION_CONNECT_TEMPLATE, ts


class Server:
    def __init__(
        self,
        host: str,
        port: int,
        window,
        connections: dict,
        save_dir: pathlib.Path,
    ) -> None:
        self.host = host
        self.port = port
        self.window = window
        self.connections = connections
        self.save_dir = save_dir

    async def _handle(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        addr = writer.get_extra_info("peername")
        conn = Connection(reader, writer, addr, self.window, self.connections, self.save_dir)
        self.connections[conn.id] = conn
        self.window.Output.addItem(CONNECTION_CONNECT_TEMPLATE.format(time=ts(), addr=addr))
        await conn.handle()

    async def serve(self) -> None:
        srv = await asyncio.start_server(self._handle, self.host, self.port)
        async with srv:
            await srv.serve_forever()
