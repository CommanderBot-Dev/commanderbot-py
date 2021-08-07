from datetime import datetime
from typing import Any

from commanderbot_ext.lib.types import JsonObject

__all__ = ("datetime_from_data",)


DEFAULT: Any = object()


def datetime_from_data(data: JsonObject, key: str, default: Any = DEFAULT) -> Any:
    if raw_datetime := data.get(key):
        return datetime.fromisoformat(raw_datetime)
    if default is not DEFAULT:
        return default
    raise KeyError(key)
