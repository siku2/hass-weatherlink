from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass
from homeassistant.const import PERCENTAGE, UnitOfTemperature

from .api.conditions import CurrentConditions, MoistureCondition
from .sensor_common import WeatherLinkSensor

__all__ = ["MoistureStatus", "SOIL_MOISTURE_CLS", "SOIL_TEMPERATURE_CLS", "LEAF_CLS"]


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
    def extra_state_attributes(self):
        c = self._moisture_condition
        return {
            "txid": c.txid,
            "battery": c.trans_battery_flag,
        }


class SoilMoistureABC(MoistureSensor, abc=True):
    _sensor_id: int

    def __init_subclass__(cls, *, sensor_id: int, **kwargs) -> None:
        super().__init_subclass__(
            sensor_name=f"Soil Moisture {sensor_id}",
            unit_of_measurement="cb",
            device_class=None,
            state_class=SensorStateClass.MEASUREMENT,
            **kwargs,
        )

        cls._sensor_id = sensor_id

    @classmethod
    def _conditions_ok(cls, conditions: CurrentConditions) -> bool:
        if not super()._conditions_ok(conditions):
            return False

        c = conditions[MoistureCondition]
        return cls._moisture(c) is not None

    @classmethod
    def _moisture(cls, c: MoistureCondition) -> float | None:
        return getattr(c, f"moist_soil_{cls._sensor_id}")

    @property
    def icon(self):
        return "mdi:sprout"

    @property
    def state(self):
        return self._moisture(self._moisture_condition)


SOIL_MOISTURE_CLS = tuple(
    type(f"SoilMoisture{n}", (SoilMoistureABC,), {}, sensor_id=n) for n in range(1, 5)
)


class SoilTemperatureABC(MoistureSensor, abc=True):
    _sensor_id: int

    def __init_subclass__(cls, *, sensor_id: int, **kwargs) -> None:
        super().__init_subclass__(
            sensor_name=f"Soil Temperature {sensor_id}",
            unit_of_measurement=UnitOfTemperature.CELSIUS,
            device_class=SensorDeviceClass.TEMPERATURE,
            **kwargs,
        )

        cls._sensor_id = sensor_id

    @classmethod
    def _conditions_ok(cls, conditions: CurrentConditions) -> bool:
        if not super()._conditions_ok(conditions):
            return False

        c = conditions[MoistureCondition]
        return cls._temp(c) is not None

    @classmethod
    def _temp(cls, c: MoistureCondition) -> float | None:
        return getattr(c, f"temp_{cls._sensor_id}")

    @property
    def state(self):
        return self._temp(self._moisture_condition)


SOIL_TEMPERATURE_CLS = tuple(
    type(f"SoilTemperature{n}", (SoilTemperatureABC,), {}, sensor_id=n)
    for n in range(1, 5)
)


class LeafABC(MoistureSensor, abc=True):
    _sensor_id: int

    def __init_subclass__(cls, *, sensor_id: int, **kwargs) -> None:
        super().__init_subclass__(
            sensor_name=f"Leaf {sensor_id}",
            unit_of_measurement=PERCENTAGE,
            device_class=SensorDeviceClass.MOISTURE,
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
    def _wet_leaf(cls, c: MoistureCondition) -> float | None:
        return getattr(c, f"wet_leaf_{cls._sensor_id}")

    @property
    def icon(self):
        return "mdi:leaf"

    @property
    def state(self):
        if wetness := self._wet_leaf(self._moisture_condition):
            return 100.0 / 15.0 * wetness
        return None

    @property
    def extra_state_attributes(self):
        return {"raw": self._wet_leaf(self._moisture_condition)}


LEAF_CLS = tuple(type(f"Leaf{n}", (LeafABC,), {}, sensor_id=n) for n in range(1, 3))
