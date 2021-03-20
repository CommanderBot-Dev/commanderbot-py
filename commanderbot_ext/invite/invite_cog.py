from typing import Optional

from commanderbot_lib import checks
from commanderbot_lib.logging import Logger, get_clogger
from discord import Message
from discord.ext.commands import Bot, Cog, Context, command, group

from commanderbot_ext.invite.invite_options import InviteOptions
from commanderbot_ext.invite.invite_state import InviteState


class InviteCog(Cog, name="commanderbot_ext.invite"):
    def __init__(self, bot: Bot, **options):
        self.bot: Bot = bot
        self.options: InviteOptions = InviteOptions(**options)
        self._log: Logger = get_clogger(self)
        self._state: Optional[InviteState] = None

    @property
    def state(self) -> InviteState:
        if not self._state:
            raise ValueError("Tried to access state before it was created")
        return self._state

    # @@ LISTENERS

    @Cog.listener()
    async def on_ready(self):
        if not self._state:
            self._state = InviteState(self.bot, self, self.options)
            await self._state.async_init()
        await self.state.on_ready()

    @Cog.listener()
    async def on_message(self, message: Message):
        await self.state.on_message(message)

    # @@ COMMANDS

    @command(name="invites")
    async def cmd_invites(self, ctx: Context):
        await self.state.list_invites(ctx)

    @cmd_invites.command(name="add")
    async def cmd_add(self, ctx: Context, name: str, link: str):
        pass

    @cmd_invites.command(name="remove")
    async def cmd_add(self, ctx: Context, name: str):
        pass

    @cmd_invites.command(name="tag")
    async def cmd_tag(self, ctx: Context):
        pass

    ## @@ faq tag

    @cmd_tag.command(name="add")
    async def cmd_tag_add(self, ctx: Context, name: str, tag: str):
        pass

    @cmd_tag.command(name="remove")
    async def cmd_tag_add(self, ctx: Context, name: str, tag: str):
        pass