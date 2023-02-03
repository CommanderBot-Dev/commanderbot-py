from dataclasses import dataclass
from typing import Callable, Optional, Tuple, Union

from discord import Client, Embed, Message, TextChannel, Thread

from commanderbot.lib.allowed_mentions import AllowedMentions
from commanderbot.lib.color import Color
from commanderbot.lib.constants import (
    MAX_EMBED_DESCRIPTION_LENGTH,
    MAX_EMBED_TITLE_LENGTH,
)
from commanderbot.lib.from_data_mixin import FromDataMixin
from commanderbot.lib.responsive_exception import ResponsiveException
from commanderbot.lib.types import ChannelID
from commanderbot.lib.utils import (
    sanitize_stacktrace,
    send_message_or_file,
    str_to_file,
)

__all__ = ("LogOptions",)


@dataclass
class LogOptions(FromDataMixin):
    """
    Data container for various log options.

    Attributes
    ----------
    channel
        The ID of the channel to log in.
    stacktrace
        Whether to print error stacktraces.
    emoji
        The emoji used to represent the type of message.
    color
        The color used to represent the type of message.
    allowed_mentions
        The types of mentions allowed in log messages. Unless otherwise specified, all
        mentions will be suppressed.
    """

    channel: ChannelID

    stacktrace: Optional[bool] = None
    emoji: Optional[str] = None
    color: Optional[Color] = None

    allowed_mentions: Optional[AllowedMentions] = None

    # @overrides FromDataMixin
    @classmethod
    def try_from_data(cls, data):
        if isinstance(data, int):
            return cls(channel=data)
        elif isinstance(data, dict):
            color = Color.from_field_optional(data, "color")
            allowed_mentions = AllowedMentions.from_field_optional(
                data, "allowed_mentions"
            )
            return cls(
                channel=data["channel"],
                stacktrace=data.get("stacktrace"),
                emoji=data.get("emoji"),
                color=color,
                allowed_mentions=allowed_mentions,
            )

    async def _require_channel(self, client: Client) -> Union[TextChannel, Thread]:
        if channel := client.get_channel(self.channel):
            if isinstance(channel, Union[TextChannel, Thread]):
                return channel
            raise ResponsiveException(f"Resolved invalid log channel: `{channel}`")
        raise ResponsiveException(
            f"Failed to resolve log channel with ID `{self.channel}`"
        )

    def _format_embed_title(self, title: str) -> str:
        title = self._prepend_emoji(title)
        if len(title) > MAX_EMBED_TITLE_LENGTH:
            return f"{title[:253]}..."
        return title

    def _prepend_emoji(self, content: str) -> str:
        if self.emoji:
            return f"{self.emoji} {content}"
        return content

    async def send(
        self,
        client: Client,
        content: str,
        *,
        file_callback: Optional[Callable[[], Tuple[str, str, str]]] = None,
        allowed_mentions: Optional[AllowedMentions] = None,
    ) -> Message:
        """
        Sends a log message to the configured log channel.
        If the message is too big, it will be sent as a file instead.
        """
        log_channel = await self._require_channel(client)
        formatted_content = self._prepend_emoji(content)
        file_callback = file_callback or (lambda: ("", formatted_content, "error.txt"))
        allowed_mentions = (
            allowed_mentions or self.allowed_mentions or AllowedMentions.none()
        )

        # Attempt to send the log message to the log channel.
        try:
            return await send_message_or_file(
                log_channel,
                formatted_content,
                file_callback=file_callback,
                allowed_mentions=allowed_mentions,
            )

        # If it fails, attempt to send a second message saying why. Keep this one short
        # in case the first message failed due to length.
        except Exception as error:
            formatted_content = self._prepend_emoji(
                f"Failed to log a message with length `{len(formatted_content)}`"
                + f" due to:\n```{error}```"
            )
            await log_channel.send(formatted_content)
            raise

    async def send_embed(
        self,
        client: Client,
        title: str,
        description: str,
        *,
        file_callback: Optional[Callable[[], Tuple[str, str, str, str]]] = None,
        allowed_mentions: Optional[AllowedMentions] = None,
    ) -> Message:
        """
        Sends a log message in an embed to the configured log channel.
        If the embed's description is too big, the file callback will be
        used to construct an embed looking message with an attached file.
        """
        log_channel = await self._require_channel(client)
        color = self.color or Color.mcc_blue()
        file_callback = file_callback or (lambda: (title, "", description, "error.txt"))
        allowed_mentions = (
            allowed_mentions or self.allowed_mentions or AllowedMentions.none()
        )

        # Attempt to send the log embed to the log channel.
        try:
            # Send the embed if the description fits
            if len(description) <= MAX_EMBED_DESCRIPTION_LENGTH:
                return await log_channel.send(
                    embed=Embed(
                        title=self._format_embed_title(title),
                        description=description,
                        color=color,
                    ),
                    allowed_mentions=allowed_mentions,
                )

            # Otherwise, send an alternative message using the file callback
            alt_title, alt_description, file_content, file_name = file_callback()
            file = str_to_file(file_content, file_name)
            return await log_channel.send(
                f"> **{self._prepend_emoji(alt_title)}**\n> {alt_description}",
                file=file,
                allowed_mentions=allowed_mentions,
            )

        # If it fails, attempt to send a second embed saying why. Keep this one short
        # in case the first embed failed due to length.
        except Exception as error:
            logging_error_embed = Embed(
                title=self._format_embed_title(
                    f"Failed to log a {len(description)} character message"
                ),
                description=f"```{error}```",
                color=self.color or Color.mcc_blue(),
            )
            await log_channel.send(embed=logging_error_embed)
            raise

    def format_channel_name(self, client: Client) -> str:
        if channel := client.get_channel(self.channel):
            if isinstance(channel, Union[TextChannel, Thread]):
                return channel.mention
            return f"Invalid channel `{channel}`"
        return f"Unknown channel `{self.channel}`"

    def formate_error_codeblock(self, error: Exception) -> str:
        error_content = self._formate_error_content(error)
        return f"```python\n{error_content}\n```"

    def _formate_error_content(self, error: Exception) -> str:
        if self.stacktrace:
            return sanitize_stacktrace(error)
        return str(error)

    def format_settings(self) -> str:
        return f"```{repr(self)}```"
