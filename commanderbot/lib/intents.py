from typing import Any, Optional, Type, TypeVar

import discord

from commanderbot.lib.data import FromData, ToData

__all__ = ("Intents",)


ST = TypeVar("ST", bound="Intents")


class Intents(discord.Intents, FromData, ToData):
    """Extends `discord.Intents` to simplify de/serialization."""

    # @overrides FromData
    @classmethod
    def try_from_data(cls: Type[ST], data: Any) -> Optional[ST]:
        if isinstance(data, int):
            return cls._from_value(data)
        elif isinstance(data, str):
            if intents_factory := getattr(cls, data, None):
                return intents_factory()
        elif isinstance(data, dict):
            return cls(**data)

    # @overrides ToData
    def to_data(self) -> Any:
        return self.__dict__
