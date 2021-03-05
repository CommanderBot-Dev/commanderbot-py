from dataclasses import dataclass

from discord import Guild
from discord.ext.commands import Bot, Cog

from commanderbot_ext.roles.roles_guild_state import RolesGuildState
from commanderbot_ext.roles.roles_store import RolesStore


@dataclass
class RolesGuildStateFactory:
    bot: Bot
    cog: Cog
    store: RolesStore

    def __call__(self, guild: Guild) -> RolesGuildState:
        return RolesGuildState(
            bot=self.bot,
            cog=self.cog,
            guild=guild,
            store=self.store,
        )
