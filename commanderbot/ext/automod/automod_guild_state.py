import asyncio
import json
from dataclasses import dataclass
from datetime import datetime
from json import JSONDecodeError
from typing import Any, Optional, cast

import yaml
from discord import (
    AllowedMentions,
    Color,
    Member,
    RawMessageDeleteEvent,
    RawMessageUpdateEvent,
    RawReactionActionEvent,
    Role,
    TextChannel,
    Thread,
    ThreadMember,
    User,
)
from yaml import YAMLError

from commanderbot.ext.automod import events
from commanderbot.ext.automod.automod_event import AutomodEvent
from commanderbot.ext.automod.automod_store import AutomodStore
from commanderbot.ext.automod.node.node_kind import NodeKind
from commanderbot.ext.automod.rule import Rule
from commanderbot.lib import (
    CogGuildState,
    GuildContext,
    LogOptions,
    ResponsiveException,
    RoleSet,
    TextMessage,
    TextReaction,
)
from commanderbot.lib.dialogs import ConfirmationResult, confirm_with_reaction
from commanderbot.lib.utils import (
    JsonPath,
    JsonPathOp,
    async_expand,
    query_json_path,
    send_message_or_file,
)


@dataclass
class AutomodGuildState(CogGuildState):
    """
    Encapsulates the state and logic of the automod cog, at the guild level.

    Attributes
    -----------
    store
        The store used to interface with persistent data in a database-agnostic way.
    """

    store: AutomodStore

    async def _get_log_options_for_rule(self, rule: Rule) -> Optional[LogOptions]:
        # First try to grab the rule's specific logging configuration, if any.
        if rule.log:
            return rule.log
        # If it doesn't have any, return the guild-wide logging configuration. This may
        # also not exist, hence why it's optional.
        return await self.store.get_default_log_options(self.guild)

    def _parse_body(self, body: str) -> Any:
        content = body.strip("\n").strip("`")
        kind, _, content = content.partition("\n")
        if kind == "json":
            try:
                return json.loads(content)
            except JSONDecodeError as ex:
                raise ResponsiveException(str(ex)) from ex
        if kind == "yaml":
            try:
                return yaml.safe_load(content)
            except YAMLError as ex:
                raise ResponsiveException(str(ex)) from ex
        raise ResponsiveException("Missing code block declared as `json` or `yaml`")

    async def reply(self, ctx: GuildContext, content: str):
        """Wraps `Context.reply()` with some extension-default boilerplate."""
        await ctx.message.reply(
            content,
            allowed_mentions=AllowedMentions.none(),
        )

    async def member_has_permission(self, member: Member) -> bool:
        permitted_roles = await self.store.get_permitted_roles(self.guild)
        if permitted_roles is None:
            return False
        has_permission = permitted_roles.member_has_some(member)
        return has_permission

    async def show_default_log_options(self, ctx: GuildContext):
        log_options = await self.store.get_default_log_options(self.guild)
        if log_options:
            channel = cast(TextChannel, self.bot.get_channel(log_options.channel))
            await self.reply(
                ctx,
                f"Default logging is configured for {channel.mention}"
                + f"\n```\n{log_options!r}\n```",
            )
        else:
            await self.reply(ctx, f"No default logging is configured")

    async def set_default_log_options(
        self,
        ctx: GuildContext,
        channel: TextChannel,
        stacktrace: Optional[bool],
        emoji: Optional[str],
        color: Optional[Color],
    ):
        new_log_options = LogOptions(
            channel=channel.id,
            stacktrace=stacktrace,
            emoji=emoji,
            color=color,
        )
        old_log_options = await self.store.set_default_log_options(
            self.guild, new_log_options
        )
        if old_log_options:
            old_log_channel = cast(
                TextChannel, self.bot.get_channel(old_log_options.channel)
            )
            await self.reply(
                ctx,
                f"Moved default logging from {old_log_channel.mention}"
                + f" to {channel.mention}",
            )
        else:
            await self.reply(ctx, f"Configured default logging for {channel.mention}")

    async def remove_default_log_options(self, ctx: GuildContext):
        old_log_options = await self.store.set_default_log_options(self.guild, None)
        if old_log_options:
            channel = cast(TextChannel, self.bot.get_channel(old_log_options.channel))
            await self.reply(ctx, f"Removed default logging from {channel.mention}")
        else:
            await self.reply(ctx, f"No default logging is configured")

    async def show_permitted_roles(self, ctx: GuildContext):
        permitted_roles = await self.store.get_permitted_roles(self.guild)
        if permitted_roles:
            count_permitted_roles = len(permitted_roles)
            role_mentions = permitted_roles.to_mentions(self.guild)
            await self.reply(
                ctx,
                f"There are {count_permitted_roles} roles permitted to manage"
                + f" automod: {role_mentions}",
            )
        else:
            await self.reply(ctx, f"No roles are permitted to manage automod")

    async def set_permitted_roles(self, ctx: GuildContext, *roles: Role):
        new_permitted_roles = RoleSet(set(role.id for role in roles))
        new_role_mentions = new_permitted_roles.to_mentions(self.guild)
        old_permitted_roles = await self.store.set_permitted_roles(
            self.guild, new_permitted_roles
        )
        if old_permitted_roles:
            old_role_mentions = old_permitted_roles.to_mentions(self.guild)
            await self.reply(
                ctx,
                f"Changed permitted roles from {old_role_mentions}"
                + f" to {new_role_mentions}",
            )
        else:
            await self.reply(ctx, f"Changed permitted roles to {new_role_mentions}")

    async def clear_permitted_roles(self, ctx: GuildContext):
        old_permitted_roles = await self.store.set_permitted_roles(self.guild, None)
        if old_permitted_roles:
            role_mentions = old_permitted_roles.to_mentions(self.guild)
            await self.reply(ctx, f"Cleared all permitted roles: {role_mentions}")
        else:
            await self.reply(ctx, f"No roles are permitted to manage automod")

    # @@ NODES

    async def list_nodes(
        self,
        ctx: GuildContext,
        node_kind: NodeKind,
        query: Optional[str] = None,
    ):
        if query:
            nodes = await async_expand(
                self.store.query_nodes(self.guild, node_kind.node_type, query)
            )
        else:
            nodes = await async_expand(
                self.store.all_nodes(self.guild, node_kind.node_type)
            )

        if nodes:
            # Build each node's title.
            titles = [node.build_title() for node in nodes]

            # Sort the node titles alphabetically.
            sorted_titles = sorted(titles, key=lambda title: title.lower())

            # Print out a code block with the node titles.
            lines = [
                "```",
                *sorted_titles,
                "```",
            ]
            content = "\n".join(lines)
            await self.reply(ctx, content)

        elif query:
            await self.reply(ctx, f"No {node_kind} matching `{query}`")

        else:
            await self.reply(ctx, f"No {node_kind.plural} currently registered")

    async def print_node(
        self,
        ctx: GuildContext,
        node_kind: NodeKind,
        query: str,
        path: Optional[JsonPath] = None,
    ):
        nodes = await async_expand(
            self.store.query_nodes(self.guild, node_kind.node_type, query)
        )
        if nodes:
            # If multiple nodes were found, just use the first.
            node = nodes[0]

            # Turn the node into raw data.
            node_data = node.to_data()

            # Take a sub-section of the data, if necessary.
            output_data = node_data
            if path:
                output_data = query_json_path(output_data, path)

            # Turn the data into a YAML string.
            output_yaml = yaml.safe_dump(output_data, sort_keys=False)

            # If the output can fit into a code block, just send a response. Otherwise,
            # stuff it into a file and send it as an attachment.
            content = f"```yaml\n{output_yaml}\n```"
            file_callback = lambda: ("", output_yaml, f"{node.name}.yaml")
            return await send_message_or_file(
                ctx,
                content,
                file_callback=file_callback,
                allowed_mentions=AllowedMentions.none(),
            )

        else:
            await self.reply(ctx, f"No {node_kind} matching `{query}`")

    async def add_node(self, ctx: GuildContext, node_kind: NodeKind, body: str):
        data = self._parse_body(body)
        node = await self.store.add_node(self.guild, node_kind.node_type, data)
        await self.reply(ctx, f"Added {node_kind} `{node.name}`")

    async def remove_node(self, ctx: GuildContext, node_kind: NodeKind, name: str):
        # Get the corresponding node.
        node = await self.store.require_node(self.guild, node_kind.node_type, name)

        # Then ask for confirmation to actually remove it.
        conf = await confirm_with_reaction(
            self.bot,
            ctx,
            f"Are you sure you want to remove {node_kind} `{node.name}`?",
        )

        # If the answer was yes, attempt to remove the node and send a response.
        if conf == ConfirmationResult.YES:
            removed_node = await self.store.remove_node(
                self.guild, node_kind.node_type, node.name
            )
            await self.reply(ctx, f"Removed {node_kind} `{removed_node.name}`")

        # If the answer was no, send a response.
        elif conf == ConfirmationResult.NO:
            await self.reply(ctx, f"Did not remove {node_kind} `{node.name}`")

    async def enable_node(self, ctx: GuildContext, node_kind: NodeKind, name: str):
        node = await self.store.enable_node(self.guild, node_kind.node_type, name)
        await self.reply(ctx, f"Enabled {node_kind} `{node.name}`")

    async def disable_node(self, ctx: GuildContext, node_kind: NodeKind, name: str):
        node = await self.store.disable_node(self.guild, node_kind.node_type, name)
        await self.reply(ctx, f"Disabled {node_kind} `{node.name}`")

    async def modify_node(
        self,
        ctx: GuildContext,
        node_kind: NodeKind,
        name: str,
        path: JsonPath,
        op: JsonPathOp,
        body: str,
    ):
        data = self._parse_body(body)
        node = await self.store.modify_node(
            self.guild, node_kind.node_type, name, path, op, data
        )
        await self.reply(ctx, f"Modified {node_kind} `{node.name}`")

    # @@ EVENT HANDLERS

    async def _handle_rule_error(self, rule: Rule, error: Exception):
        error_message = f"Rule `{rule.name}` caused an error:"

        # Re-raise the error so that it can be printed to the console.
        try:
            raise error
        except:
            self.log.exception(error_message)

        # Attempt to print the error to the log channel, if any.
        if log_options := await self._get_log_options_for_rule(rule):
            try:
                error_codeblock = log_options.format_error_codeblock(error)
                await log_options.send(
                    self.bot,
                    f"{error_message}\n{error_codeblock}",
                    file_callback=lambda: (error_message, error_codeblock, "error.txt"),
                )
            except:
                # If something went wrong here, print another exception to the console.
                self.log.exception("Failed to log message to error channel")

    async def _run_rule(self, event: AutomodEvent, rule: Rule):
        try:
            if await rule.run(event):
                await self.store.increment_rule_hits(self.guild, rule.name)
        except Exception as error:
            await self._handle_rule_error(rule, error)

    async def dispatch_event(self, event: AutomodEvent):
        # Run rules in parallel so that they don't need to wait for one another. They
        # run separately so that when a rule fails it doesn't stop the others.
        rules = await async_expand(self.store.rules_for_event(self.guild, event))
        if rules:
            tasks = [self._run_rule(event, rule) for rule in rules]
            await asyncio.gather(*tasks)

    async def on_typing(
        self, channel: TextChannel | Thread, member: Member, when: datetime
    ):
        await self.dispatch_event(
            events.MemberTyping(self, self.bot, self.log, channel, member, when)
        )

    async def on_message(self, message: TextMessage):
        await self.dispatch_event(events.MessageSent(self, self.bot, self.log, message))

    async def on_message_delete(self, message: TextMessage):
        await self.dispatch_event(
            events.MessageDeleted(self, self.bot, self.log, message)
        )

    async def on_message_edit(self, before: TextMessage, after: TextMessage):
        await self.dispatch_event(
            events.MessageEdited(self, self.bot, self.log, before, after)
        )

    async def on_reaction_add(self, reaction: TextReaction, member: Member):
        await self.dispatch_event(
            events.ReactionAdded(self, self.bot, self.log, reaction, member)
        )

    async def on_reaction_remove(self, reaction: TextReaction, member: Member):
        await self.dispatch_event(
            events.ReactionRemoved(self, self.bot, self.log, reaction, member)
        )

    async def on_channel_create(self, channel: TextChannel | Thread):
        await self.dispatch_event(
            events.GuildChannelCreated(self, self.bot, self.log, channel)
        )

    async def on_channel_delete(self, channel: TextChannel | Thread):
        await self.dispatch_event(
            events.GuildChannelDeleted(self, self.bot, self.log, channel)
        )

    async def on_channel_update(
        self, before: TextChannel | Thread, after: TextChannel | Thread
    ):
        await self.dispatch_event(
            events.GuildChannelUpdated(self, self.bot, self.log, before, after)
        )

    async def on_thread_create(self, thread: Thread):
        await self.dispatch_event(
            events.ThreadCreated(self, self.bot, self.log, thread)
        )

    async def on_thread_join(self, thread: Thread):
        await self.dispatch_event(events.ThreadJoined(self, self.bot, self.log, thread))

    async def on_thread_remove(self, thread: Thread):
        await self.dispatch_event(
            events.ThreadRemoved(self, self.bot, self.log, thread)
        )

    async def on_thread_delete(self, thread: Thread):
        await self.dispatch_event(
            events.ThreadDeleted(self, self.bot, self.log, thread)
        )

    async def on_thread_update(self, before: Thread, after: Thread):
        await self.dispatch_event(
            events.ThreadUpdated(self, self.bot, self.log, before, after)
        )

    async def on_thread_member_join(self, member: ThreadMember):
        await self.dispatch_event(
            events.ThreadMemberJoined(self, self.bot, self.log, member)
        )

    async def on_thread_member_leave(self, member: ThreadMember):
        await self.dispatch_event(
            events.ThreadMemberLeft(self, self.bot, self.log, member)
        )

    async def on_member_join(self, member: Member):
        await self.dispatch_event(events.MemberJoined(self, self.bot, self.log, member))

    async def on_member_remove(self, member: Member):
        await self.dispatch_event(events.MemberLeft(self, self.bot, self.log, member))

    async def on_member_update(self, before: Member, after: Member):
        await self.dispatch_event(
            events.MemberUpdated(self, self.bot, self.log, before, after)
        )

    async def on_user_update(self, before: User, after: User, member: Member):
        await self.dispatch_event(
            events.UserUpdated(self, self.bot, self.log, before, after, member)
        )

    async def on_user_ban(self, user: User):
        await self.dispatch_event(events.UserBanned(self, self.bot, self.log, user))

    async def on_user_unban(self, user: User):
        await self.dispatch_event(events.UserUnbanned(self, self.bot, self.log, user))

    # @@ RAW EVENT HANDLERS

    async def on_raw_message_delete(self, payload: RawMessageDeleteEvent):
        await self.dispatch_event(
            events.RawMessageDeleted(self, self.bot, self.log, payload)
        )

    async def on_raw_message_edit(self, payload: RawMessageUpdateEvent):
        await self.dispatch_event(
            events.RawMessageEdited(self, self.bot, self.log, payload)
        )

    async def on_raw_reaction_add(self, payload: RawReactionActionEvent):
        await self.dispatch_event(
            events.RawReactionAdded(self, self.bot, self.log, payload)
        )

    async def on_raw_reaction_remove(self, payload: RawReactionActionEvent):
        await self.dispatch_event(
            events.RawReactionRemoved(self, self.bot, self.log, payload)
        )
