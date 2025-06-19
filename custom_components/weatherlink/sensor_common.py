import logging
import typing
from collections.abc import Iterable, Iterator

from . import WeatherLinkCoordinator, WeatherLinkEntity
from .api.conditions import ConditionRecord, CurrentConditions
from .units import Measurement

logger = logging.getLogger(__name__)


class WeatherLinkSensor(WeatherLinkEntity):
    _SENSORS: list[type["WeatherLinkSensor"]] = []

    @typing.overload
    def __init_subclass__(
        cls,
        *,
        sensor_name: str,
        unit_of_measurement: str | type[Measurement] | None,
        device_class: str | None,
        required_conditions: Iterable[type[ConditionRecord]] | None = None,
        **kwargs: typing.Any,
    ) -> None: ...

    @typing.overload
    def __init_subclass__(
        cls,
        *,
        abc: bool,
        **kwargs: typing.Any,
    ) -> None: ...

    def __init_subclass__(
        cls,
        abc: bool = False,
        **kwargs: typing.Any,
    ) -> None:
        if abc:
            super().__init_subclass__(**kwargs)
            return

        sensor_name = kwargs.pop("sensor_name")
        unit_of_measurement = kwargs.pop("unit_of_measurement")
        device_class = kwargs.pop("device_class")
        required_conditions = kwargs.pop("required_conditions", None)

        super().__init_subclass__(**kwargs)

        cls._sensor_name = sensor_name
        cls._unit_of_measurement = unit_of_measurement
        cls._device_class = device_class

        requirements: tuple[type[ConditionRecord], ...]
        try:
            requirements = getattr(cls, "_required_conditions")
        except AttributeError:
            requirements = ()
        cls._required_conditions = requirements + tuple(required_conditions)

        cls._SENSORS.append(cls)

    @classmethod
    def _conditions_ok(cls, conditions: CurrentConditions) -> bool:
        for req in cls._required_conditions:
            if req not in conditions:
                return False

        return True

    @classmethod
    def iter_sensors_for_coordinator(
        cls, coord: WeatherLinkCoordinator
    ) -> Iterator["WeatherLinkSensor"]:
        for cls in cls._SENSORS:
            if not cls._conditions_ok(coord.data):
                logger.debug(
                    "ignoring sensor %s because requirements are not met",
                    cls.__qualname__,
                )
                continue
            yield cls(coord)

    @property
    def name(self):
        return f"{self.coordinator.device_model_name} {self._sensor_name}"

    @property
    def unit_of_measurement(self):
        unit = self._unit_of_measurement
        if unit is None or isinstance(unit, str):
            return unit

        return self.units.by_measurement(unit).info.unit_of_measurement

    @property
    def device_class(self):
        return self._device_class


def round_optional(
    f: int | float | None, ndigits: int | None = None
) -> int | float | None:
    if not f:
        return f
    return round(f, ndigits)
