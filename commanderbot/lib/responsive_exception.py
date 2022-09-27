from typing import Optional

from discord import Interaction, AllowedMentions
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
        return AllowedMentions.none()

    async def respond(
        self,
        ctx: Context | Interaction,
        allowed_mentions: Optional[AllowedMentions] = None,
    ):
        allowed_mentions = (
            allowed_mentions
            or self.allowed_mentions
            or self.allowed_mentions_default_factory()
        )

        if isinstance(ctx, Context):
            await ctx.message.reply(str(self), allowed_mentions=allowed_mentions)
        elif isinstance(ctx, Interaction):
            if not ctx.response.is_done():
                await ctx.response.send_message(
                    str(self), allowed_mentions=allowed_mentions, ephemeral=True
                )
            else:
                await ctx.followup.send(
                    str(self), allowed_mentions=allowed_mentions, ephemeral=True
                )
