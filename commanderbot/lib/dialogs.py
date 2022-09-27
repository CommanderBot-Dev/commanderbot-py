import asyncio
from enum import Enum
from typing import Optional, Union

from discord import (
    ButtonStyle,
    Interaction,
    Member,
    Message,
    Reaction,
    User,
    WebhookMessage,
)
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
    def __init__(self, user: Union[Member, User], timeout: int = 180):
        self.user: Union[Member, User] = user
        self.response: Optional[WebhookMessage] = None
        self.result: ConfirmationResult = ConfirmationResult.NO_RESPONSE
        super().__init__(timeout=timeout)

    @button(label="Yes", style=ButtonStyle.green)
    async def yes_callback(self, interaction: Interaction, button: Button):
        await interaction.response.defer()
        self.result = ConfirmationResult.YES
        await self._on_confirm(button)

    @button(label="No", style=ButtonStyle.red)
    async def no_callback(self, interaction: Interaction, button: Button):
        await interaction.response.defer()
        self.result = ConfirmationResult.NO
        await self._on_confirm(button)

    async def interaction_check(self, interaction: Interaction) -> bool:
        return self.user == interaction.user

    async def on_timeout(self):
        # Disable all buttons and set their color to gray
        for item in self.children:
            assert isinstance(item, Button)
            item.style = ButtonStyle.gray
            item.disabled = True

        # Edit the view
        assert self.response
        await self.response.edit(view=self)

    async def _on_confirm(self, button: Optional[Button] = None):
        # Stop accepting inputs
        self.stop()

        # Remove all buttons except for the one interacted with
        # The button was was inteacted with will be disabled
        for item in self.children[:]:
            assert isinstance(item, Button)
            if item is not button:
                self.remove_item(item)
            else:
                item.disabled = True

        # Edit the view
        assert self.response
        await self.response.edit(view=self)


async def confirm_with_buttons(
    interaction: Interaction, content: str, timeout: int = 60
):
    """
    Ask a user to confirm an action via a `discord.ui.View` with buttons.

    A response will be sent as a followup message to `interaction` composed of the 
    given `content`. The view will wait for up to `timeout` seconds for a "yes" or 
    "no" response. If no response is received, "no response" will be returned.
    """

    # Defer the response if necessary so the followups work correctly
    if not interaction.response.is_done():
        await interaction.response.defer()

    # Create the view and send it as a followup
    view = ConfirmView(interaction.user, timeout)
    view.response = await interaction.followup.send(content, view=view, ephemeral=True)

    # Wait for the view to have an interaction or a timeout
    await view.wait()

    # Return the result
    return view.result
