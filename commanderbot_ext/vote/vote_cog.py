import re

import discord
from commanderbot_lib.logging import Logger, get_clogger
from discord.ext.commands import Bot, Cog, Context, command


class VoteCog(Cog):
    def __init__(self, bot: Bot):
        self.bot: Bot = bot
        self._log: Logger = get_clogger(self)

    def get_emojis(self, message: discord.Message, ctx: Context):
        # Regex to get emojis in a message
        # https://github.com/Arcensoth/cogbot/blob/e4157822202151c293203adbbc5a73175307ac43/cogbot/cog_bot.py#L23
        emoji_patterns = re.compile(
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

        # Get all emojis in the message and return a generator.
        # All default emojis become unicode which can be reacted with no problem, and custom emojis become <:name:ID> which can be used normally
        emoji_matches = emoji_patterns.findall(message.clean_content)
        yield from emoji_matches

    @command(name="vote")
    async def cmd_vote(self, ctx: discord.Message):
        # If no emojis were specified, then use the default ones, then iterate over them (reaction cap is 20)
        for emoji in (self.get_emojis(ctx.message, ctx) or ("👍", "👎"))[:20]:
            try:
                # Attempt to react with the emoji specified
                await ctx.message.add_reaction(emoji)

            # If any error occurred, then don't bother adding the reaction
            except Exception as error:
                self._log.info(
                    f"Couldn't add reaction {emoji} to message {ctx.message.id}\nError is as follows:")
                self._log.info(error)
