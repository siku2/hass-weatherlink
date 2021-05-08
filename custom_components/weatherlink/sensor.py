from . import WeatherLinkCoordinator
from .api import LssBarCondition, LssTempHumCondition
from .const import DOMAIN
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
