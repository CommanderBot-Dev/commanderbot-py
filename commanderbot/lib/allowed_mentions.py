from typing import Any

import discord
from discord.mentions import default

from commanderbot.lib.from_data_mixin import FromDataMixin
from commanderbot.lib.json_serializable import JsonSerializable

__all__ = ("AllowedMentions",)


class AllowedMentions(JsonSerializable, discord.AllowedMentions, FromDataMixin):
    """Extends `discord.AllowedMentions` to simplify de/serialization."""

    @classmethod
    def not_everyone(cls):
        return cls(everyone=False)

    @classmethod
    def only_replies(cls):
        return cls(everyone=False, users=False, roles=False)

    # @overrides FromDataMixin
    @classmethod
    def try_from_data(cls, data):
        if isinstance(data, str):
            if factory := getattr(cls, data, None):
                return factory()
        if isinstance(data, dict):
            return cls(**data)

    # @implements JsonSerializable
    def to_json(self) -> Any:
        fields = ("everyone", "users", "roles", "replied_user")
        data = {}
        for field in fields:
            if (value := getattr(self, field, default)) is not default:
                data[field] = value
        return data
