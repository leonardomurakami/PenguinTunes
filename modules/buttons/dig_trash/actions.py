from abc import ABC, abstractmethod
import random

import discord


class ActionCommand(ABC):
    @abstractmethod
    async def execute(self, interaction: discord.Interaction):
        pass

    async def ensure_bet(self, interaction: discord.Interaction):
        if not self.view.bet:
            await interaction.response.send_message("You need to bet something!", ephemeral=True)
            return False
        return True

    async def ensure_minimum_balance(self, interaction: discord.Interaction, required_balance):
        if self.view.cassino_player.db_player.balance < required_balance:
            await interaction.response.send_message("You don't have enough money for this action!", ephemeral=True)
            return False
        return True

    async def update_balance(self, prize):
        self.view.cassino_player.db_player.balance += prize
        self.view.cassino_player.db_player.money_won += max(prize, 0)
        self.view.cassino_player.db_player.dig_trash_wins += max(prize, 0)
        await self.view.cassino_player.update(self.view.cassino_player.db_player)


class DigTrashAction(ActionCommand):
    def __init__(self, view):
        self.view = view

    async def execute(self, button: discord.ui.Button, interaction: discord.Interaction): 
        if (roll := random.random()) > 0.80:
            prize = int(1000*random.random())
            await self.update_balance(prize)
            content=f"You found ${prize} in the trash!"
        else:
            content=f"You found nothing in the trash! Keep digging you dirty rat!"
        await interaction.response.edit_message(content=content, view=self.view)


class DigTrashReturnAction(ActionCommand):
    def __init__(self, view):
        self.view = view

    async def execute(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.view.prepare_menu()
        await interaction.response.edit_message(content=None, view=self.view)