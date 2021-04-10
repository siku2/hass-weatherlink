import logging
from typing import Iterable, Iterator, List, Optional, Type

from . import WeatherLinkCoordinator, WeatherLinkEntity
from .api import (
    ConditionRecord,
    CurrentConditions,
    IssCondition,
    LssBarCondition,
    LssTempHumCondition,
)
from .const import DOMAIN

logger = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    c: WeatherLinkCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(list(WeatherLinkSensor.iter_sensors_for_coordinator(c)))
    return True


class WeatherLinkSensor(WeatherLinkEntity):
    _SENSORS: List[Type["WeatherLinkSensor"]] = []

    def __init_subclass__(
        cls,
        *,
        sensor_name: str,
        unit_of_measurement: Optional[str],
        device_class: Optional[str],
        required_conditions: Iterable[Type[ConditionRecord]] = None,
        **kwargs,
    ) -> None:
        super().__init_subclass__(**kwargs)

        cls._sensor_name = sensor_name
        cls._unit_of_measurement = unit_of_measurement
        cls._device_class = device_class
        try:
            requirements = cls._required_conditions
        except AttributeError:
            requirements = ()

        cls._required_conditions = requirements + tuple(required_conditions)

        cls._SENSORS.append(cls)

    @classmethod
    def _conditions_ok(cls, conditions: CurrentConditions) -> bool:
        for req in cls._required_conditions:
            if req not in conditions:
                return False

        return True

    @classmethod
    def iter_sensors_for_coordinator(
        cls, coord: WeatherLinkCoordinator
    ) -> Iterator["WeatherLinkSensor"]:
        for cls in cls._SENSORS:
            if not cls._conditions_ok(coord.current_conditions):
                logger.info("ignoring sensor %s because requirements are not met", cls)
                continue
            yield cls(coord)

    @property
    def name(self):
        return f"{super().name} {self._sensor_name}"

    @property
    def unit_of_measurement(self):
        return self._unit_of_measurement

    @property
    def device_class(self):
        return self._device_class


class Wind(
    WeatherLinkSensor,
    sensor_name="Wind",
    unit_of_measurement="km/h",
    device_class=None,
    required_conditions=(IssCondition,),
):
    @property
    def _iss_condition(self) -> IssCondition:
        return self._conditions[IssCondition]

    @property
    def state(self):
        return round(self._iss_condition.wind_speed_avg_last_2_min, 1)

    @property
    def device_state_attributes(self):
        condition = self._iss_condition
        return {
            "high": condition.wind_speed_hi_last_2_min,
            "dir": condition.wind_dir_scalar_avg_last_2_min,
            "wind_chill": condition.wind_chill,
            "10_min": condition.wind_speed_avg_last_10_min,
            "10_min_dir": condition.wind_dir_scalar_avg_last_10_min,
            "10_min_high": condition.wind_speed_hi_last_10_min,
            "10_min_high_dir": condition.wind_dir_at_hi_speed_last_10_min,
        }


class Solar(
    WeatherLinkSensor,
    sensor_name="Solar",
    unit_of_measurement="W/m²",
    device_class=None,
    required_conditions=(IssCondition,),
):
    @property
    def _iss_condition(self) -> IssCondition:
        return self._conditions[IssCondition]

    @property
    def state(self):
        return self._iss_condition.solar_rad

    @property
    def device_state_attributes(self):
        condition = self._iss_condition
        return {
            "uv_index": condition.uv_index,
        }


class Rainfall(
    WeatherLinkSensor,
    sensor_name="Rainfall",
    unit_of_measurement="mm",
    device_class=None,
    required_conditions=(IssCondition,),
):
    @property
    def _iss_condition(self) -> IssCondition:
        return self._conditions[IssCondition]

    @property
    def state(self):
        return round(self._iss_condition.rainfall_daily, 1)

    @property
    def device_state_attributes(self):
        condition = self._iss_condition
        return {
            "rate": round(condition.rain_rate_last, 1),
            "rate_high": round(condition.rain_rate_hi, 1),
            "15_min": round(condition.rainfall_last_15_min, 1),
            "15_min_high": round(condition.rain_rate_hi_last_15_min, 1),
            "60_min": round(condition.rainfall_last_60_min, 1),
            "24_hr": round(condition.rainfall_last_24_hr),
            "monthly": round(condition.rainfall_monthly),
            "yearly": round(condition.rainfall_year),
        }


class Rainstorm(
    WeatherLinkSensor,
    sensor_name="Rainstorm",
    unit_of_measurement="mm",
    device_class=None,
    required_conditions=(IssCondition,),
):
    @property
    def _iss_condition(self) -> IssCondition:
        return self._conditions[IssCondition]

    @property
    def state(self):
        return round_optional(self._iss_condition.rain_storm, 1)

    @property
    def device_state_attributes(self):
        condition = self._iss_condition
        return {
            "start": condition.rain_storm_start_at,
            "last": round_optional(condition.rain_storm_last, 1),
            "last_start": condition.rain_storm_last_start_at,
            "last_end": condition.rain_storm_last_end_at,
        }


class LssBar(
    WeatherLinkSensor,
    sensor_name="Pressure",
    unit_of_measurement="hPa",
    device_class="pressure",
    required_conditions=(LssBarCondition,),
):
    @property
    def _lss_bar_condition(self) -> LssBarCondition:
        return self._conditions[LssBarCondition]

    @property
    def state(self):
        return round(self._lss_bar_condition.bar_sea_level, 1)

    @property
    def device_state_attributes(self):
        condition = self._lss_bar_condition
        return {
            "trend": round_optional(condition.bar_trend, 1),
            "absolute": round(condition.bar_absolute, 1),
        }


class InsideTemp(
    WeatherLinkSensor,
    sensor_name="Inside Temperature",
    unit_of_measurement="°C",
    device_class="temperature",
    required_conditions=(LssTempHumCondition,),
):
    @property
    def _lss_temp_hum_condition(self) -> LssTempHumCondition:
        return self._conditions[LssTempHumCondition]

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


def round_optional(f: Optional[float], ndigits: int = 0) -> Optional[float]:
    if not f:
        return f
    return round(f, ndigits)
