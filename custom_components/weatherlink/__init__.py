import asyncio
import logging
from datetime import timedelta
from typing import Optional

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import aiohttp_client
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from .api import CurrentConditions, WeatherLinkBroadcast, WeatherLinkRest
from .const import DOMAIN, PLATFORMS
from .units import UnitConfig, get_unit_config

logger = logging.getLogger(__name__)


async def async_setup(hass, _config):
    hass.data[DOMAIN] = {}
    return True


def get_update_interval(entry: ConfigEntry) -> timedelta:
    seconds = 30.0
    try:
        seconds = float(entry.options["update_interval"])
    except KeyError:
        logger.info("no update_interval set, using default")
    except Exception:
        logger.exception(
            f"failed to read update_interval from options: {entry.options!r}"
        )

    return timedelta(seconds=seconds)


MAX_FAIL_COUNTER: int = 3
FAIL_TIMEOUT: float = 3.0


class WeatherLinkCoordinator(DataUpdateCoordinator[CurrentConditions]):
    session: WeatherLinkRest
    units: UnitConfig

    device_did: str
    device_name: str
    device_model_name: str

    __broadcast_task: Optional[asyncio.Task]

    async def __update_config(self, hass: HomeAssistant, entry: ConfigEntry):
        self.units = get_unit_config(hass, entry)
        self.update_interval = get_update_interval(entry)

    async def __initalize(self, session: WeatherLinkRest, entry: ConfigEntry) -> None:
        self.session = session
        entry.add_update_listener(self.__update_config)
        await self.__update_config(self.hass, entry)

        self.update_method = self.__fetch_data
        conditions = self.data = await self.__fetch_data()
        if conditions is None:
            raise RuntimeError(f"failed to get conditions from {session.base_url!r}")
        self.device_did = conditions.did
        device_type = conditions.determine_device_type()
        self.device_model_name = device_type.value
        self.device_name = conditions.determine_device_name()

        if device_type.supports_real_time_api():
            logger.info("starting live broadcast listener")
            self.__broadcast_task = asyncio.create_task(
                self.__broadcast_loop(), name="broadcast listener loop"
            )
        else:
            self.__broadcast_task = None

    async def __fetch_data(self) -> CurrentConditions:
        for i in range(MAX_FAIL_COUNTER):
            try:
                conditions = await self.session.current_conditions()
            except Exception as exc:
                logger.warning(
                    "failed to get current conditions, error %s / %s",
                    i + 1,
                    MAX_FAIL_COUNTER,
                    exc_info=exc,
                )
                await asyncio.sleep(FAIL_TIMEOUT)
            else:
                break
        else:
            conditions = self.data

        return conditions

    async def __broadcast_loop_once(self, broadcast: WeatherLinkBroadcast) -> None:
        conditions = await broadcast.read()
        logger.debug("received broadcast conditions")

    async def __broadcast_loop(self) -> None:
        try:
            broadcast = await WeatherLinkBroadcast.start(self.session)
        except Exception:
            logger.exception("failed to start broadcast")
            return
        try:
            while True:
                try:
                    await self.__broadcast_loop_once(broadcast)
                except Exception:
                    logger.exception("failed to read broadcast")
        finally:
            await broadcast.stop()

    @classmethod
    async def build(cls, hass, session: WeatherLinkRest, entry: ConfigEntry):
        coordinator = cls(
            hass,
            logger,
            name="state",
            update_interval=get_update_interval(entry),
        )
        await coordinator.__initalize(session, entry)

        return coordinator


async def setup_coordinator(hass, entry: ConfigEntry):
    host = entry.data["host"]

    coordinator = await WeatherLinkCoordinator.build(
        hass,
        WeatherLinkRest(aiohttp_client.async_get_clientsession(hass), host),
        entry,
    )
    hass.data[DOMAIN][entry.entry_id] = coordinator


async def async_setup_entry(hass, entry):
    await setup_coordinator(hass, entry)

    for platform in PLATFORMS:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(entry, platform)
        )

    return True


async def async_unload_entry(hass, entry):
    for platform in PLATFORMS:
        await hass.config_entries.async_forward_entry_unload(entry, platform)

    del hass.data[DOMAIN][entry.entry_id]

    return True


class WeatherLinkEntity(CoordinatorEntity):
    coordinator: WeatherLinkCoordinator

    def __init__(self, coordinator: WeatherLinkCoordinator) -> None:
        super().__init__(coordinator)

    @property
    def _conditions(self) -> CurrentConditions:
        return self.coordinator.data

    @property
    def units(self) -> UnitConfig:
        return self.coordinator.units

    @property
    def device_info(self):
        coord = self.coordinator
        return {
            "identifiers": {(DOMAIN, coord.device_did)},
            "name": coord.device_name,
            "manufacturer": "Davis Instruments",
            "model": coord.device_model_name,
            "sw_version": "v1",
        }

    @property
    def unique_id(self):
        return f"{DOMAIN}-{self.coordinator.device_did}-{type(self).__qualname__}"
