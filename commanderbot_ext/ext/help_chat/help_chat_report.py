import asyncio
import io
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import DefaultDict, Dict, Iterable, List, Optional, Tuple, cast

from discord import AllowedMentions, Embed, File, Message, TextChannel, User
from discord.ext.commands import Context

from commanderbot_ext.ext.help_chat import constants
from commanderbot_ext.ext.help_chat.help_chat_store import HelpChannel
from commanderbot_ext.lib import IDType


class ChannelStatus(Enum):
    INCOMPLETE = 0
    IN_PROGRESS = 1
    COMPLETE = 2


STATUS_EMOJI = {
    ChannelStatus.INCOMPLETE: "⬜",
    ChannelStatus.IN_PROGRESS: "🔄",
    ChannelStatus.COMPLETE: "✅",
}


@dataclass
class UserRecord:
    user_id: IDType
    username: str

    # map YYYY-MM-DD to score (initialized at 0)
    score_by_day: DefaultDict[Tuple[int, int, int], int] = field(
        default_factory=lambda: defaultdict(lambda: 0)
    )

    @property
    def total_score(self) -> int:
        return sum(self.score_by_day.values())

    @property
    def days_active(self) -> int:
        return len(self.score_by_day)


UserTable = Dict[IDType, UserRecord]


@dataclass
class ChannelState:
    help_channel: HelpChannel
    channel: TextChannel
    status: ChannelStatus = ChannelStatus.INCOMPLETE
    total_messages: int = 0
    total_message_length: int = 0

    @property
    def status_text(self) -> str:
        if self.total_messages > 0:
            return f"{self.channel.mention} ({self.total_messages:,} messages)"
        return self.channel.mention


@dataclass
class HelpChatSummaryOptions:
    split_length: int
    max_rows: int
    min_score: int


@dataclass
class HelpChatReport:
    after: datetime
    before: datetime
    label: str
    built_at: datetime
    channel_states: List[ChannelState]
    user_table: UserTable

    @property
    def title(self) -> str:
        return f"Help-chat Report: {self.label}"

    def make_summary_batch_embed(
        self, batch_no: int, count_batches: int, text: str
    ) -> Embed:
        # Create the base embed.
        embed = Embed(
            type="rich",
            title=self.title,
            description=text,
            colour=0x77B255,
        )
        # If we've got more than a single batch, include the batch number in the footer.
        if count_batches > 1:
            embed.set_footer(text=f"{batch_no} of {count_batches}")
        # Return the final embed.
        return embed

    def get_user_records(self) -> List[UserRecord]:
        # Get user results, in arbitrary order.
        return list(self.user_table.values())

    def get_sorted_user_records(self) -> List[UserRecord]:
        # Get user results, sorted by score in descending order.
        return sorted(
            self.get_user_records(), key=lambda user_record: -user_record.total_score
        )

    def build_results_file_line(self, user_record: UserRecord) -> str:
        return ",".join(
            str(elem)
            for elem in (
                user_record.user_id,
                user_record.username,
                user_record.total_score,
                user_record.days_active,
            )
        )

    def build_results_file(self) -> File:
        sorted_user_records = self.get_sorted_user_records()
        lines = [
            "User ID,Username,Score,Days Active",
            *(
                self.build_results_file_line(user_record)
                for user_record in sorted_user_records
            ),
        ]
        file_contents = "\n".join(lines)
        filename = f"{self.title}.csv"
        return File(fp=io.StringIO(file_contents), filename=filename)

    def build_summary_lines(self, options: HelpChatSummaryOptions) -> Iterable[str]:
        sorted_user_records = self.get_sorted_user_records()
        # Print some initial information about the report.
        count_results = len(sorted_user_records)
        after_str = self.after.strftime(constants.DATE_FMT_YYYY_MM_DD)
        before_str = self.before.strftime(constants.DATE_FMT_YYYY_MM_DD)
        max_results = min(options.max_rows, count_results)
        yield (
            f"Showing the top {max_results:,} of {count_results:,} results"
            + f" with a score of at least {options.min_score:,}."
            + " A user's score is determined by summing the length of all their messages"
            + f" in help channels from {after_str} up to {before_str}."
            + "\n"
        )
        # Print a line for each user.
        for i, user_record in enumerate(sorted_user_records):
            if (i >= options.max_rows) or (user_record.total_score < options.min_score):
                break
            yield (
                f"<@{user_record.user_id}>: **{user_record.total_score:,}**"
                + f" ({user_record.days_active:,} days active)"
            )

    def batch_summary_text(self, options: HelpChatSummaryOptions) -> Iterable[str]:
        batch = ""
        for line in self.build_summary_lines(options):
            would_be_text = batch + "\n" + line
            if len(would_be_text) <= options.split_length:
                batch = would_be_text
            else:
                yield batch
                batch = line
        if batch:
            yield batch

    async def summarize(self, ctx: Context, **kwargs):
        options = HelpChatSummaryOptions(**kwargs)
        # Create a simple CSV file with the full results.
        results_file = self.build_results_file()
        # Split the response into individual batches, to avoid hitting the message cap.
        batches = list(self.batch_summary_text(options))
        # Count the number of batches so we can include this information in the response.
        count_batches = len(batches)
        # Send the first (and possibly only) batch as an embed with some initial response text,
        # with the results file attached.
        first_batch = batches[0]
        await ctx.reply(
            embed=self.make_summary_batch_embed(1, count_batches, first_batch),
            file=results_file,
        )
        # Send an additional embed for each remaining batch (if any).
        for i, batch in enumerate(batches[1:]):
            # Wait a few seconds before posting each additional embed, just in case.
            await asyncio.sleep(5)
            await ctx.send(
                content=None,
                embed=self.make_summary_batch_embed(i + 2, count_batches, batch),
            )


