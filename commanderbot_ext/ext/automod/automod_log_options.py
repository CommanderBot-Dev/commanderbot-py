from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

from discord import Color

from commanderbot_ext.lib import JsonObject
from commanderbot_ext.lib.types import ChannelID
from commanderbot_ext.lib.utils import DEFAULT, color_from_field


@dataclass
class AutomodLogOptions:
    """
    Data container for various log options.

    Attributes
    ----------
    channel
        The ID of the channel to log in.
    emoji
        The emoji used to represent the type of message.
    color
        The color used for embed stripes.
    """

    channel: ChannelID

    emoji: Optional[str] = None
    color: Optional[Color] = None

    @classmethod
    def from_data(cls, data: Any) -> AutomodLogOptions:
        if isinstance(data, int):
            return AutomodLogOptions(
                channel=data,
            )
        elif isinstance(data, dict):
            return AutomodLogOptions(
                channel=data["channel"],
                emoji=data.get("emoji"),
                color=color_from_field(data, "color", None),
            )
        raise ValueError("Invalid log options")

    @classmethod
    def from_field(
        cls, data: JsonObject, key: str, default: Any = DEFAULT
    ) -> AutomodLogOptions:
        if raw_value := data.get(key):
            return cls.from_data(raw_value)
        if default is not DEFAULT:
            return default
        raise KeyError(key)
