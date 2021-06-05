import abc
import logging
from datetime import datetime
from typing import Any, Callable, Dict, Iterable, Type, TypeVar, Union

__all__ = [
    "FromJson",
    "JsonObject",
]

logger = logging.getLogger(__name__)

JsonObject = Dict[str, Any]


FromJsonT = TypeVar("FromJsonT", bound="FromJson")


class FromJson(abc.ABC):
    OPT_STRICT = "strict"

    @classmethod
    @abc.abstractmethod
    def _from_json(cls, data: JsonObject, **kwargs):
        ...

    @classmethod
    def from_json(cls: Type[FromJsonT], data: JsonObject, **kwargs) -> FromJsonT:
        try:
            return cls._from_json(data, **kwargs)
        except Exception as e:
            if not getattr(e, "_handled", False):
                logger.error(
                    f"failed to create `{cls.__qualname__}` from JSON: {data!r}"
                )
                e._handled = True

            raise e from None


def fahrenheit_to_celsius(value: float) -> float:
    return (value - 32) * 5 / 9


def mph_to_kph(value: float) -> float:
    return 1.609344 * value


def in_hg_to_hpa(value: float) -> float:
    return 33.86389 * value


def apply_converters(d: JsonObject, **converters: Callable[[Any], Any]) -> None:
    for key, converter in converters.items():
        try:
            value = d[key]
        except KeyError:
            continue

        if value is None:
            continue

        d[key] = converter(value)


def keys_to_datetime(d: JsonObject, *keys: str) -> None:
    apply_converters(d, **{key: datetime.fromtimestamp for key in keys})


def keys_to_celsius(d: JsonObject, *keys: str) -> None:
    apply_converters(d, **{key: fahrenheit_to_celsius for key in keys})


def keys_to_kph(d: JsonObject, *keys: str) -> None:
    apply_converters(d, **{key: mph_to_kph for key in keys})


def keys_to_hpa(d: JsonObject, *keys: str) -> None:
    apply_converters(d, **{key: in_hg_to_hpa for key in keys})


def remove_optional_keys(d: JsonObject, *keys: str) -> None:
    for key in keys:
        try:
            del d[key]
        except KeyError:
            continue


def keys_from_aliases(d: JsonObject, **key_aliases: Union[str, Iterable[str]]) -> None:
    for key, aliases in key_aliases.items():
        if key in d:
            continue

        if isinstance(aliases, str):
            aliases = (aliases,)

        for alias in aliases:
            try:
                value = d[alias]
            except KeyError:
                continue

            d[key] = value
            break

    for aliases in key_aliases.values():
        if isinstance(aliases, str):
            aliases = (aliases,)
        remove_optional_keys(d, *aliases)


def update_dict_where_none(d: JsonObject, updates: JsonObject) -> None:
    for key, value in updates.items():
        if d.get(key) is None:
            d[key] = value
