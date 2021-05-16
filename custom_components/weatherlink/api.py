import abc
import dataclasses
import enum
import logging
from datetime import datetime
from typing import Any, Callable, Dict, Iterable, List, Mapping, Optional, Type, TypeVar

import aiohttp

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


class ConditionType(enum.IntEnum):
    Iss = 1
    Moisture = 2
    LssBar = 3
    LssTempHum = 4
    AirQuality = 6
    """Sent by AirLink"""

    def record_class(self) -> Type["ConditionRecord"]:
        return _COND2CLS[self]


class ReceiverState(enum.IntEnum):
    Tracking = 0
    """Transmitter has been acquired and is actively being received."""
    Synched = 1
    """Transmitter has been acquired, but we have missed 1-14 packets in a row."""
    Scanning = 2
    """Transmitter has not been acquired yet, or we’ve lost it (more than 15 missed packets in a row)."""


class CollectorSize(enum.IntEnum):
    Millimeter01 = 3
    """0.1 mm"""
    Millimeter02 = 2
    """0.2 mm"""

    Inches001 = 1
    """(0.01")"""
    Inches0001 = 4
    """(0.001")"""

    def __mul__(self, x: int) -> int:
        return x * self.to_mm()

    def to_mm(self) -> float:
        return _COLLECTOR2MM[self]


_IN2MM = 25.4
_COLLECTOR2MM = {
    CollectorSize.Millimeter01: 0.1,
    CollectorSize.Millimeter02: 0.2,
    CollectorSize.Inches001: 0.01 * _IN2MM,
    CollectorSize.Inches0001: 0.001 * _IN2MM,
}


@dataclasses.dataclass()
class ConditionRecord(FromJson, abc.ABC):
    lsid: Optional[int]
    """the numeric logic sensor identifier, or null if the device has not been registered"""


@dataclasses.dataclass()
class IssCondition(ConditionRecord):
    txid: int
    """transmitter ID"""
    rx_state: Optional[ReceiverState]
    """configured radio receiver state"""

    temp: float
    """most recent valid temperature"""
    hum: float
    """most recent valid humidity **(%RH)**"""
    dew_point: float
    """"""
    wet_bulb: Optional[float]
    """"""
    heat_index: float
    """"""
    wind_chill: float
    """"""
    thw_index: float
    """"""
    thsw_index: float
    """"""

    wind_speed_last: float
    """most recent valid wind speed **(km/h)**"""
    wind_dir_last: Optional[int]
    """most recent valid wind direction **(°degree)**"""

    wind_speed_avg_last_1_min: float
    """average wind speed over last 1 min **(km/h)**"""
    wind_dir_scalar_avg_last_1_min: int
    """scalar average wind direction over last 1 min **(°degree)**"""

    wind_speed_avg_last_2_min: float
    """average wind speed over last 2 min **(km/h)**"""
    wind_dir_scalar_avg_last_2_min: float
    """scalar average wind direction over last 2 min **(°degree)**"""

    wind_speed_hi_last_2_min: Optional[float]
    """maximum wind speed over last 2 min **(km/h)**"""
    wind_dir_at_hi_speed_last_2_min: float
    """gust wind direction over last 2 min **(°degree)**"""

    wind_speed_avg_last_10_min: float
    """average wind speed over last 10 min **(km/h)**"""
    wind_dir_scalar_avg_last_10_min: Optional[float]
    """scalar average wind direction over last 10 min **(°degree)**"""

    wind_speed_hi_last_10_min: float
    """maximum wind speed over last 10 min **(km/h)**"""
    wind_dir_at_hi_speed_last_10_min: float
    """gust wind direction over last 10 min **(°degree)**"""

    rain_size: CollectorSize
    """rain collector type/size"""

    rain_rate_last: float
    rain_rate_last_counts: int
    """most recent valid rain rate **(counts/hour)**"""
    rain_rate_hi: Optional[float]
    rain_rate_hi_counts: Optional[int]
    """highest rain rate over last 1 min **(counts/hour)**"""

    rainfall_last_15_min: Optional[float]
    rainfall_last_15_min_counts: Optional[int]
    """total rain count over last 15 min **(counts)**"""
    rain_rate_hi_last_15_min: float
    rain_rate_hi_last_15_min_counts: int
    """highest rain rate over last 15 min **(counts/hour)**"""

    rainfall_last_60_min: Optional[float]
    rainfall_last_60_min_counts: Optional[int]
    """total rain count for last 60 min **(counts)**"""
    rainfall_last_24_hr: Optional[float]
    rainfall_last_24_hr_counts: Optional[int]
    """total rain count for last 24 hours **(counts)**"""

    rain_storm: Optional[float]
    rain_storm_counts: Optional[int]
    """total rain count since last 24 hour long break in rain **(counts)**"""
    rain_storm_start_at: Optional[datetime]
    """timestamp of current rain storm start"""

    solar_rad: int
    """most recent solar radiation **(W/m²)**"""
    uv_index: float
    """most recent UV index **(Index)**"""

    trans_battery_flag: int
    """transmitter battery status flag"""

    rainfall_daily: float
    rainfall_daily_counts: int
    """total rain count since local midnight **(counts)**"""
    rainfall_monthly: float
    rainfall_monthly_counts: int
    """total rain count since first of month at local midnight **(counts)**"""
    rainfall_year: float
    rainfall_year_counts: int
    """total rain count since first of user-chosen month at local midnight **(counts)**"""

    rain_storm_last: Optional[float]
    rain_storm_last_counts: Optional[int]
    """total rain count since last 24 hour long break in rain **(counts)**"""
    rain_storm_last_start_at: Optional[datetime]
    """timestamp of last rain storm start **(sec)**"""
    rain_storm_last_end_at: Optional[datetime]
    """timestamp of last rain storm end **(sec)**"""

    @classmethod
    def _from_json(cls, data: JsonObject, **kwargs):
        collector = CollectorSize(data["rain_size"])
        data["rain_size"] = collector
        json_keys_counts_to_mm(
            data,
            collector,
            "rain_rate_last",
            "rain_rate_hi",
            "rainfall_last_15_min",
            "rain_rate_hi_last_15_min",
            "rainfall_last_60_min",
            "rainfall_last_24_hr",
            "rain_storm",
            "rainfall_daily",
            "rainfall_monthly",
            "rainfall_year",
            "rain_storm_last",
        )
        json_apply_converters(data, rx_state=ReceiverState)
        json_keys_to_celsius(
            data,
            "temp",
            "dew_point",
            "wet_bulb",
            "heat_index",
            "wind_chill",
            "thw_index",
            "thsw_index",
        )
        json_keys_to_datetime(
            data,
            "rain_storm_start_at",
            "rain_storm_last_start_at",
            "rain_storm_last_end_at",
        )
        json_keys_to_kph(
            data,
            "wind_speed_last",
            "wind_speed_avg_last_1_min",
            "wind_speed_avg_last_2_min",
            "wind_speed_hi_last_2_min",
            "wind_speed_avg_last_10_min",
            "wind_speed_hi_last_10_min",
        )
        return cls(**data)


