import dataclasses
import logging
from typing import Callable, Dict, Optional, Type, Union

import voluptuous as vol
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_UNIT_SYSTEM_IMPERIAL
from homeassistant.core import HomeAssistant

logger = logging.getLogger(__name__)

FactorT = Union[Callable[[float], float], float]


@dataclasses.dataclass(frozen=True)
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
    _DATA_SCHEMA: vol.Schema
    _UNIT2KEY: Dict[Unit, str]
    _DEFAULT_UNIT: Unit

    def __init_subclass__(cls) -> None:
        super().__init_subclass__()

        cls._UNIT2KEY = {}
        for key in dir(cls):
            unit = getattr(cls, key)
            if not isinstance(unit, Unit):
                continue

            cls._UNIT2KEY[unit] = key

        cls._DATA_SCHEMA = vol.In([unit.unit_of_measurement for unit in cls._UNIT2KEY])
        cls._DEFAULT_UNIT = next(iter(cls._UNIT2KEY))

    @classmethod
    def data_schema(cls) -> vol.Schema:
        return cls._DATA_SCHEMA

    @classmethod
    def default(cls) -> Unit:
        return cls._DEFAULT_UNIT

    @classmethod
    def from_unit_of_measurement(cls, unit_of_measurement: str) -> Unit:
        try:
            return next(
                unit
                for unit in cls._UNIT2KEY
                if unit.unit_of_measurement == unit_of_measurement
            )
        except StopIteration:
            raise LookupError(
                f"{unit_of_measurement!r} not in {cls.__qualname__}"
            ) from None

    @classmethod
    def to_key(cls, unit: Unit) -> str:
        try:
            return cls._UNIT2KEY[unit]
        except KeyError:
            raise LookupError(f"{unit!r} not in {cls.__qualname__}") from None


class Temperature(Units):
    CELSIUS = Unit(unit_of_measurement="°C", ndigits=1)
    FAHRENHEIT = Unit(
        unit_of_measurement="°F", factor=lambda c: (c * 9.0 / 5.0) + 32.0, ndigits=0
    )


class Pressure(Units):
    HPA = Unit(unit_of_measurement="hPa", ndigits=0)
    PSI = Unit(unit_of_measurement="psi", factor=0.0145, ndigits=2)
    IN_HG = Unit(unit_of_measurement="inHg", factor=0.0295, ndigits=2)
    MM_HG = Unit(unit_of_measurement="mmHg", factor=0.75, ndigits=0)


class WindSpeed(Units):
    KMH = Unit(unit_of_measurement="km/h", ndigits=1)
    MPS = Unit(unit_of_measurement="m/s", factor=1.0 / 3.6, ndigits=1)
    MPH = Unit(unit_of_measurement="mph", factor=0.621, ndigits=1)
    KNOTS = Unit(unit_of_measurement="kn", factor=1.0 / 1.852, ndigits=1)
    FTPS = Unit(unit_of_measurement="ft/s", factor=0.911, ndigits=1)


class Pm(Units):
    UG_PER_M3 = Unit(unit_of_measurement="µg/m³", ndigits=2)


class RainRate(Units):
    MMH = Unit(unit_of_measurement="mm/h", ndigits=1)
    INH = Unit(unit_of_measurement="in/h", factor=1.0 / 25.4, ndigits=2)


class Rainfall(Units):
    MM = Unit(unit_of_measurement="mm", ndigits=1)
    IN = Unit(unit_of_measurement="in", factor=1.0 / 25.4, ndigits=2)


@dataclasses.dataclass()
class UnitConfig:
    temperature: Unit
    pressure: Unit
    wind_speed: Unit
    pm: Unit
    rain_rate: Unit
    rainfall: Unit

    @classmethod
    def _get_units_cls(cls, key: str) -> Type[Units]:
        return _UNIT_CONFIG_KEY2UNITS[key]

    def by_units(self, units: Type[Units]) -> Unit:
        return getattr(self, _UNIT_CONFIG_UNITS2KEY[units])

    @classmethod
    def default_metric(cls):
        return cls(
            temperature=Temperature.CELSIUS,
            pressure=Pressure.HPA,
            wind_speed=WindSpeed.KMH,
            pm=Pm.UG_PER_M3,
            rain_rate=RainRate.MMH,
            rainfall=Rainfall.MM,
        )

    @classmethod
    def default_imperial(cls):
        return cls(
            temperature=Temperature.FAHRENHEIT,
            pressure=Pressure.PSI,
            wind_speed=WindSpeed.MPH,
            pm=Pm.UG_PER_M3,
            rain_rate=RainRate.INH,
            rainfall=Rainfall.IN,
        )

    def data_schema(self) -> vol.Schema:
        return vol.Schema(
            {
                vol.Required(
                    field.name, default=getattr(self, field.name).unit_of_measurement
                ): self._get_units_cls(field.name).data_schema()
                for field in _UNIT_CONFIG_FIELDS
            }
        )

    @classmethod
    def from_dict(cls, data):
        kwargs = {}
        for field in _UNIT_CONFIG_FIELDS:
            key = field.name
            units_cls: Type[Units] = cls._get_units_cls(key)
            try:
                value = getattr(units_cls, data[key])
            except KeyError:
                value = units_cls.default()
            except Exception:
                logger.exception(f"failed to load {key!r} unit: {data!r}")
                value = units_cls.default()

            kwargs[key] = value
        return cls(**kwargs)

    def as_dict(self):
        data = {}
        for field in _UNIT_CONFIG_FIELDS:
            key = field.name
            units_cls: Type[Units] = self._get_units_cls(key)
            data[key] = units_cls.to_key(getattr(self, key))
        return data

    @classmethod
    def from_unit_of_measurement(cls, data):
        kwargs = {}
        for field in _UNIT_CONFIG_FIELDS:
            key = field.name
            units_cls: Type[Units] = cls._get_units_cls(key)
            kwargs[key] = units_cls.from_unit_of_measurement(data[key])
        return cls(**kwargs)

    def to_unit_of_measurement(self):
        return {
            field.name: getattr(self, field.name).unit_of_measurement
            for field in _UNIT_CONFIG_FIELDS
        }


_UNIT_CONFIG_FIELDS = dataclasses.fields(UnitConfig)
_UNIT_CONFIG_KEY2UNITS = {
    "temperature": Temperature,
    "pressure": Pressure,
    "wind_speed": WindSpeed,
    "pm": Pm,
    "rain_rate": RainRate,
    "rainfall": Rainfall,
}
_UNIT_CONFIG_UNITS2KEY = {value: key for key, value in _UNIT_CONFIG_KEY2UNITS.items()}


def get_unit_config(hass: HomeAssistant, entry: ConfigEntry) -> UnitConfig:
    try:
        return UnitConfig.from_dict(entry.options["units"])
    except KeyError:
        logger.info("using default units")
    except Exception:
        logger.exception(f"failed to load unit config: {entry.options!r}")

    if hass.config.units.name == CONF_UNIT_SYSTEM_IMPERIAL:
        return UnitConfig.default_imperial()

    return UnitConfig.default_metric()
