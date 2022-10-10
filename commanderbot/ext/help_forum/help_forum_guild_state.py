from dataclasses import dataclass
from enum import Enum
from typing import List, cast

from discord import (
    AllowedMentions,
    Embed,
    ForumChannel,
    ForumTag,
    HTTPException,
    Interaction,
    Message,
    Object,
    PartialEmoji,
    RawReactionActionEvent,
    RawThreadUpdateEvent,
    Thread,
)

from commanderbot.ext.help_forum.help_forum_store import HelpForum, HelpForumStore
from commanderbot.lib import CogGuildState
from commanderbot.lib.dialogs import ConfirmationResult, confirm_with_buttons
from commanderbot.lib.forums import format_tag, has_tag, tag_from_id
from commanderbot.lib.types import ForumTagID


class ThreadState(Enum):
    UNRESOLVED = "Unresolved"
    RESOLVED = "Resolved"


@dataclass
class HelpForumGuildState(CogGuildState):
    """
    Encapsulates the state and logic of the help forum cog, at the guild level.

    Attributes
    -----------
    store
        The store used to interface with persistent data in a database-agnostic way.
    """

    store: HelpForumStore

    async def _change_thread_state(
        self,
        channel: ForumChannel,
        thread: Thread,
        forum: HelpForum,
        state: ThreadState,
    ):
        # Get the state tag to apply
        new_state_tag: ForumTagID = -1
        match state:
            case ThreadState.UNRESOLVED:
                new_state_tag = forum.unresolved_tag_id
            case ThreadState.RESOLVED:
                new_state_tag = forum.resolved_tag_id

        # Check if the forum channel has the requested state tag
        thread_has_tag: bool = has_tag(channel, new_state_tag)

        # Create a new tag list by first removing the current state tags, then
        # prepend the new state tag if it exists
        tags = [
            Object(id=i.id) for i in thread.applied_tags if i.id not in forum.tag_ids
        ]
        if thread_has_tag:
            tags.insert(0, Object(id=new_state_tag))
        del tags[5:]

        # Create edit reason
        reason: str = ""
        if thread_has_tag:
            reason = f"Added the '{state.value}' tag"
        else:
            reason = f"Tried to add the '{state.value}' tag, but it doesn't exist (ID={new_state_tag})"

        # Edit the thread. The cast is needed because `applied_tags` in
        # `Thread.edit()` doesn't take snowflakes unlike `Thread.add_tags()`.
        # Resolving will archive the thread too.
        await thread.edit(
            applied_tags=cast(List[ForumTag], tags),
            archived=(state == ThreadState.RESOLVED),
            reason=reason,
        )

    async def on_thread_create(self, thread: Thread):
        """
        Called whenever a thread is created.

        This event pins the first message and sets the thread state to 'Unresolved'.
        """

        # Ignore updates to threads outside of forum channels
        channel = thread.parent
        if not isinstance(channel, ForumChannel):
            return

        # Check if the forum channel was registered as a help forum
        if forum := await self.store.get_help_forum(self.guild, channel):
            # Pin first message
            try:
                await thread.get_partial_message(thread.id).pin()
            except HTTPException:
                pass

            # Change the thread state to 'Unresolved'
            await self._change_thread_state(
                channel, thread, forum, ThreadState.UNRESOLVED
            )

            # Increment total threads
            await self.store.increment_total_threads(forum)

    async def on_thread_update(self, before: Thread, after: Thread):
        """
        Called whenever a thread in the cache is updated. This will not trigger for
        unarchived threads.

        This event enforces the channel's archive duration. It will also ignore
        threads being archived.
        """

        # Ignore updates to threads outside of forum channels
        channel = before.parent
        if not isinstance(channel, ForumChannel):
            return

        # Ignore updates to threads that are being archived or unarchived
        if before.archived or after.archived:
            return

        # Check if the forum channel was registered as a help forum
        if _ := await self.store.get_help_forum(self.guild, channel):
            # If it was, enforce the default archive duration if needed
            default_archive_duration = channel.default_auto_archive_duration
            if after.auto_archive_duration > default_archive_duration:
                await after.edit(auto_archive_duration=default_archive_duration)

    async def on_raw_thread_update(self, payload: RawThreadUpdateEvent):
        """
        Called whenever a thread is updated reguardless of if they're in the cache or not.

        This event sets the thread state to 'Unresolved' if the thread is coming back
        into the cache. This seems to happen when a thread is unarchived.
        """

        # Ignore updates to threads that are in the cache
        if payload.thread:
            return

        # Ignore updates to threads outside of forum channels
        thread = await self.bot.fetch_channel(payload.thread_id)
        assert isinstance(thread, Thread)
        channel = thread.parent
        if not isinstance(channel, ForumChannel):
            return

        # Check if the forum channel was registered as a help forum
        if forum := await self.store.get_help_forum(self.guild, channel):
            # Change the thread state to 'Unresolved'
            await self._change_thread_state(
                channel, thread, forum, ThreadState.UNRESOLVED
            )

    async def on_message(self, message: Message):
        """
        Called whenever a message is sent.

        This event sets the thread state to 'Resolved' if a message is sent in a thread
        that only contains the resolved emoji. This will ignore messages that started
        the thread.
        """

        # Ignore messages being sent outside of forum channels
        thread = message.channel
        assert isinstance(thread, Thread)
        channel = thread.parent
        if not isinstance(channel, ForumChannel):
            return

        # Ignore thread starter messages
        if message.id == thread.id:
            return

        # Check if the forum channel was registered as a help forum
        if forum := await self.store.get_help_forum(self.guild, channel):
            # Check if the message contains only the resolved emoji
            if message.content == forum.resolved_emoji:
                # Make the bot add the resolved emoji to the message the user reacted
                # to as a visual indication that it was successful
                await message.add_reaction(forum.resolved_emoji)

                # Change the thread state to 'Resolved'
                await self._change_thread_state(
                    channel, thread, forum, ThreadState.RESOLVED
                )

                # Increment resolved threads
                await self.store.increment_resolved_threads(forum)

    async def on_raw_reaction_add(self, payload: RawReactionActionEvent):
        """
        Called whenever a reaction is added to a message reguardless of if they're in the
        cache or not.

        This event sets the thread state to 'Resolved' when the user reacts to a message
        in a thread using the resolved emoji. This will ignore messages that started the
        thread.
        """

        # Ignore reactions being added outside of forum channels
        thread = await self.bot.fetch_channel(payload.channel_id)
        if not isinstance(thread, Thread):
            return

        channel = thread.parent
        if not isinstance(channel, ForumChannel):
            return

        # Ignore thread starter messages
        if payload.message_id == thread.id:
            return

        # Check if the forum channel was registered as a help forum
        if forum := await self.store.get_help_forum(self.guild, channel):
            # Check if the reaction was the resolved emoji
            resolved_emoji = PartialEmoji.from_str(forum.resolved_emoji)
            if payload.emoji == resolved_emoji:
                # Make the bot add the resolved emoji to the message the user reacted
                # to as a visual indication that it was successful
                message = thread.get_partial_message(payload.message_id)
                await message.add_reaction(resolved_emoji)

                # Change the thread state to 'Resolved'
                await self._change_thread_state(
                    channel, thread, forum, ThreadState.RESOLVED
                )

                # Increment resolved threads
                await self.store.increment_resolved_threads(forum)

    async def register_forum_channel(
        self,
        interaction: Interaction,
        channel: ForumChannel,
        resolved_emoji: str,
        unresolved_tag: str,
        resolved_tag: str,
    ):
        forum = await self.store.register_forum_channel(
            self.guild, channel, resolved_emoji, unresolved_tag, resolved_tag
        )
        await interaction.response.send_message(
            f"Registered <#{forum.channel_id}> as a help forum"
        )

    async def deregister_forum_channel(
        self,
        interaction: Interaction,
        channel: ForumChannel,
    ):
        # Try to get the forum channel
        forum = await self.store.require_help_forum(self.guild, channel)

        # If the forum does exist, send a message to show other users that a response is espected
        await interaction.response.send_message(
            f"Waiting for a response from {interaction.user.mention}...",
            allowed_mentions=AllowedMentions.none(),
        )

        # Send a confirmation dialogue to the user
        result = await confirm_with_buttons(
            interaction, f"Do you want to deregister <#{forum.channel_id}>?", timeout=10
        )

        # Handle confirmation dialog result
        match result:
            case ConfirmationResult.YES:
                await self.store.deregister_forum_channel(self.guild, channel)
                await interaction.edit_original_response(
                    content=f"Deregistered <#{forum.channel_id}> as a help forum"
                )
            case _:
                await interaction.edit_original_response(
                    content=f"Did not deregister <#{forum.channel_id}> as a help forum"
                )

    async def details(self, interaction: Interaction, channel: ForumChannel):
        # Get data from the help forum if it was registered
        forum = await self.store.require_help_forum(self.guild, channel)
        unresolved_tag = tag_from_id(channel, forum.unresolved_tag_id)
        resolved_tag = tag_from_id(channel, forum.resolved_tag_id)

        formatted_unresolved_tag = (
            f"`{format_tag(unresolved_tag)}`" if unresolved_tag else "**No tag set!**"
        )
        formatted_resolved_tag = (
            f"`{format_tag(resolved_tag)}`" if resolved_tag else "**No tag set!**"
        )

        # Create embed fields
        fields: dict = {
            "Resolved Emoji": forum.resolved_emoji,
            "Unresolved Tag": formatted_unresolved_tag,
            "Resolved Tag": formatted_resolved_tag,
            "Threads Created": f"`{forum.total_threads}`",
            "Threads Resolved": f"`{forum.resolved_threads}`",
            "Percent Resolved": f"`{forum.resolved_percentage:.2f}%`",
        }

        # Create embed and add fields
        embed: Embed = Embed(
            title=f"💬 {channel.name}",
            url=channel.jump_url,
            color=0x00ACED,
        )
        for k, v in fields.items():
            embed.add_field(name=k, value=v)

        await interaction.response.send_message(embed=embed)

    async def modify_resolved_emoji(
        self, interaction: Interaction, channel: ForumChannel, emoji: str
    ):
        forum = await self.store.modify_resolved_emoji(self.guild, channel, emoji)
        await interaction.response.send_message(
            f"Changed the resolved emoji for <#{forum.channel_id}> to {forum.resolved_emoji}"
        )

    async def modify_unresolved_tag(
        self, interaction: Interaction, channel: ForumChannel, tag: str
    ):
        forum, new_tag = await self.store.modify_unresolved_tag(
            self.guild, channel, tag
        )
        await interaction.response.send_message(
            f"Changed unresolved tag for <#{forum.channel_id}> to `{format_tag(new_tag)}`"
        )

    async def modify_resolved_tag(
        self, interaction: Interaction, channel: ForumChannel, tag: str
    ):
        forum, new_tag = await self.store.modify_resolved_tag(self.guild, channel, tag)
        await interaction.response.send_message(
            f"Changed resolved tag for <#{forum.channel_id}> to `{format_tag(new_tag)}`"
        )
