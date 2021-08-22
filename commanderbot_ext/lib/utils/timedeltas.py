from datetime import timedelta
from typing import Any, Dict, Optional

from commanderbot_ext.lib.data import MalformedData
from commanderbot_ext.lib.types import JsonObject

__all__ = (
    "timedelta_from_dict",
    "timedelta_to_dict",
    "try_timedelta_from_data",
    "timedelta_from_data",
    "timedelta_from_field",
    "timedelta_from_field_optional",
)


def timedelta_from_dict(d: Dict[str, Any]) -> timedelta:
    return timedelta(**d)


def timedelta_to_dict(td: timedelta) -> Dict[str, Any]:
    return dict(
        days=td.days,
        seconds=td.seconds,
        microseconds=td.microseconds,
    )


def try_timedelta_from_data(data: Any) -> Optional[timedelta]:
    if isinstance(data, (int, float)):
        return timedelta(milliseconds=data)
    if isinstance(data, dict):
        return timedelta_from_dict(data)


def timedelta_from_data(data: Any) -> timedelta:
    try:
        if (maybe_from_data := try_timedelta_from_data(data)) is not None:
            return maybe_from_data
    except Exception as ex:
        raise MalformedData(timedelta, data) from ex
    raise MalformedData(timedelta, data)


def timedelta_from_field(data: JsonObject, key: str) -> timedelta:
    return timedelta_from_data(data[key])


def timedelta_from_field_optional(data: JsonObject, key: str) -> Optional[timedelta]:
    if raw_value := data.get(key):
        return timedelta_from_data(raw_value)
