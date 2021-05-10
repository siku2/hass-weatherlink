from .api import AirQualityCondition
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
            "dew_point": round(c.dew_point, 1),
            "wet_bulb": round(c.wet_bulb, 1),
            "heat_index": round(c.heat_index, 1),
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


class Pm1p0(
    AirQualitySensor,
    sensor_name="PM 1.0",
    unit_of_measurement="µg/m^3",
    device_class=None,
):
    @property
    def icon(self):
        return "mdi:air-filter"

    @property
    def state(self):
        return round(self._aq_condition.pm_1, 2)


class Pm2p5(
    AirQualitySensor,
    sensor_name="PM 2.5",
    unit_of_measurement="µg/m^3",
    device_class=None,
):
    @property
    def icon(self):
        return "mdi:air-filter"

    @property
    def state(self):
        return round(self._aq_condition.pm_2p5_nowcast, 2)

    @property
    def device_state_attributes(self):
        c = self._aq_condition
        return {
            "1_min": round(c.pm_2p5, 2),
            "1_hr": round(c.pm_2p5_last_1_hour, 2),
            "3_hr": round(c.pm_2p5_last_3_hours, 2),
            "24_hr": round(c.pm_2p5_last_24_hours, 2),
        }


class Pm10p0(
    AirQualitySensor,
    sensor_name="PM 10.0",
    unit_of_measurement="µg/m^3",
    device_class=None,
):
    @property
    def icon(self):
        return "mdi:air-filter"

    @property
    def state(self):
        return round(self._aq_condition.pm_10_nowcast, 2)

    @property
    def device_state_attributes(self):
        c = self._aq_condition
        return {
            "1_min": round(c.pm_10, 2),
            "1_hr": round(c.pm_10_last_1_hour, 2),
            "3_hr": round(c.pm_10_last_3_hours, 2),
            "24_hr": round(c.pm_10_last_24_hours, 2),
        }
