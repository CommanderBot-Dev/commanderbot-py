from typing import Optional

from discord import AllowedMentions
from discord.ext.commands import Context

__all__ = ("ResponsiveException",)


class ResponsiveException(Exception):
    def __init__(
        self,
        *args,
        allowed_mentions: Optional[AllowedMentions] = None,
    ):
        self.allowed_mentions: Optional[AllowedMentions] = allowed_mentions
        super().__init__(*args)

    @classmethod
    def allowed_mentions_default_factory(cls) -> AllowedMentions:
        return AllowedMentions(
            everyone=False,
            users=False,
            roles=False,
            replied_user=True,
        )

    async def respond(
        self,
        ctx: Context,
        allowed_mentions: Optional[AllowedMentions] = None,
    ):
        allowed_mentions = (
            allowed_mentions
            or self.allowed_mentions
            or self.allowed_mentions_default_factory()
        )
        await ctx.message.reply(
            str(self),
            allowed_mentions=allowed_mentions,
        )
