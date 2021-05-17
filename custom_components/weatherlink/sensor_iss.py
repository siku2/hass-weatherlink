from .api import IssCondition
from .const import (
    DECIMALS_DIRECTION,
    DECIMALS_HUMIDITY,
    DECIMALS_RADIATION,
    DECIMALS_RAIN_RATE,
    DECIMALS_RAIN_VOLUME,
    DECIMALS_SPEED,
    DECIMALS_TEMPERATURE,
    DECIMALS_UV,
)
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
        return round(self._iss_condition.temp, DECIMALS_TEMPERATURE)

    @property
    def device_state_attributes(self):
        c = self._iss_condition
        return {
            "dew_point": round(c.dew_point, DECIMALS_TEMPERATURE),
            "wet_bulb": round_optional(c.wet_bulb, DECIMALS_TEMPERATURE),
            "heat_index": round(c.heat_index, DECIMALS_TEMPERATURE),
            "wind_chill": round(c.wind_chill, DECIMALS_TEMPERATURE),
            "thw_index": round(c.thw_index, DECIMALS_TEMPERATURE),
            "thsw_index": round(c.thsw_index, DECIMALS_TEMPERATURE),
        }


class ThswIndex(
    IssSensor,
    sensor_name="THSW index",
    unit_of_measurement="°C",
    device_class="temperature",
):
    @property
    def state(self):
        return round(self._iss_condition.thsw_index, DECIMALS_TEMPERATURE)


class Humidity(
    IssSensor,
    sensor_name="Humidity",
    unit_of_measurement="%",
    device_class="humidity",
):
    @property
    def state(self):
        return round(self._iss_condition.hum, DECIMALS_HUMIDITY)


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
        return round(self._iss_condition.wind_speed_avg_last_2_min, DECIMALS_SPEED)

    @property
    def device_state_attributes(self):
        c = self._iss_condition
        return {
            "10_min": round(c.wind_speed_avg_last_10_min, DECIMALS_SPEED),
        }


class WindMaxSpeed(
    IssSensor,
    sensor_name="Wind max speed",
    unit_of_measurement="km/h",
    device_class=None,
):
    @property
    def icon(self):
        return "mdi:weather-windy"

    @property
    def state(self):
        return round_optional(
            self._iss_condition.wind_speed_hi_last_2_min, DECIMALS_SPEED
        )

    @property
    def device_state_attributes(self):
        c = self._iss_condition
        return {
            "10_min": round(c.wind_speed_hi_last_10_min, DECIMALS_SPEED),
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
        return round(
            self._iss_condition.wind_dir_scalar_avg_last_2_min, DECIMALS_DIRECTION
        )

    @property
    def device_state_attributes(self):
        c = self._iss_condition
        return {
            "high": round(c.wind_dir_at_hi_speed_last_2_min, DECIMALS_DIRECTION),
            "10_min": round_optional(
                c.wind_dir_scalar_avg_last_10_min, DECIMALS_DIRECTION
            ),
            "10_min_high": round(
                c.wind_dir_at_hi_speed_last_10_min, DECIMALS_DIRECTION
            ),
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
        return round(self._iss_condition.solar_rad, DECIMALS_RADIATION)


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
        return round(self._iss_condition.uv_index, DECIMALS_UV)


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
        return round(self._iss_condition.rain_rate_last, DECIMALS_RAIN_RATE)

    @property
    def device_state_attributes(self):
        c = self._iss_condition
        return {
            "high": round_optional(c.rain_rate_hi, DECIMALS_RAIN_RATE),
            "15_min_high": round(c.rain_rate_hi_last_15_min, DECIMALS_RAIN_RATE),
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
        return round(self._iss_condition.rainfall_daily, DECIMALS_RAIN_VOLUME)

    @property
    def device_state_attributes(self):
        c = self._iss_condition
        return {
            "15_min": round_optional(c.rainfall_last_15_min, DECIMALS_RAIN_VOLUME),
            "60_min": round_optional(c.rainfall_last_60_min, DECIMALS_RAIN_VOLUME),
            "24_hr": round_optional(c.rainfall_last_24_hr, DECIMALS_RAIN_VOLUME),
            "monthly": round(c.rainfall_monthly, DECIMALS_RAIN_VOLUME),
            "yearly": round(c.rainfall_year, DECIMALS_RAIN_VOLUME),
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
        return round_optional(self._iss_condition.rain_storm, DECIMALS_RAIN_VOLUME)

    @property
    def device_state_attributes(self):
        c = self._iss_condition
        return {
            "start": c.rain_storm_start_at,
            "last": round_optional(c.rain_storm_last, DECIMALS_RAIN_VOLUME),
            "last_start": c.rain_storm_last_start_at,
            "last_end": c.rain_storm_last_end_at,
        }
