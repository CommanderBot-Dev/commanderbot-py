import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Tuple, cast

from discord.abc import Messageable

from commanderbot.ext.faq.faq_options import FaqOptions
from commanderbot.ext.faq.faq_store import FaqEntry, FaqStore
from commanderbot.lib import CogGuildState, GuildContext, TextMessage
from commanderbot.lib.dialogs import ConfirmationResult, confirm_with_reaction

LAZY: None = cast(None, object())


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
    options: FaqOptions

    _prefix: Optional[str] = field(init=False, default=LAZY)
    _match: Optional[re.Pattern] = field(init=False, default=LAZY)

    async def get_prefix(self) -> Optional[str]:
        if self._prefix is LAZY:
            self._prefix = await self.store.get_prefix(self.guild)
        return self._prefix

    async def get_match(self) -> Optional[re.Pattern]:
        if self._match is LAZY:
            self._match = await self.store.get_match(self.guild)
        return self._match

    async def _send_faq(self, destination: Messageable, faq: FaqEntry):
        await self.store.increment_faq_hits(faq)
        await destination.send(faq.content)

    async def _show_faq(self, destination: Messageable, name: str):
        # Check for FAQ by name (key/alias).
        if faq := await self.store.get_faq_by_name(self.guild, name):
            await self._send_faq(destination, faq)

        # If none matched, suggest FAQs if any are produced by a generic query.
        elif faqs := await self.store.get_faqs_by_query(
            self.guild, name, self.options.query_cap
        ):
            sorted_faqs = sorted(faqs, key=lambda faq: faq.key)
            keys = " ".join(f"`{faq.key}`" for faq in sorted_faqs)
            await destination.send(
                f"No FAQ named `{name}`, but maybe you meant: {keys}"
            )

        # Otherwise, let the user know nothing was found.
        else:
            await destination.send(f"No FAQ named `{name}`")

    async def on_message(self, message: TextMessage):
        content = message.content

        prefix = await self.get_prefix()
        match = await self.get_match()

        # Check if the prefix is being used.
        if prefix and self.options.allow_prefix and content.startswith(prefix):
            name = content[len(prefix) :]
            await self._show_faq(message.channel, name)

        # Otherwise scan the message using the match pattern, if any.
        elif match and self.options.allow_match:
            faqs = await self.store.get_faqs_by_match(
                self.guild, content, self.options.match_cap
            )
            for faq in faqs:
                await self._send_faq(message.channel, faq)

    async def show_faq(self, ctx: GuildContext, name: str):
        await self._show_faq(ctx, name)

    async def show_faq_details(self, ctx: GuildContext, name: str):
        if faq := await self.store.get_faq_by_name(self.guild, name):
            aliases_str = ", ".join(faq.sorted_aliases)
            tags_str = ", ".join(faq.sorted_tags)
            now = datetime.utcnow()
            added_on_timestamp = faq.added_on.isoformat()
            added_on_delta = now - faq.added_on
            added_on_str = f"{added_on_timestamp} ({added_on_delta})"
            modified_on_delta = now - faq.modified_on
            modified_on_timestamp = faq.modified_on.isoformat()
            modified_on_str = f"{modified_on_timestamp} ({modified_on_delta})"
            lines = [
                f"Link: <{faq.link}>",
                "```",
                f"Key:         {faq.key}",
                f"Aliases:     {aliases_str}",
                f"Tags:        {tags_str}",
                f"Added on:    {added_on_str}",
                f"Modified on: {modified_on_str}",
                f"Hits:        {faq.hits}",
                "```",
            ]
            content = "\n".join(lines)
            await ctx.send(content)
        else:
            await ctx.send(f"No FAQ named `{name}`")

    async def search_faqs(self, ctx: GuildContext, query: str):
        if faqs := await self.store.get_faqs_by_query(
            self.guild, query, cap=self.options.query_cap
        ):
            sorted_faqs = sorted(faqs, key=lambda faq: faq.key)
            keys = " ".join(f"`{faq.key}`" for faq in sorted_faqs)
            count = len(sorted_faqs)
            text = f"Here are {count} FAQs matching `{query}`: {keys}"
            await ctx.send(text)
        else:
            await ctx.send(f"No FAQs matching `{query}`")

    async def add_faq(self, ctx: GuildContext, key: str, link: str, content: str):
        faq = await self.store.add_faq(self.guild, key, link=link, content=content)
        await ctx.send(f"Added FAQ `{faq.key}`")

    async def remove_faq(self, ctx: GuildContext, name: str):
        # Get the corresponding FAQ entry.
        faq = await self.store.require_faq_by_name(self.guild, name)
        # Then ask for confirmation to actually remove it.
        conf = await confirm_with_reaction(
            self.bot,
            ctx,
            f"Are you sure you want to remove FAQ `{faq.key}`?",
        )
        # If the answer was yes, attempt to remove the FAQ and send a response.
        if conf == ConfirmationResult.YES:
            removed_entry = await self.store.remove_faq(self.guild, name)
            await ctx.send(f"Removed FAQ `{removed_entry.key}`")
        # If the answer was no, send a response.
        elif conf == ConfirmationResult.NO:
            await ctx.send(f"Did not remove FAQ `{name}`")
        # If no answer was provided, don't do anything.

    async def modify_faq_content(self, ctx: GuildContext, name: str, content: str):
        faq = await self.store.modify_faq_content(self.guild, name, content)
        await ctx.send(f"Set content for FAQ `{faq.key}` to:\n>>> `{faq.content}`")

    async def modify_faq_link(self, ctx: GuildContext, name: str, link: Optional[str]):
        faq = await self.store.modify_faq_link(self.guild, name, link)
        if link:
            await ctx.send(f"Set link for FAQ `{faq.key}` to: `{faq.link}`")
        else:
            await ctx.send(f"Removed link for FAQ `{faq.key}`")

    async def modify_faq_aliases(
        self, ctx: GuildContext, name: str, aliases: Tuple[str, ...]
    ):
        faq = await self.store.modify_faq_aliases(self.guild, name, aliases)
        if aliases:
            aliases_str = "`" + "` `".join(faq.sorted_aliases) + "`"
            await ctx.send(f"Set aliases for FAQ `{faq.key}` to: {aliases_str}")
        else:
            await ctx.send(f"Removed aliases for FAQ `{faq.key}`")

    async def modify_faq_tags(
        self, ctx: GuildContext, name: str, tags: Tuple[str, ...]
    ):
        faq = await self.store.modify_faq_tags(self.guild, name, tags)
        if tags:
            tags_str = "`" + "` `".join(faq.sorted_tags) + "`"
            await ctx.send(f"Set tags for FAQ `{faq.key}` to: {tags_str}")
        else:
            await ctx.send(f"Removed tags for FAQ `{faq.key}`")

    async def show_prefix(self, ctx: GuildContext):
        if prefix := await self.store.get_prefix(self.guild):
            await ctx.send(f"FAQ shortcut prefix is currently set to: `{prefix}`")
        else:
            await ctx.send("No FAQ shortcut prefix is currently configured")

    async def set_prefix(self, ctx: GuildContext, prefix: str):
        result = await self.store.set_prefix(self.guild, prefix)
        self._prefix = result
        await ctx.send(f"Set FAQ shortcut prefix to: `{prefix}`")

    async def clear_prefix(self, ctx: GuildContext):
        await self.store.set_prefix(self.guild, None)
        self._prefix = None
        await ctx.send(f"Removed FAQ shortcut prefix")

    async def show_match(self, ctx: GuildContext):
        if match := await self.store.get_match(self.guild):
            await ctx.send(f"FAQ match pattern is currently set to: `{match.pattern}`")
        else:
            await ctx.send("No FAQ match pattern is currently configured")

    async def set_match(self, ctx: GuildContext, match: str):
        try:
            result = await self.store.set_match(self.guild, match)
        except re.error as ex:
            await ctx.send(f"Invalid pattern: {ex}")
        else:
            self._match = result
            await ctx.send(f"Set FAQ match pattern to: `{match}`")

    async def clear_match(self, ctx: GuildContext):
        await self.store.set_match(self.guild, None)
        self._match = None
        await ctx.send(f"Removed FAQ match pattern")
