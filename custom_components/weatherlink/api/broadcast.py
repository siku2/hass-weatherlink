import asyncio
import json
import logging
from typing import Optional, Union

from .conditions import CurrentConditions
from .rest import WeatherLinkRest

logger = logging.getLogger(__name__)


class Protocol(asyncio.DatagramProtocol):
    remote_addr: str

    transport: asyncio.DatagramTransport
    queue: asyncio.Queue
    connection_lost_fut: asyncio.Future

    def __init__(self, *, queue_size: int = 16) -> None:
        super().__init__()
        self.remote_addr = ""

        # transport made by `connection_made`
        self.queue = asyncio.Queue(queue_size)
        self.connection_lost_fut = asyncio.Future()

    @classmethod
    async def open(cls, *, addr: str, port: int, **kwargs):
        loop = asyncio.get_running_loop()
        _, protocol = await loop.create_datagram_endpoint(
            lambda: cls(**kwargs),
            local_addr=(addr, port),
        )
        return protocol

    async def close(self) -> None:
        self.transport.close()
        await self.connection_lost_fut

    def connection_made(self, transport: asyncio.DatagramTransport) -> None:
        self.transport = transport

    def connection_lost(self, exc: Optional[Exception]) -> None:
        self.connection_lost_fut.set_result(exc)

    def datagram_received(self, data: bytes, addr: str) -> None:
        if addr != self.remote_addr:
            return

        if self.queue.full():
            logger.warning(
                "ignoring message from %s because queue is already full", addr
            )
            return

        try:
            data = json.loads(data)
        except Exception as exc:
            logger.exception(f"failed to parse broadcast payload from {addr}: {data}")
            return

        msg: Union[CurrentConditions, BaseException]
        try:
            msg = CurrentConditions.from_json(data)
        except Exception as exc:
            msg = exc

        self.queue.put_nowait(msg)


class WeatherLinkBroadcast:
    _protocol: Protocol
    _rest: WeatherLinkRest

    def __init__(self, protocol: Protocol) -> None:
        self._protocol = protocol

    @classmethod
    async def connect(cls):
        port = 22222  # TODO determine
        protocol = await Protocol.open(addr="0.0.0.0", port=port)
        return cls(protocol)

    async def disconnect(self) -> None:
        await self._protocol.close()

    async def read(self) -> CurrentConditions:
        msg = await self._protocol.queue.get()
        if isinstance(msg, BaseException):
            raise msg

        return msg
