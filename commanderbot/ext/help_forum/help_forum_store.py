from typing import Optional, Protocol, Tuple

from discord import ForumChannel, ForumTag, Guild

from commanderbot.lib import ChannelID, ForumTagID, LogOptions


class HelpForum(Protocol):
    channel_id: ChannelID
    resolved_emoji: str
    unresolved_tag_id: ForumTagID
    resolved_tag_id: ForumTagID
    threads_created: int
    resolutions: int

    @property
    def thread_state_tags(self) -> tuple[ForumTagID, ForumTagID]:
        ...


class HelpForumStore(Protocol):
    """
    Abstracts the data storage and persistence of the help forum cog
    """

    async def require_help_forum(
        self, guild: Guild, channel: ForumChannel
    ) -> HelpForum:
        ...

    async def get_help_forum(
        self, guild: Guild, channel: ForumChannel
    ) -> Optional[HelpForum]:
        ...

    async def register_forum_channel(
        self,
        guild: Guild,
        channel: ForumChannel,
        resolved_emoji: str,
        unresolved_tag: str,
        resolved_tag: str,
    ) -> HelpForum:
        ...

    async def deregister_forum_channel(
        self, guild: Guild, channel: ForumChannel
    ) -> HelpForum:
        ...

    async def increment_threads_created(self, help_forum: HelpForum):
        ...

    async def increment_resolutions(self, help_forum: HelpForum):
        ...

    async def modify_resolved_emoji(
        self, guild: Guild, channel: ForumChannel, emoji: str
    ) -> HelpForum:
        ...

    async def modify_unresolved_tag(
        self, guild: Guild, channel: ForumChannel, tag: str
    ) -> Tuple[HelpForum, ForumTag]:
        ...

    async def modify_resolved_tag(
        self, guild: Guild, channel: ForumChannel, tag: str
    ) -> Tuple[HelpForum, ForumTag]:
        ...

    async def get_log_options(self, guild: Guild) -> Optional[LogOptions]:
        ...

    async def set_log_options(
        self, guild: Guild, log_options: Optional[LogOptions]
    ) -> Optional[LogOptions]:
        ...
