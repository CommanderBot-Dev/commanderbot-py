import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Tuple, cast

from discord import AllowedMentions
from discord.abc import Messageable
from discord.ext.commands import MessageConverter

from commanderbot.ext.faq.faq_options import FaqOptions
from commanderbot.ext.faq.faq_store import FaqEntry, FaqStore
from commanderbot.lib import CogGuildState, GuildContext, TextMessage
from commanderbot.lib.dialogs import ConfirmationResult, confirm_with_reaction
from commanderbot.lib.utils import send_message_or_file

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

    _prefix_pattern: Optional[re.Pattern] = field(init=False, default=LAZY)
    _match_pattern: Optional[re.Pattern] = field(init=False, default=LAZY)

    async def get_prefix_pattern(self) -> Optional[re.Pattern]:
        if self._prefix_pattern is LAZY:
            self._prefix_pattern = await self.store.get_prefix_pattern(self.guild)
        return self._prefix_pattern

    async def get_match_pattern(self) -> Optional[re.Pattern]:
        if self._match_pattern is LAZY:
            self._match_pattern = await self.store.get_match_pattern(self.guild)
        return self._match_pattern

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

        prefix_pattern = await self.get_prefix_pattern()
        match_pattern = await self.get_match_pattern()

        # Check if the prefix is being used.
        if (
            prefix_pattern
            and self.options.allow_prefix
            and (prefix_match := prefix_pattern.match(content))
        ):
            name = "".join(prefix_match.groups())
            await self._show_faq(message.channel, name)
            return

        # Otherwise scan the message using the match pattern, if any.
        if match_pattern and self.options.allow_match:
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

    async def list_faqs(self, ctx: GuildContext):
        if faqs := await self.store.get_all_faqs(self.guild):
            sorted_faqs = sorted(faqs, key=lambda faq: faq.key)
            keys = ", ".join(f"`{faq.key}`" for faq in sorted_faqs)
            count = len(sorted_faqs)
            header = f"There are {count} FAQs available:"
            content = f"{header} {keys}"
            file_callback = lambda: (
                header,
                "\n".join(faq.key for faq in sorted_faqs),
                "faqs.txt",
            )
            await send_message_or_file(
                ctx,
                content,
                file_callback=file_callback,
                allowed_mentions=AllowedMentions.none(),
            )
        else:
            await ctx.send("No FAQs available")

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

    async def _parse_message_or_content(
        self, ctx: GuildContext, message_or_content: str
    ) -> Tuple[str, str]:
        try:
            message = await MessageConverter().convert(ctx, message_or_content)
            content = message.content
        except:
            message = ctx.message
            content = message_or_content
        return message.jump_url, content

    async def add_faq(self, ctx: GuildContext, key: str, message_or_content: str):
        link, content = await self._parse_message_or_content(ctx, message_or_content)
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

    async def modify_faq_content(
        self, ctx: GuildContext, name: str, message_or_content: str
    ):
        link, content = await self._parse_message_or_content(ctx, message_or_content)
        faq = await self.store.modify_faq_content(
            self.guild, name, link=link, content=content
        )
        await ctx.send(f"Set content for FAQ `{faq.key}` using: {link}")

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

    async def show_prefix_pattern(self, ctx: GuildContext):
        if prefix := await self.store.get_prefix_pattern(self.guild):
            await ctx.send(
                f"FAQ prefix pattern is currently set to: `{prefix.pattern}`"
            )
        else:
            await ctx.send("No FAQ prefix pattern is currently configured")

    async def set_prefix_pattern(self, ctx: GuildContext, prefix: str):
        try:
            result = await self.store.set_prefix_pattern(self.guild, prefix)
        except re.error as ex:
            await ctx.send(f"Invalid pattern: {ex}")
        else:
            self._prefix_pattern = result
            await ctx.send(f"Set FAQ prefix pattern to: `{prefix}`")

    async def clear_prefix_pattern(self, ctx: GuildContext):
        await self.store.set_prefix_pattern(self.guild, None)
        self._prefix_pattern = None
        await ctx.send(f"Removed FAQ prefix pattern")

    async def show_match_pattern(self, ctx: GuildContext):
        if match := await self.store.get_match_pattern(self.guild):
            await ctx.send(f"FAQ match pattern is currently set to: `{match.pattern}`")
        else:
            await ctx.send("No FAQ match pattern is currently configured")

    async def set_match_pattern(self, ctx: GuildContext, match: str):
        try:
            result = await self.store.set_match_pattern(self.guild, match)
        except re.error as ex:
            await ctx.send(f"Invalid pattern: {ex}")
        else:
            self._match_pattern = result
            await ctx.send(f"Set FAQ match pattern to: `{match}`")

    async def clear_match_pattern(self, ctx: GuildContext):
        await self.store.set_match_pattern(self.guild, None)
        self._match_pattern = None
        await ctx.send(f"Removed FAQ match pattern")
