from dataclasses import dataclass
from typing import Callable, Optional, Tuple

from discord import Client, Color, Message, TextChannel, Thread

from commanderbot.lib.allowed_mentions import AllowedMentions
from commanderbot.lib.from_data_mixin import FromDataMixin
from commanderbot.lib.responsive_exception import ResponsiveException
from commanderbot.lib.types import ChannelID
from commanderbot.lib.utils import (
    color_from_field_optional,
    sanitize_stacktrace,
    send_message_or_file,
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

    @classmethod
    def try_from_data(cls, data):
        if isinstance(data, int):
            return cls(channel=data)
        elif isinstance(data, dict):
            color = color_from_field_optional(data, "color")
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

    async def send(
        self,
        client: Client,
        content: str,
        *,
        file_callback: Optional[Callable[[], Tuple[str, str, str]]] = None,
        allowed_mentions: Optional[AllowedMentions] = None,
    ) -> Message:
        log_channel = await self.require_channel(client)
        formatted_content = self.format_content(content)

        # Attempt to send the log message to the log channel.
        try:
            file_callback = file_callback or (
                lambda: ("", formatted_content, "error.txt")
            )
            allowed_mentions = (
                allowed_mentions or self.allowed_mentions or AllowedMentions.none()
            )
            return await send_message_or_file(
                log_channel,
                formatted_content,
                file_callback=file_callback,
                allowed_mentions=allowed_mentions,
            )

        # If it fails, attempt to send a second message saying why. Keep this one short
        # in case the first message failed due to length.
        except Exception as error:
            formatted_content = self.format_content(
                f"Failed to log a message with length `{len(formatted_content)}`"
                + f" due to:\n```{error}```"
            )
            await log_channel.send(formatted_content)
            raise

    async def require_channel(self, client: Client) -> TextChannel | Thread:
        if channel := client.get_channel(self.channel):
            if isinstance(channel, TextChannel | Thread):
                return channel
            raise ResponsiveException(f"Resolved invalid log channel: `{channel}`")
        raise ResponsiveException(
            f"Failed to resolve log channel with ID `{self.channel}`"
        )

    def format_name(self, client: Client) -> str:
        if channel := client.get_channel(self.channel):
            if isinstance(channel, TextChannel | Thread):
                return channel.mention
            return f"Invalid channel `{channel}`"
        return f"Unknown channel `{self.channel}`"

    def format_codeblock(self) -> str:
        lines = [
            "```python",
            repr(self),
            "```",
        ]
        return "\n".join(lines)

    def format(self, client: Client) -> str:
        name = self.format_name(client)
        codeblock = self.format_codeblock()
        return f"{name}\n{codeblock}"

    def format_content(self, content: str) -> str:
        if self.emoji:
            return f"{self.emoji} {content}"
        else:
            return content

    def formate_error_content(self, error: Exception) -> str:
        if self.stacktrace:
            return sanitize_stacktrace(error)
        return str(error)

    def formate_error_codeblock(self, error: Exception) -> str:
        error_content = self.formate_error_content(error)
        lines = ["```", error_content, "```"]
        return "\n".join(lines)
