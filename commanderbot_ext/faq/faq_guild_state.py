from datetime import datetime

from commanderbot_lib.guild_state.abc.cog_guild_state import CogGuildState
from discord import Guild, Message, Reaction, User, Emoji, TextChannel
from discord.ext.commands import Context

from commanderbot_ext.faq.faq_cache import FaqEntry
from commanderbot_ext.faq.faq_options import FaqOptions
from commanderbot_ext.faq.faq_store import FaqStore
from commanderbot_ext.faq.faq_const import confirm, reject


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
            updated_on_str = faq_entry.updated_on.isoformat()
            lines = [
                f"<{faq_entry.message_link}>",
                "```",
                f"Name:       {faq_entry.name}",
                f"Aliases:    {aliases_str}",
                f"Added on:   {added_on_str}",
                f"Updated on: {updated_on_str}",
                f"Hits:       {faq_entry.hits}",
                "```",
            ]
            content = "\n".join(lines)
            await ctx.send(content)
        else:
            await ctx.send(f"No FAQ matching `{faq_query}`")

    async def add_faq(
        self, ctx: Context, faq_name: str, message: Message, content: str
    ):
        if await self.store.get_guild_faq_by_name(self.guild, faq_name):
            await ctx.send(f"FAQ named `{faq_name}` already exists")
        else:
            now = datetime.utcnow()
            faq_entry = FaqEntry(
                name=faq_name,
                content=content,
                message_link=message.jump_url,
                aliases=set(),
                added_on=now,
                updated_on=now,
                hits=0,
            )
            await self.store.add_guild_faq(self.guild, faq_entry)
            await ctx.send(f"Added FAQ named `{faq_name}`")

    async def confirm_remove_faq(self, ctx: Context, faq_name: str):
        if faq := await self.store.get_guild_faq(self.guild, faq_name):
            message: Message = await ctx.send(
                f"Are you sure you'd like to remove the FAQ `{faq.name}`? You won't be able to recover it.\n\
If you are sure, react to this message with {confirm}. To abort, react with {reject}",
                reference=ctx.message,
                mention_author=False,
            )
            await message.add_reaction(confirm)
            await message.add_reaction(reject)
            if guild_data := self.store.get_guild_data(self.guild):
                guild_data.confirmation[ctx.author.id] = (message, faq)
        else:
            await ctx.reply(
                f"Unknow FAQ {faq_name}", reference=ctx.message, mention_author=False
            )

    async def remove_faq(self, channel: TextChannel, faq: FaqEntry):
        if removed_faq_entry := await self.store.remove_guild_faq(self.guild, faq):
            await channel.send(f"Removed FAQ `{removed_faq_entry}`")

    async def update_faq(
        self, ctx: Context, faq_name: str, message: Message, content: str
    ):
        if faq_entry := await self.store.get_guild_faq_by_name(self.guild, faq_name):
            await self.store.update_faq(faq_entry, message, content)
            await ctx.send(f"Updated FAQ named `{faq_name}`")
        else:
            await ctx.send(f"No FAQ named `{faq_name}`")

    async def add_alias(
        self, ctx: Context, faq_name: str, faq_alias: str, guild: Guild
    ):
        if faq_entry := await self.store.get_guild_faq_by_name(self.guild, faq_name):
            if pre_faq := await self.store.add_alias_to_faq(
                faq_entry, faq_alias, guild
            ):
                await ctx.send(f"FAQ `{pre_faq}` already has alias `{faq_alias}`")
            else:
                await ctx.send(f"Added alias `{faq_alias}` to FAQ `{faq_name}`")
        else:
            await ctx.send(f"No FAQ named `{faq_name}`")

    async def remove_alias(self, ctx: Context, faq_alias: str, guild: Guild):
        if faq_name := await self.store.remove_alias_from_faq(faq_alias, guild):
            await ctx.send(f"Removed alias `{faq_alias}` from FAQ `{faq_name}`")
        else:
            await ctx.send(f"No FAQ has alias `{faq_alias}`")

    # @overrides CogGuildState
    async def on_message(self, message: Message):
        if await self.store.maybe_stop_confirmation(self.guild, message.author):
            await message.channel.send(
                "Aborted FAQ removal due to another message being sent"
            )
        prefix = self.options.prefix
        if prefix:
            content = message.content
            if isinstance(content, str):
                if content.startswith(prefix) and len(content) > len(prefix):
                    ctx = Context(message=message, prefix=prefix)
                    faq_query = content[len(prefix) :]
                    await self.show_faq(ctx, faq_query)

    async def on_reaction_add(self, reaction: Reaction, user: User):
        if reaction.emoji == confirm:
            if target := await self.store.test_confirmation(
                self.guild, reaction.message.id, user
            ):
                await self.remove_faq(reaction.message.channel, target)
        elif reaction.emoji == reject:
            async for user in reaction.users():
                if await self.store.maybe_stop_confirmation(self.guild, user):
                    await reaction.message.channel.send("Aborted FAQ removal")
