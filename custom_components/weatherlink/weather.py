import logging

from homeassistant.components.weather import WeatherEntity
from homeassistant.core import HomeAssistant

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
        return self.coordinator.device_name

    @property
    def temperature(self):
        # rounded by `WeatherEntity`
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
        # rounded by `WeatherEntity`
        return self._iss_condition.hum

    @property
    def wind_speed(self):
        return round(self._iss_condition.wind_speed_avg_last_2_min, 1)

    @property
    def wind_bearing(self):
        return round(self._iss_condition.wind_dir_scalar_avg_last_2_min, 1)

    @property
    def condition(self):
        c = self._iss_condition
        if c.rain_storm_start_at:
            return "pouring"

        if (c.rain_rate_hi_counts or 0.0) > 0:
            if c.temp <= 0:
                return "snowy"
            elif 0 < c.temp < 5:
                return "snowy-rainy"

            return "rainy"

        if c.wind_speed_avg_last_2_min > 20:
            return "windy"

        if c.hum > 75:
            return "fog"

        if state := self.hass.states.get("sun.sun"):
            if state.state == "below_horizon":
                return "clear-night"

        if c.solar_rad > 500:
            return "sunny"

        return "partlycloudy"
