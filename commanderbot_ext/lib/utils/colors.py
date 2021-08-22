from typing import Any, Optional

from discord import Color
from discord.ext.commands import ColourConverter

from commanderbot_ext.lib.data import MalformedData
from commanderbot_ext.lib.types import JsonObject

__all__ = (
    "color_from_hex",
    "color_to_hex",
    "try_color_from_data",
    "color_from_data",
    "color_from_field",
    "color_from_field_optional",
)


def color_from_hex(hex: str) -> Color:
    if hex.startswith("#"):
        arg = hex[1:]
    else:
        arg = hex
    return ColourConverter().parse_hex_number(arg)


def color_to_hex(color: Color) -> str:
    return str(color)


def try_color_from_data(data: Any) -> Optional[Color]:
    if isinstance(data, str):
        return color_from_hex(data)


def color_from_data(data: Any) -> Color:
    try:
        if (maybe_from_data := try_color_from_data(data)) is not None:
            return maybe_from_data
    except Exception as ex:
        raise MalformedData(Color, data) from ex
    raise MalformedData(Color, data)


def color_from_field(data: JsonObject, key: str) -> Color:
    return color_from_data(data[key])


def color_from_field_optional(data: JsonObject, key: str) -> Optional[Color]:
    if raw_value := data.get(key):
        return color_from_data(raw_value)
