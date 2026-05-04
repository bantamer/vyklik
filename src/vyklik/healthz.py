import asyncio
import contextlib
import logging
import os

log = logging.getLogger("vyklik.healthz")

HEALTHZ_PORT = int(os.environ.get("HEALTHZ_PORT", "8080"))
_RESPONSE = (
    b"HTTP/1.1 200 OK\r\n"
    b"Content-Type: text/plain\r\n"
    b"Content-Length: 2\r\n"
    b"Connection: close\r\n\r\n"
    b"ok"
)


async def _handle(_reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
    try:
        # Drain whatever the client sent so the kernel buffer doesn't fill.
        with contextlib.suppress(asyncio.TimeoutError):
            await asyncio.wait_for(_reader.read(1024), timeout=1.0)
        writer.write(_RESPONSE)
        await writer.drain()
    finally:
        writer.close()
        with contextlib.suppress(Exception):
            await writer.wait_closed()


async def serve() -> None:
    server = await asyncio.start_server(_handle, host="0.0.0.0", port=HEALTHZ_PORT)
    log.info("healthz listening on :%d", HEALTHZ_PORT)
    async with server:
        await server.serve_forever()
