"""Round-trip tests for the wire protocol."""

import asyncio
import socket
import unittest

from brutus.protocol import (
    _HEADER,
    async_recv_frame,
    async_send_frame,
    pack,
    recv_frame,
    send_frame,
)


class TestPack(unittest.TestCase):
    def test_empty(self):
        result = pack(b"")
        self.assertEqual(result, b"\x00\x00\x00\x00")

    def test_roundtrip_header(self):
        payload = b"hello world"
        frame = pack(payload)
        (length,) = _HEADER.unpack(frame[: _HEADER.size])
        self.assertEqual(length, len(payload))
        self.assertEqual(frame[_HEADER.size :], payload)

    def test_large_payload(self):
        payload = b"x" * 65536
        frame = pack(payload)
        (length,) = _HEADER.unpack(frame[: _HEADER.size])
        self.assertEqual(length, 65536)


class TestSyncSocketRoundtrip(unittest.TestCase):
    """Send a frame through a real socket pair and read it back."""

    def _make_pair(self):
        srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        srv.bind(("127.0.0.1", 0))
        srv.listen(1)
        port = srv.getsockname()[1]

        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(("127.0.0.1", port))
        server_conn, _ = srv.accept()
        srv.close()
        return client, server_conn

    def test_single_frame(self):
        sender, receiver = self._make_pair()
        try:
            payload = b"test payload"
            send_frame(sender, payload)
            result = recv_frame(receiver)
            self.assertEqual(result, payload)
        finally:
            sender.close()
            receiver.close()

    def test_multiple_frames(self):
        sender, receiver = self._make_pair()
        try:
            messages = [b"first", b"second", b"third"]
            for m in messages:
                send_frame(sender, m)
            for m in messages:
                self.assertEqual(recv_frame(receiver), m)
        finally:
            sender.close()
            receiver.close()

    def test_binary_payload(self):
        sender, receiver = self._make_pair()
        try:
            payload = bytes(range(256)) * 100
            send_frame(sender, payload)
            result = recv_frame(receiver)
            self.assertEqual(result, payload)
        finally:
            sender.close()
            receiver.close()


class TestAsyncRoundtrip(unittest.TestCase):
    """async_recv_frame / async_send_frame via asyncio streams."""

    def test_async_frame(self):
        async def _run():
            server_frames = []

            async def handle(reader, writer):
                server_frames.append(await async_recv_frame(reader))
                writer.close()

            server = await asyncio.start_server(handle, "127.0.0.1", 0)
            port = server.sockets[0].getsockname()[1]

            async with server:
                reader, writer = await asyncio.open_connection("127.0.0.1", port)
                await async_send_frame(writer, b"async hello")
                await asyncio.sleep(0.05)

            self.assertEqual(server_frames, [b"async hello"])

        asyncio.run(_run())
