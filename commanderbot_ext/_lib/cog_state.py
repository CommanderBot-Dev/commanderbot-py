from dataclasses import dataclass, field
from typing import Any, Optional, cast

from commanderbot_lib.logging import Logger, get_logger
from discord import Guild, Member, Message, TextChannel, User
from discord.abc import Messageable
from discord.ext.commands import Bot, Cog
from discord.reaction import Reaction

from commanderbot_ext._lib.types import TextMessage, TextReaction


@dataclass
class CogState:
    """
    Maintains state-related data for a particular cog within a particular guild.

    The overarching idea here is to keep state separate, as a component of the cog, to
    help clean-up the cog's namespace for other things like listeners and commands.

    Includes some convenience methods for determining whether to acknowledge (ack)
    certain events.

    Attributes
    -----------
    bot: :class:`Bot`
        The parent discord.py bot instance.
    cog: :class:`Cog`
        The parent discord.py cog instance.
    """

    bot: Bot
    cog: Cog

    log: Logger = field(init=False)

    def __post_init__(self):
        self.log = get_logger(
            f"{self.cog.qualified_name} ({self.__class__.__name__}#{id(self)})"
        )

    def ack_guild(self, guild: Any) -> Optional[Guild]:
        # Make sure this is actually a [Guild].
        if isinstance(guild, Guild):
            # TODO Guild whitelist/blacklist. (Per-extension?) #enhance
            return guild

    def ack_channel(self, channel: Any) -> Optional[Messageable]:
        # Make sure this is actually a [Messageable] (channel).
        if isinstance(channel, Messageable):
            # TODO Channel whitelist/blacklist. (Text channels? DMs? Group chats?) #enhance
            return channel

    def ack_channel_to_text_channel(self, channel: Any) -> Optional[TextChannel]:
        # Make sure this is a [Messageable] (channel) that should be acknowledged.
        if ackd_channel := self.ack_channel(channel):
            # And then make sure it's specifically a [TextChannel], as opposed to, say,
            # a [GroupChannel] or [DMChannel].
            if isinstance(ackd_channel, TextChannel):
                return ackd_channel

    def ack_user(self, user: Any) -> Optional[User]:
        # Make sure this is actually a [User] - or a [Member], because Pyright gets
        # confused by discord.py's type-hinting (or lack thereof).
        if isinstance(user, (User, Member)):
            # Use an explicit cast to account for aforementioned type-hinting issues.
            actual_user = cast(User, user)
            # TODO User whitelist/blacklist. (Per-extension? Per-guild?) #enhance
            # The bot unconditionally ignores its own actions.
            if actual_user.id != self.bot.user.id:
                return actual_user

    def ack_user_to_member(self, user: Any) -> Optional[Member]:
        # Make sure this is actually a [Member].
        if isinstance(user, Member):
            # And then make sure that they should be acknowledged.
            if self.ack_user(user):
                return user

    def ack_message(self, message: Any) -> Optional[Message]:
        # Make sure this is actually a [Message].
        if isinstance(message, Message):
            # Only acknowledge messages from acknowledged authors in acknowledged
            # channels.
            if self.ack_user(message.author) and self.ack_channel(message.channel):
                return message

    def ack_message_to_text_message(self, message: Any) -> Optional[TextMessage]:
        # Make sure this is a [Message] that should be acknowledged.
        if ackd_message := self.ack_message(message):
            # And then make sure it's in a text channel.
            if isinstance(ackd_message.channel, TextChannel):
                # Cast to a [TextMessage] (a [Message] in a [TextChannel]) to help with
                # type-hinting.
                return cast(TextMessage, ackd_message)

    def ack_message_to_text_channel(self, message: Any) -> Optional[TextChannel]:
        # Make sure this is a [TextMessage] (a [Message] in a [TextChannel]) that should
        # be acknowledged.
        if text_message := self.ack_message_to_text_message(message):
            return text_message.channel

    def ack_reaction_to_text_reaction(self, reaction: Any) -> Optional[TextReaction]:
        # Make sure this is actually a [Reaction].
        if isinstance(reaction, Reaction):
            # And then make sure it's on a [TextMessage] (a [Message] in a
            # [TextChannel]) that should be acknowledged.
            if self.ack_message_to_text_message(reaction.message):
                # Cast to a [TextReaction] (a [Reaction] on a [TextMessage]) to help
                # with type-hinting.
                return cast(TextReaction, reaction)
