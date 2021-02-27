from typing import Optional

from commanderbot_lib import checks
from discord import Colour, Embed, Message, TextChannel
from discord.ext.commands import Bot, Cog, Context, command


class PosterBoardCog(Cog, name="commanderbot_ext.poster_board"):
    def __init__(self, bot: Bot):
        self.bot: Bot = bot

    @command(name="posterboard", aliases=["pb"])
    @checks.is_administrator()
    async def cmd_posterboard(
        self,
        ctx: Context,
        message: Message,
        title: Optional[str] = None,
        colour: Optional[Colour] = None,
        destination: Optional[TextChannel] = None,
    ):
        actual_dest = destination if destination is not None else ctx.channel
        assert isinstance(actual_dest, TextChannel)
        embed = Embed(
            title=title if title is not None else Embed.Empty,
            description=message.content,
            colour=colour if colour is not None else Embed.Empty,
        )
        await actual_dest.send(embed=embed)
