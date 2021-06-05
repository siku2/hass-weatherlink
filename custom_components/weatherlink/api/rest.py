import dataclasses
from datetime import timedelta
from typing import Mapping, Type

import aiohttp

from .conditions import CurrentConditions
from .from_json import FromJson, FromJsonT, JsonObject

EP_CURRENT_CONDITIONS = "/v1/current_conditions"
EP_REAL_TIME = "/v1/real_time"


@dataclasses.dataclass()
class RealTimeBroadcastResponse(FromJson):
    addr: str = dataclasses.field(init=False)
    broadcast_port: int
    duration: float

    @classmethod
    def _from_json(cls, data: JsonObject, **kwargs):
        return cls(**data)


@dataclasses.dataclass()
class ApiError(Exception, FromJson):
    code: int
    message: str

    def __str__(self) -> str:
        return f"{self.code}: {self.message}"

    @classmethod
    def _from_json(cls, data: JsonObject, **kwargs):
        return cls(code=data["code"], message=data["message"])


def raw_data_from_body(body: JsonObject) -> JsonObject:
    if err := body.get("error"):
        raise ApiError.from_json(err)

    return body["data"]


def parse_from_json(cls: Type[FromJsonT], body: JsonObject, **kwargs) -> FromJsonT:
    data = raw_data_from_body(body)
    return cls.from_json(data, **kwargs)


class WeatherLinkRest:
    session: aiohttp.ClientSession
    base_url: str

    def __init__(self, session: aiohttp.ClientSession, base_url: str) -> None:
        self.session = session
        self.base_url = base_url

    async def _request(
        self, cls: Type[FromJsonT], path: str, /, *, params: Mapping[str, str] = None
    ) -> FromJsonT:
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
            peername_raw = resp.connection.transport.get_extra_info("peername")
            if peername_raw is None:
                raise ValueError("failed to get peername from request")

            body = await resp.json()

        broadcast_resp = parse_from_json(RealTimeBroadcastResponse, body)
        server_addr, _ = peername_raw
        broadcast_resp.addr = server_addr
        return broadcast_resp
