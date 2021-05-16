from . import WeatherLinkCoordinator
from .api import LssBarCondition, LssTempHumCondition
from .const import (
    DECIMALS_HUMIDITY,
    DECIMALS_PRESSURE,
    DECIMALS_PRESSURE_TREND,
    DECIMALS_TEMPERATURE,
    DOMAIN,
)
from .sensor_air_quality import *
from .sensor_common import WeatherLinkSensor, round_optional
from .sensor_iss import *
from .sensor_moisture import *


async def async_setup_entry(hass, entry, async_add_entities):
    c: WeatherLinkCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(list(WeatherLinkSensor.iter_sensors_for_coordinator(c)))
    return True


class Pressure(
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
        return round(self._lss_bar_condition.bar_sea_level, DECIMALS_PRESSURE)

    @property
    def device_state_attributes(self):
        condition = self._lss_bar_condition
        return {
            "trend": round_optional(condition.bar_trend, DECIMALS_PRESSURE_TREND),
            "absolute": round(condition.bar_absolute, DECIMALS_PRESSURE),
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
        return round(self._lss_temp_hum_condition.temp_in, DECIMALS_TEMPERATURE)

    @property
    def device_state_attributes(self):
        condition = self._lss_temp_hum_condition
        return {
            "dew_point": round(condition.dew_point_in, DECIMALS_TEMPERATURE),
            "heat_index": round(condition.heat_index_in, DECIMALS_TEMPERATURE),
        }


class InsideHum(
    WeatherLinkSensor,
    sensor_name="Inside Humidity",
    unit_of_measurement="%",
    device_class="humidity",
    required_conditions=(LssTempHumCondition,),
):
    @property
    def _lss_temp_hum_condition(self) -> LssTempHumCondition:
        return self._conditions[LssTempHumCondition]

    @property
    def state(self):
        return round(self._lss_temp_hum_condition.hum_in, DECIMALS_HUMIDITY)
