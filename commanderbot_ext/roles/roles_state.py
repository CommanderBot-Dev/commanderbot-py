from dataclasses import dataclass
from typing import List

from discord import Role
from discord.ext.commands import Context

from commanderbot_ext._lib.guild_partitioned_cog_state import GuildPartitionedCogState
from commanderbot_ext.roles.roles_guild_state import RolesGuildState
from commanderbot_ext.roles.roles_store import RolesStore


@dataclass
class RolesState(GuildPartitionedCogState[RolesGuildState]):
    store: RolesStore

    async def list_roles(self, ctx: Context):
        if guild := self.ack_guild(ctx.guild):
            await self.guild_states[guild].list_roles(ctx)

    async def join_roles(self, ctx: Context, roles: List[Role]):
        if guild := self.ack_guild(ctx.guild):
            await self.guild_states[guild].join_roles(ctx, roles)

    async def leave_roles(self, ctx: Context, roles: List[Role]):
        if guild := self.ack_guild(ctx.guild):
            await self.guild_states[guild].leave_roles(ctx, roles)
