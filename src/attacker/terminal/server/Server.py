import asyncio
from typing import Optional
from src.attacker.terminal.server.ConnectionHandler import ConnectionHandler
from src.attacker.util import ts, CONNECTION_CONNECT_TEMPLATE

class Server:

    client_number = 0

    def __init__(self, host, port, window, connections):
        self.host = host
        self.port = port
        self.window = window
        self._connections = connections
        self.server: Optional[asyncio.Server] = None

    async def handle_client_connection(self, reader, writer):
        """Handle a new client connection."""
        addr = writer.get_extra_info('peername')
        self.window.Output.addItem(CONNECTION_CONNECT_TEMPLATE.format(time=ts(), addr=addr))
        Server.client_number += 1
        
        connection = ConnectionHandler(reader, writer, addr, self.window, Server.client_number, self._connections)
        self._connections[Server.client_number] = connection
        
        # Handle the client in the background
        await connection.handle_client()

    async def start(self):
        """Start the asyncio server."""
        self.server = await asyncio.start_server(
            self.handle_client_connection,
            self.host,
            self.port
        )
        
    async def serve_forever(self):
        """Run the server forever."""
        if self.server:
            async with self.server:
                await self.server.serve_forever()
