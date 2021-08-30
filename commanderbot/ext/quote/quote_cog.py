from discord import AllowedMentions, Embed, Message
from discord.ext.commands import Bot, Cog, Context, command


class QuoteCog(Cog, name="commanderbot.ext.quote"):
    def __init__(self, bot: Bot):
        self.bot: Bot = bot

    async def construct_embed(self, ctx: Context, message: Message) -> Embed:
        quote_embed = Embed(
            description=message.clean_content,
            timestamp=message.created_at,
        )
        quote_embed.set_footer(
            text=f"{message.author} in #{message.channel}",
            icon_url=message.author.display_avatar.url,
        )
        return quote_embed

    async def do_quote(
        self,
        ctx: Context,
        message: Message,
        content: str,
        allowed_mentions: AllowedMentions,
    ):
        quote_embed = await self.construct_embed(ctx, message)
        await ctx.send(
            content,
            embed=quote_embed,
            allowed_mentions=allowed_mentions,
        )

    @command(name="quote")
    async def cmd_quote(self, ctx: Context, message: Message):
        content = (
            f"{ctx.author.mention} quoted {message.author.mention} {message.jump_url}"
        )
        allowed_mentions = AllowedMentions.none()
        await self.do_quote(
            ctx, message, content=content, allowed_mentions=allowed_mentions
        )

    @command(name="quotem")
    async def cmd_quotem(self, ctx: Context, message: Message):
        content = (
            f"{ctx.author.mention} quote-mentioned {message.author.mention}"
            + f" {message.jump_url}"
        )
        allowed_mentions = AllowedMentions(
            everyone=False,
            users=True,
            roles=False,
            replied_user=False,
        )
        await self.do_quote(
            ctx, message, content=content, allowed_mentions=allowed_mentions
        )
