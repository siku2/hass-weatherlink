from typing import Optional

from . import units
from .api.conditions import IssCondition
from .const import DECIMALS_HUMIDITY, DECIMALS_RADIATION, DECIMALS_UV
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
    def extra_state_attributes(self):
        c = self._iss_condition
        return {
            "txid": c.txid,
            "battery": c.trans_battery_flag,
        }


class Temperature(
    IssSensor,
    sensor_name="Temperature",
    unit_of_measurement=units.Temperature,
    device_class="temperature",
):
    @property
    def state(self):
        return self.units.temperature.convert_optional(self._iss_condition.temp)

    @property
    def extra_state_attributes(self):
        c = self._iss_condition
        u = self.units.temperature
        return {
            "dew_point": u.convert_optional(c.dew_point),
            "wet_bulb": u.convert_optional(c.wet_bulb),
            "heat_index": u.convert_optional(c.heat_index),
            "wind_chill": u.convert_optional(c.wind_chill),
            "thw_index": u.convert_optional(c.thw_index),
            "thsw_index": u.convert_optional(c.thsw_index),
        }


class ThswIndex(
    IssSensor,
    sensor_name="THSW index",
    unit_of_measurement=units.Temperature,
    device_class="temperature",
):
    @property
    def state(self):
        return self.units.temperature.convert_optional(self._iss_condition.thsw_index)


class Humidity(
    IssSensor,
    sensor_name="Humidity",
    unit_of_measurement="%",
    device_class="humidity",
):
    @property
    def state(self):
        return round_optional(self._iss_condition.hum, DECIMALS_HUMIDITY)


class WindSpeed(
    IssSensor,
    sensor_name="Wind speed",
    unit_of_measurement=units.WindSpeed,
    device_class=None,
):
    @property
    def icon(self):
        return "mdi:weather-windy"

    @property
    def state(self):
        return self.units.wind_speed.convert_optional(
            self._iss_condition.wind_speed_avg_last_2_min
        )

    @property
    def extra_state_attributes(self):
        c = self._iss_condition
        u = self.units.wind_speed
        return {
            "10_min": u.convert_optional(c.wind_speed_avg_last_10_min),
        }


class WindSpeedNow(
    IssSensor,
    sensor_name="Wind speed last",
    unit_of_measurement=units.WindSpeed,
    device_class=None,
):
    @property
    def icon(self):
        return "mdi:weather-windy"

    @property
    def state(self):
        return self.units.wind_speed.convert_optional(
            self._iss_condition.wind_speed_last
        )


class WindMaxSpeed(
    IssSensor,
    sensor_name="Wind max speed",
    unit_of_measurement=units.WindSpeed,
    device_class=None,
):
    @property
    def icon(self):
        return "mdi:weather-windy"

    @property
    def state(self):
        return self.units.wind_speed.convert_optional(
            self._iss_condition.wind_speed_hi_last_2_min
        )

    @property
    def extra_state_attributes(self):
        c = self._iss_condition
        u = self.units.wind_speed
        return {
            "10_min": u.convert_optional(c.wind_speed_hi_last_10_min),
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
        return self._iss_condition.wind_dir_scalar_avg_last_2_min

    @property
    def extra_state_attributes(self):
        c = self._iss_condition
        return {
            "high": c.wind_dir_at_hi_speed_last_2_min,
            "10_min": c.wind_dir_scalar_avg_last_10_min,
            "10_min_high": c.wind_dir_at_hi_speed_last_10_min,
        }


class WindBearingNow(
    IssSensor,
    sensor_name="Wind bearing last",
    unit_of_measurement="°",
    device_class=None,
):
    @property
    def icon(self):
        return "mdi:compass-rose"

    @property
    def state(self):
        return self._iss_condition.wind_dir_last


class WindDirection(
    IssSensor,
    sensor_name="Wind direction",
    unit_of_measurement=None,
    device_class=None,
):
    _DIRECTIONS = (
        "N",
        "NNE",
        "NE",
        "ENE",
        "E",
        "ESE",
        "SE",
        "SSE",
        "S",
        "SSW",
        "SW",
        "WSW",
        "W",
        "WNW",
        "NW",
        "NNW",
        "N",
    )

    @property
    def icon(self):
        return "mdi:compass"

    @property
    def state(self):
        return self.bearing_to_dir(self._iss_condition.wind_dir_scalar_avg_last_2_min)

    @property
    def extra_state_attributes(self):
        c = self._iss_condition
        return {
            "high": self.bearing_to_dir(c.wind_dir_at_hi_speed_last_2_min),
            "10_min": self.bearing_to_dir(c.wind_dir_scalar_avg_last_10_min),
            "10_min_high": self.bearing_to_dir(c.wind_dir_at_hi_speed_last_10_min),
        }

    @classmethod
    def bearing_to_dir(cls, deg: Optional[int]) -> Optional[str]:
        if deg is None:
            return None
        return cls._DIRECTIONS[int(((deg % 360) + 11.25) / 22.5)]


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
        return round_optional(self._iss_condition.solar_rad, DECIMALS_RADIATION)


class UvIndex(
    IssSensor,
    sensor_name="UV index",
    unit_of_measurement="UV Index",
    device_class=None,
):
    @property
    def icon(self):
        return "mdi:shield-sun"

    @property
    def state(self):
        return round_optional(self._iss_condition.uv_index, DECIMALS_UV)


class RainRate(
    IssSensor,
    sensor_name="Rain rate",
    unit_of_measurement=units.RainRate,
    device_class=None,
):
    @property
    def icon(self):
        return "mdi:water"

    @property
    def state(self):
        return self.units.rain_rate.convert(self._iss_condition.rain_rate_last)

    @property
    def extra_state_attributes(self):
        c = self._iss_condition
        u = self.units.rain_rate
        return {
            "high": u.convert_optional(c.rain_rate_hi),
            "15_min_high": u.convert_optional(c.rain_rate_hi_last_15_min),
        }


class Rainfall(
    IssSensor,
    sensor_name="Rainfall",
    unit_of_measurement=units.Rainfall,
    device_class=None,
):
    @property
    def icon(self):
        return "mdi:weather-pouring"

    @property
    def state(self):
        return self.units.rainfall.convert(self._iss_condition.rainfall_daily)

    @property
    def extra_state_attributes(self):
        c = self._iss_condition
        u = self.units.rainfall
        return {
            "15_min": u.convert_optional(c.rainfall_last_15_min),
            "60_min": u.convert_optional(c.rainfall_last_60_min),
            "24_hr": u.convert_optional(c.rainfall_last_24_hr),
            "monthly": u.convert(c.rainfall_monthly),
            "yearly": u.convert(c.rainfall_year),
        }


class Rainstorm(
    IssSensor,
    sensor_name="Rainstorm",
    unit_of_measurement=units.Rainfall,
    device_class=None,
):
    @property
    def icon(self):
        return "mdi:weather-lightning-rainy"

    @property
    def state(self):
        return self.units.rainfall.convert_optional(self._iss_condition.rain_storm)

    @property
    def extra_state_attributes(self):
        c = self._iss_condition
        u = self.units.rainfall
        return {
            "start": c.rain_storm_start_at,
            "last": u.convert_optional(c.rain_storm_last),
            "last_start": c.rain_storm_last_start_at,
            "last_end": c.rain_storm_last_end_at,
        }
