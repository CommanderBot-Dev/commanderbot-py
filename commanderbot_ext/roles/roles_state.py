from dataclasses import dataclass

from discord import Member, Role
from discord.ext.commands import Context

from commanderbot_ext._lib.guild_partitioned_cog_state import GuildPartitionedCogState
from commanderbot_ext.roles.roles_guild_state import RolesGuildState
from commanderbot_ext.roles.roles_store import RolesStore


@dataclass
class RolesState(GuildPartitionedCogState[RolesGuildState]):
    store: RolesStore

    async def register_role(
        self, ctx: Context, role: Role, joinable: bool, leavable: bool
    ):
        if guild := self.ack_guild(ctx.guild):
            await self.guild_states[guild].register_role(
                ctx, role, joinable=joinable, leavable=leavable
            )

    async def deregister_role(self, ctx: Context, role: Role):
        if guild := self.ack_guild(ctx.guild):
            await self.guild_states[guild].deregister_role(ctx, role)

    async def show_all_roles(self, ctx: Context):
        if guild := self.ack_guild(ctx.guild):
            await self.guild_states[guild].show_all_roles(ctx)

    async def show_relevant_roles(self, ctx: Context):
        if guild := self.ack_guild(ctx.guild):
            await self.guild_states[guild].show_relevant_roles(ctx)

    async def join_role(self, ctx: Context, role: Role):
        if guild := self.ack_guild(ctx.guild):
            await self.guild_states[guild].join_role(ctx, role)

    async def leave_role(self, ctx: Context, role: Role):
        if guild := self.ack_guild(ctx.guild):
            await self.guild_states[guild].leave_role(ctx, role)
