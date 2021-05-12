from .api import IssCondition
from .sensor_common import WeatherLinkSensor, round_optional

__all__ = [
    "IssStatus",
    "Temperature",
    "ThswIndex",
    "Humidity",
    "WindSpeed",
    "WindBearing",
    "SolarRad",
    "UvIndex",
    "Rainfall",
    "Rainstorm",
]


class IssSensor(WeatherLinkSensor, abc=True):
    def __init_subclass__(
        cls,
        abc: bool = False,
        **kwargs,
    ) -> None:
        if not abc:
            kwargs["required_conditions"] = (IssCondition,)
        super().__init_subclass__(abc=abc, **kwargs)

    @property
    def _iss_condition(self) -> IssCondition:
        return self._conditions[IssCondition]

    @property
    def unique_id(self):
        return f"{super().unique_id}-iss"


class IssStatus(
    IssSensor,
    sensor_name="ISS Status",
    unit_of_measurement=None,
    device_class=None,
):
    @property
    def icon(self):
        return "mdi:information"

    @property
    def state(self):
        rx_state = self._iss_condition.rx_state
        if rx_state is None:
            return None
        return rx_state.name

    @property
    def device_state_attributes(self):
        c = self._iss_condition
        return {
            "txid": c.txid,
            "battery": c.trans_battery_flag,
        }


class Temperature(
    IssSensor,
    sensor_name="Temperature",
    unit_of_measurement="°C",
    device_class="temperature",
):
    @property
    def state(self):
        return round(self._iss_condition.temp, 1)

    @property
    def device_state_attributes(self):
        c = self._iss_condition
        return {
            "dew_point": round(c.dew_point, 1),
            "wet_bulb": round_optional(c.wet_bulb, 1),
            "heat_index": round(c.heat_index, 1),
            "wind_chill": round(c.wind_chill, 1),
            "thw_index": round(c.thw_index, 1),
            "thsw_index": round(c.thsw_index, 1),
        }


class ThswIndex(
    IssSensor,
    sensor_name="THSW index",
    unit_of_measurement="°C",
    device_class="temperature",
):
    @property
    def state(self):
        return round(self._iss_condition.thsw_index, 1)


class Humidity(
    IssSensor,
    sensor_name="Humidity",
    unit_of_measurement="%",
    device_class="humidity",
):
    @property
    def state(self):
        return round(self._iss_condition.hum, 1)


class WindSpeed(
    IssSensor,
    sensor_name="Wind speed",
    unit_of_measurement="km/h",
    device_class=None,
):
    @property
    def icon(self):
        return "mdi:weather-windy"

    @property
    def state(self):
        return round(self._iss_condition.wind_speed_avg_last_2_min, 1)

    @property
    def device_state_attributes(self):
        c = self._iss_condition
        return {
            "high": round(c.wind_speed_hi_last_2_min, 1),
            "10_min": round(c.wind_speed_avg_last_10_min, 1),
            "10_min_high": round(c.wind_speed_hi_last_10_min, 1),
        }


class WindBearing(
    IssSensor,
    sensor_name="Wind bearing",
    unit_of_measurement="°",
    device_class=None,
):
    @property
    def icon(self):
        return "mdi:compass-rose"

    @property
    def state(self):
        return round(self._iss_condition.wind_dir_scalar_avg_last_2_min, 1)

    @property
    def device_state_attributes(self):
        c = self._iss_condition
        return {
            "high_dir": round(c.wind_dir_at_hi_speed_last_2_min, 1),
            "10_min_dir": round(c.wind_dir_scalar_avg_last_10_min, 1),
            "10_min_high_dir": round(c.wind_dir_at_hi_speed_last_10_min, 1),
        }


class SolarRad(
    IssSensor,
    sensor_name="Solar rad",
    unit_of_measurement="W/m²",
    device_class=None,
):
    @property
    def icon(self):
        return "mdi:white-balance-sunny"

    @property
    def state(self):
        return self._iss_condition.solar_rad


class UvIndex(
    IssSensor,
    sensor_name="UV index",
    unit_of_measurement=None,
    device_class=None,
):
    @property
    def icon(self):
        return "mdi:shield-sun"

    @property
    def state(self):
        return round(self._iss_condition.uv_index, 1)


class RainRate(
    IssSensor,
    sensor_name="Rain rate",
    unit_of_measurement="mm/h",
    device_class=None,
):
    @property
    def icon(self):
        return "mdi:water"

    @property
    def state(self):
        return round(self._iss_condition.rain_rate_last, 1)

    @property
    def device_state_attributes(self):
        c = self._iss_condition
        return {
            "high": round_optional(c.rain_rate_hi, 1),
            "15_min_high": round(c.rain_rate_hi_last_15_min, 1),
        }


class Rainfall(
    IssSensor,
    sensor_name="Rainfall",
    unit_of_measurement="mm",
    device_class=None,
):
    @property
    def icon(self):
        return "mdi:weather-pouring"

    @property
    def state(self):
        return round(self._iss_condition.rainfall_daily, 1)

    @property
    def device_state_attributes(self):
        c = self._iss_condition
        return {
            "15_min": round_optional(c.rainfall_last_15_min, 1),
            "60_min": round_optional(c.rainfall_last_60_min, 1),
            "24_hr": round_optional(c.rainfall_last_24_hr, 1),
            "monthly": round(c.rainfall_monthly, 1),
            "yearly": round(c.rainfall_year, 1),
        }


class Rainstorm(
    IssSensor,
    sensor_name="Rainstorm",
    unit_of_measurement="mm",
    device_class=None,
):
    @property
    def icon(self):
        return "mdi:weather-lightning-rainy"

    @property
    def state(self):
        return round_optional(self._iss_condition.rain_storm, 1)

    @property
    def device_state_attributes(self):
        c = self._iss_condition
        return {
            "start": c.rain_storm_start_at,
            "last": round_optional(c.rain_storm_last, 1),
            "last_start": c.rain_storm_last_start_at,
            "last_end": c.rain_storm_last_end_at,
        }
