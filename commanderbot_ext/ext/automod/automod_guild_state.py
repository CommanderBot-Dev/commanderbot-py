import asyncio
import json
from dataclasses import dataclass
from datetime import datetime
from json.decoder import JSONDecodeError
from typing import Optional, cast

import yaml
from discord import (
    Color,
    Member,
    RawMessageDeleteEvent,
    RawMessageUpdateEvent,
    RawReactionActionEvent,
    TextChannel,
    User,
)
from yaml.error import YAMLError

from commanderbot_ext.ext.automod import events
from commanderbot_ext.ext.automod.automod_event import AutomodEventBase
from commanderbot_ext.ext.automod.automod_log_options import AutomodLogOptions
from commanderbot_ext.ext.automod.automod_rule import AutomodRule
from commanderbot_ext.ext.automod.automod_store import AutomodStore
from commanderbot_ext.lib import CogGuildState, TextMessage
from commanderbot_ext.lib.dialogs import ConfirmationResult, confirm_with_reaction
from commanderbot_ext.lib.json import to_data
from commanderbot_ext.lib.responsive_exception import ResponsiveException
from commanderbot_ext.lib.types import GuildContext, JsonObject, TextReaction
from commanderbot_ext.lib.utils import async_expand, sanitize_stacktrace


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
    ) -> Optional[AutomodLogOptions]:
        # First try to grab the rule's specific logging configuration, if any.
        if rule.log:
            return rule.log
        # If it doesn't have any, return the guild-wide logging configuration. This may
        # also not exist, hence why it's optional.
        return await self.store.get_default_log_options(self.guild)

    async def _maybe_log_rule_error_to_channel(
        self, rule: AutomodRule, error: Exception
    ):
        try:
            if log_options := await self._get_log_options_for_rule(rule):
                channel = cast(TextChannel, self.bot.get_channel(log_options.channel))
                lines = [f"Rule `{rule.name}` caused an error:", "```"]
                if log_options.stacktrace:
                    lines.append(sanitize_stacktrace(error))
                else:
                    lines.append(str(error))
                lines.append("```")
                content = "\n".join(lines)
                await channel.send(content)
        except:
            self.log.exception("Failed to log message to error channel:")

    async def _do_event_for_rule(self, event: AutomodEventBase, rule: AutomodRule):
        try:
            if await rule.run(event):
                await self.store.increment_rule_hits(self.guild, rule.name)
        except Exception as error:
            self.log.exception("Automod rule caused an error:")
            await self._maybe_log_rule_error_to_channel(rule, error)

    async def _do_event(self, event: AutomodEventBase):
        # Run rules in parallel so that they don't need to wait for one another.
        rules = await async_expand(self.store.rules_for_event(self.guild, event))
        tasks = [self._do_event_for_rule(event, rule) for rule in rules]
        await asyncio.gather(*tasks)

    def _parse_body(self, body: str) -> JsonObject:
        content = body.strip("\n").strip("`")
        kind, _, content = content.partition("\n")
        if kind == "json":
            try:
                data = json.loads(content)
            except JSONDecodeError as ex:
                raise ResponsiveException(str(ex)) from ex
        elif kind == "yaml":
            try:
                data = yaml.safe_load(content)
            except YAMLError as ex:
                raise ResponsiveException(str(ex)) from ex
        else:
            raise ResponsiveException("Missing code block declared as `json` or `yaml`")
        return data

    async def show_default_log_options(self, ctx: GuildContext):
        try:
            if log_options := await self.store.get_default_log_options(self.guild):
                channel = cast(TextChannel, self.bot.get_channel(log_options.channel))
                await ctx.send(f"Default logging is configured for {channel.mention}")
            else:
                await ctx.send(f"No default logging configured")
        except ResponsiveException as ex:
            await ex.respond(ctx)

    async def set_default_log_options(
        self,
        ctx: GuildContext,
        channel: TextChannel,
        stacktrace: Optional[bool],
        emoji: Optional[str],
        color: Optional[Color],
    ):
        try:
            new_log_options = AutomodLogOptions(
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
                await ctx.send(
                    f"Moved default logging from {old_log_channel.mention}"
                    + f" to {channel.mention}"
                )
            else:
                await ctx.send(f"Configured default logging for {channel.mention}")
        except ResponsiveException as ex:
            await ex.respond(ctx)

    async def remove_default_log_options(self, ctx: GuildContext):
        try:
            old_log_options = await self.store.set_default_log_options(self.guild, None)
            if old_log_options:
                channel = cast(
                    TextChannel, self.bot.get_channel(old_log_options.channel)
                )
                await ctx.send(f"Removed default logging from {channel.mention}")
            else:
                await ctx.send(f"No default logging configured")
        except ResponsiveException as ex:
            await ex.respond(ctx)

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
            await ctx.send(content)
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
            await ctx.send(content)
        elif query:
            await ctx.send(f"No rules matching `{query}`")
        else:
            await ctx.send(f"No rules available")

    async def print_rule(self, ctx: GuildContext, query: str):
        rules = await async_expand(self.store.query_rules(self.guild, query))
        if rules:
            rule = rules[0]
            rule_data = to_data(rule)
            rule_yaml = yaml.safe_dump(rule_data, sort_keys=False)
            lines = [
                f"`{rule.name}`",
                "```yaml",
                rule_yaml,
                "```",
            ]
            content = "\n".join(lines)
            await ctx.send(content)
        else:
            await ctx.send(f"No rule found matching `{query}`")

    async def add_rule(self, ctx: GuildContext, body: str):
        try:
            data = self._parse_body(body)
            rule = await self.store.add_rule(self.guild, data)
            await ctx.send(f"Added automod rule `{rule.name}`")
        except ResponsiveException as ex:
            await ex.respond(ctx)

    async def remove_rule(self, ctx: GuildContext, name: str):
        # Wrap this in case of multiple confirmations.
        try:
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
                await ctx.send(f"Removed automod rule `{removed_rule.name}`")
            # If the answer was no, send a response.
            elif conf == ConfirmationResult.NO:
                await ctx.send(f"Did not remove automod rule `{rule.name}`")
        # If a known error occurred, send a response.
        except ResponsiveException as ex:
            await ex.respond(ctx)

    async def modify_rule(self, ctx: GuildContext, name: str, body: str):
        try:
            data = self._parse_body(body)
            rule = await self.store.modify_rule(self.guild, name, data)
            await ctx.send(f"Modified automod rule `{rule.name}`")
        except ResponsiveException as ex:
            await ex.respond(ctx)

    async def enable_rule(self, ctx: GuildContext, name: str):
        try:
            rule = await self.store.enable_rule(self.guild, name)
            await ctx.send(f"Enabled automod rule `{rule.name}`")
        except ResponsiveException as ex:
            await ex.respond(ctx)

    async def disable_rule(self, ctx: GuildContext, name: str):
        try:
            rule = await self.store.disable_rule(self.guild, name)
            await ctx.send(f"Disabled automod rule `{rule.name}`")
        except ResponsiveException as ex:
            await ex.respond(ctx)

    # @@ EVENT HANDLERS

    async def on_typing(self, channel: TextChannel, member: Member, when: datetime):
        await self._do_event(events.MemberTyping(self.bot, channel, member, when))

    async def on_message(self, message: TextMessage):
        await self._do_event(events.MessageSent(self.bot, message))

    async def on_message_delete(self, message: TextMessage):
        await self._do_event(events.MessageDeleted(self.bot, message))

    async def on_message_edit(self, before: TextMessage, after: TextMessage):
        await self._do_event(events.MessageEdited(self.bot, before, after))

    async def on_reaction_add(self, reaction: TextReaction, member: Member):
        await self._do_event(events.ReactionAdded(self.bot, reaction, member))

    async def on_reaction_remove(self, reaction: TextReaction, member: Member):
        await self._do_event(events.ReactionRemoved(self.bot, reaction, member))

    async def on_member_join(self, member: Member):
        await self._do_event(events.MemberJoined(self.bot, member))

    async def on_member_remove(self, member: Member):
        await self._do_event(events.MemberLeft(self.bot, member))

    async def on_member_update(self, before: Member, after: Member):
        await self._do_event(events.MemberUpdated(self.bot, before, after))

    async def on_user_update(self, before: User, after: User, member: Member):
        await self._do_event(events.UserUpdated(self.bot, before, after, member))

    async def on_user_ban(self, user: User):
        await self._do_event(events.UserBanned(self.bot, user))

    async def on_user_unban(self, user: User):
        await self._do_event(events.UserUnbanned(self.bot, user))

    # @@ RAW EVENT HANDLERS

    async def on_raw_message_delete(self, payload: RawMessageDeleteEvent):
        await self._do_event(events.RawMessageDeleted(self.bot, payload))

    async def on_raw_message_edit(self, payload: RawMessageUpdateEvent):
        await self._do_event(events.RawMessageEdited(self.bot, payload))

    async def on_raw_reaction_add(self, payload: RawReactionActionEvent):
        await self._do_event(events.RawReactionAdded(self.bot, payload))

    async def on_raw_reaction_remove(self, payload: RawReactionActionEvent):
        await self._do_event(events.RawReactionRemoved(self.bot, payload))
