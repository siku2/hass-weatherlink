import logging
import typing
from typing import Iterable, Iterator, List, Optional, Type, Union

from . import WeatherLinkCoordinator, WeatherLinkEntity
from .api import ConditionRecord, CurrentConditions
from .units import Units

logger = logging.getLogger(__name__)


class WeatherLinkSensor(WeatherLinkEntity):
    _SENSORS: List[Type["WeatherLinkSensor"]] = []

    @typing.overload
    def __init_subclass__(
        cls,
        *,
        sensor_name: str,
        unit_of_measurement: Union[str, Type[Units], None],
        device_class: Optional[str],
        required_conditions: Iterable[Type[ConditionRecord]] = None,
        **kwargs,
    ) -> None:
        ...

    @typing.overload
    def __init_subclass__(
        cls,
        *,
        abc: bool,
        **kwargs,
    ) -> None:
        ...

    def __init_subclass__(
        cls,
        abc: bool = False,
        **kwargs,
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
        try:
            requirements = cls._required_conditions
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
            if not cls._conditions_ok(coord.current_conditions):
                logger.info("ignoring sensor %s because requirements are not met", cls)
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

        return self.units.by_units(unit).unit_of_measurement

    @property
    def device_class(self):
        return self._device_class


def round_optional(
    f: Optional[Union[int, float]], ndigits: int = None
) -> Optional[Union[int, float]]:
    if not f:
        return f
    return round(f, ndigits)
