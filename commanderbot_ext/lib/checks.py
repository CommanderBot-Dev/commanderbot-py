from discord import Member
from discord.ext import commands

# NOTE See: https://discordpy.readthedocs.io/en/latest/ext/commands/commands.html#checks


def has_guild_permissions(**perms):
    original = commands.has_guild_permissions(**perms).predicate

    async def extended_check(ctx):
        if ctx.guild is None:
            return False
        return await original(ctx)

    return commands.check(extended_check)


def is_owner():
    return commands.is_owner()


def is_administrator():
    return has_guild_permissions(administrator=True)


def is_guild_admin_or_bot_owner():
    return commands.check_any(
        is_administrator(),
        is_owner(),
    )


def guild_only():
    return commands.guild_only()


def member_only():
    def predicate(ctx: commands.Context) -> bool:
        return isinstance(ctx.author, Member)

    return commands.check(predicate)


def any_of(*checks):
    return commands.check_any(*checks)
