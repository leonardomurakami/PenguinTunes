import discord
import wavelink

from modules.globals import config
from modules.player.player import CassinoPlayer


class CassinoSelect(discord.ui.Select):
    def __init__(
        self,
    ):
        options = [
            discord.SelectOption(label="Slots", value="slots", description="Play Slots"),
            discord.SelectOption(label="Blackjack", value="blackjack", description="Play Blackjack"),
            discord.SelectOption(label="Roulette", value="roulette", description="Play Roulette"),
            discord.SelectOption(label="Video Poker", value="video_poker", description="Play Video Poker"),
        ]
        super().__init__(
            placeholder="Choose your game...",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, interaction: discord.Interaction):
        """
        The asynchronous callback executed when the button is clicked.
        - interaction: The interaction instance associated with the button click.
        """
        if interaction.user.id != self.view.member.id:
            await interaction.response.send_message("This is not your cassino!", ephemeral=True)
            return
        
        if self.values[0] == "slots":
            await self.slots(interaction)
        elif self.values[0] == "blackjack":
            await self.blackjack(interaction)
        elif self.values[0] == "roulette":
            await self.roulette(interaction)
        elif self.values[0] == "video_poker":
            await self.video_poker(interaction)

    async def slots(self, interaction: discord.Interaction):
        """
        The asynchronous callback executed when the button is clicked.
        - interaction: The interaction instance associated with the button click.
        """
        await self.view.prepare_slots()
        await interaction.response.edit_message(view=self.view)

    async def blackjack(self, interaction: discord.Interaction):
        """
        The asynchronous callback executed when the button is clicked.
        - interaction: The interaction instance associated with the button click.
        """
        await self.view.prepare_blackjack()
        await interaction.response.edit_message(view=self.view)

    async def roulette(self, interaction: discord.Interaction):
        """
        The asynchronous callback executed when the button is clicked.
        - interaction: The interaction instance associated with the button click.
        """
        await self.view.prepare_roulette()
        await interaction.response.edit_message(view=self.view)
    async def video_poker(self, interaction: discord.Interaction):
        """
        The asynchronous callback executed when the button is clicked.
        - interaction: The interaction instance associated with the button click.
        """
        await self.view.prepare_video_poker()
        await interaction.response.edit_message(view=self.view)
