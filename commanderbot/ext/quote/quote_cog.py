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
        created_at_ts = int(message.created_at.timestamp())
        quote_ts = f"<t:{created_at_ts}:R>"
        if message.edited_at is not None:
            edited_at_ts = int(message.edited_at.timestamp())
            quote_ts += f" (edited <ts:{edited_at_ts}:R>)"
        content = (
            f"{ctx.author.mention} {phrasing} {message.author.mention}"
            + f" in {message.channel.mention} from {quote_ts}:"
            + f"\n{message.jump_url}"
        )

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

        # Account for any attachments to the original message.
        quote_files: List[File] = []
        failed_attachments: List[Attachment] = []
        for att in message.attachments:
            try:
                file = await att.to_file()
            except:
                failed_attachments.append(att)
            else:
                quote_files.append(file)

        # Send the message with the embed attached, if any.
        if quote_embed:
            await ctx.send(
                content,
                embed=quote_embed,
                files=quote_files,
                allowed_mentions=allowed_mentions,
            )
        elif quote_files:
            await ctx.send(
                content,
                files=quote_files,
                allowed_mentions=allowed_mentions,
            )
        else:
            await ctx.message.reply("🤔 There's nothing to quote.")
            return

        # Let the user know if any attachments failed.
        if failed_attachments:
            await ctx.message.add_reaction("⚠️")

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
