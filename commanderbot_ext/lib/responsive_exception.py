from discord.ext.commands import Context

__all__ = ("ResponsiveException",)


class ResponsiveException(Exception):
    async def respond(self, ctx: Context):
        await ctx.reply(str(self))
