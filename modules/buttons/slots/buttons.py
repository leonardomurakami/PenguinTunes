import discord

from modules.buttons.slots.actions import ActionCommand


class SlotButton(discord.ui.Button):
    def __init__(
        self,
        label: str,
        action: ActionCommand,
        row: int = None,
        style: discord.ButtonStyle = discord.ButtonStyle.secondary,
    ):
        self.action = action
        super().__init__(
            style=style,
            label=label,
            row=row,
        )

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.view.member.id:
            await interaction.response.send_message("This is not your cassino!", ephemeral=True)
            return
        
        await self.action.execute(button=self, interaction=interaction)