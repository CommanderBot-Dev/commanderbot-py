from dataclasses import dataclass

from discord import Embed, ForumChannel, Interaction

from commanderbot.ext.help_forum.help_forum_store import HelpForumStore
from commanderbot.lib import CogGuildState
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
        forum = await self.store.deregister_forum_channel(self.guild, channel)
        await interaction.response.send_message(
            f"Deregistered <#{forum.channel_id}> as a help forum"
        )

    async def details(self, interaction: Interaction, channel: ForumChannel):
        forum = await self.store.try_get_forum(self.guild, channel)
        unresolved_tag = try_get_tag_from_channel(channel, str(forum.unresolved_tag_id))
        resolved_tag = try_get_tag_from_channel(channel, str(forum.resolved_tag_id))

        fields: dict = {
            "Resolved Emoji": forum.resolved_emoji,
            "Unresolved Tag": format_tag(unresolved_tag) if unresolved_tag else None,
            "Resolved Tag": format_tag(resolved_tag) if resolved_tag else None,
            "Threads Created": f"`{forum.total_threads}`",
            "Threads Resolved": f"`{forum.resolved_threads}`",
            "Percent Resolved": f"`{forum.resolved_percentage}%`",
        }

        jump_url: str = ""
        jump_name: str = ""
        if jump_to := self.bot.get_channel(forum.channel_id):
            assert isinstance(jump_to, ForumChannel)
            jump_url = jump_to.jump_url
            jump_name = jump_to.name

        embed: Embed = Embed(
            title=f"💬 {jump_name}",
            url=jump_url,
            color=0x00ACED,
        )
        for k, v in fields.items():
            embed.add_field(name=k, value=v)

        await interaction.response.send_message(embed=embed)

    async def modify_resolved_emoji(self, interaction: Interaction, channel: ForumChannel, emoji: str):
        forum = await self.store.modify_resolved_emoji(self.guild, channel, emoji)
        await interaction.response.send_message(f"Changed the resolved emoji for <#{forum.channel_id}> to {forum.resolved_emoji}")
