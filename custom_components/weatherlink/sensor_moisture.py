from .api import MoistureCondition
from .sensor_common import WeatherLinkSensor

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
        **kwargs,
    ) -> None:
        super().__init_subclass__(required_conditions=(MoistureCondition,), **kwargs)

    @property
    def _moisture_condition(self) -> MoistureCondition:
        return self._conditions[MoistureCondition]

    @property
    def name(self):
        return f"{self.coordinator.device_name} Moisture {self._sensor_name}"

    @property
    def unique_id(self):
        return f"{super().unique_id}-moisture"


class MoistureStatus(
    MoistureSensor,
    sensor_name="Status",
    unit_of_measurement=None,
    device_class=None,
):
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
            unit_of_measurement="%",
            device_class="humidity",
            **kwargs,
        )

        cls._sensor_id = sensor_id

    @property
    def state(self):
        return getattr(self._moisture_condition, f"moist_soil_{self._sensor_id}")

    @property
    def device_state_attributes(self):
        c = self._moisture_condition
        return {
            "temperature": getattr(c, f"temp_{self._sensor_id}"),
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


class Leaf1(
    MoistureSensor,
    sensor_name="Leaf 1",
    unit_of_measurement="%",
    device_class="humidity",
):
    @property
    def state(self):
        return self._moisture_condition.wet_leaf_1


class Leaf2(
    MoistureSensor,
    sensor_name="Leaf 2",
    unit_of_measurement="%",
    device_class="humidity",
):
    @property
    def state(self):
        return self._moisture_condition.wet_leaf_2
