import re
from typing import List, cast

from discord import Interaction
from discord.app_commands import AppCommandError, Choice, Transformer
from emoji import is_emoji

from commanderbot.lib import Color, ResponsiveException

__all__ = (
    "EmojiTransformer",
    "ColorTransformer",
)


CUSTOM_EMOJI_PATTERN = re.compile(r"\<a?\:\w+\:\d+\>")


class TransformerException(ResponsiveException, AppCommandError):
    pass


class InvalidEmoji(TransformerException):
    def __init__(self, emoji: str):
        self.emoji = emoji
        super().__init__(f"`{self.emoji}` is not a valid Discord or Unicode emoji")


class InvalidColor(TransformerException):
    def __init__(self, color: str):
        self.color = color
        super().__init__(
            f"`{self.color}` is not a valid color\n"
            "The supported color formats are "
            "`0x<hex>`, `#<hex>`, `0x#<hex>`, and `rgb(<number>, <number>, <number>)`"
        )


class EmojiTransformer(Transformer):
    """
    A transformer that validates that a string is a valid Unicode or Discord emoji
    """

    async def transform(self, interaction: Interaction, value: str) -> str:
        if is_emoji(value):
            return value
        elif CUSTOM_EMOJI_PATTERN.match(value):
            return value
        raise InvalidEmoji(value)


class ColorTransformer(Transformer):
    async def transform(self, interaction: Interaction, value: str) -> Color:
        try:
            return Color.from_str(value)
        except ValueError:
            raise InvalidColor(value)

    async def autocomplete(
        self, interaction: Interaction, value: str
    ) -> List[Choice[str]]:
        colors: list[Choice] = []
        for name, color in Color.presets(color_filter=value).items():
            if len(colors) == 25:
                break
            colors.append(Choice(name=name, value=color.to_hex()))
        return colors
