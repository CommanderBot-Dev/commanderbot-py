import re

from discord import Interaction
from discord.app_commands import AppCommandError, Transformer
from emoji import is_emoji

from commanderbot.lib.responsive_exception import ResponsiveException

__all__ = ("EmojiTransformer",)


CUSTOM_EMOJI_PATTERN = re.compile(r"\<a?\:\w+\:\d+\>")


class TransformerException(ResponsiveException, AppCommandError):
    pass


class InvalidEmoji(TransformerException):
    def __init__(self, emoji: str):
        self.emoji = emoji
        super().__init__(f"`{self.emoji}` is not a valid Discord or Unicode emoji")


class EmojiTransformer(Transformer):
    """
    A transformer that validates that a string is a valid Unicode or Discord emoji
    """

    async def transform(self, interaction: Interaction, emoji: str) -> str:
        if is_emoji(emoji):
            return emoji
        elif CUSTOM_EMOJI_PATTERN.match(emoji):
            return emoji
        raise InvalidEmoji(emoji)
