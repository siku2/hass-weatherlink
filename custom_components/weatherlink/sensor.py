from . import WeatherLinkCoordinator, units
from .api.conditions import LssBarCondition, LssTempHumCondition
from .const import DECIMALS_HUMIDITY, DOMAIN
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
    unit_of_measurement=units.Pressure,
    device_class="pressure",
    required_conditions=(LssBarCondition,),
):
    @property
    def _lss_bar_condition(self) -> LssBarCondition:
        return self._conditions[LssBarCondition]

    @property
    def state(self):
        return self.units.pressure.convert(self._lss_bar_condition.bar_sea_level)

    @property
    def device_state_attributes(self):
        condition = self._lss_bar_condition
        u = self.units.pressure
        return {
            "trend": u.convert_optional(condition.bar_trend),
            "absolute": u.convert(condition.bar_absolute),
        }


class InsideTemp(
    WeatherLinkSensor,
    sensor_name="Inside Temperature",
    unit_of_measurement=units.Temperature,
    device_class="temperature",
    required_conditions=(LssTempHumCondition,),
):
    @property
    def _lss_temp_hum_condition(self) -> LssTempHumCondition:
        return self._conditions[LssTempHumCondition]

    @property
    def state(self):
        return self.units.temperature.convert(self._lss_temp_hum_condition.temp_in)

    @property
    def device_state_attributes(self):
        condition = self._lss_temp_hum_condition
        u = self.units.temperature
        return {
            "dew_point": u.convert(condition.dew_point_in),
            "heat_index": u.convert(condition.heat_index_in),
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
