from dataclasses import dataclass
from typing import Optional, Tuple, Type, TypeVar, cast

from discord import Member, TextChannel, Thread
from discord.abc import Messageable

from commanderbot.ext.automod.automod_action import (
    AutomodAction,
    AutomodActionBase,
    deserialize_actions,
)
from commanderbot.ext.automod.automod_condition import (
    AutomodCondition,
    deserialize_conditions,
)
from commanderbot.ext.automod.automod_event import AutomodEvent, AutomodEventBase
from commanderbot.lib import ChannelID, JsonObject, TextMessage

ST = TypeVar("ST")


@dataclass
class CheckingMessage(AutomodEventBase):
    _message: TextMessage

    @property
    def channel(self) -> TextChannel | Thread:
        return self._message.channel

    @property
    def message(self) -> TextMessage:
        return self._message

    @property
    def author(self) -> Member:
        return self._message.author  # type: ignore

    @property
    def actor(self) -> Member:
        return self._message.author  # type: ignore

    @property
    def member(self) -> Member:
        return self._message.author  # type: ignore


@dataclass
class CheckMessages(AutomodActionBase):
    """
    Check recent messages and apply actions to those that pass the conditions.

    Attributes
    ----------
    conditions
        The conditions to check messages against.
    actions
        The actions to apply to messages that pass the conditions.
    lookup_limit
        The number of messages to fetch and check. Defaults to 100.
    channel
        The channel to perform the search in. Defaults to the channel in context.
    """

    conditions: Tuple[AutomodCondition]
    actions: Tuple[AutomodAction]

    lookup_limit: Optional[int] = None

    channel: Optional[ChannelID] = None

    @classmethod
    def from_data(cls: Type[ST], data: JsonObject) -> ST:
        raw_conditions = data["conditions"]
        conditions = deserialize_conditions(raw_conditions)
        raw_actions = data["actions"]
        actions = deserialize_actions(raw_actions)
        return cls(
            description=data.get("description"),
            conditions=conditions,
            actions=actions,
            lookup_limit=data.get("lookup_limit"),
        )

    async def resolve_channel(self, event: AutomodEvent) -> Optional[Messageable]:
        if self.channel is not None:
            return event.bot.get_channel(self.channel)  # type: ignore
        return event.channel

    async def apply_message(self, dummy_event: CheckingMessage):
        for action in self.actions:
            await action.apply(dummy_event)

    async def check_message(self, dummy_event: CheckingMessage):
        for condition in self.conditions:
            if not await condition.check(dummy_event):
                return
        await self.apply_message(dummy_event)

    async def apply(self, event: AutomodEvent):
        if channel := await self.resolve_channel(event):
            async for message in channel.history(limit=self.lookup_limit or 100):
                message = cast(TextMessage, message)
                dummy_event = CheckingMessage(event.bot, event.log, message)
                await self.check_message(dummy_event)


def create_action(data: JsonObject) -> AutomodAction:
    return CheckMessages.from_data(data)
