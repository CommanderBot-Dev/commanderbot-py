from typing import Optional

from commanderbot_lib import checks
from commanderbot_lib.logging import Logger, get_clogger
from discord import Message
from discord.ext.commands import Bot, Cog, Context, command, group

from commanderbot_ext.faq.faq_options import FaqOptions
from commanderbot_ext.faq.faq_state import FaqState


# TODO Try to cut-down on the amount of boilerplate by sub-classing `Cog`. #refactor
class FaqCog(Cog, name="commanderbot_ext.faq"):
    def __init__(self, bot: Bot, **options):
        self.bot: Bot = bot
        self.options: FaqOptions = FaqOptions(**options)
        self._log: Logger = get_clogger(self)
        self._state: Optional[FaqState] = None

    @property
    def state(self) -> FaqState:
        if not self._state:
            raise ValueError("Tried to access state before it was created")
        return self._state

    # @@ LISTENERS

    @Cog.listener()
    async def on_ready(self):
        if not self._state:
            self._state = FaqState(self.bot, self, self.options)
            await self._state.async_init()
        await self.state.on_ready()

    @Cog.listener()
    async def on_message(self, message: Message):
        await self.state.on_message(message)

    # @@ COMMANDS

    @command(name="faqs")
    async def cmd_faqs(self, ctx: Context):
        await self.state.list_faqs(ctx)

    @group(name="faq")
    async def cmd_faq(self, ctx: Context):
        if not ctx.invoked_subcommand:
            await ctx.send_help(self.cmd_faq)

    @cmd_faq.command(name="list")
    async def cmd_faq_list(self, ctx: Context):
        await self.state.list_faqs(ctx)

    @cmd_faq.command(name="show")
    async def cmd_faq_show(self, ctx: Context, faq_query: str):
        await self.state.show_faq(ctx, faq_query)

    @cmd_faq.command(name="details")
    async def cmd_faq_details(self, ctx: Context, faq_query: str):
        await self.state.show_faq_details(ctx, faq_query)

    # @@ faq add

    @cmd_faq.group(name="add")
    @checks.is_administrator()
    async def cmd_faq_add(self, ctx: Context):
        if not ctx.invoked_subcommand:
            await ctx.send_help(self.cmd_faq_add)

    @cmd_faq_add.command(name="message")
    @checks.is_administrator()
    async def cmd_faq_add_message(self, ctx: Context, faq_name: str, message: Message):
        await self.state.add_faq(ctx, faq_name, message, message.content)

    @cmd_faq_add.command(name="content")
    @checks.is_administrator()
    async def cmd_faq_add_content(self, ctx: Context, faq_name: str, *, content: str):
        await self.state.add_faq(ctx, faq_name, ctx.message, content)

    # @@ faq remove

    @cmd_faq.command(name="remove")
    @checks.is_administrator()
    async def cmd_faq_remove(self, ctx: Context, faq_name: str):
        await self.state.remove_faq(ctx, faq_name)

    # @@ faq update

    @cmd_faq.group(name="update")
    @checks.is_administrator()
    async def cmd_faq_update(self, ctx: Context):
        if not ctx.invoked_subcommand:
            await ctx.send_help(self.cmd_faq_update)

    @cmd_faq_update.command(name="message")
    @checks.is_administrator()
    async def cmd_faq_update_message(
        self, ctx: Context, faq_name: str, message: Message
    ):
        await self.state.update_faq(ctx, faq_name, message, message.content)

    @cmd_faq_update.command(name="content")
    @checks.is_administrator()
    async def cmd_faq_update_content(
        self, ctx: Context, faq_name: str, *, content: str
    ):
        await self.state.update_faq(ctx, faq_name, ctx.message, content)

    # @@ faq alias

    @cmd_faq.group(name="alias")
    @checks.is_administrator()
    async def cmd_faq_alias(self, ctx: Context):
        if not ctx.invoked_subcommand:
            await ctx.send_help(self.cmd_faq_alias)

    @cmd_faq_alias.command(name="add")
    @checks.is_administrator()
    async def cmd_faq_alias_add(self, ctx: Context, faq_name: str, alias_to_add: str):
        await self.state.add_alias(ctx, faq_name, alias_to_add)

    @cmd_faq_alias.command(name="remove")
    @checks.is_administrator()
    async def cmd_faq_alias_remove(
        self, ctx: Context, faq_name: str, alias_to_remove: str
    ):
        await self.state.remove_alias(ctx, faq_name, alias_to_remove)
