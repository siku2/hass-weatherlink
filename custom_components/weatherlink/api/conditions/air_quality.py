import dataclasses
from datetime import datetime
from typing import Any, override

from .. import from_json
from .condition import ConditionRecord

__all__ = [
    "AirQualityCondition",
]


@dataclasses.dataclass()
class AirQualityCondition(ConditionRecord):
    temp: float
    """most recent valid air temperature reading"""
    hum: float
    """most recent valid humidity reading in %RH"""
    dew_point: float
    """dew point temperature calculated from the most recent valid temperature / humidity reading"""
    wet_bulb: float
    """wet bulb temperature calculated from the most recent valid temperature / humidity reading and user elevation"""
    heat_index: float
    """heat index temperature calculated from the most recent valid temperature / humidity reading"""

    pm_1_last: int
    """most recent valid PM 1.0 reading calculated using atmospheric calibration in µg/m^3."""
    pm_2p5_last: int
    """most recent valid PM 2.5 reading calculated using atmospheric calibration in µg/m^3."""
    pm_10_last: int
    """most recent valid PM 10.0 reading calculated using atmospheric calibration in µg/m^3."""

    pm_1: float
    """average of all PM 1.0 readings in the last minute calculated using atmospheric calibration in µg/m^3."""
    pm_2p5: float
    """average of all PM 2.5 readings in the last minute calculated using atmospheric calibration in µg/m^3."""
    pm_10: float
    """average of all PM 10.0 readings in the last minute calculated using atmospheric calibration in µg/m^3."""

    pm_2p5_last_1_hour: float
    """average of all PM 2.5 readings in the last hour calculated using atmospheric calibration in µg/m^3."""
    pm_2p5_last_3_hours: float
    """average of all PM 2.5 readings in the last 3 hours calculated using atmospheric calibration in µg/m^3."""
    pm_2p5_last_24_hours: float
    """weighted average of all PM 2.5 readings in the last 24 hours calculated using atmospheric calibration in µg/m^3."""
    pm_2p5_nowcast: float
    """weighted average of all PM 2.5 readings in the last 12 hours calculated using atmospheric calibration in µg/m^3."""

    pm_10_last_1_hour: float
    """average of all PM 10.0 readings in the last hour calculated using atmospheric calibration in µg/m^3."""
    pm_10_last_3_hours: float
    """average of all PM 10.0 readings in the last 3 hours calculated using atmospheric calibration in µg/m^3."""
    pm_10_last_24_hours: float
    """weighted average of all PM 10.0 readings in the last 24 hours calculated using atmospheric calibration in µg/m^3."""
    pm_10_nowcast: float
    """weighted average of all PM 10.0 readings in the last 12 hours calculated using atmospheric calibration in µg/m^3."""

    last_report_time: datetime
    """timestamp of the last time a valid reading was received from the PM sensor (or time since boot if time has not been synced), with resolution of seconds."""

    pct_pm_data_last_1_hour: int
    """amount of PM data available to calculate averages in the last hour (rounded down to the nearest percent)"""
    pct_pm_data_last_3_hours: int
    """amount of PM data available to calculate averages in the last 3 hours (rounded down to the nearest percent)"""
    pct_pm_data_last_24_hours: int
    """amount of PM data available to calculate averages in the last 24 hours (rounded down to the nearest percent)"""
    pct_pm_data_nowcast: int
    """amount of PM data available to calculate averages in the last 12 hours (rounded down to the nearest percent)"""

    @classmethod
    @override
    def _from_json(cls, data: from_json.JsonObject, **kwargs: Any):
        from_json.keys_to_celsius(data, "temp", "dew_point", "wet_bulb", "heat_index")
        from_json.keys_to_datetime(data, "last_report_time")
        return cls(**data)
