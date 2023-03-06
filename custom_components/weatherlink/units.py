import dataclasses
import logging
from typing import Mapping, Optional, Type, Union

import voluptuous as vol
from homeassistant.config_entries import ConfigEntry
from homeassistant.util.unit_system import US_CUSTOMARY_SYSTEM
from homeassistant.core import HomeAssistant

from .units_db import (
    Measurement,
    Pm,
    Pressure,
    Rainfall,
    RainRate,
    Temperature,
    UnitInfo,
    WindSpeed,
)

logger = logging.getLogger(__name__)

IntOrFloat = Union[float, int]


@dataclasses.dataclass()
class Unit:
    info: UnitInfo
    ndigits: Optional[int]

    def __round(self, v: float) -> IntOrFloat:
        if self.ndigits is None:
            return v
        # 0 -> None so it's rounded to an int
        return round(v, self.ndigits or None)

    def convert(self, v: float) -> IntOrFloat:
        return self.__round(self.info.convert(v))

    def convert_optional(self, v: Optional[float]) -> Optional[IntOrFloat]:
        if v is None:
            return v
        return self.convert(v)

    @classmethod
    def from_unit_info(cls, info: UnitInfo):
        return cls(info=info, ndigits=info.default_ndigits)

    @classmethod
    def default(cls, measurement: Type[Measurement]):
        return cls.from_unit_info(measurement.default())

    @classmethod
    def from_dict(cls, measurement: Type[Measurement], data):
        info: UnitInfo
        ndigits: Optional[int]

        if isinstance(data, str):
            # compatibility for version 0.3.0
            info = getattr(measurement, data)
            ndigits = info.default_ndigits
        else:
            info = getattr(measurement, data["key"])
            ndigits = data["ndigits"]
            if ndigits is not None:
                ndigits = int(ndigits)

        return cls(info=info, ndigits=ndigits)

    def as_dict(self):
        return {"key": self.info.key, "ndigits": self.ndigits}


def ndigits2rounding(ndigits: Optional[int]) -> str:
    if ndigits is None:
        return "raw"
    if ndigits <= 0:
        return "1"
    return f"0.{1:0{ndigits}}"


def rounding_schema(max_ndigits: int) -> vol.In:
    return vol.In(
        [
            ndigits2rounding(None),
            *(ndigits2rounding(n) for n in range(0, max_ndigits + 1)),
        ]
    )


def rounding2ndigits(rounding: str) -> Optional[int]:
    if rounding == "raw":
        return None
    return rounding.count("0")


@dataclasses.dataclass()
class UnitConfig:
    temperature: Unit
    pressure: Unit
    wind_speed: Unit
    pm: Unit
    rain_rate: Unit
    rainfall: Unit

    def by_measurement(self, measurement: Type[Measurement]) -> Unit:
        return getattr(self, _UNIT_CONFIG_MEASUREMENT2KEY[measurement])

    def units_schema(self) -> vol.Schema:
        schema = {}
        for key, measurement in _UNIT_CONFIG_KEY2MEASUREMENT.items():
            unit = getattr(self, key)
            key_schema = vol.Required(
                key,
                default=unit.info.unit_of_measurement,
            )
            schema[key_schema] = measurement.data_schema()

        return vol.Schema(schema)

    def rounding_schema(self) -> vol.Schema:
        schema = {}
        for key in _UNIT_CONFIG_KEY2MEASUREMENT:
            unit = getattr(self, key)
            key_schema = vol.Required(
                key,
                default=ndigits2rounding(unit.ndigits),
            )
            schema[key_schema] = rounding_schema(4)

        return vol.Schema(schema)

    @classmethod
    def from_config_flow(cls, units: dict, rounding: dict):
        kwargs = {}
        for key, measurement in _UNIT_CONFIG_KEY2MEASUREMENT.items():
            info = measurement.from_unit_of_measurement(units[key])
            ndigits = rounding2ndigits(rounding[key])
            kwargs[key] = Unit(info=info, ndigits=ndigits)
        return cls(**kwargs)

    @classmethod
    def _from_unit_infos(cls, **kwargs):
        for key, info in kwargs.items():
            kwargs[key] = Unit.from_unit_info(info)
        return cls(**kwargs)

    @classmethod
    def default_metric(cls):
        return cls._from_unit_infos(
            temperature=Temperature.CELSIUS,
            pressure=Pressure.HPA,
            wind_speed=WindSpeed.KMH,
            pm=Pm.UG_PER_M3,
            rain_rate=RainRate.MMH,
            rainfall=Rainfall.MM,
        )

    @classmethod
    def default_imperial(cls):
        return cls._from_unit_infos(
            temperature=Temperature.FAHRENHEIT,
            pressure=Pressure.PSI,
            wind_speed=WindSpeed.MPH,
            pm=Pm.UG_PER_M3,
            rain_rate=RainRate.INH,
            rainfall=Rainfall.IN,
        )

    @classmethod
    def from_dict(cls, data):
        kwargs = {}
        for key, measurement in _UNIT_CONFIG_KEY2MEASUREMENT.items():
            try:
                value = Unit.from_dict(measurement, data[key])
            except KeyError:
                value = Unit.default(measurement)
            except Exception:
                logger.exception(f"failed to load {key!r} unit: {data!r}")
                value = Unit.default(measurement)

            kwargs[key] = value
        return cls(**kwargs)

    def as_dict(self) -> dict:
        data = {}
        for key in _UNIT_CONFIG_KEY2MEASUREMENT:
            data[key] = getattr(self, key).as_dict()
        return data


_UNIT_CONFIG_KEY2MEASUREMENT: Mapping[str, Type[Measurement]] = {
    "temperature": Temperature,
    "pressure": Pressure,
    "wind_speed": WindSpeed,
    "pm": Pm,
    "rain_rate": RainRate,
    "rainfall": Rainfall,
}
_UNIT_CONFIG_MEASUREMENT2KEY = {
    value: key for key, value in _UNIT_CONFIG_KEY2MEASUREMENT.items()
}


def get_unit_config(hass: HomeAssistant, entry: ConfigEntry) -> UnitConfig:
    try:
        return UnitConfig.from_dict(entry.options["units"])
    except KeyError:
        logger.info("using default units")
    except Exception:
        logger.exception(f"failed to load unit config: {entry.options!r}")

    if hass.config.units == US_CUSTOMARY_SYSTEM:
        return UnitConfig.default_imperial()

    return UnitConfig.default_metric()
