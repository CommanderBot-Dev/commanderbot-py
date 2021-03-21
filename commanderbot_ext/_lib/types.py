from typing import Any, Union

from discord import Guild, Member, Message, Reaction, TextChannel, User
from discord.ext.commands import Context

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
    this [Message] does indeed contain a [TextChannel] and [Guild].

    This is not intended to be used anywhere other than type-hinting.
    """

    channel: TextChannel
    guild: Guild


class TextReaction(Reaction):
    """
    A [Reaction] to a [Message] in a [TextChannel].

    This is a dummy class that can be used in casts to convince static analysis that
    this [Reaction] does indeed contain a [TextMessage].

    This is not intended to be used anywhere other than type-hinting.
    """

    message: TextMessage


class GuildContext(Context):
    """
    A [Context] from within a [Guild].

    This is a dummy class that can be used in casts to convince static analysis that
    this [Context] does indeed contain a [Guild].

    This is not intended to be used anywhere other than type-hinting.
    """

    guild: Guild
