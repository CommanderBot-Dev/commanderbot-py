import asyncio
import json
from dataclasses import dataclass
from datetime import datetime
from json.decoder import JSONDecodeError

import yaml
from yaml.error import YAMLError

from commanderbot_ext.ext.automod import events
from commanderbot_ext.ext.automod.automod_event import AutomodEventBase
from commanderbot_ext.ext.automod.automod_exception import AutomodException
from commanderbot_ext.ext.automod.automod_store import AutomodStore
from commanderbot_ext.lib import CogGuildState, TextMessage
from commanderbot_ext.lib.dialogs import ConfirmationResult, confirm_with_reaction
from commanderbot_ext.lib.types import GuildContext, JsonObject
from commanderbot_ext.lib.utils import async_expand


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

    def _parse_body(self, body: str) -> JsonObject:
        content = body.strip("\n").strip("`")
        kind, _, content = content.partition("\n")
        if kind == "json":
            try:
                data = json.loads(content)
            except JSONDecodeError as ex:
                raise AutomodException(str(ex)) from ex
        elif kind == "yaml":
            try:
                data = yaml.safe_load(content)
            except YAMLError as ex:
                raise AutomodException(str(ex)) from ex
        else:
            raise AutomodException("Missing code block declared as `json` or `yaml`")
        return data

    async def show_rules(self, ctx: GuildContext, query: str = ""):
        if query:
            rules = await async_expand(self.store.query_rules(self.guild, query))
        else:
            rules = await async_expand(self.store.all_rules(self.guild))
        count_rules = len(rules)
        if count_rules > 1:
            lines = ["```"]
            for rule in rules:
                line = f"[{rule.name}]"
                if rule.description:
                    line += f" {rule.description}"
                lines.append(line)
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
            name_line = f"[{rule.name}]"
            if rule.description:
                name_line += f" {rule.description}"
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
            serialized_rule = await self.store.serialize_rule(self.guild, rule.name)
            rule_yaml = yaml.safe_dump(serialized_rule, sort_keys=False)
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
        except AutomodException as ex:
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
        except AutomodException as ex:
            await ex.respond(ctx)

    async def modify_rule(self, ctx: GuildContext, name: str, body: str):
        try:
            data = self._parse_body(body)
            rule = await self.store.modify_rule(self.guild, name, data)
            await ctx.send(f"Modified automod rule `{rule.name}`")
        except AutomodException as ex:
            await ex.respond(ctx)

    async def do_event(self, event: AutomodEventBase):
        async for rule in self.store.rules_for_event(self.guild, event):
            if await rule.run(event):
                await self.store.increment_rule_hits(self.guild, rule.name)

    # @@ EVENT HANDLERS

    async def on_message(self, message: TextMessage):
        await self.do_event(events.MessageSent(bot=self.bot, _message=message))

    async def on_message_edit(self, before: TextMessage, after: TextMessage):
        await self.do_event(
            events.MessageEdited(bot=self.bot, _before=before, _after=after)
        )