@dataclasses.dataclass()
class MoistureCondition(ConditionRecord):
    txid: int
    rx_state: Optional[ReceiverState]
    """configured radio receiver state"""

    temp_1: Optional[float]
    """most recent valid soil temp slot 1"""
    temp_2: Optional[float]
    """most recent valid soil temp slot 2"""
    temp_3: Optional[float]
    """most recent valid soil temp slot 3"""
    temp_4: Optional[float]
    """most recent valid soil temp slot 4"""

    moist_soil_1: Optional[float]
    """most recent valid soil moisture slot 1 **(|cb|)**"""
    moist_soil_2: Optional[float]
    """most recent valid soil moisture slot 2 **(|cb|)**"""
    moist_soil_3: Optional[float]
    """most recent valid soil moisture slot 3 **(|cb|)**"""
    moist_soil_4: Optional[float]
    """most recent valid soil moisture slot 4 **(|cb|)**"""

    wet_leaf_1: Optional[float]
    """most recent valid leaf wetness slot 1"""
    wet_leaf_2: Optional[float]
    """most recent valid leaf wetness slot 2"""

    trans_battery_flag: Optional[int]
    """transmitter battery status flag"""

    @classmethod
    def _from_json(cls, data: JsonObject, **kwargs):
        json_apply_converters(data, rx_state=ReceiverState)
        json_keys_to_celsius(data, "temp_1", "temp_2", "temp_3", "temp_4")
        return cls(**data)


@dataclasses.dataclass()
class LssBarCondition(ConditionRecord):
    bar_sea_level: float
    """most recent bar sensor reading with elevation adjustment **(hpa)**"""
    bar_trend: Optional[float]
    """current 3 hour bar trend **(hpa)**"""
    bar_absolute: float
    """raw bar sensor reading **(hpa)**"""

    @classmethod
    def _from_json(cls, data: JsonObject, **kwargs):
        json_keys_to_hpa(data, "bar_sea_level", "bar_trend", "bar_absolute")
        return cls(**data)


