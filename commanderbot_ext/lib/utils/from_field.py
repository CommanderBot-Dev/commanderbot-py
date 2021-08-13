from datetime import datetime
from typing import Any

from commanderbot_ext.lib.types import JsonObject
from commanderbot_ext.lib.utils.utils import color_from_hex

__all__ = (
    "datetime_from_field",
    "color_from_field",
)


DEFAULT: Any = object()


def datetime_from_field(data: JsonObject, key: str, default: Any = DEFAULT) -> Any:
    if raw_datetime := data.get(key):
        return datetime.fromisoformat(raw_datetime)
    if default is not DEFAULT:
        return default
    raise KeyError(key)


def color_from_field(data: JsonObject, key: str, default: Any = DEFAULT) -> Any:
    if raw_color := data.get(key):
        return color_from_hex(raw_color)
    if default is not DEFAULT:
        return default
    raise KeyError(key)
