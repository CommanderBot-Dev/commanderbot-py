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
from commanderbot.ext.automod.automod_event import AutomodEventBase
from commanderbot.ext.automod.automod_rule import AutomodRule
from commanderbot.ext.automod.automod_store import AutomodStore
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
from commanderbot.lib.json import to_data
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

    async def _get_log_options_for_rule(
        self, rule: AutomodRule
    ) -> Optional[LogOptions]:
        # First try to grab the rule's specific logging configuration, if any.
        if rule.log:
            return rule.log
        # If it doesn't have any, return the guild-wide logging configuration. This may
        # also not exist, hence why it's optional.
        return await self.store.get_default_log_options(self.guild)

    async def _handle_rule_error(self, rule: AutomodRule, error: Exception):
        error_message = f"Rule `{rule.name}` caused an error:"

        # Re-raise the error so that it can be printed to the console.
        try:
            raise error
        except:
            self.log.exception(error_message)

        # Attempt to print the error to the log channel, if any.
        if log_options := await self._get_log_options_for_rule(rule):
            try:
                error_codeblock = log_options.formate_error_codeblock(error)
                await log_options.send(
                    self.bot,
                    f"{error_message}\n{error_codeblock}",
                    file_callback=lambda: (error_message, error_codeblock, "error.txt"),
                )
            except:
                # If something went wrong here, print another exception to the console.
                self.log.exception("Failed to log message to error channel")

    async def _do_event_for_rule(self, event: AutomodEventBase, rule: AutomodRule):
        try:
            if await rule.run(event):
                await self.store.increment_rule_hits(self.guild, rule.name)
        except Exception as error:
            await self._handle_rule_error(rule, error)

    async def _do_event(self, event: AutomodEventBase):
        # Run rules in parallel so that they don't need to wait for one another. They
        # run separately so that when a rule fails it doesn't stop the others.
        rules = await async_expand(self.store.rules_for_event(self.guild, event))
        tasks = [self._do_event_for_rule(event, rule) for rule in rules]
        await asyncio.gather(*tasks)

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

    async def show_rules(self, ctx: GuildContext, query: str = ""):
        if query:
            rules = await async_expand(self.store.query_rules(self.guild, query))
        else:
            rules = await async_expand(self.store.all_rules(self.guild))
        count_rules = len(rules)
        if count_rules > 1:
            lines = ["```"]
            sorted_rules = sorted(rules, key=lambda rule: (rule.disabled, rule.name))
            for rule in sorted_rules:
                lines.append(rule.build_title())
            lines.append("```")
            content = "\n".join(lines)
            await self.reply(ctx, content)
        elif count_rules == 1:
            rule = rules[0]
            now = datetime.utcnow()
            added_on_timestamp = rule.added_on.isoformat()
            added_on_delta = now - rule.added_on
            added_on_str = f"{added_on_timestamp} ({added_on_delta})"
            modified_on_delta = now - rule.modified_on
            modified_on_timestamp = rule.modified_on.isoformat()
            modified_on_str = f"{modified_on_timestamp} ({modified_on_delta})"
            name_line = rule.build_title()
            lines = [
                "```",
                name_line,
                f"  Hits:        {rule.hits}",
                f"  Added on:    {added_on_str}",
                f"  Modified on: {modified_on_str}",
                "  Triggers:",
            ]
            for i, trigger in enumerate(rule.triggers):
                description = trigger.description or "(No description)"
                lines.append(f"    {i+1}. {description}")
            lines.append("  Conditions:")
            for i, condition in enumerate(rule.conditions):
                description = condition.description or "(No description)"
                lines.append(f"    {i+1}. {description}")
            lines.append("  Actions:")
            for i, action in enumerate(rule.actions):
                description = action.description or "(No description)"
                lines.append(f"    {i+1}. {description}")
            lines.append("```")
            content = "\n".join(lines)
            await self.reply(ctx, content)
        elif query:
            await self.reply(ctx, f"No rules matching `{query}`")
        else:
            await self.reply(ctx, f"No rules available")

    async def print_rule(
        self,
        ctx: GuildContext,
        query: str,
        path: Optional[JsonPath] = None,
    ):
        rules = await async_expand(self.store.query_rules(self.guild, query))
        if rules:
            # If multiple rules were found, just use the first.
            rule = rules[0]

            # Turn the rule into raw data.
            rule_data = to_data(rule)

            # Take a sub-section of the data, if necessary.
            output_data = rule_data
            if path:
                output_data = query_json_path(output_data, path)

            # Turn the data into a YAML string.
            output_yaml = yaml.safe_dump(output_data, sort_keys=False)

            # If the output can fit into a code block, just send a response. Otherwise,
            # stuff it into a file and send it as an attachment.
            content = f"```yaml\n{output_yaml}\n```"
            file_callback = lambda: ("", output_yaml, f"{rule.name}.yaml")
            return await send_message_or_file(
                ctx,
                content,
                file_callback=file_callback,
                allowed_mentions=AllowedMentions.none(),
            )

        else:
            await self.reply(ctx, f"No rule found matching `{query}`")

    async def add_rule(self, ctx: GuildContext, body: str):
        data = self._parse_body(body)
        rule = await self.store.add_rule(self.guild, data)
        await self.reply(ctx, f"Added automod rule `{rule.name}`")

    async def remove_rule(self, ctx: GuildContext, name: str):
        # Get the corresponding rule.
        rule = await self.store.require_rule(self.guild, name)
        # Then ask for confirmation to actually remove it.
        conf = await confirm_with_reaction(
            self.bot,
            ctx,
            f"Are you sure you want to remove automod rule `{rule.name}`?",
        )
        # If the answer was yes, attempt to remove the rule and send a response.
        if conf == ConfirmationResult.YES:
            removed_rule = await self.store.remove_rule(self.guild, rule.name)
            await self.reply(ctx, f"Removed automod rule `{removed_rule.name}`")
        # If the answer was no, send a response.
        elif conf == ConfirmationResult.NO:
            await self.reply(ctx, f"Did not remove automod rule `{rule.name}`")

    async def modify_rule(
        self,
        ctx: GuildContext,
        name: str,
        path: JsonPath,
        op: JsonPathOp,
        body: str,
    ):
        data = self._parse_body(body)
        rule = await self.store.modify_rule(self.guild, name, path, op, data)
        await self.reply(ctx, f"Modified automod rule `{rule.name}`")

    async def enable_rule(self, ctx: GuildContext, name: str):
        rule = await self.store.enable_rule(self.guild, name)
        await self.reply(ctx, f"Enabled automod rule `{rule.name}`")

    async def disable_rule(self, ctx: GuildContext, name: str):
        rule = await self.store.disable_rule(self.guild, name)
        await self.reply(ctx, f"Disabled automod rule `{rule.name}`")

    async def member_has_permission(self, member: Member) -> bool:
        permitted_roles = await self.store.get_permitted_roles(self.guild)
        if permitted_roles is None:
            return False
        has_permission = permitted_roles.member_has_some(member)
        return has_permission

    # @@ EVENT HANDLERS

    async def on_typing(
        self, channel: TextChannel | Thread, member: Member, when: datetime
    ):
        await self._do_event(
            events.MemberTyping(self.bot, self.log, channel, member, when)
        )

    async def on_message(self, message: TextMessage):
        await self._do_event(events.MessageSent(self.bot, self.log, message))

    async def on_message_delete(self, message: TextMessage):
        await self._do_event(events.MessageDeleted(self.bot, self.log, message))

    async def on_message_edit(self, before: TextMessage, after: TextMessage):
        await self._do_event(events.MessageEdited(self.bot, self.log, before, after))

    async def on_reaction_add(self, reaction: TextReaction, member: Member):
        await self._do_event(events.ReactionAdded(self.bot, self.log, reaction, member))

    async def on_reaction_remove(self, reaction: TextReaction, member: Member):
        await self._do_event(
            events.ReactionRemoved(self.bot, self.log, reaction, member)
        )

    async def on_channel_create(self, channel: TextChannel | Thread):
        await self._do_event(events.GuildChannelCreated(self.bot, self.log, channel))

    async def on_channel_delete(self, channel: TextChannel | Thread):
        await self._do_event(events.GuildChannelDeleted(self.bot, self.log, channel))

    async def on_channel_update(
        self, before: TextChannel | Thread, after: TextChannel | Thread
    ):
        await self._do_event(
            events.GuildChannelUpdated(self.bot, self.log, before, after)
        )

    async def on_thread_create(self, thread: Thread):
        await self._do_event(events.ThreadCreated(self.bot, self.log, thread))

    async def on_thread_join(self, thread: Thread):
        await self._do_event(events.ThreadJoined(self.bot, self.log, thread))

    async def on_thread_remove(self, thread: Thread):
        await self._do_event(events.ThreadRemoved(self.bot, self.log, thread))

    async def on_thread_delete(self, thread: Thread):
        await self._do_event(events.ThreadDeleted(self.bot, self.log, thread))

    async def on_thread_update(self, before: Thread, after: Thread):
        await self._do_event(events.ThreadUpdated(self.bot, self.log, before, after))

    async def on_thread_member_join(self, member: ThreadMember):
        await self._do_event(events.ThreadMemberJoined(self.bot, self.log, member))

    async def on_thread_member_leave(self, member: ThreadMember):
        await self._do_event(events.ThreadMemberLeft(self.bot, self.log, member))

    async def on_member_join(self, member: Member):
        await self._do_event(events.MemberJoined(self.bot, self.log, member))

    async def on_member_remove(self, member: Member):
        await self._do_event(events.MemberLeft(self.bot, self.log, member))

    async def on_member_update(self, before: Member, after: Member):
        await self._do_event(events.MemberUpdated(self.bot, self.log, before, after))

    async def on_user_update(self, before: User, after: User, member: Member):
        await self._do_event(
            events.UserUpdated(self.bot, self.log, before, after, member)
        )

    async def on_user_ban(self, user: User):
        await self._do_event(events.UserBanned(self.bot, self.log, user))

    async def on_user_unban(self, user: User):
        await self._do_event(events.UserUnbanned(self.bot, self.log, user))

    # @@ RAW EVENT HANDLERS

    async def on_raw_message_delete(self, payload: RawMessageDeleteEvent):
        await self._do_event(events.RawMessageDeleted(self.bot, self.log, payload))

    async def on_raw_message_edit(self, payload: RawMessageUpdateEvent):
        await self._do_event(events.RawMessageEdited(self.bot, self.log, payload))

    async def on_raw_reaction_add(self, payload: RawReactionActionEvent):
        await self._do_event(events.RawReactionAdded(self.bot, self.log, payload))

    async def on_raw_reaction_remove(self, payload: RawReactionActionEvent):
        await self._do_event(events.RawReactionRemoved(self.bot, self.log, payload))
