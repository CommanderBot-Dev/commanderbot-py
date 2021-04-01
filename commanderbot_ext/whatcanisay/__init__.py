from discord.ext import commands

from commanderbot_ext.whatcanisay.whatcanisay_cog import WhatcanisayCog


def setup(bot: commands.Bot):
    bot.add_cog(WhatcanisayCog(bot))
