import dataclasses
from typing import Callable, Optional, Union, Tuple

import voluptuous as vol

FactorT = Union[Callable[[float], float], float]


@dataclasses.dataclass()
class Unit:
    unit_of_measurement: str
    ndigits: int
    factor: Optional[FactorT] = None

    def __round(self, v: float) -> float:
        ndigits = self.ndigits or None
        return round(v, ndigits)

    def convert(self, v: float) -> float:
        if factor := self.factor:
            if callable(factor):
                v = factor(v)
            else:
                v *= factor

        return self.__round(v)

    def convert_optional(self, v: Optional[float]) -> Optional[float]:
        if v is None:
            return v
        return self.convert(v)


class Units:
    @classmethod
    def unit_keys(cls) -> Tuple[str, ...]:
        try:
            return cls.__UNIT_KEYS
        except AttributeError:
            pass

        cls.__UNIT_KEYS = tuple(
            key for key in dir(cls) if isinstance(getattr(cls, key), Unit)
        )
        return cls.__UNIT_KEYS

    @classmethod
    def data_schema(cls) -> vol.Schema:
        return vol.Schema(str)


class Temperature(Units):
    CELSIUS = Unit(unit_of_measurement="°C", ndigits=1)

    FAHRENHEIT = Unit(
        unit_of_measurement="°F", factor=lambda c: (c * 9.0 / 5.0) + 32.0, ndigits=0
    )
    KELVIN = Unit(unit_of_measurement="K", factor=lambda c: c + 273.15, ndigits=1)


class Pressure(Units):
    HPA = Unit(unit_of_measurement="hPa", ndigits=0)
    PSI = Unit(unit_of_measurement="psi", factor=0.0145, ndigits=2)
    IN_HG = Unit(unit_of_measurement="″Hg", factor=0.0295, ndigits=2)
    MM_HG = Unit(unit_of_measurement="mmHg", factor=0.75, ndigits=0)


class Speed(Units):
    KMH = Unit(unit_of_measurement="km/h", ndigits=1)
    MPS = Unit(unit_of_measurement="m/s", factor=1.0 / 3.6, ndigits=1)
    MPH = Unit(unit_of_measurement="mph", factor=0.621, ndigits=1)
    KNOTS = Unit(unit_of_measurement="kn", factor=1.0 / 1.852, ndigits=1)
    FTPS = Unit(unit_of_measurement="ft/s", factor=0.911, ndigits=1)


class Pm(Units):
    UG_PER_M3 = Unit(unit_of_measurement="µg/m³", ndigits=2)


@dataclasses.dataclass()
class UnitConfig:
    temperature: Unit
    pressure: Unit
    speed: Unit
    pm: Unit

    @classmethod
    def default_metric(cls):
        return cls(
            temperature=Temperature.CELSIUS,
            pressure=Pressure.HPA,
            speed=Speed.KMH,
            pm=Pm.UG_PER_M3,
        )

    @classmethod
    def default_imperial(cls):
        return cls(
            temperature=Temperature.FAHRENHEIT,
            pressure=Pressure.PSI,
            speed=Speed.MPH,
            pm=Pm.UG_PER_M3,
        )

    @classmethod
    def data_schema(cls) -> vol.Schema:
        return vol.Schema(
            {
                vol.Required("temperature"): Temperature.data_schema(),
                vol.Required("pressure"): Pressure.data_schema(),
                vol.Required("speed"): Speed.data_schema(),
                vol.Required("pm"): Pm.data_schema(),
            }
        )
