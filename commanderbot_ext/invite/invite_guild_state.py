from datetime import datetime

from commanderbot_lib.guild_state.abc.cog_guild_state import CogGuildState
from discord import Message
from discord.ext.commands import Context

from commanderbot_ext.invite.invite_cache import InviteEntry
from commanderbot_ext.invite.invite_options import InviteOptions
from commanderbot_ext.invite.invite_store import InviteStore


class InviteGuildState(CogGuildState[InviteOptions, InviteStore]):
    async def list_invites(self, ctx: Context):
        entries = await self.store.iter_guild_invites(self.guild)
        if len(entries) > 0:
            # Sort entries by name.
            sorted_entries = sorted(entries, key=lambda entry: entry.name)
            count = len(sorted_entries)
            invite_names = (entry.name for entry in sorted_entries)
            header = f"There are {count} invite available:\n```"
            if count == 1:
                header = f"There is 1 invite available:\n```"
            text = header + "\n".join(invite_names) + "\n```"
            await ctx.send(text)
        else:
            await ctx.send("There are no invites available")

    async def add_invite(self, ctx: Context, name: str, link: str):
        if existing_entry := await self.store.add_invite(self.guild, name, link):
            await ctx.send(f"An invite already exists under the name {name}:\n{link}")
        else:
            await ctx.send(f"Added invite {name}")

    async def remove_invite(self, ctx: Context, name: str):
        if await self.store.remove_invite(self.guild, name):
            await ctx.send(f"Invite {name} removed")
        else:
            await ctx.send(f"No invite exists called {name}")
