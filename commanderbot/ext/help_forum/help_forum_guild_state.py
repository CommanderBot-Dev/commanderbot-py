from dataclasses import dataclass
from enum import Enum
from typing import Optional, Union

from discord import (
    AllowedMentions,
    Embed,
    ForumChannel,
    ForumTag,
    Interaction,
    Message,
    PartialEmoji,
    PartialMessage,
    Thread,
)

from commanderbot.ext.help_forum.help_forum_exceptions import (
    UnableToResolveUnregistered,
)
from commanderbot.ext.help_forum.help_forum_store import HelpForum, HelpForumStore
from commanderbot.lib import AllowedMentions, CogGuildState
from commanderbot.lib.dialogs import ConfirmationResult, confirm_with_buttons
from commanderbot.lib.forums import format_tag, require_tag


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
        # Require that the tags exist
        valid_unresolved_tag: ForumTag = require_tag(channel, forum.unresolved_tag_id)
        valid_resolved_tag: ForumTag = require_tag(channel, forum.resolved_tag_id)

        # Create a new tag list from the first 4 tags that aren't a state tag
        tags: list[ForumTag] = []
        applied_tag_gen = (
            t for t in thread.applied_tags if t.id not in forum.thread_state_tags
        )
        for tag in applied_tag_gen:
            if len(tags) == 4:
                break
            tags.append(tag)

        # Add the new state tag
        match state:
            case ThreadState.UNRESOLVED:
                tags = [*tags, valid_unresolved_tag]
            case ThreadState.RESOLVED:
                tags = [valid_resolved_tag, *tags]

        await thread.edit(
            applied_tags=tags,
            archived=(state == ThreadState.RESOLVED),
            reason=f"Added the {state.value} tag",
        )

    async def _get_help_forum(self, forum: ForumChannel) -> Optional[HelpForum]:
        return await self.store.get_help_forum(self.guild, forum)

    async def on_thread_create(self, forum: ForumChannel, thread: Thread):
        """
        Whenever a thread is created, pin the first message and set the state to unresolved
        """

        # Get help forum data
        forum_data = await self._get_help_forum(forum)
        if not forum_data:
            return

        # Pin first message
        await thread.get_partial_message(thread.id).pin()

        # Change the thread state to 'unresolved'
        await self._change_thread_state(
            forum, thread, forum_data, ThreadState.UNRESOLVED
        )

        # Increment threads created
        await self.store.increment_threads_created(forum_data)

    async def on_unresolve(self, forum: ForumChannel, thread: Thread):
        """
        If `forum` is a help forum, set the thread state to unresolved
        """

        # Get help forum data
        forum_data = await self._get_help_forum(forum)
        if not forum_data:
            return

        # Change the thread state to 'unresolved'
        await self._change_thread_state(
            forum, thread, forum_data, ThreadState.UNRESOLVED
        )

    async def on_resolve(
        self,
        forum: ForumChannel,
        thread: Thread,
        message: Union[Message, PartialMessage],
        emoji: PartialEmoji,
    ):
        """
        If `forum` is a help forum, set the thread state to resolved if `emoji` matches the resolved emoji
        """

        # Get help forum data
        forum_data = await self._get_help_forum(forum)
        if not forum_data:
            return

        if emoji == forum_data.partial_resolved_emoji:
            await message.add_reaction(forum_data.partial_resolved_emoji)

            # Change the thread state to 'resolved'
            await self._change_thread_state(
                forum, thread, forum_data, ThreadState.RESOLVED
            )

            # Increment resolutions
            await self.store.increment_resolutions(forum_data)

    async def on_resolve_command(
        self, interaction: Interaction, forum: ForumChannel, thread: Thread
    ):
        """
        If `forum` is a help forum, set the thread state to resolved when `/resolve` is ran in `thread`
        """

        # Get help forum data
        forum_data = await self._get_help_forum(forum)
        if not forum_data:
            raise UnableToResolveUnregistered(forum.id)

        # Send resolved message
        emoji: PartialEmoji = forum_data.partial_resolved_emoji
        await interaction.response.send_message(
            f"{emoji} {interaction.user.mention} resolved this thread",
            allowed_mentions=AllowedMentions.none(),
        )

        # Change the thread state to 'resolved'
        await self._change_thread_state(forum, thread, forum_data, ThreadState.RESOLVED)

        # Increment resolutions
        await self.store.increment_resolutions(forum_data)

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

        # If the forum does exist, send a message to show other users that a response is expected
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
                await interaction.delete_original_response()

    async def details(self, interaction: Interaction, channel: ForumChannel):
        # Get data from the help forum if it was registered
        forum = await self.store.require_help_forum(self.guild, channel)
        unresolved_tag = channel.get_tag(forum.unresolved_tag_id)
        resolved_tag = channel.get_tag(forum.resolved_tag_id)

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
            "Threads Created": f"`{forum.threads_created}`",
            "Resolutions": f"`{forum.resolutions}`",
            "Ratio": f"`{':'.join(map(str, forum.ratio))}`",
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
