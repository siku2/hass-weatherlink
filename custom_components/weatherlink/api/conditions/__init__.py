import dataclasses
import enum
import logging
from collections.abc import Iterable, Mapping
from datetime import datetime
from typing import TypeVar

from .. import from_json
from .air_quality import AirQualityCondition
from .condition import ConditionRecord, ReceiverState
from .iss import CollectorSize, IssCondition
from .lss import LssBarCondition, LssTempHumCondition
from .moisture import MoistureCondition

__all__ = [
    "ConditionType",
    "CurrentConditions",
    "DeviceType",
    "AirQualityCondition",
    "ReceiverState",
    "ConditionRecord",
    "CollectorSize",
    "IssCondition",
    "LssBarCondition",
    "LssTempHumCondition",
    "MoistureCondition",
]

logger = logging.getLogger(__name__)


class ConditionType(enum.IntEnum):
    Iss = 1
    Moisture = 2
    LssBar = 3
    LssTempHum = 4
    AirQuality = 6
    """Sent by AirLink"""

    def record_class(self) -> type["ConditionRecord"]:
        return _COND2CLS[self]


class DeviceType(enum.Enum):
    WeatherLink = "WeatherLink"
    AirLink = "AirLink"

    def supports_real_time_api(self) -> bool:
        return self != self.AirLink


RecordT = TypeVar("RecordT", bound=ConditionRecord)


@dataclasses.dataclass()
class CurrentConditions(from_json.FromJson, Mapping[type[RecordT], RecordT]):
    did: str
    """the device serial number as a string"""
    ts: datetime
    """the timestamp of the moment the response was generated, with a resolution of seconds.

    If the time has not yet been synchronized from the network, this will instead measure the time in seconds since bootup.
    """

    conditions: list[ConditionRecord]
    """a list of current condition data records, one per logical sensor."""

    name: str | None = None
    """Only present for AirLink"""

    @classmethod
    def _from_json(cls, data: from_json.JsonObject, **kwargs):
        conditions = []
        raw_conditions = flatten_conditions(data["conditions"])
        for i, cond_data in enumerate(raw_conditions):
            try:
                cond = condition_from_json(cond_data, **kwargs)
            except Exception:
                if kwargs.get(cls.OPT_STRICT):
                    raise

                logger.exception(
                    f"failed to build condition record at index {i}: {cond_data!r}"
                )
                continue

            conditions.append(cond)

        return cls(
            did=data["did"],
            ts=datetime.fromtimestamp(data["ts"]),
            conditions=conditions,
            name=data.get("name"),
        )

    def __getitem__(self, cls: type[RecordT]) -> RecordT:
        try:
            return next(cond for cond in self.conditions if isinstance(cond, cls))
        except StopIteration:
            raise KeyError(repr(cls.__qualname__)) from None

    def __iter__(self) -> Iterable[ConditionRecord]:
        return iter(self.conditions)

    def __len__(self) -> int:
        return len(self.conditions)

    def get(self, cls: type[RecordT]) -> RecordT | None:
        try:
            return self[cls]
        except KeyError:
            return None

    def determine_device_type(self) -> DeviceType:
        if self.name is None:
            return DeviceType.WeatherLink
        else:
            return DeviceType.AirLink

    def determine_device_name(self) -> str:
        name = self.name
        if name:
            return name

        model_name = self.determine_device_type().name
        return f"{model_name} {self.did}"

    def update_from(self, other: "CurrentConditions") -> None:
        for other_condition in other:
            condition_cls = type(other_condition)
            try:
                condition: ConditionRecord = self[condition_cls]
            except KeyError:
                self.conditions.append(other_condition)
            else:
                condition.update_from(other_condition)


_STRUCTURE_TYPE_KEY = "data_structure_type"

_COND2CLS = {
    ConditionType.Iss: IssCondition,
    ConditionType.Moisture: MoistureCondition,
    ConditionType.LssBar: LssBarCondition,
    ConditionType.LssTempHum: LssTempHumCondition,
    ConditionType.AirQuality: AirQualityCondition,
}


def condition_from_json(data: from_json.JsonObject, **kwargs) -> ConditionRecord:
    cond_ty = ConditionType(data.pop(_STRUCTURE_TYPE_KEY))
    cls = cond_ty.record_class()
    return cls.from_json(data, **kwargs)


def flatten_conditions(
    conditions: Iterable[from_json.JsonObject],
) -> list[from_json.JsonObject]:
    cond_by_type = {}
    for cond in conditions:
        cond_type = cond[_STRUCTURE_TYPE_KEY]
        try:
            existing = cond_by_type[cond_type]
        except KeyError:
            cond_by_type[cond_type] = cond
        else:
            from_json.update_dict_where_none(existing, cond)

    return list(cond_by_type.values())
