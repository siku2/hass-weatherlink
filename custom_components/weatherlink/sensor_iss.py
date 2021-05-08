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
    def name(self):
        return f"{self.coordinator.device_name} ISS {self._sensor_name}"

    @property
    def unique_id(self):
        return f"{super().unique_id}-iss"


class IssStatus(
    IssSensor,
    sensor_name="Status",
    unit_of_measurement=None,
    device_class=None,
):
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
            "dew_point": c.dew_point,
            "wet_bulb": c.wet_bulb,
            "heat_index": c.heat_index,
            "wind_chill": c.wind_chill,
            "thw_index": c.thw_index,
            "thsw_index": c.thsw_index,
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
    def state(self):
        return round(self._iss_condition.wind_speed_avg_last_2_min, 1)

    @property
    def device_state_attributes(self):
        c = self._iss_condition
        return {
            "high": c.wind_speed_hi_last_2_min,
            "10_min": c.wind_speed_avg_last_10_min,
            "10_min_high": c.wind_speed_hi_last_10_min,
        }


class WindBearing(
    IssSensor,
    sensor_name="Wind bearing",
    unit_of_measurement="°",
    device_class=None,
):
    @property
    def state(self):
        return round(self._iss_condition.wind_dir_scalar_avg_last_2_min, 1)

    @property
    def device_state_attributes(self):
        c = self._iss_condition
        return {
            "high_dir": c.wind_dir_at_hi_speed_last_2_min,
            "10_min_dir": c.wind_dir_scalar_avg_last_10_min,
            "10_min_high_dir": c.wind_dir_at_hi_speed_last_10_min,
        }


class SolarRad(
    IssSensor,
    sensor_name="Solar rad",
    unit_of_measurement="W/m²",
    device_class=None,
):
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
    def state(self):
        return self._iss_condition.uv_index


class Rainfall(
    IssSensor,
    sensor_name="Rainfall",
    unit_of_measurement="mm",
    device_class=None,
):
    @property
    def state(self):
        return round(self._iss_condition.rainfall_daily, 1)

    @property
    def device_state_attributes(self):
        c = self._iss_condition
        return {
            "rate": round(c.rain_rate_last, 1),
            "rate_high": round(c.rain_rate_hi, 1),
            "15_min": round(c.rainfall_last_15_min, 1),
            "15_min_high": round(c.rain_rate_hi_last_15_min, 1),
            "60_min": round(c.rainfall_last_60_min, 1),
            "24_hr": round(c.rainfall_last_24_hr),
            "monthly": round(c.rainfall_monthly),
            "yearly": round(c.rainfall_year),
        }


class Rainstorm(
    IssSensor,
    sensor_name="Rainstorm",
    unit_of_measurement="mm",
    device_class=None,
):
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
