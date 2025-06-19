import asyncio
import dataclasses
from collections.abc import Mapping
from datetime import timedelta
from typing import Any, override

import aiohttp

from .conditions import CurrentConditions
from .from_json import FromJson, JsonObject

EP_CURRENT_CONDITIONS = "/v1/current_conditions"
EP_REAL_TIME = "/v1/real_time"


@dataclasses.dataclass()
class RealTimeBroadcastResponse(FromJson):
    addr: str = dataclasses.field(init=False)
    broadcast_port: int
    duration: float

    @classmethod
    @override
    def _from_json(cls, data: JsonObject, **kwargs: Any):
        return cls(**data)


@dataclasses.dataclass()
class ApiError(Exception, FromJson):
    code: int
    message: str

    def __str__(self) -> str:
        return f"{self.code}: {self.message}"

    @classmethod
    @override
    def _from_json(cls, data: JsonObject, **kwargs: Any):
        return cls(code=data["code"], message=data["message"])


def raw_data_from_body(body: JsonObject) -> JsonObject:
    if err := body.get("error"):
        raise ApiError.from_json(err)

    return body["data"]


def parse_from_json[T: FromJson](cls: type[T], body: JsonObject, **kwargs: Any) -> T:
    data = raw_data_from_body(body)
    return cls.from_json(data, **kwargs)


class WeatherLinkRest:
    session: aiohttp.ClientSession
    base_url: str

    _lock: asyncio.Lock

    def __init__(self, session: aiohttp.ClientSession, base_url: str) -> None:
        self.session = session
        self.base_url = base_url

        self._lock = asyncio.Lock()

    async def _request[T: FromJson](
        self,
        cls: type[T],
        path: str,
        /,
        *,
        params: Mapping[str, str] | None = None,
    ) -> T:
        # lock is needed because the WeatherLink hardware can't serve multiple clients at once
        async with self._lock:
            async with self.session.get(self.base_url + path, params=params) as resp:
                body = await resp.json()
            return parse_from_json(cls, body)

    async def current_conditions(self) -> CurrentConditions:
        return await self._request(CurrentConditions, EP_CURRENT_CONDITIONS)

    async def real_time(self, *, duration: timedelta) -> RealTimeBroadcastResponse:
        async with self.session.get(
            self.base_url + EP_REAL_TIME,
            params={"duration": int(duration.total_seconds())},
        ) as resp:
            assert resp.connection is not None, "no connection for response"
            assert resp.connection.transport is not None, (
                "no transport for response connection"
            )
            peername_raw = resp.connection.transport.get_extra_info("peername")
            if peername_raw is None:
                raise ValueError("failed to get peername from request")

            body = await resp.json()

        broadcast_resp = parse_from_json(RealTimeBroadcastResponse, body)
        server_addr, _ = peername_raw
        broadcast_resp.addr = server_addr
        return broadcast_resp