class HelpChatReportBuildContext:
    def __init__(
        self,
        ctx: Context,
        help_channels: List[HelpChannel],
        after: datetime,
        before: datetime,
        label: str,
    ):
        self.ctx: Context = ctx
        self.help_channels: List[HelpChannel] = help_channels
        self.after: datetime = after
        self.before: datetime = before
        self.label: str = label

        self._progress_message: Optional[Message] = None
        self._built_at: Optional[datetime] = None
        self._channel_states: Optional[List[ChannelState]] = None
        self._user_table: Optional[UserTable] = None

    @property
    def channel(self) -> TextChannel:
        return cast(TextChannel, self.ctx.channel)

    def reset(self):
        self._built_at = datetime.utcnow()
        self._progress_message = None
        self._channel_states = [
            ChannelState(help_channel, help_channel.channel(self.ctx))
            for help_channel in self.help_channels
        ]
        self._user_table = {}

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
        after_str = self.after.strftime(constants.DATE_FMT_YYYY_MM_DD)
        before_str = self.before.strftime(constants.DATE_FMT_YYYY_MM_DD)

        progress_emoji = " ".join(
            STATUS_EMOJI[state.status] for state in self._channel_states
        )

        status_text = ""
        if states_in_progress := self.get_states_in_progress():
            status_text = "Scanning: " + " ".join(
                state.status_text for state in states_in_progress
            )
        elif self.is_finished():
            status_text = "Done!"

        text = (
            f"\nScanning message history from {after_str} up to {before_str}, across"
            + f" {len(self.help_channels)} help channels..."
            + f"\n> {progress_emoji}"
            + f"\n{status_text}"
        )

        return text

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

    async def build(self) -> HelpChatReport:
        # Reset temporary state variables.
        self.reset()
        # Invoke an update, which will send the initial progress message.
        await self.update()
        # Since scanning message history is a long/expensive operation, we'll make it look like
        # we're typing until we're finished.
        async with self.channel.typing():
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
                    author: User = cast(User, message.author)
                    user_record = self._user_table.get(author.id)
                    if user_record is None:
                        # Create a new record for this user, if one does not already exist.
                        user_record = UserRecord(
                            user_id=author.id, username=str(author)
                        )
                        self._user_table[author.id] = user_record
                    # Build the daily record key from YYYY-MM-DD.
                    daily_key = (
                        message.created_at.year,
                        message.created_at.month,
                        message.created_at.day,
                    )
                    # Increment the user's daily score by message count.
                    user_record.score_by_day[daily_key] += message_length
                    # Update progress every X messages.
                    if channel_state.total_messages % 1000 == 0:
                        await self.update()
                # Mark the channel as complete. Don't bother updating here, because we're going to
                # update anyway as soon as we either (1) finish and run off the end of the loop or
                # (2) enter the next iteration of the loop and mark the next channel to in-progress.
                channel_state.status = ChannelStatus.COMPLETE
        # Invoking one final update, which will make the final edit to the progress message.
        await self.update()
        # Return the final result, encapsulated in an object.
        assert self._built_at is not None
        assert self._channel_states is not None
        assert self._user_table is not None
        return HelpChatReport(
            after=self.after,
            before=self.before,
            label=self.label,
            built_at=self._built_at,
            channel_states=self._channel_states,
            user_table=self._user_table,
        )
