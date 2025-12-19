from datetime import datetime

from homeassistant.components.sensor import SensorDeviceClass
from homeassistant.const import (
    CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
    PERCENTAGE,
    UnitOfTemperature,
)

from .api.conditions import AirQualityCondition
from .sensor_common import WeatherLinkSensor

__all__ = [
    "AirQualityStatus",
    "Temperature",
    "Humidity",
    "Pm1p0",
    "Pm2p5",
    "Pm10p0",
]


class AirQualitySensor(WeatherLinkSensor, abc=True):
    def __init_subclass__(
        cls,
        abc: bool = False,
        **kwargs,
    ) -> None:
        if not abc:
            kwargs["required_conditions"] = (AirQualityCondition,)
        super().__init_subclass__(abc=abc, **kwargs)

    @property
    def _aq_condition(self) -> AirQualityCondition:
        return self._conditions[AirQualityCondition]

    # doesn't need name or unique_id because it's a separate device


class AirQualityStatus(
    AirQualitySensor,
    sensor_name="Status",
    unit_of_measurement=None,
    device_class=None,
):
    @property
    def icon(self):
        return "mdi:information"

    @property
    def state(self):
        update_interval = self.coordinator.update_interval
        if not update_interval:
            return "unknown"

        deadline = datetime.now() - 2 * update_interval
        last_report_time = self._aq_condition.last_report_time
        # last report time is older than two update intervals
        if last_report_time < deadline:
            return "disconnected"

        return "connected"

    @property
    def extra_state_attributes(self):
        c = self._aq_condition
        return {
            "last_report_time": c.last_report_time,
            "pm_data_1_hr": c.pct_pm_data_last_1_hour,
            "pm_data_3_hr": c.pct_pm_data_last_3_hours,
            "pm_data_24_hr": c.pct_pm_data_last_24_hours,
            "pm_data_nowcast": c.pct_pm_data_nowcast,
        }


class Temperature(
    AirQualitySensor,
    sensor_name="Temperature",
    unit_of_measurement=UnitOfTemperature.CELSIUS,
    device_class=SensorDeviceClass.TEMPERATURE,
):
    @property
    def state(self):
        return self._aq_condition.temp

    @property
    def extra_state_attributes(self):
        c = self._aq_condition
        return {
            "dew_point": c.dew_point,
            "wet_bulb": c.wet_bulb,
            "heat_index": c.heat_index,
        }


class Humidity(
    AirQualitySensor,
    sensor_name="Humidity",
    unit_of_measurement=PERCENTAGE,
    device_class=SensorDeviceClass.HUMIDITY,
):
    @property
    def state(self):
        return self._aq_condition.hum


class Pm1p0(
    AirQualitySensor,
    sensor_name="PM 1.0",
    unit_of_measurement=CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
    device_class=SensorDeviceClass.PM1,
):
    @property
    def icon(self):
        return "mdi:air-filter"

    @property
    def state(self):
        return self._aq_condition.pm_1


class Pm2p5(
    AirQualitySensor,
    sensor_name="PM 2.5",
    unit_of_measurement=CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
    device_class=SensorDeviceClass.PM25,
):
    @property
    def icon(self):
        return "mdi:air-filter"

    @property
    def state(self):
        return self._aq_condition.pm_2p5_nowcast

    @property
    def extra_state_attributes(self):
        c = self._aq_condition
        return {
            "1_min": c.pm_2p5,
            "1_hr": c.pm_2p5_last_1_hour,
            "3_hr": c.pm_2p5_last_3_hours,
            "24_hr": c.pm_2p5_last_24_hours,
        }


class Pm10p0(
    AirQualitySensor,
    sensor_name="PM 10.0",
    unit_of_measurement=CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
    device_class=SensorDeviceClass.PM10,
):
    @property
    def icon(self):
        return "mdi:air-filter"

    @property
    def state(self):
        return self._aq_condition.pm_10_nowcast

    @property
    def extra_state_attributes(self):
        c = self._aq_condition
        return {
            "1_min": c.pm_10,
            "1_hr": c.pm_10_last_1_hour,
            "3_hr": c.pm_10_last_3_hours,
            "24_hr": c.pm_10_last_24_hours,
        }
