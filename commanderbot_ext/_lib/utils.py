from typing import List

from discord.ext.commands import Bot


def get_command_prefixes(bot: Bot) -> List[str]:
    if isinstance(bot.command_prefix, str):
        return [bot.command_prefix]
    if isinstance(bot.command_prefix, list):
        if prefixes := [p for p in bot.command_prefix if isinstance(p, str)]:
            return prefixes
    raise ValueError(f"Unable to get bot's command prefixes from: {bot.command_prefix}")


def get_command_prefix(bot: Bot) -> str:
    return get_command_prefixes(bot)[0]
