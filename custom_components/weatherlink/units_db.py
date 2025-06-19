import dataclasses
from collections.abc import Callable

import voluptuous as vol

type FactorT = Callable[[float], float] | float


@dataclasses.dataclass(unsafe_hash=True)
class UnitInfo:
    key: str = dataclasses.field(init=False)
    measurement: type["Measurement"] = dataclasses.field(init=False)

    unit_of_measurement: str
    default_ndigits: int | None
    factor: FactorT | None = None

    def convert(self, v: float) -> float:
        if factor := self.factor:
            if callable(factor):
                v = factor(v)
            else:
                v *= factor
        return v


class Measurement:
    _UNITS: tuple[UnitInfo, ...]
    _DATA_SCHEMA: vol.In

    def __init_subclass__(cls) -> None:
        super().__init_subclass__()

        units: list[UnitInfo] = []
        for key in dir(cls):
            unit = getattr(cls, key)
            if not isinstance(unit, UnitInfo):
                continue

            unit.key = key
            unit.measurement = cls

            units.append(unit)

        cls._UNITS = tuple(units)
        cls._DATA_SCHEMA = vol.In(
            tuple(unit.unit_of_measurement for unit in cls._UNITS)
        )

    @classmethod
    def default(cls) -> UnitInfo | None:
        return next(iter(cls._UNITS), None)

    @classmethod
    def data_schema(cls) -> vol.In:
        return cls._DATA_SCHEMA

    @classmethod
    def from_unit_of_measurement(cls, unit_of_measurement: str):
        try:
            return next(
                unit
                for unit in cls._UNITS
                if unit.unit_of_measurement == unit_of_measurement
            )
        except StopIteration:
            raise LookupError(
                f"{unit_of_measurement!r} not in {cls.__qualname__}"
            ) from None


class Temperature(Measurement):
    CELSIUS = UnitInfo(unit_of_measurement="°C", default_ndigits=1)
    FAHRENHEIT = UnitInfo(
        unit_of_measurement="°F",
        factor=lambda c: (c * 9.0 / 5.0) + 32.0,
        default_ndigits=0,
    )


class Pressure(Measurement):
    HPA = UnitInfo(unit_of_measurement="hPa", default_ndigits=0)
    PSI = UnitInfo(unit_of_measurement="psi", factor=0.0145, default_ndigits=2)
    IN_HG = UnitInfo(unit_of_measurement="inHg", factor=0.0295, default_ndigits=2)
    MM_HG = UnitInfo(unit_of_measurement="mmHg", factor=0.75, default_ndigits=0)


class WindSpeed(Measurement):
    KMH = UnitInfo(unit_of_measurement="km/h", default_ndigits=1)
    MPS = UnitInfo(unit_of_measurement="m/s", factor=1.0 / 3.6, default_ndigits=1)
    MPH = UnitInfo(unit_of_measurement="mph", factor=0.621, default_ndigits=1)
    KNOTS = UnitInfo(unit_of_measurement="kn", factor=1.0 / 1.852, default_ndigits=1)
    FTPS = UnitInfo(unit_of_measurement="ft/s", factor=0.911, default_ndigits=1)


class Pm(Measurement):
    UG_PER_M3 = UnitInfo(unit_of_measurement="µg/m³", default_ndigits=2)


class RainRate(Measurement):
    MMH = UnitInfo(unit_of_measurement="mm/h", default_ndigits=1)
    INH = UnitInfo(unit_of_measurement="in/h", factor=1.0 / 25.4, default_ndigits=2)


class Rainfall(Measurement):
    MM = UnitInfo(unit_of_measurement="mm", default_ndigits=1)
    IN = UnitInfo(unit_of_measurement="in", factor=1.0 / 25.4, default_ndigits=2)
