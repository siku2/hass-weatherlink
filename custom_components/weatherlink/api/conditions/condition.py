import abc
import dataclasses
import enum

from ..from_json import FromJson

__all__ = [
    "ConditionRecord",
    "ReceiverState",
]


class ReceiverState(enum.IntEnum):
    Tracking = 0
    """Transmitter has been acquired and is actively being received."""
    Synched = 1
    """Transmitter has been acquired, but we have missed 1-14 packets in a row."""
    Scanning = 2
    """Transmitter has not been acquired yet, or we’ve lost it (more than 15 missed packets in a row)."""


@dataclasses.dataclass()
class ConditionRecord(FromJson, abc.ABC):
    lsid: int | None
    """the numeric logic sensor identifier, or null if the device has not been registered"""

    def update_from(self, other: "ConditionRecord") -> None:
        for key, value in dataclasses.asdict(other).items():
            if value is None:
                continue
            setattr(self, key, value)
