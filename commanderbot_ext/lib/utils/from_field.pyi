from datetime import datetime
from typing import TypeVar, Union, overload

from discord import Color

from commanderbot_ext.lib.types import JsonObject

T = TypeVar("T")

@overload
def datetime_from_field(data: JsonObject, key: str) -> datetime: ...
@overload
def datetime_from_field(
    data: JsonObject, key: str, default: T
) -> Union[datetime, T]: ...
@overload
def color_from_field(data: JsonObject, key: str) -> Color: ...
@overload
def color_from_field(data: JsonObject, key: str, default: T) -> Union[Color, T]: ...
