import dataclasses
import enum
from datetime import datetime
from typing import Any, override

from .. import from_json
from .condition import ConditionRecord, ReceiverState

__all__ = [
    "CollectorSize",
    "IssCondition",
]


class CollectorSize(enum.IntEnum):
    Millimeter01 = 3
    """0.1 mm"""
    Millimeter02 = 2
    """0.2 mm"""

    Inches001 = 1
    """(0.01")"""
    Inches0001 = 4
    """(0.001")"""

    def to_mm(self, value: float | None) -> float:
        mul = _COLLECTOR2MM[self]
        return value * mul if value is not None else mul


@dataclasses.dataclass()
class IssCondition(ConditionRecord):
    txid: int
    """transmitter ID"""

    rain_size: CollectorSize
    """rain collector type/size"""

    rain_rate_last: float
    rain_rate_last_counts: int
    """most recent valid rain rate **(counts/hour)**"""

    rainfall_daily: float
    rainfall_daily_counts: int
    """total rain count since local midnight **(counts)**"""
    rainfall_monthly: float
    rainfall_monthly_counts: int
    """total rain count since first of month at local midnight **(counts)**"""
    rainfall_year: float
    rainfall_year_counts: int
    """total rain count since first of user-chosen month at local midnight **(counts)**"""

    rx_state: ReceiverState | None = None
    """configured radio receiver state"""

    temp: float | None = None
    """most recent valid temperature"""
    hum: float | None = None
    """most recent valid humidity **(%RH)**"""
    dew_point: float | None = None
    """"""
    wet_bulb: float | None = None
    """"""
    heat_index: float | None = None
    """"""
    wind_chill: float | None = None
    """"""
    thw_index: float | None = None
    """"""
    thsw_index: float | None = None
    """"""

    wind_speed_last: float | None = None
    """most recent valid wind speed **(km/h)**"""
    wind_dir_last: int | None = None
    """most recent valid wind direction **(°degree)**"""

    wind_speed_avg_last_1_min: float | None = None
    """average wind speed over last 1 min **(km/h)**"""
    wind_dir_scalar_avg_last_1_min: int | None = None
    """scalar average wind direction over last 1 min **(°degree)**"""

    wind_speed_avg_last_2_min: float | None = None
    """average wind speed over last 2 min **(km/h)**"""
    wind_dir_scalar_avg_last_2_min: int | None = None
    """scalar average wind direction over last 2 min **(°degree)**"""

    wind_speed_hi_last_2_min: float | None = None
    """maximum wind speed over last 2 min **(km/h)**"""
    wind_dir_at_hi_speed_last_2_min: int | None = None
    """gust wind direction over last 2 min **(°degree)**"""

    wind_speed_avg_last_10_min: float | None = None
    """average wind speed over last 10 min **(km/h)**"""
    wind_dir_scalar_avg_last_10_min: int | None = None
    """scalar average wind direction over last 10 min **(°degree)**"""

    wind_speed_hi_last_10_min: float | None = None
    """maximum wind speed over last 10 min **(km/h)**"""
    wind_dir_at_hi_speed_last_10_min: int | None = None
    """gust wind direction over last 10 min **(°degree)**"""

    rain_rate_hi: float | None = None
    rain_rate_hi_counts: int | None = None
    """highest rain rate over last 1 min **(counts/hour)**"""
    rain_rate_hi_last_15_min: float | None = None
    rain_rate_hi_last_15_min_counts: int | None = None
    """highest rain rate over last 15 min **(counts/hour)**"""

    rainfall_last_15_min: float | None = None
    rainfall_last_15_min_counts: int | None = None
    """total rain count over last 15 min **(counts)**"""
    rainfall_last_60_min: float | None = None
    rainfall_last_60_min_counts: int | None = None
    """total rain count for last 60 min **(counts)**"""
    rainfall_last_24_hr: float | None = None
    rainfall_last_24_hr_counts: int | None = None
    """total rain count for last 24 hours **(counts)**"""

    rain_storm: float | None = None
    rain_storm_counts: int | None = None
    """total rain count since last 24 hour long break in rain **(counts)**"""
    rain_storm_start_at: datetime | None = None
    """timestamp of current rain storm start"""

    solar_rad: int | None = None
    """most recent solar radiation **(W/m²)**"""
    uv_index: float | None = None
    """most recent UV index **(Index)**"""

    trans_battery_flag: int | None = None
    """transmitter battery status flag"""

    rain_storm_last: float | None = None
    rain_storm_last_counts: int | None = None
    """total rain count since last 24 hour long break in rain **(counts)**"""
    rain_storm_last_start_at: datetime | None = None
    """timestamp of last rain storm start **(sec)**"""
    rain_storm_last_end_at: datetime | None = None
    """timestamp of last rain storm end **(sec)**"""

    @classmethod
    @override
    def _from_json(cls, data: from_json.JsonObject, **kwargs: Any):
        collector = CollectorSize(data["rain_size"])
        data["rain_size"] = collector
        from_json.keys_from_aliases(
            data,
            rainfall_last_15_min="rain_15_min",
            rainfall_last_60_min="rain_60_min",
            rainfall_last_24_hr="rain_24_hr",
        )
        keys_counts_to_mm(
            data,
            collector,
            "rain_rate_last",
            "rain_rate_hi",
            "rainfall_last_15_min",
            "rain_rate_hi_last_15_min",
            "rainfall_last_60_min",
            "rainfall_last_24_hr",
            "rain_storm",
            "rainfall_daily",
            "rainfall_monthly",
            "rainfall_year",
            "rain_storm_last",
        )
        from_json.apply_converters(data, rx_state=ReceiverState)
        from_json.keys_to_celsius(
            data,
            "temp",
            "dew_point",
            "wet_bulb",
            "heat_index",
            "wind_chill",
            "thw_index",
            "thsw_index",
        )
        from_json.keys_to_datetime(
            data,
            "rain_storm_start_at",
            "rain_storm_last_start_at",
            "rain_storm_last_end_at",
        )
        from_json.keys_to_kph(
            data,
            "wind_speed_last",
            "wind_speed_avg_last_1_min",
            "wind_speed_avg_last_2_min",
            "wind_speed_hi_last_2_min",
            "wind_speed_avg_last_10_min",
            "wind_speed_hi_last_10_min",
        )
        return cls(**data)


_IN2MM = 25.4
_COLLECTOR2MM = {
    CollectorSize.Millimeter01: 0.1,
    CollectorSize.Millimeter02: 0.2,
    CollectorSize.Inches001: 0.01 * _IN2MM,
    CollectorSize.Inches0001: 0.001 * _IN2MM,
}


def keys_counts_to_mm(d: from_json.JsonObject, collector: CollectorSize, *keys: str):
    for key in keys:
        counts = d.get(key)
        d[f"{key}_counts"] = counts
        if counts:
            d[key] = collector.to_mm(counts)
