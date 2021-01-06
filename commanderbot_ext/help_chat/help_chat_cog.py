from typing import Optional

from commanderbot_ext.help_chat.help_chat_options import HelpChatOptions
from commanderbot_ext.help_chat.help_chat_state import HelpChatState
from commanderbot_lib import checks
from commanderbot_lib.logging import Logger, get_clogger
from discord import Message, TextChannel
from discord.ext.commands import Bot, Cog, Context, group
from discord.ext.commands.converter import Greedy


# TODO Try to cut-down on the amount of boilerplate by sub-classing `Cog`. #refactor
class HelpChatCog(Cog, name="commanderbot_ext.help_chat"):
    def __init__(self, bot: Bot, **options):
        self.bot: Bot = bot
        self.options: HelpChatOptions = HelpChatOptions(**options)
        self._log: Logger = get_clogger(self)
        self._state: Optional[HelpChatState] = None

    @property
    def state(self) -> HelpChatState:
        if not self._state:
            raise ValueError("Tried to access state before it was created")
        return self._state

    # @@ LISTENERS

    @Cog.listener()
    async def on_ready(self):
        if not self._state:
            self._state = HelpChatState(self.bot, self, self.options)
            await self._state.async_init()
        await self.state.on_ready()

    @Cog.listener()
    async def on_message(self, message: Message):
        await self.state.on_message(message)

    # @@ COMMANDS

    @group(name="helpchat", aliases=["hc"])
    async def cmd_helpchat(self, ctx: Context):
        if not ctx.invoked_subcommand:
            await ctx.send_help(self.cmd_helpchat)

    # @@ helpchat channels

    @cmd_helpchat.group(name="channels", aliases=["ch"])
    @checks.is_administrator()
    async def cmd_helpchat_channels(self, ctx: Context):
        if not ctx.invoked_subcommand:
            await ctx.send_help(self.cmd_helpchat_channels)

    @cmd_helpchat_channels.command(name="show")
    @checks.is_administrator()
    async def cmd_helpchat_channels_show(self, ctx: Context):
        await self.state.show_channels(ctx)

    @cmd_helpchat_channels.command(name="list")
    @checks.is_administrator()
    async def cmd_helpchat_channels_list(self, ctx: Context):
        await self.state.list_channels(ctx)

    @cmd_helpchat_channels.command(name="add")
    @checks.is_administrator()
    async def cmd_helpchat_channels_add(self, ctx: Context, channels: Greedy[TextChannel]):
        await self.state.add_channels(ctx, channels)

    @cmd_helpchat_channels.command(name="remove")
    @checks.is_administrator()
    async def cmd_helpchat_channels_remove(self, ctx: Context, channels: Greedy[TextChannel]):
        await self.state.remove_channels(ctx, channels)