@dataclasses.dataclass()
class LssTempHumCondition(ConditionRecord):
    temp_in: float
    """most recent valid inside temp"""
    hum_in: float
    """most recent valid inside humidity **(%RH)**"""
    dew_point_in: float
    """"""
    heat_index_in: float
    """"""

    @classmethod
    def _from_json(cls, data: JsonObject, **kwargs):
        json_keys_to_celsius(data, "temp_in", "dew_point_in", "heat_index_in")
        return cls(**data)


@dataclasses.dataclass()
class AirQualityCondition(ConditionRecord):
    temp: float
    """most recent valid air temperature reading"""
    hum: float
    """most recent valid humidity reading in %RH"""
    dew_point: float
    """dew point temperature calculated from the most recent valid temperature / humidity reading"""
    wet_bulb: float
    """wet bulb temperature calculated from the most recent valid temperature / humidity reading and user elevation"""
    heat_index: float
    """heat index temperature calculated from the most recent valid temperature / humidity reading"""

    pm_1_last: int
    """most recent valid PM 1.0 reading calculated using atmospheric calibration in µg/m^3."""
    pm_2p5_last: int
    """most recent valid PM 2.5 reading calculated using atmospheric calibration in µg/m^3."""
    pm_10_last: int
    """most recent valid PM 10.0 reading calculated using atmospheric calibration in µg/m^3."""

    pm_1: float
    """average of all PM 1.0 readings in the last minute calculated using atmospheric calibration in µg/m^3."""
    pm_2p5: float
    """average of all PM 2.5 readings in the last minute calculated using atmospheric calibration in µg/m^3."""
    pm_10: float
    """average of all PM 10.0 readings in the last minute calculated using atmospheric calibration in µg/m^3."""

    pm_2p5_last_1_hour: float
    """average of all PM 2.5 readings in the last hour calculated using atmospheric calibration in µg/m^3."""
    pm_2p5_last_3_hours: float
    """average of all PM 2.5 readings in the last 3 hours calculated using atmospheric calibration in µg/m^3."""
    pm_2p5_last_24_hours: float
    """weighted average of all PM 2.5 readings in the last 24 hours calculated using atmospheric calibration in µg/m^3."""
    pm_2p5_nowcast: float
    """weighted average of all PM 2.5 readings in the last 12 hours calculated using atmospheric calibration in µg/m^3."""

    pm_10_last_1_hour: float
    """average of all PM 10.0 readings in the last hour calculated using atmospheric calibration in µg/m^3."""
    pm_10_last_3_hours: float
    """average of all PM 10.0 readings in the last 3 hours calculated using atmospheric calibration in µg/m^3."""
    pm_10_last_24_hours: float
    """weighted average of all PM 10.0 readings in the last 24 hours calculated using atmospheric calibration in µg/m^3."""
    pm_10_nowcast: float
    """weighted average of all PM 10.0 readings in the last 12 hours calculated using atmospheric calibration in µg/m^3."""

    last_report_time: datetime
    """timestamp of the last time a valid reading was received from the PM sensor (or time since boot if time has not been synced), with resolution of seconds."""

    pct_pm_data_last_1_hour: int
    """amount of PM data available to calculate averages in the last hour (rounded down to the nearest percent)"""
    pct_pm_data_last_3_hours: int
    """amount of PM data available to calculate averages in the last 3 hours (rounded down to the nearest percent)"""
    pct_pm_data_last_24_hours: int
    """amount of PM data available to calculate averages in the last 24 hours (rounded down to the nearest percent)"""
    pct_pm_data_nowcast: int
    """amount of PM data available to calculate averages in the last 12 hours (rounded down to the nearest percent)"""

    @classmethod
    def _from_json(cls, data: JsonObject, **kwargs):
        json_keys_to_celsius(data, "temp", "dew_point", "wet_bulb", "heat_index")
        json_keys_to_datetime(data, "last_report_time")
        return cls(**data)


_COND2CLS = {
    ConditionType.Iss: IssCondition,
    ConditionType.Moisture: MoistureCondition,
    ConditionType.LssBar: LssBarCondition,
    ConditionType.LssTempHum: LssTempHumCondition,
    ConditionType.AirQuality: AirQualityCondition,
}


def condition_from_json(data: JsonObject, **kwargs) -> ConditionRecord:
    cond_ty = ConditionType(data.pop("data_structure_type"))
    cls = cond_ty.record_class()
    return cls.from_json(data, **kwargs)


class DeviceType(enum.Enum):
    WeatherLink = "WeatherLink"
    AirLink = "AirLink"


RecordT = TypeVar("RecordT", bound=ConditionRecord)


