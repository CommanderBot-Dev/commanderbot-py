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
from commanderbot.lib import AllowedMentions, CogGuildState, ForumTagID
from commanderbot.lib.dialogs import ConfirmationResult, confirm_with_buttons
from commanderbot.lib.forums import format_tag, require_tag_id, thread_has_tag_id


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
        forum: ForumChannel,
        thread: Thread,
        forum_data: HelpForum,
        state: ThreadState,
    ):
        # Require the tags to exist
        unresolved_tag_id: ForumTagID = forum_data.unresolved_tag_id
        resolved_tag_id: ForumTagID = forum_data.resolved_tag_id

        valid_unresolved_tag: ForumTag = require_tag_id(forum, unresolved_tag_id)
        valid_resolved_tag: ForumTag = require_tag_id(forum, resolved_tag_id)

        # Create a new tag list from the first 4 tags that aren't a state tag
        tags: list[ForumTag] = []

        applied_tags_gen = (
            t
            for t in sorted(thread.applied_tags, key=lambda x: x.id)
            if t.id not in forum_data.thread_state_tags
        )
        for tag in applied_tags_gen:
            if len(tags) == 4:
                break
            tags.append(tag)

        # Add the new state tag
        match state:
            case ThreadState.UNRESOLVED:
                tags = [*tags, valid_unresolved_tag]
            case ThreadState.RESOLVED:
                tags = [valid_resolved_tag, *tags]

        # Edit thread to change tags and state
        await thread.edit(
            applied_tags=tags,
            archived=(state == ThreadState.RESOLVED),
            reason=f"{state.value} the thread",
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

        # Ignore newly created threads if it has the resolved tag
        # This is a QoL feature for server moderators so they can create threads that will be pinned
        if thread_has_tag_id(thread, forum_data.resolved_tag_id):
            return

        # Send a message with an embed that tells users how to resolve their thread
        resolved_emoji: str = forum_data.resolved_emoji
        description: list[str] = [
            f"• When your question has been answered, please resolve your thread.",
            f"• You can resolve your thread by using `/resolve`, reacting to a message with {resolved_emoji}, or sending {resolved_emoji} as a message.",
        ]
        resolve_embed: Embed = Embed(
            title="Thanks for asking your question",
            description="\n".join(description),
            color=0x00ACED,
        )
        await thread.send(embed=resolve_embed)

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
        forum: ForumChannel,
        resolved_emoji: str,
        unresolved_tag: str,
        resolved_tag: str,
    ):
        forum_data = await self.store.register_forum_channel(
            self.guild, forum, resolved_emoji, unresolved_tag, resolved_tag
        )
        await interaction.response.send_message(
            f"Registered <#{forum_data.channel_id}> as a help forum"
        )

    async def deregister_forum_channel(
        self,
        interaction: Interaction,
        forum: ForumChannel,
    ):
        # Try to get the forum channel
        forum_data = await self.store.require_help_forum(self.guild, forum)

        # If the forum does exist, send a message to show other users that a response is expected
        await interaction.response.send_message(
            f"Waiting for a response from {interaction.user.mention}...",
            allowed_mentions=AllowedMentions.none(),
        )

        # Send a confirmation dialogue to the user
        result = await confirm_with_buttons(
            interaction,
            f"Do you want to deregister <#{forum_data.channel_id}>?",
            timeout=10,
        )

        # Handle confirmation dialog result
        match result:
            case ConfirmationResult.YES:
                await self.store.deregister_forum_channel(self.guild, forum)
                await interaction.edit_original_response(
                    content=f"Deregistered <#{forum_data.channel_id}> as a help forum"
                )
            case _:
                await interaction.delete_original_response()

    async def details(self, interaction: Interaction, forum: ForumChannel):
        # Get data from the help forum if it was registered
        forum_data = await self.store.require_help_forum(self.guild, forum)
        unresolved_tag = forum.get_tag(forum_data.unresolved_tag_id)
        resolved_tag = forum.get_tag(forum_data.resolved_tag_id)

        formatted_unresolved_tag = (
            f"{format_tag(unresolved_tag)}" if unresolved_tag else "**No tag set!**"
        )
        formatted_resolved_tag = (
            f"{format_tag(resolved_tag)}" if resolved_tag else "**No tag set!**"
        )

        # Create embed fields
        fields: dict = {
            "Resolved Emoji": forum_data.resolved_emoji,
            "Unresolved Tag": formatted_unresolved_tag,
            "Resolved Tag": formatted_resolved_tag,
            "Threads Created": f"`{forum_data.threads_created}`",
            "Resolutions": f"`{forum_data.resolutions}`",
            "Ratio": f"`{':'.join(map(str, forum_data.ratio))}`",
        }

        # Create embed and add fields
        embed: Embed = Embed(
            title=f"💬 {forum.name}",
            url=forum.jump_url,
            color=0x00ACED,
        )
        for k, v in fields.items():
            embed.add_field(name=k, value=v)

        await interaction.response.send_message(embed=embed)

    async def modify_resolved_emoji(
        self, interaction: Interaction, forum: ForumChannel, emoji: str
    ):
        forum_data = await self.store.modify_resolved_emoji(self.guild, forum, emoji)
        await interaction.response.send_message(
            f"Changed the resolved emoji for <#{forum_data.channel_id}> to {forum_data.resolved_emoji}"
        )

    async def modify_unresolved_tag(
        self, interaction: Interaction, forum: ForumChannel, tag: str
    ):
        forum_data, new_tag = await self.store.modify_unresolved_tag(
            self.guild, forum, tag
        )
        await interaction.response.send_message(
            f"Changed unresolved tag for <#{forum_data.channel_id}> to {format_tag(new_tag)}"
        )

    async def modify_resolved_tag(
        self, interaction: Interaction, forum: ForumChannel, tag: str
    ):
        forum_data, new_tag = await self.store.modify_resolved_tag(
            self.guild, forum, tag
        )
        await interaction.response.send_message(
            f"Changed resolved tag for <#{forum_data.channel_id}> to {format_tag(new_tag)}"
        )
