from typing import Any

import discord

from commanderbot.lib.from_data_mixin import FromDataMixin
from commanderbot.lib.json_serializable import JsonSerializable

__all__ = ("Intents",)


class Intents(JsonSerializable, discord.Intents, FromDataMixin):
    """Extends `discord.Intents` to simplify de/serialization."""

    # @overrides FromDataMixin
    @classmethod
    def try_from_data(cls, data):
        if isinstance(data, int):
            return cls._from_value(data)
        elif isinstance(data, str):
            if intents_factory := getattr(cls, data, None):
                return intents_factory()
        elif isinstance(data, dict):
            return cls(**data)

    # @implements JsonSerializable
    def to_json(self) -> Any:
        return self.__dict__
