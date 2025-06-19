import logging

from homeassistant.components.air_quality import AirQualityEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import WeatherLinkCoordinator, WeatherLinkEntity
from .api.conditions import AirQualityCondition
from .const import DOMAIN

logger = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> bool:
    c: WeatherLinkCoordinator = hass.data[DOMAIN][entry.entry_id]
    if AirQualityCondition in c.data:
        async_add_entities([AirQuality(c)])

    return True


class AirQuality(AirQualityEntity, WeatherLinkEntity):
    @property
    def _aq_condition(self) -> AirQualityCondition:
        return self._conditions[AirQualityCondition]

    @property
    def name(self):
        return self.coordinator.device_name

    @property
    def particulate_matter_2_5(self) -> float:
        return self.units.pm.convert(self._aq_condition.pm_2p5_nowcast)

    @property
    def particulate_matter_10(self) -> float:
        return self.units.pm.convert(self._aq_condition.pm_10_nowcast)

    @property
    def particulate_matter_0_1(self) -> float:
        return self.units.pm.convert(self._aq_condition.pm_1)

    # TODO calculate AQI
    # @property
    # def air_quality_index(self) -> float:
    #     return None
