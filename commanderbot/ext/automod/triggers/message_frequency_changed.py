from dataclasses import dataclass
from datetime import timedelta
from typing import Any, Dict, Optional

from commanderbot.ext.automod import events
from commanderbot.ext.automod.automod_event import AutomodEvent
from commanderbot.ext.automod.bucket import BucketRef
from commanderbot.ext.automod.buckets.message_frequency import MessageFrequency
from commanderbot.ext.automod.trigger import Trigger, TriggerBase
from commanderbot.lib.utils import timedelta_from_field


@dataclass
class MessageFrequencyChanged(TriggerBase):
    """
    Fires when a message author is suspect of spamming.

    Attributes
    ----------
    bucket
        The bucket being used to track message frequency.
    message_threshold
        The minimum number of messages a user must send before being suspected of spam.
        Defaults to 3 messages.
    channel_threshold
        The minimum number of channels in which user must send messages before being
        suspected of spam. Defaults to 3 channels.
    timeframe
        How far back to consider a user's activity for spam. Defaults to 30 seconds.
    """

    event_types = (events.MessageFrequencyChanged,)

    bucket: BucketRef[MessageFrequency]
    message_threshold: int
    channel_threshold: int
    timeframe: timedelta

    # @overrides NodeBase
    @classmethod
    def build_complex_fields(cls, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        bucket = BucketRef.from_field(data, "bucket")
        timeframe = timedelta_from_field(data, "timeframe")
        return dict(
            bucket=bucket,
            timeframe=timeframe,
        )

    async def ignore(self, event: AutomodEvent) -> bool:
        # Ignore events without a message.
        message = event.message
        if not message:
            return True

        # Use the bucket to build a record out of our timeframe.
        bucket = await self.bucket.resolve(event)
        since = message.created_at - self.timeframe
        record = bucket.build_user_record_since(message.author, since)

        # Ignore if the record does not meet our thresholds.
        enough_messages = record.message_count >= self.message_threshold
        enough_channels = record.channel_count >= self.channel_threshold
        return enough_messages and enough_channels


def create_trigger(data: Any) -> Trigger:
    return MessageFrequencyChanged.from_data(data)
