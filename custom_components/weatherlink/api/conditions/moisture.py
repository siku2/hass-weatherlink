import dataclasses
from typing import Any

from .. import from_json
from .condition import ConditionRecord, ReceiverState

__all__ = [
    "MoistureCondition",
]


@dataclasses.dataclass()
class MoistureCondition(ConditionRecord):
    txid: int
    rx_state: ReceiverState | None
    """configured radio receiver state"""

    temp_1: float | None
    """most recent valid soil temp slot 1"""
    temp_2: float | None
    """most recent valid soil temp slot 2"""
    temp_3: float | None
    """most recent valid soil temp slot 3"""
    temp_4: float | None
    """most recent valid soil temp slot 4"""

    moist_soil_1: float | None
    """most recent valid soil moisture slot 1 **(|cb|)**"""
    moist_soil_2: float | None
    """most recent valid soil moisture slot 2 **(|cb|)**"""
    moist_soil_3: float | None
    """most recent valid soil moisture slot 3 **(|cb|)**"""
    moist_soil_4: float | None
    """most recent valid soil moisture slot 4 **(|cb|)**"""

    wet_leaf_1: float | None
    """most recent valid leaf wetness slot 1"""
    wet_leaf_2: float | None
    """most recent valid leaf wetness slot 2"""

    trans_battery_flag: int | None
    """transmitter battery status flag"""

    @classmethod
    def _from_json(cls, data: from_json.JsonObject, **kwargs: Any):
        from_json.apply_converters(data, rx_state=ReceiverState)
        from_json.keys_to_celsius(data, "temp_1", "temp_2", "temp_3", "temp_4")
        return cls(**data)
