import logging
import typing
from collections.abc import Iterable, Iterator

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity

from . import WeatherLinkCoordinator, WeatherLinkEntity
from .api.conditions import ConditionRecord, CurrentConditions

logger = logging.getLogger(__name__)


class WeatherLinkSensor(WeatherLinkEntity, SensorEntity):
    _SENSORS: list[type["WeatherLinkSensor"]] = []

    @typing.overload
    def __init_subclass__(
        cls,
        *,
        sensor_name: str,
        unit_of_measurement: str | None,
        device_class: SensorDeviceClass | None,
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
        required_conditions = kwargs.pop("required_conditions", None)
        cls._attr_native_unit_of_measurement = kwargs.pop("unit_of_measurement")
        cls._attr_device_class = kwargs.pop("device_class")

        super().__init_subclass__(**kwargs)

        cls._sensor_name = sensor_name

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
