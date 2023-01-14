from typing import Optional, Protocol, Tuple

from discord import ForumChannel, ForumTag, Guild, PartialEmoji

from commanderbot.lib import ChannelID, ForumTagID


class HelpForum(Protocol):
    channel_id: ChannelID
    resolved_emoji: str
    unresolved_tag_id: ForumTagID
    resolved_tag_id: ForumTagID
    threads_created: int
    resolutions: int

    @property
    def partial_resolved_emoji(self) -> PartialEmoji:
        ...

    @property
    def thread_state_tags(self) -> tuple[ForumTagID, ForumTagID]:
        ...

    @property
    def ratio(self) -> tuple[int, int]:
        ...


class HelpForumStore(Protocol):
    """
    Abstracts the data storage and persistence of the help forum cog
    """

    async def require_help_forum(self, guild: Guild, forum: ForumChannel) -> HelpForum:
        ...

    async def get_help_forum(
        self, guild: Guild, forum: ForumChannel
    ) -> Optional[HelpForum]:
        ...

    async def register_forum_channel(
        self,
        guild: Guild,
        forum: ForumChannel,
        resolved_emoji: str,
        unresolved_tag: str,
        resolved_tag: str,
    ) -> HelpForum:
        ...

    async def deregister_forum_channel(
        self, guild: Guild, forum: ForumChannel
    ) -> HelpForum:
        ...

    async def increment_threads_created(self, help_forum: HelpForum):
        ...

    async def increment_resolutions(self, help_forum: HelpForum):
        ...

    async def modify_resolved_emoji(
        self, guild: Guild, forum: ForumChannel, emoji: str
    ) -> HelpForum:
        ...

    async def modify_unresolved_tag(
        self, guild: Guild, forum: ForumChannel, tag: str
    ) -> Tuple[HelpForum, ForumTag]:
        ...

    async def modify_resolved_tag(
        self, guild: Guild, forum: ForumChannel, tag: str
    ) -> Tuple[HelpForum, ForumTag]:
        ...
