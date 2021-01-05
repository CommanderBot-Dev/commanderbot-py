from datetime import datetime

from commanderbot_ext.faq.faq_cache import FaqEntry
from commanderbot_ext.faq.faq_options import FaqOptions
from commanderbot_ext.faq.faq_store import FaqStore
from commanderbot_lib.guild_state.abc.cog_guild_state import CogGuildState
from discord import Message
from discord.ext.commands import Context


class FaqGuildState(CogGuildState[FaqOptions, FaqStore]):
    async def list_faqs(self, ctx: Context):
        if entries := await self.store.iter_guild_faqs(self.guild):
            # Sort entries by hits -> name.
            sorted_entries = sorted(entries, key=lambda entry: (entry.hits, entry.name))
            count = len(sorted_entries)
            faq_names = (entry.name for entry in sorted_entries)
            text = f"There are {count} FAQs available: `" + "` `".join(faq_names) + "`"
            await ctx.send(text)
        else:
            await ctx.send(f"No FAQs available")

    async def show_faq(self, ctx: Context, faq_query: str):
        if entry := await self.store.get_guild_faq(self.guild, faq_query):
            await self.store.increment_faq_hits(entry)
            await ctx.send(entry.content)
        else:
            await ctx.send(f"No FAQ matching `{faq_query}`")

    async def show_faq_details(self, ctx: Context, faq_query: str):
        if faq_entry := await self.store.get_guild_faq(self.guild, faq_query):
            aliases_str = ", ".join(faq_entry.aliases)
            added_on_str = faq_entry.added_on.isoformat()
            last_modified_on_str = faq_entry.last_modified_on.isoformat()
            lines = [
                f"<{faq_entry.message_link}>",
                "```",
                f"Name:             {faq_entry.name}",
                f"Aliases:          {aliases_str}",
                f"Added on:         {added_on_str}",
                f"Last modified on: {last_modified_on_str}",
                f"Hits:             {faq_entry.hits}",
                "```",
            ]
            content = "\n".join(lines)
            await ctx.send(content)
        else:
            await ctx.send(f"No FAQ matching `{faq_query}`")

    async def add_faq(self, ctx: Context, faq_name: str, message: Message, content: str):
        if await self.store.get_guild_faq_by_name(self.guild, faq_name):
            await ctx.send(f"FAQ named `{faq_name}` already exists")
        else:
            now = datetime.utcnow()
            faq_entry = FaqEntry(
                name=faq_name,
                content=content,
                message_link=message.jump_url,
                aliases=[],
                added_on=now,
                last_modified_on=now,
                hits=0,
            )
            await self.store.add_guild_faq(self.guild, faq_entry)
            await ctx.send(f"Added FAQ named `{faq_name}`")

    async def remove_faq(self, ctx: Context, faq_name: str):
        if removed_faq_entry := await self.store.remove_guild_faq(self.guild, faq_name):
            await ctx.send(f"Removed FAQ `{removed_faq_entry.name}`")
        else:
            await ctx.send(f"No FAQ named `{faq_name}`")

    async def add_alias(self, ctx: Context, faq_name: str, faq_alias: str):
        if faq_entry := await self.store.get_guild_faq_by_name(self.guild, faq_name):
            if await self.store.add_alias_to_faq(faq_entry, faq_alias):
                await ctx.send(f"Added alias `{faq_alias}` to FAQ `{faq_name}`")
            else:
                await ctx.send(f"FAQ `{faq_name}` already has alias `{faq_alias}`")
        else:
            await ctx.send(f"No FAQ named `{faq_name}`")

    async def remove_alias(self, ctx: Context, faq_name: str, faq_alias: str):
        if faq_entry := await self.store.get_guild_faq_by_name(self.guild, faq_name):
            if await self.store.remove_alias_from_faq(faq_entry, faq_alias):
                await ctx.send(f"Removed alias `{faq_alias}` from FAQ `{faq_name}`")
            else:
                await ctx.send(f"FAQ `{faq_name}` has no alias `{faq_alias}`")
        else:
            await ctx.send(f"No FAQ named `{faq_name}`")

    # @overrides CogGuildState
    async def on_message(self, message: Message):
        prefix = self.options.prefix
        if prefix:
            content = message.content
            if isinstance(content, str):
                if content.startswith(prefix) and len(content) > len(prefix):
                    ctx = Context(message=message, prefix=prefix)
                    faq_query = content[len(prefix) :]
                    await self.show_faq(ctx, faq_query)
