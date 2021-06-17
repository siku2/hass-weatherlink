from datetime import datetime

from . import units
from .api.conditions import AirQualityCondition
from .const import DECIMALS_HUMIDITY
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
    unit_of_measurement=units.Temperature,
    device_class="temperature",
):
    @property
    def state(self):
        return self.units.temperature.convert(self._aq_condition.temp)

    @property
    def device_state_attributes(self):
        c = self._aq_condition
        u = self.units.temperature
        return {
            "dew_point": u.convert(c.dew_point),
            "wet_bulb": u.convert(c.wet_bulb),
            "heat_index": u.convert(c.heat_index),
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
    unit_of_measurement=units.Pm,
    device_class=None,
):
    @property
    def icon(self):
        return "mdi:air-filter"

    @property
    def state(self):
        return self.units.pm.convert(self._aq_condition.pm_1)


class Pm2p5(
    AirQualitySensor,
    sensor_name="PM 2.5",
    unit_of_measurement=units.Pm,
    device_class=None,
):
    @property
    def icon(self):
        return "mdi:air-filter"

    @property
    def state(self):
        return self.units.pm.convert(self._aq_condition.pm_2p5_nowcast)

    @property
    def device_state_attributes(self):
        c = self._aq_condition
        u = self.units.pm
        return {
            "1_min": u.convert(c.pm_2p5),
            "1_hr": u.convert(c.pm_2p5_last_1_hour),
            "3_hr": u.convert(c.pm_2p5_last_3_hours),
            "24_hr": u.convert(c.pm_2p5_last_24_hours),
        }


class Pm10p0(
    AirQualitySensor,
    sensor_name="PM 10.0",
    unit_of_measurement=units.Pm,
    device_class=None,
):
    @property
    def icon(self):
        return "mdi:air-filter"

    @property
    def state(self):
        return self.units.pm.convert(self._aq_condition.pm_10_nowcast)

    @property
    def device_state_attributes(self):
        c = self._aq_condition
        u = self.units.pm
        return {
            "1_min": u.convert(c.pm_10),
            "1_hr": u.convert(c.pm_10_last_1_hour),
            "3_hr": u.convert(c.pm_10_last_3_hours),
            "24_hr": u.convert(c.pm_10_last_24_hours),
        }
