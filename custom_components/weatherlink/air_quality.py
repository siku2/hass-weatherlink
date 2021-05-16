import logging

from homeassistant.components.air_quality import AirQualityEntity

from . import WeatherLinkCoordinator, WeatherLinkEntity
from .api import AirQualityCondition
from .const import DECIMALS_PM, DOMAIN

logger = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    c: WeatherLinkCoordinator = hass.data[DOMAIN][entry.entry_id]
    if AirQualityCondition in c.current_conditions:
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
        return round(self._aq_condition.pm_2p5_nowcast, DECIMALS_PM)

    @property
    def particulate_matter_10(self) -> float:
        return round(self._aq_condition.pm_10_nowcast, DECIMALS_PM)

    @property
    def particulate_matter_0_1(self) -> float:
        return round(self._aq_condition.pm_1, DECIMALS_PM)

    # TODO calculate AQI
    # @property
    # def air_quality_index(self) -> float:
    #     return None
