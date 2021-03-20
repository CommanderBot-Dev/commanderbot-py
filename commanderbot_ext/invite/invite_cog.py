from typing import Optional, Tuple

from commanderbot_lib import checks
from commanderbot_lib.logging import Logger, get_clogger
from discord import Message
from discord.ext.commands import Bot, Cog, Context, command, group

from commanderbot_ext.invite.invite_options import InviteOptions
from commanderbot_ext.invite.invite_state import InviteState

# Split into invite name / arg
def split(args: str) -> Tuple[str, str]:
    words = args.split(" ")
    return (" ".join(words[:-1]), words[-1])


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

    @command(name="invite")
    async def cmd_invite(self, ctx: Context, *, invite: str):
        await self.state.show_invite(ctx, invite)

    @group(name="invites")
    async def cmd_invites(self, ctx: Context):
        if not ctx.invoked_subcommand:
            await self.state.list_invites(ctx)

    @cmd_invites.command(name="add")
    @checks.is_administrator()
    async def cmd_add(self, ctx: Context, link: str):
        await self.state.add_invite(ctx, link)

    @cmd_invites.command(name="update", usage="<name> <link>")
    @checks.is_administrator()
    async def cmd_update(self, ctx: Context, *, args: str):
        name, link = split(args)
        await self.state.update_invite(ctx, name, link)

    @cmd_invites.command(name="remove")
    async def cmd_remove(self, ctx: Context, *, name: str):
        await self.state.remove_invite(ctx, name)

    @cmd_invites.command(name="details")
    async def cmd_details(self, ctx: Context, *, name: str):
        await self.state.details(ctx, name)

    @cmd_invites.group(name="tag")
    @checks.is_administrator()
    async def cmd_tag(self, ctx: Context):
        if not ctx.invoked_subcommand:
            await ctx.send_help(self.cmd_tag)

    ## @@ faq tag

    @cmd_tag.command(name="add", usage="<name> <tag>")
    async def cmd_tag_add(self, ctx: Context, *, args: str):
        name, tag = split(args)
        await self.state.add_tag(ctx, name, tag)

    @cmd_tag.command(name="remove", usage="<name> <tag>")
    async def cmd_tag_remove(self, ctx: Context, *, args: str):
        name, tag = split(args)
        await self.state.remove_tag(ctx, name, tag)
