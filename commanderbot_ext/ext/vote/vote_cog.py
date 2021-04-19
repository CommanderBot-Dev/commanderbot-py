import re
from typing import Iterable, cast

from discord import Message
from discord.ext.commands import Bot, Cog, Context, command

DEFAULT_VOTE_EMOJIS = ("👍", "👎")

EMOJIS_PATTERN = re.compile(
    "["
    "\U0001F1E0-\U0001F1FF"
    "\U0001F300-\U0001F5FF"
    "\U0001F600-\U0001F64F"
    "\U0001F680-\U0001F6FF"
    "\U0001F700-\U0001F77F"
    "\U0001F780-\U0001F7FF"
    "\U0001F800-\U0001F8FF"
    "\U0001F900-\U0001F9FF"
    "\U0001FA00-\U0001FA6F"
    "\U0001FA70-\U0001FAFF"
    "\U00002702-\U000027B0"
    "\U000024C2-\U0001F251"
    "\U0000200d"
    "]+|"
    r"\<\:\w+\:\d+\>"
    "",
    flags=re.UNICODE,
)


class VoteCog(Cog, name="commanderbot_ext.ext.vote"):
    def __init__(self, bot: Bot):
        self.bot: Bot = bot

    @staticmethod
    def get_vote_emojis(message: Message) -> Iterable[str]:
        # If the message has content, look for emojis within it.
        if message.clean_content:
            # If any emojis were found, use them instead of the defaults.
            if found_emojis := EMOJIS_PATTERN.findall(str(message.clean_content)):
                return found_emojis
        # If nothing else was returned, use the default vote emojis.
        return DEFAULT_VOTE_EMOJIS

    @command(name="vote")
    async def cmd_vote(self, ctx: Context):
        # Determine which emoji reactions to seed the message with, silently ignoring
        # errors raised by any individual emoji.
        for emoji in self.get_vote_emojis(cast(Message, ctx.message)):
            try:
                await ctx.message.add_reaction(emoji)
            except:
                pass
