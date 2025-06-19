import dataclasses
from typing import Any

from .. import from_json
from .condition import ConditionRecord

__all__ = [
    "LssBarCondition",
    "LssTempHumCondition",
]


@dataclasses.dataclass()
class LssBarCondition(ConditionRecord):
    bar_sea_level: float
    """most recent bar sensor reading with elevation adjustment **(hpa)**"""
    bar_trend: float | None
    """current 3 hour bar trend **(hpa)**"""
    bar_absolute: float
    """raw bar sensor reading **(hpa)**"""

    @classmethod
    def _from_json(cls, data: from_json.JsonObject, **kwargs: Any):
        from_json.keys_to_hpa(data, "bar_sea_level", "bar_trend", "bar_absolute")
        return cls(**data)


@dataclasses.dataclass()
class LssTempHumCondition(ConditionRecord):
    temp_in: float
    """most recent valid inside temp"""
    hum_in: float
    """most recent valid inside humidity **(%RH)**"""
    dew_point_in: float
    """"""
    heat_index_in: float
    """"""

    @classmethod
    def _from_json(cls, data: from_json.JsonObject, **kwargs: Any):
        from_json.keys_to_celsius(data, "temp_in", "dew_point_in", "heat_index_in")
        return cls(**data)
