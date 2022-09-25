from typing import Optional, Protocol

from discord import ForumChannel, Guild

from commanderbot.lib import ChannelID, ForumTagID, LogOptions, ResponsiveException


class HelpForumException(ResponsiveException):
    pass


class ForumChannelAlreadyRegistered(HelpForumException):
    def __init__(self, name: str):
        self.name = name
        super().__init__(f"🤷 Forum channel `{name}` is already registered")


class ForumChannelNotRegistered(HelpForumException):
    def __init__(self, name: str):
        self.name = name
        super().__init__(f"🤷 Forum channel `{name}` is not registered")


class HelpForumForumData(Protocol):
    channel_id: ChannelID
    resolved_emoji: str
    unresolved_tag_id: ForumTagID
    resolved_tag_id: ForumTagID


class HelpForumStore(Protocol):
    """
    Abstracts the data storage and persistence of the help forum cog
    """

    async def is_forum_registered(
        self, guild: Guild, forum_channel: ForumChannel
    ) -> bool:
        ...

    async def register_forum_channel(
        self,
        guild: Guild,
        forum_channel: ForumChannel,
        resolved_emoji: str,
        unresolved_tag: ForumTagID,
        resolved_tag: ForumTagID,
    ) -> HelpForumForumData:
        ...

    async def deregister_forum_channel(
        self, guild: Guild, forum_channel: ForumChannel
    ) -> HelpForumForumData:
        ...

    async def get_help_forum_data(
        self, guild: Guild, forum_channel: ForumChannel
    ) -> Optional[HelpForumForumData]:
        ...

    async def get_resolved_emoji(
        self, guild: Guild, forum_channel: ForumChannel
    ) -> Optional[str]:
        ...

    async def get_unresolved_tag_id(
        self, guild: Guild, forum_channel: ForumChannel
    ) -> Optional[ForumTagID]:
        ...

    async def get_resolved_tag_id(
        self, guild: Guild, forum_channel: ForumChannel
    ) -> Optional[ForumTagID]:
        ...

    async def modify_resolved_emoji(
        self, guild: Guild, forum_channel: ForumChannel, emoji: str
    ) -> HelpForumForumData:
        ...

    async def modify_unresolved_tag_id(
        self, guild: Guild, forum_channel: ForumChannel, tag: ForumTagID
    ) -> HelpForumForumData:
        ...

    async def modify_resolved_tag_id(
        self, guild: Guild, forum_channel: ForumChannel, tag: ForumTagID
    ) -> HelpForumForumData:
        ...

    async def set_log_options(
        self, guild: Guild, log_options: Optional[LogOptions]
    ) -> Optional[LogOptions]:
        ...
