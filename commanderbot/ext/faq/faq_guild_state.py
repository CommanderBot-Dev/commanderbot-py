import re
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Tuple

from commanderbot_ext.ext.faq.faq_store import FaqException, FaqStore
from commanderbot_ext.lib import CogGuildState, GuildContext, TextMessage
from commanderbot_ext.lib.dialogs import ConfirmationResult, confirm_with_reaction
from commanderbot_ext.lib.utils import async_expand


@dataclass
class FaqGuildState(CogGuildState):
    """
    Encapsulates the state and logic of the FAQ cog, at the guild level.

    Attributes
    -----------
    store
        The store used to interface with persistent data in a database-agnostic way.
    """

    store: FaqStore

    async def on_message(self, message: TextMessage):
        # Check the message for any inline FAQ queries.
        if faq_entries := await self.store.scan_for_faqs(self.guild, message.content):
            for faq_entry in faq_entries:
                await self.store.increment_faq_hits(faq_entry)
                await message.channel.send(faq_entry.content)

    async def show_faq(self, ctx: GuildContext, faq_query: str):
        if faq_entries := await async_expand(
            self.store.query_faq_entries(self.guild, faq_query)
        ):
            for faq_entry in faq_entries:
                await self.store.increment_faq_hits(faq_entry)
                await ctx.send(faq_entry.content)
        else:
            await ctx.send(f"No FAQs matching `{faq_query}`")

    async def show_faq_details(self, ctx: GuildContext, faq_query: str):
        if faq_entries := await async_expand(
            self.store.query_faq_entries(self.guild, faq_query)
        ):
            for faq_entry in faq_entries:
                aliases_str = ", ".join(faq_entry.sorted_aliases)
                tags_str = ", ".join(faq_entry.sorted_tags)
                now = datetime.utcnow()
                added_on_timestamp = faq_entry.added_on.isoformat()
                added_on_delta = now - faq_entry.added_on
                added_on_str = f"{added_on_timestamp} ({added_on_delta})"
                modified_on_delta = now - faq_entry.modified_on
                modified_on_timestamp = faq_entry.modified_on.isoformat()
                modified_on_str = f"{modified_on_timestamp} ({modified_on_delta})"
                lines = [
                    f"Link: <{faq_entry.link}>",
                    "```",
                    f"Key:         {faq_entry.key}",
                    f"Aliases:     {aliases_str}",
                    f"Tags:        {tags_str}",
                    f"Added on:    {added_on_str}",
                    f"Modified on: {modified_on_str}",
                    f"Hits:        {faq_entry.hits}",
                    "```",
                ]
                content = "\n".join(lines)
                await ctx.send(content)
        else:
            await ctx.send(f"No FAQs matching `{faq_query}`")

    async def list_faqs(self, ctx: GuildContext):
        if faq_entries := await self.store.get_faq_entries(self.guild):
            # Sort entries alphabetically by key.
            sorted_faq_entries = sorted(
                faq_entries, key=lambda faq_entry: faq_entry.key
            )
            count = len(sorted_faq_entries)
            faq_keys = (entry.key for entry in sorted_faq_entries)
            text = f"There are {count} FAQs available: `" + "` `".join(faq_keys) + "`"
            await ctx.send(text)
        else:
            await ctx.send(f"No FAQs available")

    async def add_faq(self, ctx: GuildContext, faq_key: str, link: str, content: str):
        try:
            faq_entry = await self.store.add_faq(
                self.guild, faq_key, link=link, content=content
            )
            await ctx.send(f"Added FAQ `{faq_entry.key}`")
        except FaqException as ex:
            await ex.respond(ctx)

    async def remove_faq(self, ctx: GuildContext, faq_key: str):
        # Wrap this in case of multiple confirmations.
        try:
            # Get the corresponding FAQ entry.
            faq_entry = await self.store.require_faq_entry(self.guild, faq_key)
            # Then ask for confirmation to actually remove it.
            conf = await confirm_with_reaction(
                self.bot,
                ctx,
                f"Are you sure you want to remove FAQ `{faq_entry.key}`?",
            )
            # If the answer was yes, attempt to remove the FAQ and send a response.
            if conf == ConfirmationResult.YES:
                removed_entry = await self.store.remove_faq(self.guild, faq_key)
                await ctx.send(f"Removed FAQ `{removed_entry.key}`")
            # If the answer was no, send a response.
            elif conf == ConfirmationResult.NO:
                await ctx.send(f"Did not remove FAQ `{faq_key}`")
            # If no answer was provided, don't do anything.
        # If a known error occurred, send a response.
        except FaqException as ex:
            await ex.respond(ctx)

    async def modify_faq_content(self, ctx: GuildContext, faq_key: str, content: str):
        try:
            faq_entry = await self.store.modify_faq_content(
                self.guild, faq_key, content
            )
            await ctx.send(
                f"Set content for FAQ `{faq_entry.key}` to:\n>>> `{faq_entry.content}`"
            )
        except FaqException as ex:
            await ex.respond(ctx)

    async def modify_faq_link(
        self, ctx: GuildContext, faq_key: str, link: Optional[str]
    ):
        try:
            faq_entry = await self.store.modify_faq_link(self.guild, faq_key, link)
            if link:
                await ctx.send(
                    f"Set link for FAQ `{faq_entry.key}` to: `{faq_entry.link}`"
                )
            else:
                await ctx.send(f"Removed link for FAQ `{faq_entry.key}`")
        except FaqException as ex:
            await ex.respond(ctx)

    async def modify_faq_aliases(
        self, ctx: GuildContext, faq_key: str, aliases: Tuple[str, ...]
    ):
        try:
            faq_entry = await self.store.modify_faq_aliases(
                self.guild, faq_key, aliases
            )
            if aliases:
                aliases_str = "`" + "` `".join(faq_entry.sorted_aliases) + "`"
                await ctx.send(
                    f"Set aliases for FAQ `{faq_entry.key}` to: {aliases_str}"
                )
            else:
                await ctx.send(f"Removed aliases for FAQ `{faq_entry.key}`")
        except FaqException as ex:
            await ex.respond(ctx)

    async def modify_faq_tags(
        self, ctx: GuildContext, faq_key: str, tags: Tuple[str, ...]
    ):
        try:
            faq_entry = await self.store.modify_faq_tags(self.guild, faq_key, tags)
            if tags:
                tags_str = "`" + "` `".join(faq_entry.sorted_tags) + "`"
                await ctx.send(f"Set tags for FAQ `{faq_entry.key}` to: {tags_str}")
            else:
                await ctx.send(f"Removed tags for FAQ `{faq_entry.key}`")
        except FaqException as ex:
            await ex.respond(ctx)

    async def configure_prefix(self, ctx: GuildContext, prefix: Optional[str]):
        await self.store.configure_prefix(self.guild, prefix)
        if prefix:
            await ctx.send(f"Set FAQ prefix to: `{prefix}`")
        else:
            await ctx.send(f"Removed FAQ prefix")

    async def configure_match(self, ctx: GuildContext, match: Optional[str]):
        try:
            await self.store.configure_match(self.guild, match)
            if match:
                await ctx.send(f"Set FAQ match pattern to: `{match}`")
            else:
                await ctx.send(f"Removed FAQ match pattern")
        except re.error as ex:
            await ctx.send(f"Invalid pattern: {ex}")
