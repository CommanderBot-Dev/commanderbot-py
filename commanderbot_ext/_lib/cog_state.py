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
        if isinstance(guild, Guild):
            # TODO Guild ignore list. (Per-extension?) #enhance
            return guild

    def ack_channel(self, channel: Any) -> Optional[Messageable]:
        if isinstance(channel, Messageable):
            # TODO Channel ignore list. (Text channels? DMs? Group chats?) #enhance
            return channel

    def ack_channel_to_text_channel(self, channel: Any) -> Optional[TextChannel]:
        if ackd_channel := self.ack_channel(channel):
            if isinstance(ackd_channel, TextChannel):
                return ackd_channel

    def ack_user(self, user: Any) -> Optional[User]:
        if isinstance(user, (User, Member)):
            # Yes, I'm pretty sure members are also users...
            actual_user = cast(User, user)
            # TODO User ignore list. (Per-extension? Per-guild?) #enhance
            # The bot unconditionally ignores its own actions.
            if actual_user.id != self.bot.user.id:
                return actual_user

    def ack_user_to_member(self, user: Any) -> Optional[Member]:
        if ackd_user := self.ack_user(user):
            if isinstance(ackd_user, Member):
                return ackd_user

    def ack_message(self, message: Any) -> Optional[Message]:
        if isinstance(message, Message):
            # Ack'ing a message ack's both he author and the channel.
            if self.ack_user(message.author) and self.ack_channel(message.channel):
                return message

    def ack_message_to_text_message(self, message: Any) -> Optional[TextMessage]:
        if ackd_message := self.ack_message(message):
            if isinstance(ackd_message.channel, TextChannel):
                return cast(TextMessage, ackd_message)

    def ack_message_to_text_channel(self, message: Any) -> Optional[TextChannel]:
        if text_message := self.ack_message_to_text_message(message):
            return text_message.channel

    def ack_reaction_to_text_reaction(self, reaction: Any) -> Optional[TextReaction]:
        if isinstance(reaction, Reaction):
            if self.ack_message_to_text_message(reaction.message):
                return cast(TextReaction, reaction)
