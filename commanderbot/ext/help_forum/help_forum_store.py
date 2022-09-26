from typing import Optional, Protocol

from discord import ForumChannel, Guild

from commanderbot.lib import ChannelID, ForumTagID, LogOptions, ResponsiveException


class HelpForumException(ResponsiveException):
    pass


class ForumChannelAlreadyRegistered(HelpForumException):
    def __init__(self, channel_id: ChannelID):
        self.channel_id = channel_id
        super().__init__(f"🤷 Forum channel <#{self.channel_id}> is already registered")


class ForumChannelNotRegistered(HelpForumException):
    def __init__(self, channel_id: ChannelID):
        self.channel_id = channel_id
        super().__init__(f"🤷 Forum channel <#{self.channel_id}> is not registered")


class HelpForum(Protocol):
    channel_id: ChannelID
    resolved_emoji: str
    unresolved_tag_id: ForumTagID
    resolved_tag_id: ForumTagID
    total_threads: int
    resolved_threads: int

    @property
    def resolved_percentage(self) -> float:
        ...


class HelpForumStore(Protocol):
    """
    Abstracts the data storage and persistence of the help forum cog
    """

    async def is_forum_registered(
        self, guild: Guild, channel: ForumChannel
    ) -> bool:
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

    async def increment_total_threads(self, help_forum: HelpForum):
        ...

    async def increment_resolved_threads(self, help_forum: HelpForum):
        ...

    async def try_get_forum(
        self, guild: Guild, channel: ForumChannel
    ) -> HelpForum:
        ...

    async def get_forum(
        self, guild: Guild, channel: ForumChannel
    ) -> Optional[HelpForum]:
        ...

    async def modify_resolved_emoji(
        self, guild: Guild, channel: ForumChannel, emoji: str
    ) -> HelpForum:
        ...

    async def modify_unresolved_tag_id(
        self, guild: Guild, channel: ForumChannel, tag: ForumTagID
    ) -> HelpForum:
        ...

    async def modify_resolved_tag_id(
        self, guild: Guild, channel: ForumChannel, tag: ForumTagID
    ) -> HelpForum:
        ...

    async def set_log_options(
        self, guild: Guild, log_options: Optional[LogOptions]
    ) -> Optional[LogOptions]:
        ...
