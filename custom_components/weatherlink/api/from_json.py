import abc
import logging
from collections.abc import Callable, Iterable
from datetime import datetime
from typing import Any, Self

__all__ = [
    "FromJson",
    "JsonObject",
]

logger = logging.getLogger(__name__)

type JsonObject = dict[str, Any]


class FromJson(abc.ABC):
    OPT_STRICT = "strict"

    @classmethod
    @abc.abstractmethod
    def _from_json(cls, data: JsonObject, **kwargs: Any) -> Self: ...

    @classmethod
    def from_json(cls, data: JsonObject, **kwargs: Any) -> Self:
        try:
            return cls._from_json(data, **kwargs)
        except Exception as e:
            if not getattr(e, "_handled", False):
                logger.error(
                    f"failed to create `{cls.__qualname__}` from JSON: {data!r}"
                )
                setattr(e, "_handled", True)

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
    apply_converters(d, **dict.fromkeys(keys, datetime.fromtimestamp))


def keys_to_celsius(d: JsonObject, *keys: str) -> None:
    apply_converters(d, **dict.fromkeys(keys, fahrenheit_to_celsius))


def keys_to_kph(d: JsonObject, *keys: str) -> None:
    apply_converters(d, **dict.fromkeys(keys, mph_to_kph))


def keys_to_hpa(d: JsonObject, *keys: str) -> None:
    apply_converters(d, **dict.fromkeys(keys, in_hg_to_hpa))


def remove_optional_keys(d: JsonObject, *keys: str) -> None:
    for key in keys:
        try:
            del d[key]
        except KeyError:
            continue


def keys_from_aliases(d: JsonObject, **key_aliases: str | Iterable[str]) -> None:
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
