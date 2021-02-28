from discord.ext.commands import Bot

from commanderbot_ext.pack.pack_cog import PackCog


def setup(bot: Bot):
    bot.add_cog(PackCog(bot))
