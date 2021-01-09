from collections import defaultdict
from datetime import datetime
from enum import Enum
from typing import AsyncIterable, DefaultDict, Iterable, List, Optional, Tuple

from commanderbot_ext.help_chat.help_chat_cache import HelpChannel
from commanderbot_ext.help_chat.help_chat_options import HelpChatOptions
from commanderbot_ext.help_chat.utils import DATE_FMT_YYYY_MM_DD, DATE_FMT_YYYY_MM_DD_HH_MM_SS
from commanderbot_lib.types import IDType
from discord import AllowedMentions, Embed, Message, TextChannel, User
from discord.ext.commands import Context

UserTable = DefaultDict[IDType, DefaultDict[Tuple[int, int, int], int]]


class ChannelStatus(Enum):
    INCOMPLETE = 0
    IN_PROGRESS = 1
    COMPLETE = 2


STATUS_EMOJI = {
    ChannelStatus.INCOMPLETE: "⬜",
    ChannelStatus.IN_PROGRESS: "🔄",
    ChannelStatus.COMPLETE: "✅",
}


class ChannelState:
    def __init__(
        self,
        help_channel: HelpChannel,
        channel: TextChannel,
        status: ChannelStatus = ChannelStatus.INCOMPLETE,
        total_messages: Optional[int] = None,
        total_message_length: Optional[int] = None,
    ):
        self.help_channel: HelpChannel = help_channel
        self.channel: TextChannel = channel
        self.status: ChannelStatus = status
        self.total_messages: Optional[int] = total_messages
        self.total_message_length: Optional[int] = total_message_length


