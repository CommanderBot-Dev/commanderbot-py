from datetime import datetime
from typing import TypeVar, Union, overload

from commanderbot_ext.lib.types import JsonObject

T = TypeVar("T")

@overload
def datetime_from_data(data: JsonObject, key: str) -> datetime: ...
@overload
def datetime_from_data(
    data: JsonObject, key: str, default: T
) -> Union[datetime, T]: ...
