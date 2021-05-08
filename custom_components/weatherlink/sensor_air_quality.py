from .api import AirQualityCondition
from .sensor_common import WeatherLinkSensor

__all__ = ["AirQualityStatus"]


class AirQualitySensor(WeatherLinkSensor, abc=True):
    def __init_subclass__(
        cls,
        abc: bool = False,
        **kwargs,
    ) -> None:
        if not abc:
            kwargs["required_conditions"] = (AirQualityCondition,)
        super().__init_subclass__(**kwargs)

    @property
    def _aq_condition(self) -> AirQualityCondition:
        return self._conditions[AirQualityCondition]

    @property
    def name(self):
        return f"{self.coordinator.device_name} Air {self._sensor_name}"

    @property
    def unique_id(self):
        return f"{super().unique_id}-air_quality"


class AirQualityStatus(
    AirQualitySensor,
    sensor_name="Status",
    unit_of_measurement=None,
    device_class=None,
):
    @property
    def state(self):
        return self._aq_condition.last_report_time

    @property
    def device_state_attributes(self):
        c = self._aq_condition
        return {
            "pm_data_1_hr": c.pct_pm_data_last_1_hour,
            "pm_data_3_hr": c.pct_pm_data_last_3_hours,
            "pm_data_24_hr": c.pct_pm_data_last_24_hours,
            "pm_data_nowcast": c.pct_pm_data_nowcast,
        }


class Temperature(
    AirQualitySensor,
    sensor_name="Temperature",
    unit_of_measurement="°C",
    device_class="temperature",
):
    @property
    def state(self):
        return round(self._aq_condition.temp, 1)

    @property
    def device_state_attributes(self):
        c = self._aq_condition
        return {
            "dew_point": c.dew_point,
            "wet_bulb": c.wet_bulb,
            "heat_index": c.heat_index,
        }


class Humidity(
    AirQualitySensor,
    sensor_name="Humidity",
    unit_of_measurement="%",
    device_class="humidity",
):
    @property
    def state(self):
        return round(self._aq_condition.hum, 1)
