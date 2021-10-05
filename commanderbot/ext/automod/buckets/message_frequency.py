from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Iterable, Optional, Type, TypeAlias, TypeVar

from discord import Member, Message, User

from commanderbot.ext.automod import events
from commanderbot.ext.automod.automod_event import AutomodEvent
from commanderbot.ext.automod.bucket import Bucket, BucketBase
from commanderbot.lib import ChannelID, UserID
from commanderbot.lib.utils import timedelta_from_field_optional

ST = TypeVar("ST")


class UserTicket:
    def __init__(self):
        self.message_count: int = 0
        self.unique_channels: set[ChannelID] = set()

    @property
    def channel_count(self) -> int:
        return len(self.unique_channels)

    def increment(self, message: Message):
        """Increment this ticket with the given message."""
        self.message_count += 1
        self.unique_channels.add(message.channel.id)

    def add(self, other: UserTicket):
        """Add another ticket to this one."""
        self.message_count += other.message_count
        self.unique_channels.update(other.unique_channels)


UserBuckets: TypeAlias = defaultdict[UserID, UserTicket]
IntervalBuckets: TypeAlias = defaultdict[int, UserBuckets]


def user_buckets_factory() -> UserBuckets:
    return defaultdict(default_factory=lambda: UserTicket())


def interval_buckets_factory() -> IntervalBuckets:
    return defaultdict(default_factory=user_buckets_factory)


@dataclass
class MessageFrequencyState:
    interval_buckets: IntervalBuckets = field(
        init=False, default_factory=interval_buckets_factory
    )


@dataclass
class MessageFrequency(BucketBase):
    """
    Track user activity across channels for potential spam.

    Attributes
    ----------
    bucket_lifetime
        For how long to record history. Longer durations are able to record more
        history for potential queries, but take more memory on average.
    bucket_interval
        The interval by which to partition buckets. This is used to decide when to
        release old, unused buckets and free memory. For example: a value of 3600 will
        partition buckets by the hour, and 60 will partition by the minute.
    """

    bucket_lifetime: timedelta
    bucket_interval: timedelta

    _state: MessageFrequencyState

    @classmethod
    def try_from_data(cls: Type[ST], data: Any) -> Optional[ST]:
        if isinstance(data, dict):
            bucket_interval = timedelta_from_field_optional(data, "bucket_interval")
            return cls(bucket_interval=bucket_interval)

    @property
    def bucket_lifetime_in_seconds(self) -> int:
        return int(self.bucket_lifetime.total_seconds())

    @property
    def bucket_interval_in_seconds(self) -> int:
        return int(self.bucket_interval.total_seconds())

    def _message_to_interval(self, message: Message) -> int:
        message_seconds = int(message.created_at.timestamp())
        interval = message_seconds // self.bucket_interval_in_seconds
        return interval

    def get_user_buckets_since(self, since: datetime) -> Iterable[UserBuckets]:
        # Calculate the interval in which the since-time lies.
        since_interval = int(since.timestamp())
        # Iterate over each interval...
        for interval, user_buckets in self._state.interval_buckets.items():
            # If it's happened since, yield it.
            if interval >= since_interval:
                yield user_buckets

    def get_user_tickets_since(
        self, user: User | Member, since: datetime
    ) -> Iterable[UserTicket]:
        # Iterate over each interval bucket within the given timeframe...
        for user_buckets in self.get_user_buckets_since(since):
            # If the user has a ticket in this bucket, yield it.
            if user_ticket := user_buckets.get(user.id):
                yield user_ticket

    def build_user_record_since(
        self, user: User | Member, since: datetime
    ) -> UserTicket:
        record = UserTicket()
        for ticket in self.get_user_tickets_since(user, since):
            record.add(ticket)
        return record

    def clean_buckets(self):
        # IMPL clean buckets to free memory
        ...

    async def add(self, event: AutomodEvent):
        # Short-circuit if the event does not contain a message.
        message = event.message
        if not message:
            return

        # Release old buckets to free memory.
        self.clean_buckets()

        # Calculate the interval based on the most recent message timestamp, and use it
        # to get/create the corresponding interval bucket.
        interval = self._message_to_interval(message)
        interval_bucket = self._state.interval_buckets[interval]

        # Within this interval, get/create and increment the user's ticket.
        author = message.author
        user_ticket = interval_bucket[author.id]
        user_ticket.increment(message)

        # Dispatch an event.
        await event.state.dispatch_event(
            events.MessageFrequencyChanged(event.state, event.bot, event.log, message)
        )


def create_bucket(data: Any) -> Bucket:
    return MessageFrequency.from_data(data)
