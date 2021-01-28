import logging

from . import WeatherLinkCoordinator, WeatherLinkEntity
from .api import LssBarCondition, LssTempHumCondition
from .const import DOMAIN

logger = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    c: WeatherLinkCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities = []
    if LssBarCondition in c.current_conditions:
        entities.append(LssBar(c))
    if LssTempHumCondition in c.current_conditions:
        entities.append(InsideTemp(c))

    async_add_entities(entities)
    return True


class LssBar(WeatherLinkEntity):
    @property
    def _lss_bar_condition(self) -> LssBarCondition:
        return self._conditions[LssBarCondition]

    @property
    def name(self):
        return f"{super().name} LSS Bar"

    @property
    def state(self):
        return round(self._lss_bar_condition.bar_sea_level, 1)

    @property
    def device_state_attributes(self):
        condition = self._lss_bar_condition
        return {
            "trend": round(condition.bar_trend or 0, 1),
            "absolute": round(condition.bar_absolute, 1),
        }

    @property
    def unit_of_measurement(self):
        return "inches"

    @property
    def device_class(self):
        return "pressure"


class InsideTemp(WeatherLinkEntity):
    @property
    def _lss_temp_hum_condition(self) -> LssTempHumCondition:
        return self._conditions[LssTempHumCondition]

    @property
    def name(self):
        return f"{super().name} Temperature Inside"

    @property
    def state(self):
        return round(self._lss_temp_hum_condition.temp_in, 1)

    @property
    def device_state_attributes(self):
        condition = self._lss_temp_hum_condition
        return {
            "humidity": round(condition.hum_in, 1),
            "dew_point": round(condition.dew_point_in, 1),
            "heat_index": round(condition.heat_index_in, 1),
        }

    @property
    def unit_of_measurement(self):
        return "°C"

    @property
    def device_class(self):
        return "temperature"
