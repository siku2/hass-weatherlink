import asyncio
import contextlib
import json
import logging
import time
from datetime import timedelta
from typing import Any, override

from .conditions import CurrentConditions
from .rest import WeatherLinkRest

logger = logging.getLogger(__name__)


class Protocol(asyncio.DatagramProtocol):
    remote_addr: str

    transport: asyncio.DatagramTransport
    queue: asyncio.Queue[CurrentConditions | BaseException]
    connection_lost_fut: asyncio.Future[Exception | None]

    def __init__(self, remote_addr: str, *, queue_size: int = 16) -> None:
        super().__init__()
        self.remote_addr = remote_addr

        # transport made by `connection_made`
        self.queue = asyncio.Queue(queue_size)
        self.connection_lost_fut = asyncio.Future()

    def __str__(self) -> str:
        return f"<{type(self).__qualname__} {self.remote_addr=!r}>"

    @classmethod
    async def open(cls, remote_addr: str, *, addr: str, port: int, **kwargs: Any):
        loop = asyncio.get_running_loop()
        _, protocol = await loop.create_datagram_endpoint(
            lambda: cls(remote_addr, **kwargs),
            local_addr=(addr, port),
        )
        return protocol

    def connection_made(self, transport: asyncio.DatagramTransport) -> None:
        logger.debug("%s connection made", self)
        self.transport = transport

    def connection_lost(self, exc: Exception | None) -> None:
        logger.debug("%s connection lost with error: %s", self, exc)
        self.connection_lost_fut.set_result(exc)

    def __queue_put(self, item: CurrentConditions | BaseException) -> None:
        with contextlib.suppress(asyncio.QueueFull):
            self.queue.put_nowait(item)

    @override
    def datagram_received(self, data: bytes, addr: tuple[str, int]) -> None:
        if addr[0] != self.remote_addr:
            return

        if self.queue.full():
            logger.warning(
                "ignoring message from %s because queue is already full", addr
            )
            return

        try:
            parsed_data = json.loads(data)
        except Exception:
            logger.exception(f"failed to parse broadcast payload from {addr}: {data}")
            return

        msg: CurrentConditions | BaseException
        try:
            msg = CurrentConditions.from_json(parsed_data)
        except Exception as exc:
            msg = exc

        self.__queue_put(msg)

    async def close(self) -> None:
        self.transport.close()
        await self.connection_lost_fut

    def raise_if_connection_lost(self) -> None:
        fut = self.connection_lost_fut
        if not fut.done():
            return

        if exc := fut.result():
            raise exc

        raise RuntimeError("connection closed")

    async def __queue_get_raw(self) -> CurrentConditions | BaseException:
        try:
            return self.queue.get_nowait()
        except asyncio.QueueEmpty:
            pass

        conn_lost = self.connection_lost_fut
        queue_get = asyncio.create_task(self.queue.get())
        await asyncio.wait({conn_lost, queue_get}, return_when=asyncio.FIRST_COMPLETED)
        # handle the case where the connection was lost
        self.raise_if_connection_lost()
        return await queue_get

    async def queue_get(self) -> CurrentConditions:
        msg = await self.__queue_get_raw()
        if isinstance(msg, BaseException):
            raise msg
        return msg


class BroadcastRenewer:
    remote_addr: str
    broadcast_port: int

    _rest: WeatherLinkRest
    _duration: timedelta
    _renew_at: float

    def __init__(
        self,
        rest: WeatherLinkRest,
        duration: timedelta,
    ) -> None:
        self._rest = rest
        self._duration = duration
        self._renew_at = 0.0

    @classmethod
    async def init(cls, rest: WeatherLinkRest, *, duration: timedelta):
        inst = cls(rest, duration)
        await inst.update()
        return inst

    def should_renew(self) -> bool:
        return time.time() >= self._renew_at

    async def update(self) -> bool:
        if not self.should_renew():
            return False

        logger.info("renewing real-time broadcast")
        rt = await self._rest.real_time(duration=self._duration)

        self._renew_at = time.time() + rt.duration / 2
        self.remote_addr = rt.addr
        self.broadcast_port = rt.broadcast_port
        return True


class WeatherLinkBroadcast:
    _protocol: Protocol
    _renewer: BroadcastRenewer

    def __init__(self, protocol: Protocol, renewer: BroadcastRenewer) -> None:
        self._protocol = protocol
        self._renewer = renewer

    @classmethod
    async def start(cls, rest: WeatherLinkRest):
        renewer: BroadcastRenewer = await BroadcastRenewer.init(
            rest, duration=timedelta(hours=1)
        )
        protocol = await Protocol.open(
            renewer.remote_addr, addr="0.0.0.0", port=renewer.broadcast_port
        )
        return cls(protocol, renewer)

    async def stop(self) -> None:
        await self._protocol.close()

    async def read(self) -> CurrentConditions:
        if await self._renewer.update():
            self._protocol.remote_addr = self._renewer.remote_addr
        return await self._protocol.queue_get()
