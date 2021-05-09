from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Tuple

from commanderbot_ext.ext.invite.invite_store import (
    InviteEntry,
    InviteException,
    InviteStore,
)
from commanderbot_ext.lib import CogGuildState, GuildContext
from commanderbot_ext.lib.dialogs import ConfirmationResult, confirm_with_reaction
from commanderbot_ext.lib.utils import async_expand


@dataclass
class InviteGuildState(CogGuildState):
    """
    Encapsulates the state and logic of the invite cog, at the guild level.

    Attributes
    -----------
    store
        The store used to interface with persistent data in a database-agnostic way.
    """

    store: InviteStore

    async def _show_invite_entry(self, ctx: GuildContext, invite_entry: InviteEntry):
        await self.store.increment_invite_hits(invite_entry)
        text = invite_entry.link
        if invite_entry.description:
            text = f"{invite_entry.description} - {invite_entry.link}"
        await ctx.send(text)

    async def show_invite(self, ctx: GuildContext, invite_query: str):
        if invite_entries := await async_expand(
            self.store.query_invite_entries(self.guild, invite_query)
        ):
            for invite_entry in invite_entries:
                await self._show_invite_entry(ctx, invite_entry)
        else:
            await ctx.send(f"No invites matching `{invite_query}`")

    async def show_guild_invite(self, ctx: GuildContext):
        if invite_entry := await self.store.get_guild_invite_entry(self.guild):
            await self._show_invite_entry(ctx, invite_entry)
        else:
            await self.list_invites(ctx)

    async def show_invite_details(self, ctx: GuildContext, invite_query: str):
        if invite_entries := await async_expand(
            self.store.query_invite_entries(self.guild, invite_query)
        ):
            for invite_entry in invite_entries:
                tags_str = ", ".join(invite_entry.sorted_tags)
                now = datetime.utcnow()
                added_on_timestamp = invite_entry.added_on.isoformat()
                added_on_delta = now - invite_entry.added_on
                added_on_str = f"{added_on_timestamp} ({added_on_delta})"
                modified_on_timestamp = invite_entry.modified_on.isoformat()
                modified_on_delta = now - invite_entry.modified_on
                modified_on_str = f"{modified_on_timestamp} ({modified_on_delta})"
                lines = [
                    "```",
                    f"Key:         {invite_entry.key}",
                    f"Tags:        {tags_str}",
                    f"Description: {invite_entry.description}",
                    f"Added on:    {added_on_str}",
                    f"Modified on: {modified_on_str}",
                    f"Hits:        {invite_entry.hits}",
                    "```",
                ]
                content = "\n".join(lines)
                await ctx.send(content)
        else:
            await ctx.send(f"No invites matching `{invite_query}`")

    async def list_invites(self, ctx: GuildContext):
        if invite_entries := await self.store.get_invite_entries(self.guild):
            # Sort entries alphabetically by key.
            sorted_invite_entries = sorted(
                invite_entries, key=lambda invite_entry: invite_entry.key
            )
            count = len(sorted_invite_entries)
            lines = [f"There are {count} invites available:", "```"]
            for invite_entry in sorted_invite_entries:
                if invite_entry.description:
                    lines.append(f"{invite_entry.key} - {invite_entry.description}")
                else:
                    lines.append(f"{invite_entry.key}")
            lines.append("```")
            text = "\n".join(lines)
            await ctx.send(text)
        else:
            await ctx.send(f"No invites available")

    async def add_invite(self, ctx: GuildContext, invite_key: str, link: str):
        try:
            invite_entry = await self.store.add_invite(
                self.guild, invite_key, link=link
            )
            await ctx.send(f"Added invite `{invite_entry.key}`")
        except InviteException as ex:
            await ex.respond(ctx)

    async def remove_invite(self, ctx: GuildContext, invite_key: str):
        # Wrap this in case of multiple confirmations.
        try:
            # Get the corresponding invite entry.
            invite_entry = await self.store.require_invite_entry(self.guild, invite_key)
            # Then ask for confirmation to actually remove it.
            conf = await confirm_with_reaction(
                self.bot,
                ctx,
                f"Are you sure you want to remove invite `{invite_entry.key}`?",
            )
            # If the answer was yes, attempt to remove the invite and send a response.
            if conf == ConfirmationResult.YES:
                removed_entry = await self.store.remove_invite(self.guild, invite_key)
                await ctx.send(f"Removed invite `{removed_entry.key}`")
            # If the answer was no, send a response.
            elif conf == ConfirmationResult.NO:
                await ctx.send(f"Did not remove invite `{invite_key}`")
            # If no answer was provided, don't do anything.
        # If a known error occurred, send a response.
        except InviteException as ex:
            await ex.respond(ctx)

    async def modify_invite_link(self, ctx: GuildContext, invite_key: str, link: str):
        try:
            invite_entry = await self.store.modify_invite_link(
                self.guild, invite_key, link
            )
            await ctx.send(
                f"Set link for invite `{invite_entry.key}` to: `{invite_entry.link}`"
            )
        except InviteException as ex:
            await ex.respond(ctx)

    async def modify_invite_tags(
        self, ctx: GuildContext, invite_key: str, tags: Tuple[str, ...]
    ):
        try:
            invite_entry = await self.store.modify_invite_tags(
                self.guild, invite_key, tags
            )
            if tags:
                tags_str = "`" + "` `".join(invite_entry.sorted_tags) + "`"
                await ctx.send(
                    f"Set tags for invite `{invite_entry.key}` to: {tags_str}"
                )
            else:
                await ctx.send(f"Removed tags for invite `{invite_entry.key}`")
        except InviteException as ex:
            await ex.respond(ctx)

    async def modify_invite_description(
        self, ctx: GuildContext, invite_key: str, description: Optional[str]
    ):
        try:
            invite_entry = await self.store.modify_invite_description(
                self.guild, invite_key, description
            )
            if description:
                await ctx.send(
                    f"Set description for invite `{invite_entry.key}` to: `{description}`"
                )
            else:
                await ctx.send(f"Removed description for invite `{invite_entry.key}`")
        except InviteException as ex:
            await ex.respond(ctx)

    async def configure_guild_key(self, ctx: GuildContext, invite_key: Optional[str]):
        try:
            if invite_entry := await self.store.configure_guild_key(
                self.guild, invite_key
            ):
                await ctx.send(
                    f"Set the invite key for this guild to: `{invite_entry.key}` {invite_entry.link}"
                )
            else:
                await ctx.send(f"Removed the invite key for this guild")
        except InviteException as ex:
            await ex.respond(ctx)
