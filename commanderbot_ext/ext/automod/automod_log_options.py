from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from discord import Color

from commanderbot_ext.lib import ChannelID
from commanderbot_ext.lib.from_data_mixin import FromDataMixin
from commanderbot_ext.lib.utils import color_from_field


@dataclass
class AutomodLogOptions(FromDataMixin):
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
    def try_from_data(cls, data):
        if isinstance(data, int):
            return cls(channel=data)
        elif isinstance(data, dict):
            return cls(
                channel=data["channel"],
                emoji=data.get("emoji"),
                color=color_from_field(data, "color", None),
            )
