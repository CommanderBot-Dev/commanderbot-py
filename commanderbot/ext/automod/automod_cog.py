from datetime import datetime
from typing import Optional, cast

from discord import (
    Color,
    Guild,
    Member,
    Message,
    RawMessageDeleteEvent,
    RawMessageUpdateEvent,
    RawReactionActionEvent,
    Reaction,
    Role,
    TextChannel,
    Thread,
    ThreadMember,
    User,
)
from discord.abc import GuildChannel
from discord.ext import commands
from discord.ext.commands import Bot, Cog, Context

from commanderbot.ext.automod.automod_data import AutomodData
from commanderbot.ext.automod.automod_guild_state import AutomodGuildState
from commanderbot.ext.automod.automod_json_store import AutomodJsonStore
from commanderbot.ext.automod.automod_options import AutomodOptions
from commanderbot.ext.automod.automod_state import AutomodState
from commanderbot.ext.automod.automod_store import AutomodStore
from commanderbot.lib import (
    CogGuildStateManager,
    GuildContext,
    InMemoryDatabaseOptions,
    JsonFileDatabaseAdapter,
    JsonFileDatabaseOptions,
    MessageableChannel,
    TextMessage,
    TextReaction,
    UnsupportedDatabaseOptions,
    checks,
)
from commanderbot.lib.utils import is_bot, parse_json_path, parse_json_path_op


def make_automod_store(bot: Bot, cog: Cog, options: AutomodOptions) -> AutomodStore:
    db_options = options.database
    if isinstance(db_options, InMemoryDatabaseOptions):
        return AutomodData()
    if isinstance(db_options, JsonFileDatabaseOptions):
        return AutomodJsonStore(
            bot=bot,
            cog=cog,
            db=JsonFileDatabaseAdapter(
                options=db_options,
                serializer=lambda cache: cache.to_data(),
                deserializer=AutomodData.from_data,
            ),
        )
    raise UnsupportedDatabaseOptions(db_options)


def member_has_permission():
    async def predicate(ctx: Context):
        cog = cast(AutomodCog, ctx.cog)
        return (
            isinstance(ctx.guild, Guild)
            and isinstance(ctx.author, Member)
            and await cog.state[ctx.guild].member_has_permission(ctx.author)
        )

    return commands.check(predicate)


