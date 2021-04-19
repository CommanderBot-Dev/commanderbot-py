import asyncio
from enum import Enum

from discord import Member, Message, Reaction
from discord.ext.commands import Bot, Context


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
    conf_message: Message = await ctx.reply(content)

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