@dataclasses.dataclass()
class CurrentConditions(FromJson, Mapping[Type[RecordT], RecordT]):
    did: str
    """the device serial number as a string"""
    ts: datetime
    """the timestamp of the moment the response was generated, with a resolution of seconds.
    
    If the time has not yet been synchronized from the network, this will instead measure the time in seconds since bootup.
    """

    conditions: List[ConditionRecord]
    """a list of current condition data records, one per logical sensor."""

    name: Optional[str] = None
    """Only present for AirLink"""

    @classmethod
    def _from_json(cls, data: JsonObject, **kwargs):
        conditions = []
        for i, cond_data in enumerate(data["conditions"]):
            try:
                cond = condition_from_json(cond_data, **kwargs)
            except Exception:
                if kwargs.get(cls.OPT_STRICT):
                    raise

                logger.exception(
                    f"failed to build condition record at index {i}: {cond_data!r}"
                )
                continue

            conditions.append(cond)

        return cls(
            did=data["did"],
            ts=datetime.fromtimestamp(data["ts"]),
            conditions=conditions,
            name=data.get("name"),
        )

    def __getitem__(self, cls: Type[RecordT]) -> RecordT:
        try:
            return next(cond for cond in self.conditions if isinstance(cond, cls))
        except StopIteration:
            raise KeyError(repr(cls.__qualname__)) from None

    def __iter__(self) -> Iterable[ConditionRecord]:
        return iter(self.conditions)

    def __len__(self) -> int:
        return len(self.conditions)

    def get(self, cls: Type[RecordT]) -> Optional[RecordT]:
        try:
            return self[cls]
        except KeyError:
            return None

    def determine_device_type(self) -> DeviceType:
        if self.name is None:
            return DeviceType.WeatherLink
        else:
            return DeviceType.AirLink

    def determine_device_name(self) -> str:
        name = self.name
        if name:
            return name

        model_name = self.determine_device_type().name
        return f"{model_name} {self.did}"


@dataclasses.dataclass()
class ApiError(Exception, FromJson):
    code: int
    message: str

    def __str__(self) -> str:
        return f"{self.code}: {self.message}"

    @classmethod
    def _from_json(cls, data: JsonObject, **kwargs):
        return cls(code=data["code"], message=data["message"])


def get_data_from_body(body: JsonObject) -> JsonObject:
    if err := body.get("error"):
        raise ApiError.from_json(err)

    return body["data"]


class WeatherLinkSession:
    EP_CURRENT_CONDITIONS = "/v1/current_conditions"

    session: aiohttp.ClientSession
    base_url: str

    def __init__(self, session: aiohttp.ClientSession, base_url: str) -> None:
        self.session = session
        self.base_url = base_url

    async def _request(self, path: str) -> JsonObject:
        async with self.session.get(self.base_url + path) as resp:
            body = await resp.json()
            return get_data_from_body(body)

    async def current_conditions(self) -> CurrentConditions:
        raw_data = await self._request(self.EP_CURRENT_CONDITIONS)
        return CurrentConditions.from_json(raw_data)


def fahrenheit_to_celsius(value: float) -> float:
    c = (value - 32) * 5 / 9
    return round(c, 3)


def mph_to_kph(value: float) -> float:
    kph = 1.60934 * value
    return round(kph, 3)


def in_hg_to_hpa(value: float) -> float:
    hpa = 33.86389 * value
    return round(hpa, 3)


def json_apply_converters(d: JsonObject, **converters: Callable[[Any], Any]) -> None:
    for key, converter in converters.items():
        try:
            value = d[key]
        except KeyError:
            continue

        if value is None:
            continue

        d[key] = converter(value)


def json_keys_to_datetime(d: JsonObject, *keys: str) -> None:
    json_apply_converters(d, **{key: datetime.fromtimestamp for key in keys})


def json_keys_to_celsius(d: JsonObject, *keys: str) -> None:
    json_apply_converters(d, **{key: fahrenheit_to_celsius for key in keys})


def json_keys_to_kph(d: JsonObject, *keys: str) -> None:
    json_apply_converters(d, **{key: mph_to_kph for key in keys})


def json_keys_to_hpa(d: JsonObject, *keys: str) -> None:
    json_apply_converters(d, **{key: in_hg_to_hpa for key in keys})


def json_keys_counts_to_mm(d: JsonObject, collector: CollectorSize, *keys: str):
    for key in keys:
        counts = d.get(key)
        d[f"{key}_counts"] = counts
        if counts:
            d[key] = collector * counts


def json_set_default_none(d: JsonObject, *keys: str) -> None:
    for key in keys:
        if key not in d:
            d[key] = None
