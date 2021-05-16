from datetime import datetime

from .api import AirQualityCondition
from .const import DECIMALS_HUMIDITY, DECIMALS_PM, DECIMALS_TEMPERATURE
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
    def device_state_attributes(self):
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
    unit_of_measurement="°C",
    device_class="temperature",
):
    @property
    def state(self):
        return round(self._aq_condition.temp, DECIMALS_TEMPERATURE)

    @property
    def device_state_attributes(self):
        c = self._aq_condition
        return {
            "dew_point": round(c.dew_point, DECIMALS_TEMPERATURE),
            "wet_bulb": round(c.wet_bulb, DECIMALS_TEMPERATURE),
            "heat_index": round(c.heat_index, DECIMALS_TEMPERATURE),
        }


class Humidity(
    AirQualitySensor,
    sensor_name="Humidity",
    unit_of_measurement="%",
    device_class="humidity",
):
    @property
    def state(self):
        return round(self._aq_condition.hum, DECIMALS_HUMIDITY)


class Pm1p0(
    AirQualitySensor,
    sensor_name="PM 1.0",
    unit_of_measurement="µg/m³",
    device_class=None,
):
    @property
    def icon(self):
        return "mdi:air-filter"

    @property
    def state(self):
        return round(self._aq_condition.pm_1, DECIMALS_PM)


class Pm2p5(
    AirQualitySensor,
    sensor_name="PM 2.5",
    unit_of_measurement="µg/m³",
    device_class=None,
):
    @property
    def icon(self):
        return "mdi:air-filter"

    @property
    def state(self):
        return round(self._aq_condition.pm_2p5_nowcast, DECIMALS_PM)

    @property
    def device_state_attributes(self):
        c = self._aq_condition
        return {
            "1_min": round(c.pm_2p5, DECIMALS_PM),
            "1_hr": round(c.pm_2p5_last_1_hour, DECIMALS_PM),
            "3_hr": round(c.pm_2p5_last_3_hours, DECIMALS_PM),
            "24_hr": round(c.pm_2p5_last_24_hours, DECIMALS_PM),
        }


class Pm10p0(
    AirQualitySensor,
    sensor_name="PM 10.0",
    unit_of_measurement="µg/m³",
    device_class=None,
):
    @property
    def icon(self):
        return "mdi:air-filter"

    @property
    def state(self):
        return round(self._aq_condition.pm_10_nowcast, DECIMALS_PM)

    @property
    def device_state_attributes(self):
        c = self._aq_condition
        return {
            "1_min": round(c.pm_10, DECIMALS_PM),
            "1_hr": round(c.pm_10_last_1_hour, DECIMALS_PM),
            "3_hr": round(c.pm_10_last_3_hours, DECIMALS_PM),
            "24_hr": round(c.pm_10_last_24_hours, DECIMALS_PM),
        }
