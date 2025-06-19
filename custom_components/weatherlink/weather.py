import logging

from homeassistant.components.weather import WeatherEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    UnitOfPressure,
    UnitOfSpeed,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import WeatherLinkCoordinator, WeatherLinkEntity
from .api.conditions import IssCondition, LssBarCondition
from .const import DOMAIN

logger = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> bool:
    c: WeatherLinkCoordinator = hass.data[DOMAIN][entry.entry_id]
    if IssCondition in c.data:
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
    def native_temperature(self):
        # rounded by `WeatherEntity`
        return self._iss_condition.temp

    @property
    def native_temperature_unit(self):
        return UnitOfTemperature.CELSIUS

    @property
    def native_pressure(self):
        if condition := self._conditions.get(LssBarCondition):
            return condition.bar_sea_level

        return None

    @property
    def native_pressure_unit(self):
        return UnitOfPressure.HPA

    @property
    def humidity(self):
        # rounded by `WeatherEntity`
        return self._iss_condition.hum

    @property
    def native_wind_speed(self):
        return self._iss_condition.wind_speed_avg_last_2_min

    @property
    def native_wind_speed_unit(self):
        return UnitOfSpeed.KILOMETERS_PER_HOUR

    @property
    def wind_bearing(self):
        return self._iss_condition.wind_dir_scalar_avg_last_2_min

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
