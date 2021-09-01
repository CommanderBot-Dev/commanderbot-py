from typing import Optional, Type

from discord.ext.commands import Bot, Cog

from commanderbot.core.commander_bot_base import CommanderBotBase


def check_commander_bot(bot: Bot) -> Optional[CommanderBotBase]:
    if isinstance(bot, CommanderBotBase):
        return bot


def add_configured_cog(bot: Bot, ext_name: str, cog_class: Type[Cog]):
    cog = None
    if cb := check_commander_bot(bot):
        if options := cb.get_extension_options(ext_name):
            cog = cog_class(bot, **options)
    if not cog:
        cog = cog_class(bot)
    bot.add_cog(cog)
