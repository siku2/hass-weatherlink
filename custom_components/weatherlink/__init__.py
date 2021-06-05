import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import aiohttp_client
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from .api import CurrentConditions, WeatherLinkRest
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


MAX_FAIL_COUNTER = 3


class WeatherLinkCoordinator(DataUpdateCoordinator[CurrentConditions]):
    session: WeatherLinkRest
    units: UnitConfig

    device_did: str
    device_name: str
    device_model_name: str

    _fail_counter: int

    async def __update_config(self, hass: HomeAssistant, entry: ConfigEntry):
        self.units = get_unit_config(hass, entry)
        self.update_interval = get_update_interval(entry)

    async def __initalize(self, session: WeatherLinkRest, entry: ConfigEntry) -> None:
        self.session = session
        entry.add_update_listener(self.__update_config)
        await self.__update_config(self.hass, entry)

        self.update_method = self.__fetch_data
        await self.__fetch_data()

        conditions = self.data
        self.device_did = conditions.did
        self.device_model_name = conditions.determine_device_type().value
        self.device_name = conditions.determine_device_name()

        self._fail_counter = 0

    async def __fetch_data(self) -> CurrentConditions:
        try:
            conditions = await self.session.current_conditions()
        except Exception:
            self._fail_counter += 1
            if self._fail_counter > MAX_FAIL_COUNTER:
                raise

            logger.warning(
                "failed to get current conditions, error %s / %s",
                self._fail_counter,
                MAX_FAIL_COUNTER,
            )
            # reuse previous data
            conditions = self.data
        else:
            self._fail_counter = 0

        return conditions

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
