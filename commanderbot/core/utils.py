from typing import Optional, Type, Union

from discord import Interaction
from discord.abc import Snowflake
from discord.app_commands import AppCommand
from discord.ext.commands import Bot, Cog

from commanderbot.core.commander_bot_base import CommanderBotBase
from commanderbot.lib import AppCommandID, GuildID


def check_commander_bot(bot: Bot) -> Optional[CommanderBotBase]:
    if isinstance(bot, CommanderBotBase):
        return bot


def require_commander_bot(bot: Bot) -> CommanderBotBase:
    if isinstance(bot, CommanderBotBase):
        return bot
    raise TypeError("Bot is not a subclass of CommanderBotBase")


async def add_configured_cog(bot: Bot, ext_name: str, cog_class: Type[Cog]):
    cog = None
    if cb := check_commander_bot(bot):
        if options := cb.get_extension_options(ext_name):
            cog = cog_class(bot, **options)
    if not cog:
        cog = cog_class(bot)
    await bot.add_cog(cog)


def get_app_command(
    bot: Bot,
    command: Union[str, Interaction, AppCommandID],
    *,
    guild: Optional[Union[Snowflake, GuildID]] = None,
) -> Optional[AppCommand]:
    # Return early if we were passed an empty string
    if isinstance(command, str) and not command:
        return

    # Return early if the bot isn't a subclass of `CommanderBotBase`
    cb = check_commander_bot(bot)
    if not cb:
        return

    # If we were passed an interaction, check if it's for a command
    # and try extracting the qualified command name
    if isinstance(command, Interaction):
        if not command.command:
            return
        command = command.command.qualified_name

    # Try getting the app command
    return cb.command_tree.get_app_command(command, guild=guild)
