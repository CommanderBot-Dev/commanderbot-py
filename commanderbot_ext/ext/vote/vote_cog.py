from typing import Iterable, cast

from discord import Message
from discord.ext.commands import Bot, Cog, Context, command
from emoji.core import distinct_emoji_lis

DEFAULT_VOTE_EMOJIS = ("👍", "👎")


class VoteCog(Cog, name="commanderbot_ext.ext.vote"):
    def __init__(self, bot: Bot):
        self.bot: Bot = bot

    @staticmethod
    def get_emojis(message: Message) -> Iterable[str]:
        # Get message content and cast it to a string
        message_content = str(message.clean_content)

        # If message contents had any emojis, return them
        if emojis := distinct_emoji_lis(message_content):
            return emojis

        # Return default emojis if none were found
        return DEFAULT_VOTE_EMOJIS

    @command(name="vote")
    async def cmd_vote(self, ctx: Context):
        # Determine which emoji reactions to seed the message with, silently ignoring
        # errors raised by any individual emoji.
        for emoji in self.get_emojis(cast(Message, ctx.message)):
            try:
                await ctx.message.add_reaction(emoji)
            except:
                pass
