from datetime import datetime, timedelta
from typing import Optional

from discord import AllowedMentions, Colour, Embed, Message
from discord.abc import Messageable
from discord.ext.commands import Bot, Cog, Context, group
from discord.ext.commands.converter import ColourConverter

from commanderbot.lib import MessageableChannel, checks

HEADING_PREFIX = "👉"


class PosterBoardCog(Cog, name="commanderbot.ext.poster_board"):
    def __init__(self, bot: Bot):
        self.bot: Bot = bot

    async def send_embed(
        self,
        destination: Messageable,
        title: Optional[str] = None,
        content: Optional[str] = None,
        colour: Optional[Colour] = None,
    ):
        embed = Embed(
            title=title if title is not None else Embed.Empty,
            description=content if content is not None else Embed.Empty,
            colour=colour if colour is not None else Embed.Empty,
        )
        await destination.send(embed=embed)

    @group(name="posterboard", aliases=["pb"])
    @checks.is_administrator()
    async def cmd_posterboard(self, ctx: Context):
        if not ctx.invoked_subcommand:
            await ctx.send_help(self.cmd_posterboard)

    @cmd_posterboard.command(name="embed")
    @checks.is_administrator()
    async def cmd_posterboard_embed(
        self,
        ctx: Context,
        colour: Optional[Colour] = None,
        title: Optional[str] = None,
        destination: Optional[MessageableChannel] = None,
        *,
        content: Optional[str] = None,
    ):
        actual_dest = destination if destination is not None else ctx.channel
        await self.send_embed(
            destination=actual_dest, title=title, content=content, colour=colour
        )

    @cmd_posterboard.command(name="copy")
    @checks.is_administrator()
    async def cmd_posterboard_copy(
        self,
        ctx: Context,
        from_message: Message,
        to_message: Optional[Message] = None,
        destination: Optional[MessageableChannel] = None,
        limit: Optional[int] = 100,
    ):
        actual_dest = destination if destination is not None else ctx.channel
        to_message = to_message if to_message is not None else from_message
        after_ts: datetime = from_message.created_at - timedelta(milliseconds=1)
        before_ts: datetime = to_message.created_at + timedelta(milliseconds=1)
        messages = ctx.history(
            limit=limit, after=after_ts, before=before_ts, oldest_first=True
        )
        async for message in messages:
            content = str(message.content)
            if content.startswith(HEADING_PREFIX):
                em_tokens = content[len(HEADING_PREFIX) :].split(maxsplit=1)
                em_colour_str = em_tokens[0].strip()
                em_colour = await ColourConverter().convert(ctx, em_colour_str)
                em_content = em_tokens[1]
                await self.send_embed(
                    destination=actual_dest, content=em_content, colour=em_colour
                )
            else:
                files = [
                    await attachment.to_file() for attachment in message.attachments
                ]
                embeds = message.embeds
                allowed_mentions = AllowedMentions.none()
                await actual_dest.send(
                    content,
                    files=files,
                    embeds=embeds,
                    allowed_mentions=allowed_mentions,
                )
