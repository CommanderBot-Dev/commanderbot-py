from typing import Any, Optional, Type, TypeVar

import discord
from discord.mentions import default

from commanderbot.lib.data import FromData, ToData

__all__ = ("AllowedMentions",)


ST = TypeVar("ST", bound="AllowedMentions")


class AllowedMentions(discord.AllowedMentions, FromData, ToData):
    """Extends `discord.AllowedMentions` to simplify de/serialization."""

    @classmethod
    def not_everyone(cls):
        return cls(everyone=False)

    @classmethod
    def only_replies(cls):
        return cls(everyone=False, users=False, roles=False)

    # @overrides FromData
    @classmethod
    def try_from_data(cls: Type[ST], data: Any) -> Optional[ST]:
        if isinstance(data, str):
            if factory := getattr(cls, data, None):
                return factory()
        if isinstance(data, dict):
            return cls(**data)

    # @overrides ToData
    def to_data(self) -> Any:
        fields = ("everyone", "users", "roles", "replied_user")
        data = {}
        for field in fields:
            if (value := getattr(self, field, default)) is not default:
                data[field] = value
        return data
