import re
from typing import List, Optional

from discord import AllowedMentions, Embed, Member, Message, TextChannel, Thread, User
from discord.ext.commands import Bot, Cog, Context, command

AUTO_EMBED_PATTERN = re.compile(r"^https?:\/\/\S\S+$")


class QuoteCog(Cog, name="commanderbot.ext.quote"):
    def __init__(self, bot: Bot):
        self.bot: Bot = bot

    def user_can_quote(
        self, user: User | Member, channel: TextChannel | Thread
    ) -> bool:
        if not isinstance(user, Member):
            return False
        quoter_permissions = channel.permissions_for(user)
        can_quote = (
            quoter_permissions.read_messages and quoter_permissions.read_message_history
        )
        return can_quote

    async def do_quote(
        self,
        ctx: Context,
        message: Message,
        phrasing: str,
        allowed_mentions: AllowedMentions,
    ):
        # Make sure the channel can be quoted from.
        channel = message.channel
        if not isinstance(channel, TextChannel | Thread):
            await ctx.message.reply("😳 I can't quote that.")
            return

        # Make sure the quoter has read permissions in the channel.
        quoter = ctx.author
        if not self.user_can_quote(quoter, channel):
            await ctx.message.reply("😠 You can't quote that.")
            return

        # Build the message content containing the quote metadata.
        lines: List[str] = []
        created_at_ts = int(message.created_at.timestamp())
        quote_ts = f"<t:{created_at_ts}:R>"
        if message.edited_at is not None:
            edited_at_ts = int(message.edited_at.timestamp())
            quote_ts += f" (edited <t:{edited_at_ts}:R>)"
        lines.append(
            f"{ctx.author.mention} {phrasing} {message.author.mention}"
            + f" in {channel.mention} from {quote_ts}:"
        )
        lines.append(message.jump_url)
        content = "\n".join(lines)

        content_to_quote: Optional[str] = message.content

        # Special-case: message is just a media link, which creates a single embed.
        # In this case, omit the quote embed.
        just_media_link = len(message.embeds) == 1 and AUTO_EMBED_PATTERN.match(
            content_to_quote
        )
        if just_media_link:
            content_to_quote = None

        # Build the embed containing the actual quote content, if any.
        quote_embed: Optional[Embed] = None
        if content_to_quote:
            quote_embed = Embed(
                description=content_to_quote,
            )
            quote_embed.set_author(
                name=str(message.author),
                icon_url=message.author.display_avatar.url,
            )

        # Send the message with the quote embed attached, if any.
        if quote_embed:
            await ctx.send(
                content, embed=quote_embed, allowed_mentions=allowed_mentions
            )
        else:
            await ctx.send(content, allowed_mentions=allowed_mentions)

        # Account for any attachments/embeds on the original message. We have to send
        # these separately from the quote embed, because the quote embed takes
        # precedence and will stop other attachments/embeds from appearing.
        attachment_urls = [att.url for att in message.attachments]
        embed_urls = [
            embed.url for embed in message.embeds if isinstance(embed.url, str)
        ]
        urls_to_quote: List[str] = attachment_urls + embed_urls
        for url in urls_to_quote:
            await ctx.send(url)

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
