import re
from typing import Iterable, cast

import emoji
from discord import Message
from discord.ext.commands import Bot, Cog, Context, command

DEFAULT_VOTE_EMOJIS = ("👍", "👎")
CUSTOM_EMOJI_PATTERN = re.compile(r"\<\:\w+\:\d+\>")


class VoteCog(Cog, name="commanderbot.ext.vote"):
    def __init__(self, bot: Bot):
        self.bot: Bot = bot

    @staticmethod
    def get_emojis(message: Message) -> Iterable[str]:
        # Get message content and cast it to a string
        message_content: str = str(message.clean_content)

        # Find unicode and custom emojis in the message
        found_emojis: list = emoji.emoji_list(message_content)
        for custom_emoji in CUSTOM_EMOJI_PATTERN.finditer(message_content):
            found_emojis.append(
                {
                    "match_start": custom_emoji.start(),
                    "match_end": custom_emoji.end(),
                    "emoji": custom_emoji.group(),
                }
            )

        # Return early with the default emojis if no emojis were found
        if not found_emojis:
            return DEFAULT_VOTE_EMOJIS

        # Create a list of unique emojis that are sorted in the order they appeared
        emojis: list[str] = []
        for e in sorted(found_emojis, key=lambda i: i["match_start"]):
            emoji_char: str = str(e["emoji"])
            if emoji_char not in emojis:
                emojis.append(emoji_char)

        return emojis

    @command(name="vote")
    async def cmd_vote(self, ctx: Context):
        # Determine which emoji reactions to seed the message with, silently ignoring
        # errors raised by any individual emoji.
        for emoji in self.get_emojis(cast(Message, ctx.message)):
            try:
                await ctx.message.add_reaction(emoji)
            except:
                pass
