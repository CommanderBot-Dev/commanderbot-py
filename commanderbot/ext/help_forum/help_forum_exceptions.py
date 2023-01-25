from commanderbot.lib import ChannelID, ResponsiveException


class HelpForumException(ResponsiveException):
    pass


class ForumChannelAlreadyRegistered(HelpForumException):
    def __init__(self, channel_id: ChannelID):
        self.channel_id = channel_id
        super().__init__(
            f"🤷 <#{self.channel_id}> is already registered as a help forum"
        )


class ForumChannelNotRegistered(HelpForumException):
    def __init__(self, channel_id: ChannelID):
        self.channel_id = channel_id
        super().__init__(f"🤷 <#{self.channel_id}> is not a registered help forum")


class HelpForumInvalidTag(HelpForumException):
    def __init__(self, channel: ChannelID, tag: str):
        self.channel_id = channel
        self.tag = tag
        super().__init__(f"😬 Tag `{self.tag}` does not exist in <#{self.channel_id}>")


class InvalidResolveLocation(HelpForumException):
    def __init__(self):
        super().__init__("😬 You can only use this command in forum posts")


class UnableToResolvePinned(HelpForumException):
    def __init__(self):
        super().__init__("😠 You can't resolve pinned posts")


class UnableToResolveUnregistered(HelpForumException):
    def __init__(self, channel: ChannelID):
        self.channel_id = channel
        super().__init__(
            f"😬 Unable to resolve this post because <#{self.channel_id}> is not registered as a help forum"
        )
