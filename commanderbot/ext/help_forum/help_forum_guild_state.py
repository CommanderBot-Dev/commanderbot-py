from dataclasses import dataclass

from discord import Embed, ForumChannel, Interaction

from commanderbot.ext.help_forum.help_forum_store import HelpForumStore
from commanderbot.lib import CogGuildState
from commanderbot.lib.dialogs import ConfirmationResult, confirm_with_buttons
from commanderbot.lib.utils.forums import format_tag, try_get_tag_from_channel


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

        # If it does exist, send a confirm dialogue to the user
        result = await confirm_with_buttons(
            interaction, f"Do you want to deregister <#{forum.channel_id}>?", timeout=10
        )

        # Remove forum if the user pressed `yes`
        if result == ConfirmationResult.YES:
            await self.store.deregister_forum_channel(self.guild, channel)
            await interaction.followup.send(
                f"Deregistered <#{forum.channel_id}> as a help forum"
            )
        else:
            await interaction.followup.send(f"Did not deregister <#{forum.channel_id}>")

    async def details(self, interaction: Interaction, channel: ForumChannel):
        # Get data from the help forum if it was registered
        forum = await self.store.require_help_forum(self.guild, channel)
        unresolved_tag = try_get_tag_from_channel(channel, str(forum.unresolved_tag_id))
        resolved_tag = try_get_tag_from_channel(channel, str(forum.resolved_tag_id))

        # Create embed fields
        fields: dict = {
            "Resolved Emoji": forum.resolved_emoji,
            "Unresolved Tag": format_tag(unresolved_tag) if unresolved_tag else None,
            "Resolved Tag": format_tag(resolved_tag) if resolved_tag else None,
            "Threads Created": f"`{forum.total_threads}`",
            "Threads Resolved": f"`{forum.resolved_threads}`",
            "Percent Resolved": f"`{forum.resolved_percentage}%`",
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
        forum = await self.store.modify_unresolved_tag(self.guild, channel, tag)
        unresolved_tag = try_get_tag_from_channel(channel, str(forum.unresolved_tag_id))
        assert unresolved_tag
        await interaction.response.send_message(
            f"Changed unresolved tag for <#{forum.channel_id}> to {format_tag(unresolved_tag)}"
        )

    async def modify_resolved_tag(
        self, interaction: Interaction, channel: ForumChannel, tag: str
    ):
        forum = await self.store.modify_resolved_tag(self.guild, channel, tag)
        resolved_tag = try_get_tag_from_channel(channel, str(forum.resolved_tag_id))
        assert resolved_tag
        await interaction.response.send_message(
            f"Changed resolved tag for <#{forum.channel_id}> to {format_tag(resolved_tag)}"
        )