class HelpChatNomContext:
    def __init__(
        self,
        ctx: Context,
        options: HelpChatOptions,
        help_channels: List[HelpChannel],
        after: datetime,
        before: datetime,
    ):
        self.ctx: Context = ctx
        self.options: HelpChatOptions = options
        self.help_channels: List[HelpChannel] = help_channels
        self.after: datetime = after
        self.before: datetime = before
        # TODO Use discord-flags library to make these configurable. #enhance
        self.report_split_length = 1000
        self.report_min_score = 100
        self.report_max_rows = 5

        self._timestamp: Optional[datetime] = None
        self._progress_message: Optional[Message] = None
        self._summary_messages: Optional[List[Message]] = []
        self._channel_states: Optional[List[ChannelState]] = None
        self._user_table: Optional[UserTable] = None

    def reset(self):
        self._timestamp = datetime.utcnow()
        self._progress_message = None
        self._summary_messages = None
        self._channel_states = [
            ChannelState(help_channel, help_channel.channel(self.ctx))
            for help_channel in self.help_channels
        ]
        self._user_table = defaultdict(lambda: defaultdict(int))

    def get_states_with_status(self, status: ChannelStatus) -> List[ChannelState]:
        return [state for state in self._channel_states if state.status == status]

    def get_states_incomplete(self) -> List[ChannelState]:
        return self.get_states_with_status(ChannelStatus.INCOMPLETE)

    def get_states_in_progress(self) -> List[ChannelState]:
        return self.get_states_with_status(ChannelStatus.IN_PROGRESS)

    def get_states_complete(self) -> List[ChannelState]:
        return self.get_states_with_status(ChannelStatus.COMPLETE)

    def is_finished(self) -> bool:
        for state in self._channel_states:
            if state.status != ChannelStatus.COMPLETE:
                return False
        return True

    def build_progress_text(self) -> str:
        after_str = self.after.strftime(DATE_FMT_YYYY_MM_DD)
        before_str = self.before.strftime(DATE_FMT_YYYY_MM_DD)

        progress_emoji = " ".join(STATUS_EMOJI[state.status] for state in self._channel_states)

        status_text = ""
        if (states_in_progress := self.get_states_in_progress()) :
            status_text = "Scanning: " + " ".join(
                state.channel.mention for state in states_in_progress
            )
        elif self.is_finished():
            status_text = "Done!"

        text = (
            f"\nScanning message history from {after_str} to {before_str}, across"
            + f" {len(self.help_channels)} help channels..."
            + f"\n> {progress_emoji}"
            + f"\n{status_text}"
        )

        return text

    def get_user_results(self) -> Iterable[Tuple[IDType, int, int]]:
        for user_id, user_record in self._user_table.items():
            score = sum(user_record.values())
            days_active = len(user_record)
            yield user_id, score, days_active

    def build_summary_lines(self) -> Iterable[str]:
        # Sort the user results, descending by score.
        sorted_user_results = sorted(self.get_user_results(), key=lambda row: -row[1])
        # Print some initial information about the report.
        count_results = len(sorted_user_results)
        yield (
            f"Showing the top {self.report_max_rows} results (of {count_results})"
            + f" with a minimum score of {self.report_min_score}."
            + "\n"
        )
        # Print a line for each user.
        for i, (user_id, score, days_active) in enumerate(sorted_user_results):
            if (i >= self.report_max_rows) or (score < self.report_min_score):
                break
            yield (f"<@{user_id}>: **{score}**" + f" ({days_active} days active)")

    def batch_summary_text(self) -> Iterable[str]:
        batch = ""
        for line in self.build_summary_lines():
            would_be_text = batch + "\n" + line
            if len(would_be_text) <= self.report_split_length:
                batch = would_be_text
            else:
                yield batch
                batch = line
        if batch:
            yield batch

    def make_summary_batch_embed(self, batch_no: int, count_batches: int, text: str) -> Embed:
        # Create the base embed.
        timestamp_str = self._timestamp.strftime(DATE_FMT_YYYY_MM_DD_HH_MM_SS)
        embed = Embed(
            type="rich",
            title=f"Help-chat Summary {timestamp_str}",
            description=text,
        )
        # If we've got more than a single batch, include the batch number in the footer.
        if count_batches > 1:
            embed.set_footer(text=f"{batch_no} of {count_batches}")
        # Return the final embed.
        return embed

    async def send_summary_messages(self) -> AsyncIterable[Message]:
        # NOTE We yield each `Message` sent here so that the caller can capture them.
        # Split the response into individual batches, to avoid hitting the message cap.
        batches = list(self.batch_summary_text())
        # Count the number of batches so we can include this information in the response.
        count_batches = len(batches)
        # Send the first (and possibly only) batch as an embed with some initial response text.
        first_batch = batches[0]
        yield await self.ctx.reply(
            content="The results are in:",
            embed=self.make_summary_batch_embed(1, count_batches, first_batch),
        )
        # Send an additional embed for each remaining batch (if any).
        for i, batch in enumerate(batches[1:]):
            yield await self.ctx.send(
                content=None,
                embed=self.make_summary_batch_embed(i + 2, count_batches, batch),
            )

    async def update(self):
        # Update the progress message, or send a new one if it doesn't already exist.
        progress_text = self.build_progress_text()
        if self._progress_message is not None:
            await self._progress_message.edit(
                content=progress_text,
                allowed_mentions=AllowedMentions(replied_user=False),
            )
        else:
            self._progress_message = await self.ctx.reply(
                content=progress_text,
                mention_author=False,
            )
        # Send the summary messages if we're done and they don't already exist.
        if self.is_finished() and self._summary_messages is None:
            self._summary_messages = []
            async for message in self.send_summary_messages():
                self._summary_messages.append(message)

    async def run(self):
        # Reset temporary state variables.
        self.reset()
        # Invoke an update, which will send the initial progress message.
        await self.update()
        # Since scanning message history is a long/expensive operation, we'll make it look like
        # we're typing until we're finished.
        async with self.ctx.channel.typing():
            # Iterate over one channel at a time, which will help us convey progress.
            for channel_state in self._channel_states:
                # Immediately mark the channel as in-progress and send an update, which will make an
                # edit to the progress message.
                channel_state.status = ChannelStatus.IN_PROGRESS
                await self.update()
                # Iterate over the history of the channel within the given timeframe.
                history = channel_state.channel.history(
                    after=self.after, before=self.before, limit=None
                )
                channel_state.total_messages = 0
                channel_state.total_message_length = 0
                async for message in history:
                    message: Message
                    content = message.content
                    # Skip messages that don't have any content.
                    if not isinstance(content, str):
                        continue
                    # Update the channel state.
                    message_length = len(content)
                    channel_state.total_messages += 1
                    channel_state.total_message_length += message_length
                    # Update the author's record.
                    author: User = message.author
                    user_record = self._user_table[author.id]
                    # Build the daily record key from YYYY-MM-DD.
                    daily_key = (
                        message.created_at.year,
                        message.created_at.month,
                        message.created_at.day,
                    )
                    # Increment the user's daily record by message count.
                    user_record[daily_key] += message_length
                # Mark the channel as complete. Don't bother updating here, because we're going to
                # update anyway as soon as we either (1) finish and run off the end of the loop or
                # (2) enter the next iteration of the loop and mark the next channel to in-progress.
                channel_state.status = ChannelStatus.COMPLETE
        # Invoking one final update, which will make the final edit to the progress message and send
        # one or more summary messages.
        await self.update()
