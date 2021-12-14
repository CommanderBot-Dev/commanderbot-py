from dataclasses import dataclass
from datetime import timedelta
from typing import Any, Dict, Optional

from commanderbot.ext.automod.bucket import BucketRef
from commanderbot.ext.automod.buckets.message_frequency import (
    MessageFrequencyBucket,
    MessageFrequencyEvent,
)
from commanderbot.ext.automod.trigger import Trigger, TriggerBase
from commanderbot.lib.integer_range import IntegerRange
from commanderbot.lib.utils import timedelta_from_field


@dataclass
class MessageFrequencyTrigger(TriggerBase):
    """
    Fires when a message author is suspect of spamming.

    Attributes
    ----------
    bucket
        The bucket being used to track message frequency.
    timeframe
        How far back to consider a user's activity for spam.
    message_count
        The number of messages a user must send before being suspected of spam.
    channel_count
        The number of channels in which user must send messages before being suspected
        of spam.
    """

    event_types = (MessageFrequencyEvent,)

    bucket: BucketRef[MessageFrequencyBucket]
    timeframe: timedelta
    message_count: IntegerRange
    channel_count: IntegerRange

    # @overrides NodeBase
    @classmethod
    def build_complex_fields(cls, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        bucket = BucketRef.from_field(data, "bucket")
        timeframe = timedelta_from_field(data, "timeframe")
        message_count = IntegerRange.from_field(data, "message_count")
        channel_count = IntegerRange.from_field(data, "channel_count")
        return dict(
            bucket=bucket,
            timeframe=timeframe,
            message_count=message_count,
            channel_count=channel_count,
        )

    async def ignore(self, event: MessageFrequencyEvent) -> bool:
        # Ignore events dispatched by other buckets.
        bucket = event.bucket
        if bucket.name != self.bucket.name:
            return True

        # Use the bucket to build a record out of our timeframe.
        message = event.message
        since = message.created_at - self.timeframe
        record = bucket.build_user_record_since(message.author, since)

        # Ignore if the record does not meet our thresholds.
        record_messages = record.messages
        record_channels = record.channels
        enough_messages = self.message_count.includes(len(record_messages))
        enough_channels = self.channel_count.includes(len(record_channels))
        ignore = not (enough_messages and enough_channels)
        return ignore


def create_trigger(data: Any) -> Trigger:
    return MessageFrequencyTrigger.from_data(data)
