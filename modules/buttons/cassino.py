import discord
import wavelink

from modules.globals import config
from modules.player.cassino import CassinoPlayer


class CassinoSelect(discord.ui.Select):
    def __init__(
        self,
    ):
        options = [
            discord.SelectOption(label="Slots", value="slots", description="Play Slots"),
            #discord.SelectOption(label="Blackjack", value="blackjack", description="Play Blackjack"),
            #discord.SelectOption(label="Roulette", value="roulette", description="Play Roulette"),
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

class CassinoButton(discord.ui.Button):
    def __init__(
        self,
        label: str,
        action: str,
        row: int | None = None,
        style: discord.ButtonStyle | None = discord.ButtonStyle.secondary,
    ):
        """
        Initializes the MusicButton with specific properties.
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
            row=row,
        )

    def bet_change_style(self, style):
        for item in self.view.children:
            if isinstance(item, CassinoButton) and item.style == discord.ButtonStyle.green:
                item.style = discord.ButtonStyle.grey
        self.style = style

    async def callback(self, interaction: discord.Interaction):
        """
        The asynchronous callback executed when the button is clicked.
        - interaction: The interaction instance associated with the button click.
        """
        if interaction.user.id != self.view.member.id:
            await interaction.response.send_message("This is not your cassino!", ephemeral=True)
            return

        if self.action.startswith("bet"):
            await self.bet(interaction)
        elif self.action == "spin":
            await self.spin(interaction)
        elif self.action == "back":
            await self.back(interaction)
        elif self.action == "prizes":
            await self.prizes(interaction)
        elif self.action == "increase_bet":
            await self.increase_bet(interaction)
        elif self.action == "decrease_bet":
            await self.decrease_bet(interaction)

    async def bet(self, interaction: discord.Interaction):
        amount = int(self.action.split("_")[1])
        if self.view.cassino_player.db_player.balance < amount:
            await interaction.response.send_message("You don't have enough money to bet that amount!", ephemeral=True)
            return
        self.view.cassino_player.bet = amount
        self.bet_change_style(discord.ButtonStyle.green)
        await interaction.response.edit_message(view=self.view)

    async def spin(self, interaction: discord.Interaction):
        if self.view.cassino_player.bet > self.view.cassino_player.db_player.balance:
            await interaction.response.send_message("You don't have enough money to bet that amount!", ephemeral=True)
            return
        machine_result = self.view.slot_machine.spin()    
        prize = await self.view.slot_machine.calculate_prize(machine_result, self.view.cassino_player.bet)

        content = " ".join(machine_result)
        if prize != 0:
            self.view.cassino_player.db_player.balance += prize
            self.view.cassino_player.db_player.money_won += prize
            self.view.cassino_player.db_player.slot_wins += prize
            content += f"\nYou won ${prize}!"
        else:
            self.view.cassino_player.db_player.money_lost += self.view.cassino_player.bet
            content += "\nYou lost!"
        self.view.cassino_player.db_player.balance -= self.view.cassino_player.bet
        content += f"\nYour balance is now ${self.view.cassino_player.db_player.balance}"
        await self.view.cassino_player.update(self.view.cassino_player.db_player)
        await interaction.response.edit_message(content=content, view=self.view)

    async def prizes(self, interaction: discord.Interaction):
        table_data = self.view.slot_machine.display_prizes()
        await interaction.response.send_message(table_data, ephemeral=True)

    async def back(self, interaction: discord.Interaction):
        self.view.prepare_menu()
        await interaction.response.edit_message(content=None, view=self.view)

    async def increase_bet(self, interaction: discord.Interaction):
        self.view.bet_multiplier += 1
        self.view.cassino_player.bet *= 10
        await self.view.prepare_slots()
        await interaction.response.edit_message(view=self.view)

    async def decrease_bet(self, interaction: discord.Interaction):
        if self.view.bet_multiplier == 1:
            await interaction.response.send_message("You can't bet less than $10!", ephemeral=True)
            return
        self.view.bet_multiplier -= 1
        self.view.cassino_player.bet /= 10
        await self.view.prepare_slots()
        await interaction.response.edit_message(view=self.view)