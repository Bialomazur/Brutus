"""Wire protocol: 4-byte big-endian length prefix around every message.

Both attacker and victim use these helpers so the framing is always consistent.
Sync variants work on raw sockets (victim); async variants work with asyncio
StreamReader/StreamWriter (attacker server).
"""

import struct

_HEADER = struct.Struct("!I")


def pack(payload: bytes) -> bytes:
    """Prefix *payload* with its 4-byte length and return the full frame."""
    return _HEADER.pack(len(payload)) + payload


# ---------------------------------------------------------------------------
# Synchronous helpers (victim / raw-socket callers)
# ---------------------------------------------------------------------------


def _recv_exactly(sock, n: int) -> bytes:
    buf = bytearray()
    while len(buf) < n:
        chunk = sock.recv(n - len(buf))
        if not chunk:
            raise ConnectionError("connection closed")
        buf += chunk
    return bytes(buf)


def recv_frame(sock) -> bytes:
    """Read exactly one framed message from *sock* (blocking)."""
    header = _recv_exactly(sock, _HEADER.size)
    (length,) = _HEADER.unpack(header)
    return _recv_exactly(sock, length)


def send_frame(sock, payload: bytes) -> None:
    """Send *payload* as a framed message over *sock*."""
    sock.sendall(pack(payload))


# ---------------------------------------------------------------------------
# Async helpers (attacker asyncio server)
# ---------------------------------------------------------------------------


async def async_recv_frame(reader) -> bytes:
    """Read exactly one framed message from an asyncio StreamReader."""
    header = await reader.readexactly(_HEADER.size)
    (length,) = _HEADER.unpack(header)
    return await reader.readexactly(length)


async def async_send_frame(writer, payload: bytes) -> None:
    """Write a framed message to an asyncio StreamWriter."""
    writer.write(pack(payload))
    await writer.drain()
