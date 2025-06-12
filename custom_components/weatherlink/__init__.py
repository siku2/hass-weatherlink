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
from .api.conditions import DeviceType
from .config_flow import get_listen_to_broadcasts
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

    _device_type: DeviceType
    device_did: str
    device_name: str
    device_model_name: str

    __broadcast_task: Optional[asyncio.Task] = None

    def __set_broadcast_task_state(self, on: bool) -> None:
        if self.__broadcast_task:
            logger.debug("stopping current broadcast task")
            self.__broadcast_task.cancel()

        if on:
            logger.info("starting live broadcast listener")
            self.__broadcast_task = asyncio.create_task(
                self.__broadcast_loop(), name="broadcast listener loop"
            )
        else:
            self.__broadcast_task = None

    async def __update_config(self, hass: HomeAssistant, entry: ConfigEntry):
        self.units = get_unit_config(hass, entry)
        self.update_interval = get_update_interval(entry)

        self.__set_broadcast_task_state(
            self._device_type.supports_real_time_api()
            and get_listen_to_broadcasts(entry)
        )

    async def __initalize(self, session: WeatherLinkRest, entry: ConfigEntry) -> None:
        self.session = session
        entry.add_update_listener(self.__update_config)

        self.update_method = self.__fetch_data
        conditions = self.data = await self.__fetch_data()
        if conditions is None:
            raise RuntimeError(f"failed to get conditions from {session.base_url!r}")
        self._device_type = conditions.determine_device_type()
        self.device_did = conditions.did
        self.device_model_name = self._device_type.value
        self.device_name = conditions.determine_device_name()

        await self.__update_config(self.hass, entry)

    async def __fetch_data(self) -> CurrentConditions:
        exc_info = None
        for _ in range(MAX_FAIL_COUNTER):
            try:
                conditions = await self.session.current_conditions()
            except Exception as exc:
                exc_info = exc
                await asyncio.sleep(FAIL_TIMEOUT)
            else:
                break
        else:
            logger.warning(
                f"failed to get current conditions in {MAX_FAIL_COUNTER} attempt(s)",
                exc_info=exc_info,
            )
            conditions = self.data

        return conditions

    async def __broadcast_loop_once(self, broadcast: WeatherLinkBroadcast) -> None:
        logger.debug("received broadcast conditions")
        conditions = await broadcast.read()
        self.data.update_from(conditions)

        # TODO theoretically this only needs to update sensors which actually make use of the live data
        # notify all listeners without resetting the polling interval
        self.async_update_listeners()

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

    async def destroy(self) -> None:
        self.__set_broadcast_task_state(False)


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

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass, entry):
    for platform in PLATFORMS:
        await hass.config_entries.async_forward_entry_unload(entry, platform)

    coordinator: WeatherLinkCoordinator = hass.data[DOMAIN].pop(entry.entry_id)
    await coordinator.destroy()

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
