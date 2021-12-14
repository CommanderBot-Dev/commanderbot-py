from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Iterable, List, Optional, TypeAlias

from discord import Member, Message, TextChannel, Thread, User

from commanderbot.ext.automod.bucket import Bucket, BucketBase
from commanderbot.ext.automod.event import Event, EventBase
from commanderbot.ext.automod.event.event_base import EventBase
from commanderbot.lib import ChannelID, MessageID, TextMessage, ToData, UserID
from commanderbot.lib.utils import timedelta_from_field, utcnow_aware


@dataclass
class _MessageRecord:
    channel_id: ChannelID
    message_id: MessageID
    time: datetime


@dataclass
class _ChannelRecord:
    channel_id: ChannelID

    _messages: Dict[MessageID, _MessageRecord] = field(default_factory=lambda: {})

    @property
    def messages(self) -> List[_MessageRecord]:
        return list(self._messages.values())


@dataclass
class _UserTicket:
    _channels: Dict[ChannelID, _ChannelRecord] = field(default_factory=lambda: {})

    @property
    def channels(self) -> List[_ChannelRecord]:
        return list(self._channels.values())

    @property
    def messages(self) -> List[_MessageRecord]:
        messages = []
        for channel in self.channels:
            messages += channel.messages
        return messages

    def add_message_record(self, message_record: _MessageRecord):
        """Add a message record to this ticket."""
        channel_id = message_record.channel_id
        channel_record = self._channels.get(channel_id)
        if channel_record is None:
            channel_record = _ChannelRecord(channel_id=channel_id)
            self._channels[channel_id] = channel_record
        message_id = message_record.message_id
        channel_record._messages[message_id] = message_record

    def add_message(self, message: Message):
        """Add a message to this ticket."""
        message_time = message.edited_at or message.created_at
        message_record = _MessageRecord(
            channel_id=message.channel.id,
            message_id=message.id,
            time=message_time,
        )
        self.add_message_record(message_record)

    def add_from(self, other: _UserTicket, since: datetime):
        """Add the message records of another ticket to this ticket."""
        for message_record in other.messages:
            if message_record.time >= since:
                self.add_message_record(message_record)


_UserBuckets: TypeAlias = defaultdict[UserID, _UserTicket]
_IntervalBuckets: TypeAlias = defaultdict[datetime, _UserBuckets]


def _user_buckets_factory() -> _UserBuckets:
    return defaultdict(lambda: _UserTicket())


def _interval_buckets_factory() -> _IntervalBuckets:
    return defaultdict(_user_buckets_factory)


@dataclass
class _MessageFrequencyState:
    interval_buckets: _IntervalBuckets = field(
        default_factory=_interval_buckets_factory
    )


@dataclass
class MessageFrequencyEvent(EventBase):
    bucket: MessageFrequencyBucket

    _message: TextMessage

    @property
    def channel(self) -> TextChannel | Thread:
        return self._message.channel

    @property
    def message(self) -> TextMessage:
        return self._message

    @property
    def author(self) -> Member:
        return self._message.author

    @property
    def actor(self) -> Member:
        return self._message.author

    @property
    def member(self) -> Member:
        return self._message.author


@dataclass
class MessageFrequencyBucket(BucketBase):
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

    _state: _MessageFrequencyState = field(
        init=False,
        default_factory=lambda: _MessageFrequencyState(),
        metadata={ToData.Flags: [ToData.Flags.ExcludeFromData]},
    )

    # @overrides NodeBase
    @classmethod
    def build_complex_fields(cls, data: dict[str, Any]) -> Optional[dict[str, Any]]:
        bucket_lifetime = timedelta_from_field(data, "bucket_lifetime")
        bucket_interval = timedelta_from_field(data, "bucket_interval")
        return dict(
            bucket_lifetime=bucket_lifetime,
            bucket_interval=bucket_interval,
        )

    @property
    def bucket_lifetime_in_seconds(self) -> int:
        return int(self.bucket_lifetime.total_seconds())

    @property
    def bucket_interval_in_seconds(self) -> int:
        return int(self.bucket_interval.total_seconds())

    def _to_interval(self, dt: datetime) -> datetime:
        message_seconds = int(dt.timestamp())
        accuracy = self.bucket_interval_in_seconds
        interval_ts = (message_seconds // accuracy) * accuracy
        interval = datetime.fromtimestamp(interval_ts, tz=timezone.utc)
        return interval

    def get_user_buckets_since(
        self, since_interval: datetime
    ) -> Iterable[_UserBuckets]:
        # Iterate over each interval...
        for interval, user_buckets in self._state.interval_buckets.items():
            # If it's happened since, yield it.
            if interval >= since_interval:
                yield user_buckets

    def get_user_tickets_since(
        self, user: User | Member, since_interval: datetime
    ) -> Iterable[_UserTicket]:
        # Iterate over each interval bucket within the given timeframe...
        for user_buckets in self.get_user_buckets_since(since_interval):
            # If the user has a ticket in this bucket, yield it.
            if user_ticket := user_buckets.get(user.id):
                yield user_ticket

    def build_user_record_since(
        self, user: User | Member, since: datetime
    ) -> _UserTicket:
        since_interval = self._to_interval(since)
        record = _UserTicket()
        for ticket in self.get_user_tickets_since(user, since_interval):
            record.add_from(ticket, since)
        return record

    def clean_buckets(self):
        # Clean expired buckets to free memory.
        cutoff = utcnow_aware() - self.bucket_lifetime
        for interval in self._state.interval_buckets.copy():
            if interval < cutoff:
                del self._state.interval_buckets[interval]

    async def add(self, event: Event):
        # Short-circuit if the event does not contain a message.
        message = event.message
        if not message:
            return

        # Release old buckets to free memory.
        self.clean_buckets()

        # Calculate the interval based on the most recent message timestamp, and use it
        # to get/create the corresponding interval bucket.
        message_time = message.edited_at or message.created_at
        message_interval = self._to_interval(message_time)
        interval_bucket = self._state.interval_buckets[message_interval]

        # Within this interval, get/create and increment the user's ticket.
        author = message.author
        user_ticket = interval_bucket[author.id]
        user_ticket.add_message(message)

        # Dispatch an event.
        await event.state.dispatch_event(
            MessageFrequencyEvent(event.state, event.bot, event.log, self, message)
        )


def create_bucket(data: Any) -> Bucket:
    return MessageFrequencyBucket.from_data(data)
