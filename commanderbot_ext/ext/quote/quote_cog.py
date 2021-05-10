from discord import Embed
from discord.ext.commands import Bot, Cog, Context, command


class QuoteCog(Cog, name="commanderbot_ext.ext.quote"):
    def __init__(self, bot: Bot):
        self.bot: Bot = bot

    async def construct_embed(self, msg_link: str, quotem: bool = False):
        message_link = msg_link.split("/")
        message_channel = self.bot.get_channel(int(message_link[-2]))
        message = await message_channel.fetch_message(int(message_link[-1]))

        # message.author is name + discrim, icon_url is authors avatar
        quote_embed = Embed(
            description=message.clean_content, timestamp=message.created_at
        )
        quote_embed.set_author(
            name=str(message.author), icon_url=str(message.author.avatar_url)
        )
        quote_embed.set_footer(text=f"#{message_channel.name}")

        if quotem:
            return (quote_embed, message.author)
        return quote_embed

    @command(name="quote")
    async def cmd_quote(self, ctx: Context, msg_link: str):
        quote_embed = await self.construct_embed(msg_link)
        await ctx.send(f"{msg_link}", embed=quote_embed, reference=ctx.message)

    @command(name="quotem")
    async def cmd_quotem(self, ctx: Context, msg_link: str):
        quote_embed = await self.construct_embed(msg_link, quotem=True)
        await ctx.send(
            f"{quote_embed[1].mention}\n{msg_link}",
            embed=quote_embed[0],
            reference=ctx.message,
        )
