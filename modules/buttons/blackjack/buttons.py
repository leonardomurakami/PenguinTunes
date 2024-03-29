import discord
from modules.buttons.slots.actions import ActionCommand


class BlackjackButton(discord.ui.Button):
    def __init__(
        self,
        label: str,
        action: str,
        disabled: bool = False,
        row: int | None = None,
        style: discord.ButtonStyle | None = discord.ButtonStyle.secondary,
    ):
        """
        Initializes the BlackJackButton with specific properties.
        - player: The `wavelink.Player` instance associated with the button.
        - label: The text label displayed on the button.
        - action: The action to be performed when the button is clicked.
        - row: The row where the button should be placed in the Discord UI.
        - style: The style of the button (color/theme).
        """
        self.action = action
        super().__init__(
            style=style,
            label=label,
            disabled=disabled,
            row=row,
        )

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.view.member.id:
            await interaction.response.send_message("This is not your cassino!", ephemeral=True)
            return
        
        await self.action.execute(button=self, interaction=interaction)

    