class AutomodCog(Cog, name="commanderbot.ext.automod"):
    """
    Automate a variety of moderation tasks.

    Attributes
    ----------
    bot
        The bot/client instance this cog is attached to.
    options
        Immutable, pre-defined settings that define core cog behaviour.
    store
        Abstracts the data storage and persistence of this cog.
    state
        Encapsulates the state and logic of this cog, for each guild.
    """

    def __init__(self, bot: Bot, **options):
        self.bot: Bot = bot
        self.bot = bot
        self.options = AutomodOptions.from_dict(options)
        self.store: AutomodStore = make_automod_store(bot, self, self.options)
        self.state = AutomodState(
            bot=self.bot,
            cog=self,
            guilds=CogGuildStateManager(
                bot=self.bot,
                cog=self,
                factory=lambda guild: AutomodGuildState(
                    bot=bot, cog=self, guild=guild, store=self.store
                ),
            ),
            store=self.store,
        )

    def _guild_state_for_message(self, message: Message) -> Optional[AutomodGuildState]:
        if isinstance(message.channel, TextChannel | Thread) and (
            not is_bot(self.bot, message.author)
        ):
            return self.state[message.channel.guild]

    def _guild_state_for_member(self, member: Member) -> Optional[AutomodGuildState]:
        if not is_bot(self.bot, member):
            return self.state[member.guild]

    def _guild_state_for_channel(
        self, channel: GuildChannel
    ) -> Optional[AutomodGuildState]:
        if isinstance(channel, TextChannel | Thread):
            return self.state[channel.guild]

    def _guild_state_for_thread(self, thread: Thread) -> Optional[AutomodGuildState]:
        if (parent := thread.parent) and (guild := parent.guild):
            return self.state[guild]

    def _guild_state_for_thread_member(
        self, member: ThreadMember
    ) -> Optional[AutomodGuildState]:
        return self._guild_state_for_thread(member.thread)

    def _guild_state_for_channel_user(
        self, channel: MessageableChannel, user: User
    ) -> Optional[AutomodGuildState]:
        if (
            isinstance(channel, TextChannel | Thread)
            and isinstance(user, Member)
            and (not is_bot(self.bot, user))
        ):
            return self.state[channel.guild]

    def _guild_state_for_reaction_actor(
        self, reaction: Reaction, actor: User
    ) -> Optional[AutomodGuildState]:
        if (
            isinstance(reaction.message.channel, TextChannel | Thread)
            and isinstance(actor, Member)
            and (not is_bot(self.bot, actor))
        ):
            return self.state[reaction.message.channel.guild]

    # @@ EVENT LISTENERS

    @Cog.listener()
    async def on_typing(self, channel: MessageableChannel, user: User, when: datetime):
        # https://discordpy.readthedocs.io/en/stable/api.html?highlight=events#discord.on_typing
        if guild_state := self._guild_state_for_channel_user(channel, user):
            await guild_state.on_typing(
                channel=cast(TextChannel, channel),
                member=cast(Member, user),
                when=when,
            )

    @Cog.listener()
    async def on_message(self, message: Message):
        # https://discordpy.readthedocs.io/en/stable/api.html?highlight=events#discord.on_message
        if guild_state := self._guild_state_for_message(message):
            await guild_state.on_message(
                message=cast(TextMessage, message),
            )

    @Cog.listener()
    async def on_message_delete(self, message: Message):
        # https://discordpy.readthedocs.io/en/stable/api.html?highlight=events#discord.on_message_delete
        if guild_state := self._guild_state_for_message(message):
            await guild_state.on_message_delete(
                message=cast(TextMessage, message),
            )

    @Cog.listener()
    async def on_message_edit(self, before: Message, after: Message):
        # https://discordpy.readthedocs.io/en/stable/api.html?highlight=events#discord.on_message_edit
        if guild_state := self._guild_state_for_message(after):
            await guild_state.on_message_edit(
                before=cast(TextMessage, before),
                after=cast(TextMessage, after),
            )

    @Cog.listener()
    async def on_reaction_add(self, reaction: Reaction, user: User):
        # https://discordpy.readthedocs.io/en/stable/api.html?highlight=events#discord.on_reaction_add
        if guild_state := self._guild_state_for_reaction_actor(reaction, user):
            await guild_state.on_reaction_add(
                reaction=cast(TextReaction, reaction),
                member=cast(Member, user),
            )

    @Cog.listener()
    async def on_reaction_remove(self, reaction: Reaction, user: User):
        # https://discordpy.readthedocs.io/en/stable/api.html?highlight=events#discord.on_reaction_remove
        if guild_state := self._guild_state_for_reaction_actor(reaction, user):
            await guild_state.on_reaction_remove(
                reaction=cast(TextReaction, reaction),
                member=cast(Member, user),
            )

    @Cog.listener()
    async def on_guild_channel_create(self, channel: GuildChannel):
        # https://discordpy.readthedocs.io/en/stable/api.html?highlight=events#discord.on_guild_channel_create
        if guild_state := self._guild_state_for_channel(channel):
            await guild_state.on_channel_create(
                channel=cast(TextChannel | Thread, channel),
            )

    @Cog.listener()
    async def on_guild_channel_delete(self, channel: GuildChannel):
        # https://discordpy.readthedocs.io/en/stable/api.html?highlight=events#discord.on_guild_channel_delete
        if guild_state := self._guild_state_for_channel(channel):
            await guild_state.on_channel_delete(
                channel=cast(TextChannel | Thread, channel),
            )

    @Cog.listener()
    async def on_guild_channel_update(self, before: GuildChannel, after: GuildChannel):
        # https://discordpy.readthedocs.io/en/stable/api.html?highlight=events#discord.on_guild_channel_update
        if guild_state := self._guild_state_for_channel(after):
            await guild_state.on_channel_update(
                before=cast(TextChannel | Thread, before),
                after=cast(TextChannel | Thread, after),
            )

    @Cog.listener()
    async def on_thread_join(self, thread: Thread):
        # https://discordpy.readthedocs.io/en/master/api.html#discord.on_thread_join
        # NOTE Blame the official Discord API for this jank work-around.
        # From the discord.py docs:
        # > Note that from the API’s perspective there is no way to differentiate
        # > between a thread being created or the bot joining a thread.
        # So what we do is we check the `me` property of the thread to determine whether
        # we're a member of it, and use that to determine how to proceed.
        if guild_state := self._guild_state_for_thread(thread):
            # If we're a member of the thread, we must've just joined it.
            if thread.me:
                await guild_state.on_thread_join(thread)
            # Otherwise, it must be a newly-created thread.
            else:
                await guild_state.on_thread_create(thread)

    @Cog.listener()
    async def on_thread_remove(self, thread: Thread):
        # https://discordpy.readthedocs.io/en/master/api.html#discord.on_thread_remove
        if guild_state := self._guild_state_for_thread(thread):
            await guild_state.on_thread_remove(thread)

    @Cog.listener()
    async def on_thread_delete(self, thread: Thread):
        # https://discordpy.readthedocs.io/en/master/api.html#discord.on_thread_delete
        if guild_state := self._guild_state_for_thread(thread):
            await guild_state.on_thread_delete(thread)

    @Cog.listener()
    async def on_thread_update(self, before: Thread, after: Thread):
        # https://discordpy.readthedocs.io/en/master/api.html#discord.on_thread_update
        if guild_state := self._guild_state_for_thread(after):
            await guild_state.on_thread_update(before, after)

    @Cog.listener()
    async def on_thread_member_join(self, member: ThreadMember):
        # https://discordpy.readthedocs.io/en/master/api.html#discord.on_thread_member_join
        if guild_state := self._guild_state_for_thread_member(member):
            await guild_state.on_thread_member_join(member)

    @Cog.listener()
    async def on_thread_member_leave(self, member: ThreadMember):
        # https://discordpy.readthedocs.io/en/master/api.html#discord.on_thread_member_leave
        if guild_state := self._guild_state_for_thread_member(member):
            await guild_state.on_thread_member_leave(member)

    @Cog.listener()
    async def on_member_join(self, member: Member):
        # https://discordpy.readthedocs.io/en/stable/api.html?highlight=events#discord.on_member_join
        if guild_state := self._guild_state_for_member(member):
            await guild_state.on_member_join(member)

    @Cog.listener()
    async def on_member_remove(self, member: Member):
        # https://discordpy.readthedocs.io/en/stable/api.html?highlight=events#discord.on_member_remove
        if guild_state := self._guild_state_for_member(member):
            await guild_state.on_member_remove(member)

    @Cog.listener()
    async def on_member_update(self, before: Member, after: Member):
        # https://discordpy.readthedocs.io/en/stable/api.html?highlight=events#discord.on_member_update
        if guild_state := self._guild_state_for_member(after):
            await guild_state.on_member_update(before, after)

    @Cog.listener()
    async def on_user_update(self, before: User, after: User):
        # https://discordpy.readthedocs.io/en/stable/api.html?highlight=events#discord.on_user_update
        # Go through every guild we can see, and check if the user is a member there.
        # For every guild the user is a member of, run the event handler.
        for guild in self.bot.guilds:
            guild: Guild
            if member := guild.get_member(after.id):
                if guild_state := self._guild_state_for_member(member):
                    await guild_state.on_user_update(before, after, member)

    @Cog.listener()
    async def on_member_ban(self, guild: Guild, user: User):
        # https://discordpy.readthedocs.io/en/stable/api.html?highlight=events#discord.on_member_ban
        guild_state = self.state[guild]
        await guild_state.on_user_ban(user)

    @Cog.listener()
    async def on_member_unban(self, guild: Guild, user: User):
        # https://discordpy.readthedocs.io/en/stable/api.html?highlight=events#discord.on_member_unban
        guild_state = self.state[guild]
        await guild_state.on_user_unban(user)

    # @@ RAW EVENT LISTENERS

    @Cog.listener()
    async def on_raw_message_edit(self, payload: RawMessageUpdateEvent):
        # https://discordpy.readthedocs.io/en/stable/api.html?highlight=events#discord.on_raw_message_edit
        if (guild_id := payload.guild_id) is not None:
            await self.state[guild_id].on_raw_message_edit(payload)

    @Cog.listener()
    async def on_raw_message_delete(self, payload: RawMessageDeleteEvent):
        # https://discordpy.readthedocs.io/en/stable/api.html?highlight=events#discord.on_raw_message_delete
        if (guild_id := payload.guild_id) is not None:
            await self.state[guild_id].on_raw_message_delete(payload)

    @Cog.listener()
    async def on_raw_reaction_add(self, payload: RawReactionActionEvent):
        # https://discordpy.readthedocs.io/en/stable/api.html?highlight=events#discord.on_raw_reaction_add
        if (guild_id := payload.guild_id) is not None:
            await self.state[guild_id].on_raw_reaction_add(payload)

    @Cog.listener()
    async def on_raw_reaction_remove(self, payload: RawReactionActionEvent):
        # https://discordpy.readthedocs.io/en/stable/api.html?highlight=events#discord.on_raw_reaction_remove
        if (guild_id := payload.guild_id) is not None:
            await self.state[guild_id].on_raw_reaction_remove(payload)

    # @@ COMMANDS

    # @@ automod

    @commands.group(
        name="automod",
        brief="Manage automod features.",
        aliases=["am"],
    )
    @checks.guild_only()
    @checks.any_of(
        checks.is_administrator(),
        member_has_permission(),
        commands.is_owner(),
    )
    async def cmd_automod(self, ctx: GuildContext):
        if not ctx.invoked_subcommand:
            await ctx.send_help(self.cmd_automod)

    # @@ automod options

    @cmd_automod.group(
        name="options",
        brief="Configure various automod options.",
    )
    async def cmd_automod_options(self, ctx: GuildContext):
        if not ctx.invoked_subcommand:
            await ctx.send_help(self.cmd_automod_options)

    # @@ automod options log

    @cmd_automod_options.group(
        name="log",
        brief="Configure the default logging behaviour.",
    )
    async def cmd_automod_options_log(self, ctx: GuildContext):
        if not ctx.invoked_subcommand:
            if ctx.subcommand_passed:
                await ctx.send_help(self.cmd_automod_options_log)
            else:
                await self.state[ctx.guild].show_default_log_options(ctx)

    @cmd_automod_options_log.command(
        name="show",
        brief="Show the default logging behaviour.",
    )
    async def cmd_automod_options_log_show(self, ctx: GuildContext):
        await self.state[ctx.guild].show_default_log_options(ctx)

    @cmd_automod_options_log.command(
        name="set",
        brief="Set the default logging behaviour.",
    )
    async def cmd_automod_options_log_set(
        self,
        ctx: GuildContext,
        channel: TextChannel,
        stacktrace: Optional[bool],
        emoji: Optional[str],
        color: Optional[Color],
    ):
        await self.state[ctx.guild].set_default_log_options(
            ctx,
            channel=channel,
            stacktrace=stacktrace,
            emoji=emoji,
            color=color,
        )

    @cmd_automod_options_log.command(
        name="remove",
        brief="Remove the default logging behaviour.",
    )
    async def cmd_automod_options_log_remove(self, ctx: GuildContext):
        await self.state[ctx.guild].remove_default_log_options(ctx)

    # @@ automod options permit

    # NOTE Only guild admins and bot owners can manage permitted roles.

    @cmd_automod_options.group(
        name="permit",
        brief="Configure the set of roles permitted to manage automod.",
    )
    @checks.is_guild_admin_or_bot_owner()
    async def cmd_automod_options_permit(self, ctx: GuildContext):
        if not ctx.invoked_subcommand:
            if ctx.subcommand_passed:
                await ctx.send_help(self.cmd_automod_options_permit)
            else:
                await self.state[ctx.guild].show_permitted_roles(ctx)

    @cmd_automod_options_permit.command(
        name="show",
        brief="Show the roles permitted to manage automod.",
    )
    async def cmd_automod_options_permit_show(self, ctx: GuildContext):
        await self.state[ctx.guild].show_permitted_roles(ctx)

    @cmd_automod_options_permit.command(
        name="set",
        brief="Set the roles permitted to manage automod.",
    )
    async def cmd_automod_options_permit_set(self, ctx: GuildContext, *roles: Role):
        await self.state[ctx.guild].set_permitted_roles(ctx, *roles)

    @cmd_automod_options_permit.command(
        name="clear",
        brief="Clear all roles permitted to manage automod.",
    )
    async def cmd_automod_options_permit_clear(self, ctx: GuildContext):
        await self.state[ctx.guild].clear_permitted_roles(ctx)

    # @@ automod rules

    @cmd_automod.group(
        name="rules",
        brief="Browse and manage automod rules.",
    )
    async def cmd_automod_rules(self, ctx: GuildContext):
        if not ctx.invoked_subcommand:
            if ctx.subcommand_passed:
                await ctx.send_help(self.cmd_automod_rules)
            else:
                await self.state[ctx.guild].show_rules(ctx)

    @cmd_automod_rules.command(
        name="show",
        brief="List and show automod rules.",
    )
    async def cmd_automod_rules_show(self, ctx: GuildContext, query: str):
        await self.state[ctx.guild].show_rules(ctx, query)

    @cmd_automod_rules.command(
        name="print",
        brief="Print the code of an automod rule.",
    )
    async def cmd_automod_rules_print(
        self,
        ctx: GuildContext,
        query: str,
        path: Optional[str],
    ):
        parsed_path = parse_json_path(path) if path else None
        await self.state[ctx.guild].print_rule(ctx, query, parsed_path)

    @cmd_automod_rules.command(
        name="add",
        brief="Add a new automod rule.",
    )
    async def cmd_automod_rules_add(self, ctx: GuildContext, *, body: str):
        await self.state[ctx.guild].add_rule(ctx, body)

    @cmd_automod_rules.command(
        name="remove",
        brief="Remove an automod rule.",
    )
    async def cmd_automod_rules_remove(self, ctx: GuildContext, name: str):
        await self.state[ctx.guild].remove_rule(ctx, name)

    @cmd_automod_rules.command(
        name="modify",
        brief="Modify an automod rule",
    )
    async def cmd_automod_rules_modify(
        self,
        ctx: GuildContext,
        name: str,
        path: str,
        op: str,
        *,
        body: str,
    ):
        parsed_path = parse_json_path(path)
        parsed_op = parse_json_path_op(op)
        await self.state[ctx.guild].modify_rule(ctx, name, parsed_path, parsed_op, body)

    @cmd_automod_rules.command(
        name="enable",
        brief="Enable an automod rule",
    )
    async def cmd_automod_rules_enable(self, ctx: GuildContext, name: str):
        await self.state[ctx.guild].enable_rule(ctx, name)

    @cmd_automod_rules.command(
        name="disable",
        brief="Disable an automod rule",
    )
    async def cmd_automod_rules_disable(self, ctx: GuildContext, name: str):
        await self.state[ctx.guild].disable_rule(ctx, name)
