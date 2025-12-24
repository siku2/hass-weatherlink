from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, UnitOfPressure, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import WeatherLinkCoordinator
from .api.conditions import LssBarCondition, LssTempHumCondition
from .const import DOMAIN
from .sensor_air_quality import (
    AirQualityStatus,
    Humidity,
    Pm1p0,
    Pm2p5,
    Pm10p0,
    Temperature,
)
from .sensor_common import WeatherLinkSensor
from .sensor_iss import (
    IssHumidity,
    IssStatus,
    IssTemperature,
    Rainfall,
    Rainstorm,
    SolarRad,
    ThswIndex,
    UvIndex,
    WindBearing,
    WindSpeed,
)
from .sensor_moisture import (
    LEAF_CLS,
    SOIL_MOISTURE_CLS,
    SOIL_TEMPERATURE_CLS,
    MoistureStatus,
)

__all__ = [
    "AirQualityStatus",
    "Temperature",
    "Humidity",
    "Pm1p0",
    "Pm2p5",
    "Pm10p0",
    "IssStatus",
    "IssTemperature",
    "ThswIndex",
    "IssHumidity",
    "WindSpeed",
    "WindBearing",
    "SolarRad",
    "UvIndex",
    "Rainfall",
    "Rainstorm",
    "MoistureStatus",
    "SOIL_MOISTURE_CLS",
    "SOIL_TEMPERATURE_CLS",
    "LEAF_CLS",
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> bool:
    c: WeatherLinkCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(list(WeatherLinkSensor.iter_sensors_for_coordinator(c)))
    return True


class Pressure(
    WeatherLinkSensor,
    sensor_name="Pressure",
    unit_of_measurement=UnitOfPressure.HPA,
    device_class=SensorDeviceClass.PRESSURE,
    state_class=SensorStateClass.MEASUREMENT,
    required_conditions=(LssBarCondition,),
):
    @property
    def _lss_bar_condition(self) -> LssBarCondition:
        return self._conditions[LssBarCondition]

    @property
    def native_value(self):
        return self._lss_bar_condition.bar_sea_level

    @property
    def extra_state_attributes(self):
        condition = self._lss_bar_condition
        return {
            "trend": condition.bar_trend,
            "absolute": condition.bar_absolute,
        }


class InsideTemp(
    WeatherLinkSensor,
    sensor_name="Inside Temperature",
    unit_of_measurement=UnitOfTemperature.CELSIUS,
    device_class=SensorDeviceClass.TEMPERATURE,
    state_class=SensorStateClass.MEASUREMENT,
    required_conditions=(LssTempHumCondition,),
):
    @property
    def _lss_temp_hum_condition(self) -> LssTempHumCondition:
        return self._conditions[LssTempHumCondition]

    @property
    def native_value(self):
        return self._lss_temp_hum_condition.temp_in

    @property
    def extra_state_attributes(self):
        condition = self._lss_temp_hum_condition
        return {
            "dew_point": condition.dew_point_in,
            "heat_index": condition.heat_index_in,
        }


class InsideHum(
    WeatherLinkSensor,
    sensor_name="Inside Humidity",
    unit_of_measurement=PERCENTAGE,
    device_class=SensorDeviceClass.HUMIDITY,
    state_class=SensorStateClass.MEASUREMENT,
    required_conditions=(LssTempHumCondition,),
):
    @property
    def _lss_temp_hum_condition(self) -> LssTempHumCondition:
        return self._conditions[LssTempHumCondition]

    @property
    def native_value(self):
        return self._lss_temp_hum_condition.hum_in
