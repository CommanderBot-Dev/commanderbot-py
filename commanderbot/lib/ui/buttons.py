from typing import Optional

from discord import Message, Interaction, ButtonStyle, ui
from discord.ext.commands import Context


class DeleteMessageButton(ui.View):
    def __init__(self, ctx: Context, *, timeout: Optional[float] = 5):
        self.ctx: Context = ctx
        self.to_delete: list[Message] = list()
        super().__init__(timeout=timeout)

    @ui.button(label="Delete", emoji="🗑️", style=ButtonStyle.danger)
    async def delete_message(self, interaction: Interaction, button: ui.Button):
        if interaction.user != self.ctx.author:
            return

        # If this view's interation detection isn't explicitly stopped, 'on_timeout()' might 
        # try to edit a deleted message. The timeout is also useless once we press the button.
        self.stop()

        # Delete the messages we added to this view
        for msg in self.to_delete:
            try:
                await msg.delete()
            except:
                pass

        # Delete the message that ran the command
        try:
            await self.ctx.message.delete()
        except:
            pass

    # Since this view should be added to the last message in 'self.to_delete',
    # We only need to edit the view on the last one
    async def on_timeout(self):
        try:
            await self.to_delete[-1].edit(view=None)
        except:
            pass
