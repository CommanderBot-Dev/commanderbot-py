import asyncio
from enum import Enum
from typing import Optional

import discord
from discord import ButtonStyle, Interaction, Member, Message, Reaction, WebhookMessage
from discord.ext.commands import Bot, Context
from discord.ui import Button, View, button

from commanderbot.lib import AllowedMentions

__all__ = (
    "ConfirmationResult",
    "confirm_with_reaction",
    "confirm_with_buttons",
)


class ConfirmationResult(Enum):
    YES = "yes"
    NO = "no"
    NO_RESPONSE = "timeout"


async def confirm_with_reaction(
    bot: Bot,
    ctx: Context,
    content: str,
    timeout: float = 60.0,
    reaction_yes: str = "✅",
    reaction_no: str = "❌",
) -> ConfirmationResult:
    """
    Ask a user to confirm an action via emoji reaction.

    The `bot` will send a reply to the message contained within `ctx`, composed of the
    given `content`. It wait for up to `timeout` seconds for a "yes" or "no" response,
    in the form of an emoji reaction. If no response is received, the answer "no" will
    be assumed.
    """

    # Build and send a confirmation message.
    conf_message: Message = await ctx.message.reply(
        content,
        allowed_mentions=AllowedMentions.only_replies(),
    )

    # Have the bot pre-fill the possible choices for convenience.
    await conf_message.add_reaction(reaction_yes)
    await conf_message.add_reaction(reaction_no)

    # Define a callback to listen for a reaction to the confirmation message.
    def reacted_to_conf_message(reaction: Reaction, user: Member):
        return (
            reaction.message == conf_message
            and user == ctx.author
            and str(reaction.emoji) in (reaction_yes, reaction_no)
        )

    # Attempt to wait for a reaction to the confirmation message.
    try:
        conf_reaction, _ = await bot.wait_for(
            "reaction_add", timeout=timeout, check=reacted_to_conf_message
        )

    # If an appropriate reaction is not received soon enough, assume "no."
    except asyncio.TimeoutError:
        await conf_message.remove_reaction(reaction_yes, bot.user)
        await conf_message.remove_reaction(reaction_no, bot.user)
        return ConfirmationResult.NO_RESPONSE

    # Otherwise, check which reaction was applied.
    else:
        assert isinstance(conf_reaction, Reaction)
        # Check if the response is a "yes."
        if str(conf_reaction.emoji) == reaction_yes:
            await conf_message.remove_reaction(reaction_no, bot.user)
            return ConfirmationResult.YES

    # If we get this far, the answer is an explicit "no."
    await conf_message.remove_reaction(reaction_yes, bot.user)
    return ConfirmationResult.NO


class ConfirmView(View):
    def __init__(
        self,
        original_interaction: Interaction,
        timeout: int = 180,
    ):
        self.original_interaction = original_interaction
        self.result = ConfirmationResult.NO_RESPONSE
        self.followup_message: Optional[WebhookMessage] = None
        super().__init__(timeout=timeout)

    @button(label="Yes", style=ButtonStyle.green)
    async def yes_callback(self, interaction: Interaction, button: Button):
        self.result = ConfirmationResult.YES
        # Run `_on_confirm()` before deferring so the buttons and view doesn't get re-enabled for a short time
        await self._on_confirm(button)
        # Defer the interaction (Mostly to prevent exceptions)
        await interaction.response.defer()

    @button(label="No", style=ButtonStyle.red)
    async def no_callback(self, interaction: Interaction, button: Button):
        self.result = ConfirmationResult.NO
        # Run `_on_confirm()` before deferring so the buttons and view doesn't get re-enabled for a short time
        await self._on_confirm(button)
        # Defer the interaction (Mostly to prevent exceptions)
        await interaction.response.defer()

    async def interaction_check(self, interaction: Interaction) -> bool:
        # Only allow the user, who this view is for, to interact with it
        if self.original_interaction.user != interaction.user:
            await interaction.response.send_message(
                "😠 This confirmation dialog isn't for you!", ephemeral=True
            )
            return False
        return True

    async def on_timeout(self):
        # Disable all buttons and set their color to gray
        for item in self.children:
            assert isinstance(item, Button)
            item.style = ButtonStyle.gray
            item.disabled = True

        # Edit the view
        assert self.followup_message
        await self.followup_message.edit(view=self)

    async def _on_confirm(self, button: Button):
        # Stop accepting inputs
        self.stop()

        # Remove all buttons except for the one interacted with
        for item in self.children[:]:
            assert isinstance(item, Button)
            if item is not button:
                self.remove_item(item)

        # Disable the button that was interacted with
        button.disabled = True

        # Edit the view
        assert self.followup_message
        await self.followup_message.edit(view=self)


async def confirm_with_buttons(
    interaction: Interaction,
    content: str,
    *,
    timeout: int = 60,
    ephemeral=True,
    allowed_mentions: discord.AllowedMentions = discord.AllowedMentions.none()
):
    """
    Ask a user to confirm an action via a `discord.ui.View` with buttons.

    A response will be sent as a followup message to `interaction` composed of the
    given `content`. The view will wait for up to `timeout` seconds for a "yes" or
    "no" response. If no response is received, "no response" will be returned.
    """

    # Create the view and send it as a followup
    view = ConfirmView(interaction, timeout)
    view.followup_message = await interaction.followup.send(
        content, view=view, ephemeral=ephemeral, allowed_mentions=allowed_mentions
    )

    # Wait for the view to have an interaction or a timeout
    await view.wait()

    # Return the result
    return view.result
