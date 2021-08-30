from typing import Any, Dict

from discord import (
    DMChannel,
    GroupChannel,
    Guild,
    Member,
    Message,
    PartialMessageable,
    Reaction,
    TextChannel,
    Thread,
    User,
)
from discord.ext.commands import Context, MessageConverter

__all__ = (
    "IDType",
    "GuildID",
    "ChannelID",
    "RoleID",
    "UserID",
    "RawOptions",
    "JsonObject",
    "MemberOrUser",
    "PartialMessageableChannel",
    "MessageableChannel",
    "TextMessage",
    "TextReaction",
    "GuildContext",
    "MemberContext",
)


IDType = int

GuildID = IDType
ChannelID = IDType
RoleID = IDType
UserID = IDType

RawOptions = Any

JsonObject = Dict[str, Any]

MemberOrUser = Member | User

PartialMessageableChannel = TextChannel | Thread | DMChannel | PartialMessageable
MessageableChannel = PartialMessageableChannel | GroupChannel


class TextMessage(Message):
    """
    A [Message] in a [TextChannel] or [Thread].

    This is a dummy class that can be used in casts to convince static analysis that
    this [Message] does indeed contain a [TextChannel] and [Guild].

    This is not intended to be used anywhere other than type-hinting.
    """

    channel: TextChannel | Thread
    guild: Guild

    @classmethod
    async def convert(cls, ctx: Context, argument: Any):
        """
        Attempt to convert the given argument into a `Role` from within a `Guild`.

        Note that discord.py's built-in `Role` is special-cased, so what we do here is
        explicitly make this subclass convertible and then just return the underlying
        `Role` anyway.
        """
        return await MessageConverter().convert(ctx, argument)


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


class MemberContext(GuildContext):
    """
    A [Context] from within a [Guild] with an author that is a [Member].

    This is a dummy class that can be used in casts to convince static analysis that
    this [Context] contains an `author` that is a [Member] and not just a [User].

    This is not intended to be used anywhere other than type-hinting.
    """

    author: Member
