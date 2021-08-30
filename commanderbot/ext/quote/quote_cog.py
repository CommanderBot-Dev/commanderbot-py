from typing import List, Optional

from discord import (
    AllowedMentions,
    Attachment,
    Embed,
    File,
    Message,
    TextChannel,
    Thread,
)
from discord.ext.commands import Bot, Cog, Context, command


class QuoteCog(Cog, name="commanderbot.ext.quote"):
    def __init__(self, bot: Bot):
        self.bot: Bot = bot

    async def do_quote(
        self,
        ctx: Context,
        message: Message,
        phrasing: str,
        allowed_mentions: AllowedMentions,
    ):
        if not isinstance(message.channel, TextChannel | Thread):
            await ctx.message.reply("😔 I can't quote that.")
            return

        # Build the message content containing the quote metadata.
        lines: List[str] = []
        created_at_ts = int(message.created_at.timestamp())
        quote_ts = f"<t:{created_at_ts}:R>"
        if message.edited_at is not None:
            edited_at_ts = int(message.edited_at.timestamp())
            quote_ts += f" (edited <ts:{edited_at_ts}:R>)"
        lines.append(
            f"{ctx.author.mention} {phrasing} {message.author.mention}"
            + f" in {message.channel.mention} from {quote_ts}:"
        )
        lines.append(message.jump_url)

        # Account for any attachments to the original message.
        if message.attachments:
            attachment_urls = [att.url for att in message.attachments]
            lines += attachment_urls

        # Account for any media embeds on the original message.
        if message.embeds:
            embed_urls = [
                embed.url for embed in message.embeds if isinstance(embed.url, str)
            ]
            lines += embed_urls

        # Build the embed containing the actual quote content, if any.
        quote_embed: Optional[Embed] = None
        original_content = message.content
        if original_content:
            quote_embed = Embed(
                description=original_content,
            )
            quote_embed.set_author(
                name=str(message.author),
                icon_url=message.author.display_avatar.url,
            )

        # Send the message with the embed attached, if any.
        content = "\n".join(lines)
        if quote_embed:
            await ctx.send(
                content, embed=quote_embed, allowed_mentions=allowed_mentions
            )
        else:
            await ctx.send(content, allowed_mentions=allowed_mentions)

    @command(name="quote")
    async def cmd_quote(self, ctx: Context, message: Message):
        await self.do_quote(
            ctx,
            message,
            phrasing="quoted",
            allowed_mentions=AllowedMentions.none(),
        )

    @command(name="quotem")
    async def cmd_quotem(self, ctx: Context, message: Message):
        await self.do_quote(
            ctx,
            message,
            phrasing="quote-mentioned",
            allowed_mentions=AllowedMentions(
                everyone=False,
                users=True,
                roles=False,
                replied_user=False,
            ),
        )
