import logging

from homeassistant.components.weather import WeatherEntity

from . import WeatherLinkCoordinator, WeatherLinkEntity
from .api import IssCondition, LssBarCondition
from .const import DECIMALS_DIRECTION, DECIMALS_PRESSURE, DECIMALS_SPEED, DOMAIN
from .sensor_common import round_optional

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
            return round(condition.bar_sea_level, DECIMALS_PRESSURE)

        return None

    @property
    def humidity(self):
        # rounded by `WeatherEntity`
        return self._iss_condition.hum

    @property
    def wind_speed(self):
        return round_optional(
            self._iss_condition.wind_speed_avg_last_2_min, DECIMALS_SPEED
        )

    @property
    def wind_bearing(self):
        return round_optional(
            self._iss_condition.wind_dir_scalar_avg_last_2_min, DECIMALS_DIRECTION
        )

    @property
    def condition(self):
        c = self._iss_condition

        rain_rate = c.rain_rate_hi or 0.0
        if rain_rate > 0.25:
            if temp := c.temp:
                if temp <= 0:
                    return "snowy"
                elif 0 < temp < 5:
                    return "snowy-rainy"

            if rain_rate > 4.0:
                return "pouring"

            return "rainy"

        if (c.wind_speed_avg_last_2_min or 0.0) > 20:
            return "windy"

        if state := self.hass.states.get("sun.sun"):
            if state.state == "below_horizon":
                return "clear-night"

        if (c.solar_rad or 0) > 500:
            return "sunny"

        return "partlycloudy"
