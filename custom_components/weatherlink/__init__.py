import asyncio
import dataclasses
import logging
from datetime import timedelta
from typing import cast

from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers import aiohttp_client
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from .api import CurrentConditions, DeviceType, WeatherLinkSession
from .const import DOMAIN, PLATFORMS

logger = logging.getLogger(__name__)


async def async_setup(hass, _config):
    hass.data[DOMAIN] = {}
    return True


class WeatherLinkCoordinator(DataUpdateCoordinator):
    session: WeatherLinkSession
    current_conditions: CurrentConditions

    async def __initalize(self) -> None:
        self.update_method = self.__fetch_data
        await self.__fetch_data()

    async def __fetch_data(self) -> None:
        self.current_conditions = await self.session.current_conditions()

    @classmethod
    async def build(cls, hass, session: WeatherLinkSession):
        coordinator = cls(
            hass,
            logger,
            name="state",
            update_interval=timedelta(seconds=10),
        )
        coordinator.session = session
        await coordinator.__initalize()

        return coordinator


async def setup_coordinator(hass, entry: ConfigEntry):
    host = entry.data["host"]

    session = WeatherLinkSession(aiohttp_client.async_get_clientsession(hass), host)
    coordinator = await WeatherLinkCoordinator.build(hass, session)
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
    _did: str
    _model: str
    _name: str

    def __init__(self, coordinator: WeatherLinkCoordinator) -> None:
        super().__init__(coordinator)

        self._did = coordinator.current_conditions.did
        self._model = coordinator.current_conditions.determine_device_type().value
        self._name = coordinator.current_conditions.name or self._model

    @property
    def _conditions(self) -> CurrentConditions:
        return self.coordinator.current_conditions

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._did)},
            "name": self._name,
            "manufacturer": "Davis Instruments",
            "model": self._model,
            "sw_version": "v1",
        }

    @property
    def name(self):
        return self._name

    @property
    def unique_id(self):
        return f"{DOMAIN}-{self._did}-{type(self).__qualname__}"
