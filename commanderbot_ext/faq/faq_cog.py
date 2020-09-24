from commanderbot_ext.faq.faq_options import FaqOptions
from commanderbot_ext.faq.faq_state import FaqState
from commanderbot_lib import checks
from commanderbot_lib.logging import Logger, get_clogger
from discord import Message
from discord.ext.commands import Bot, Cog, Context, group
from discord.ext.commands.help import HelpCommand


# TODO Try to cut-down on the amount of boilerplate by sub-classing `Cog`. #refactor
class FaqCog(Cog, name="commanderbot_ext.faq"):
    def __init__(self, bot: Bot, **options):
        self.bot: Bot = bot
        self.options: FaqOptions = FaqOptions(**options)
        self._log: Logger = get_clogger(self)
        self._state: FaqState = None

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

    @group(name="faq")
    async def cmd_faq(self, ctx: Context):
        if not ctx.invoked_subcommand:
            await ctx.send_help(self.cmd_faq)

    @cmd_faq.command(name="list")
    async def cmd_faq_list(self, ctx: Context):
        await self.state.list_faqs(ctx)

    @cmd_faq.command(name="show")
    async def cmd_faq_show(self, ctx: Context, *, name: str):
        await self.state.show_faq(ctx, name)

    @cmd_faq.command(name="add")
    @checks.is_administrator()
    async def cmd_faq_add(self, ctx: Context, message: Message, *, name: str):
        await self.state.add_faq(ctx, name, message)

    @cmd_faq.command(name="remove")
    @checks.is_administrator()
    async def cmd_faq_remove(self, ctx: Context, *, name: str):
        await self.state.remove_faq(ctx, name)
