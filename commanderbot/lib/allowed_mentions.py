from typing import Any, Optional, Type, TypeVar

import discord

from commanderbot.lib.data import FromData, ToData

__all__ = ("AllowedMentions",)


ST = TypeVar("ST", bound="AllowedMentions")


class AllowedMentions(discord.AllowedMentions, FromData, ToData):
    """Extends `discord.AllowedMentions` to simplify de/serialization."""

    @classmethod
    def not_everyone(cls):
        return cls(everyone=False, users=True, roles=True, replied_user=True)

    @classmethod
    def only_replies(cls):
        return cls(everyone=False, users=False, roles=False, replied_user=True)

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
        return dict(
            everyone=self.everyone,
            users=self.users,
            roles=self.roles,
            replied_user=self.replied_user,
        )
