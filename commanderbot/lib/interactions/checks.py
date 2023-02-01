from discord import Interaction, Member, app_commands

import commanderbot.lib.utils as utils


def is_owner():
    def predicate(interaction: Interaction) -> bool:
        return utils.is_owner(interaction.client, interaction.user)

    return app_commands.check(predicate)


def is_administrator():
    return app_commands.checks.has_permissions(administrator=True)


def is_guild_admin_or_bot_owner():
    def predicate(interaction: Interaction) -> bool:
        # Check if the interaction user is a bot owner
        if utils.is_owner(interaction.client, interaction.user):
            return True

        # Check if the interaction user is a guild admin
        if interaction.guild and isinstance(interaction.user, Member):
            return interaction.user.guild_permissions.administrator

        return False

    return app_commands.check(predicate)
