import re
from ast import alias
from typing import Iterable, cast

import emoji
from discord import Message
from discord.ext.commands import Bot, Cog, Context, command

DEFAULT_VOTE_EMOJIS = ("👍", "👎")
CUSTOM_EMOJI_PATTERN = re.compile(r"\<a?\:\w+\:\d+\>")
LEFTOVERS_PATTERN = re.compile("🇦|🇧|🇨|🇩|🇪|🇫|🇬|🇭|🇮|🇯|🇰|🇱|🇲|🇳|🇴|🇵|🇶|🇷|🇸|🇹|🇺|🇻|🇼|🇽|🇾|🇿")


class VoteCog(Cog, name="commanderbot.ext.vote"):
    def __init__(self, bot: Bot):
        self.bot: Bot = bot

    @staticmethod
    def get_emojis(message: Message) -> Iterable[str]:
        # Get message content and cast it to a string
        message_content: str = str(message.clean_content)

        # Find unicode emoji in the message
        found_emojis: list = emoji.emoji_list(message_content)

        # Find custom Discord emoji
        for match in CUSTOM_EMOJI_PATTERN.finditer(message_content):
            found_emojis.append(
                {
                    "match_start": match.start(),
                    "match_end": match.end(),
                    "emoji": match.group(),
                }
            )

        # Create a copy of the message with all emojis removed
        leftovers = message_content
        for e in found_emojis:
            i = e["match_start"]
            j = e["match_end"]
            leftovers = leftovers[:i] + leftovers[j + 1 :]

        # Find any other leftover matches, such as regional indicators
        for match in LEFTOVERS_PATTERN.finditer(leftovers):
            found_emojis.append(
                {
                    "match_start": match.start(),
                    "match_end": match.end(),
                    "emoji": match.group(),
                }
            )

        # Return early with the default emojis if no emojis were found
        if not found_emojis:
            return DEFAULT_VOTE_EMOJIS

        # Create a list of unique emojis that are sorted in the order they appeared
        unique_emojis: list[str] = []
        for e in sorted(found_emojis, key=lambda i: i["match_start"]):
            emoji_char: str = str(e["emoji"])
            if emoji_char not in unique_emojis:
                unique_emojis.append(emoji_char)

        return unique_emojis

    @command(name="vote", aliases=["poll"])
    async def cmd_vote(self, ctx: Context):
        # Determine which emoji reactions to seed the message with, silently ignoring
        # errors raised by any individual emoji.
        for emoji in self.get_emojis(cast(Message, ctx.message)):
            try:
                await ctx.message.add_reaction(emoji)
            except:
                pass
