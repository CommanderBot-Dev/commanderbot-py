from typing import Any, Union

from discord import Guild, Member, Message, Reaction, TextChannel, User

IDType = int

GuildID = IDType
ChannelID = IDType
RoleID = IDType
UserID = IDType

RawOptions = Any

MemberOrUser = Union[User, Member]


class TextMessage(Message):
    """
    A [Message] in a [TextChannel].

    This is a dummy class that can be used in casts to convince static analysis that
    this [Message] does indeed belong to a [TextChannel].

    This is not intended to be used anywhere other than type-hinting.
    """

    channel: TextChannel
    guild: Guild


class TextReaction(Reaction):
    """
    A [Reaction] to a [Message] in a [TextChannel].

    Similar to [TextMessage], this is intended to be used only for type-hinting.
    """

    message: TextMessage
