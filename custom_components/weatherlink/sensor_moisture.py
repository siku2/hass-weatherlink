from typing import Optional

from .api import CurrentConditions, MoistureCondition
from .sensor_common import WeatherLinkSensor, round_optional

__all__ = [
    "MoistureStatus",
    "Soil1",
    "Soil2",
    "Soil3",
    "Soil4",
    "Leaf1",
    "Leaf2",
]


class MoistureSensor(WeatherLinkSensor, abc=True):
    def __init_subclass__(
        cls,
        abc: bool = False,
        **kwargs,
    ) -> None:
        if not abc:
            kwargs["required_conditions"] = (MoistureCondition,)
        super().__init_subclass__(abc=abc, **kwargs)

    @property
    def _moisture_condition(self) -> MoistureCondition:
        return self._conditions[MoistureCondition]

    @property
    def unique_id(self):
        return f"{super().unique_id}-moisture"


class MoistureStatus(
    MoistureSensor,
    sensor_name="Moisture Status",
    unit_of_measurement=None,
    device_class=None,
):
    @property
    def icon(self):
        return "mdi:information"

    @property
    def state(self):
        rx_state = self._moisture_condition.rx_state
        if rx_state is None:
            return None
        return rx_state.name

    @property
    def device_state_attributes(self):
        c = self._moisture_condition
        return {
            "txid": c.txid,
            "battery": c.trans_battery_flag,
        }


class SoilABC(MoistureSensor, abc=True):
    _sensor_id: int

    def __init_subclass__(cls, *, sensor_id: int, **kwargs) -> None:
        super().__init_subclass__(
            sensor_name=f"Soil {sensor_id}",
            unit_of_measurement="cb",
            device_class=None,
            **kwargs,
        )

        cls._sensor_id = sensor_id

    @classmethod
    def _conditions_ok(cls, conditions: CurrentConditions) -> bool:
        if not super()._conditions_ok(conditions):
            return False

        c = conditions[MoistureCondition]
        return (cls._moist_soil(c) or cls._temp(c)) is not None

    @classmethod
    def _moist_soil(cls, c: MoistureCondition) -> Optional[float]:
        return getattr(c, f"moist_soil_{cls._sensor_id}")

    @classmethod
    def _temp(cls, c: MoistureCondition) -> Optional[float]:
        return getattr(c, f"temp_{cls._sensor_id}")

    @property
    def icon(self):
        return "mdi:sprout"

    @property
    def state(self):
        return round_optional(self._moist_soil(self._moisture_condition), 1)

    @property
    def device_state_attributes(self):
        return {
            "temperature": round_optional(self._temp(self._moisture_condition), 1),
        }


class Soil1(
    SoilABC,
    sensor_id=1,
):
    ...


class Soil2(
    SoilABC,
    sensor_id=2,
):
    ...


class Soil3(
    SoilABC,
    sensor_id=3,
):
    ...


class Soil4(
    SoilABC,
    sensor_id=4,
):
    ...


_WETNESS2PERCENTAGE = 100.0 / 15.0


class LeafABC(MoistureSensor, abc=True):
    _sensor_id: int

    def __init_subclass__(cls, *, sensor_id: int, **kwargs) -> None:
        super().__init_subclass__(
            sensor_name=f"Leaf {sensor_id}",
            unit_of_measurement="%",
            device_class=None,
            **kwargs,
        )

        cls._sensor_id = sensor_id

    @classmethod
    def _conditions_ok(cls, conditions: CurrentConditions) -> bool:
        if not super()._conditions_ok(conditions):
            return False

        c = conditions[MoistureCondition]
        return cls._wet_leaf(c) is not None

    @classmethod
    def _wet_leaf(cls, c: MoistureCondition) -> Optional[float]:
        return getattr(c, f"wet_leaf_{cls._sensor_id}")

    @property
    def icon(self):
        return "mdi:leaf"

    @property
    def state(self):
        if wetness := self._wet_leaf(self._moisture_condition):
            return round(_WETNESS2PERCENTAGE * wetness, 0)
        return None

    @property
    def device_state_attributes(self):
        return {
            "raw": round_optional(self._wet_leaf(self._moisture_condition), 1),
        }


class Leaf1(
    LeafABC,
    sensor_id=1,
):
    ...


class Leaf2(
    LeafABC,
    sensor_id=2,
):
    ...
