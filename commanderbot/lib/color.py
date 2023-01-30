import inspect
from typing import Dict, Optional, Self

from discord import Colour

from commanderbot.lib.from_data_mixin import FromDataMixin

__all__ = ("Color",)


class Color(Colour, FromDataMixin):
    """Extends `discord.Colour` to simplify deserialization."""

    # @overrides FromDataMixin
    @classmethod
    def try_from_data(cls, data):
        if isinstance(data, str):
            return cls.from_str(data)
        elif isinstance(data, int):
            return cls(data)
        elif isinstance(data, dict):
            return cls.from_field_optional(data, "color")

    @classmethod
    def presets(cls, *, color_filter: Optional[str] = None) -> Dict[str, Self]:
        """
        Returns a dictionary containing all color presets.
        The `color_filter` parameter can be used to filter the color presets that are returned
        """

        colors: dict[str, Color] = {}
        for func_name, func in inspect.getmembers(Color, inspect.ismethod):
            # If we're seaching for specific functions, skip the current
            # function if it doesn't have the string we're searching for.
            if color_filter and color_filter not in func_name:
                continue

            # Check if the current function is one of the `@classmethod`s that
            # take no arguments and return this class/`discord.Color``
            signature = inspect.signature(func)
            doc_str = doc if (doc := inspect.getdoc(func)) else ""
            if len(signature.parameters) == 0 and "value of ``0" in doc_str:
                colors[func_name] = func()

        return colors

    def to_hex(self) -> str:
        return str(self)

    @classmethod
    def mcc_blue(cls) -> Self:
        """A factory method that returns a :class:`Color` with a value of ``0x00aced``."""
        return cls(0x00ACED)

   

