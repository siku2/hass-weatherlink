import logging

from homeassistant.components.weather import WeatherEntity

from . import WeatherLinkCoordinator, WeatherLinkEntity
from .api import IssCondition, LssBarCondition
from .const import DOMAIN

logger = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    c: WeatherLinkCoordinator = hass.data[DOMAIN][entry.entry_id]
    if IssCondition in c.current_conditions:
        async_add_entities([Weather(c)])

    return True


class Weather(WeatherEntity, WeatherLinkEntity):
    @property
    def _iss_condition(self) -> IssCondition:
        return self._conditions[IssCondition]

    @property
    def name(self):
        return self.coordinator.name

    @property
    def temperature(self):
        return self._iss_condition.temp

    @property
    def temperature_unit(self):
        return "°C"

    @property
    def pressure(self):
        if condition := self._conditions.get(LssBarCondition):
            return round(condition.bar_sea_level, 1)

        return None

    @property
    def humidity(self):
        return self._iss_condition.hum

    @property
    def wind_speed(self):
        return self._iss_condition.wind_speed_avg_last_2_min

    @property
    def wind_bearing(self):
        return self._iss_condition.wind_dir_scalar_avg_last_2_min

    @property
    def condition(self):
        # TODO: determine this
        return "unknown"
