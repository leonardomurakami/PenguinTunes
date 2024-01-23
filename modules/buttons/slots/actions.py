from abc import ABC, abstractmethod

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

    def update_balance(self, prize, bet):
        player = self.view.cassino_player.db_player
        player.balance += prize - bet
        player.money_won += max(prize, 0)
        player.money_lost += bet
        if prize > 0:
            player.slot_wins += prize


class SpinAction(ActionCommand):
    def __init__(self, view):
        self.view = view

    async def execute(self, button: discord.ui.Button, interaction: discord.Interaction):
        if not await self.ensure_bet(interaction):
            return
        if not await self.ensure_minimum_balance(interaction, self.view.bet):
            return
        
        machine_result = self.view.slot_machine.spin()
        prize = await self.view.slot_machine.calculate_prize(machine_result, self.view.bet)
        self.update_balance(prize, self.view.bet)
        
        content = " ".join(machine_result)
        content += f"\nYou {'won' if prize > 0 else 'lost'} ${prize if prize > 0 else self.view.bet}!"
        content += f"\nYour balance is now ${self.view.cassino_player.db_player.balance}"
        
        await self.view.cassino_player.update(self.view.cassino_player.db_player)
        await interaction.response.edit_message(content=content, view=self.view)


class SlotsBetAction(ActionCommand):
    def __init__(self, view, amount):
        self.view = view
        self.amount = amount

    async def execute(self, button: discord.ui.Button, interaction: discord.Interaction):
        if not await self.ensure_minimum_balance(interaction, self.amount):
            return
        self.view.bet = self.amount
        self.bet_change_style(button, discord.ButtonStyle.green)
        await interaction.response.edit_message(view=self.view)
        
    def bet_change_style(self, button: discord.ui.Button, style):
        for item in self.view.children:
            if isinstance(item, discord.ui.Button) and item.style == discord.ButtonStyle.green:
                item.style = discord.ButtonStyle.grey
        button.style = style


class DisplayPrizesAction(ActionCommand):
    def __init__(self, view):
        self.view = view

    async def execute(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.send_message(self.view.slot_machine.display_prizes(), ephemeral=True)


class SlotsReturnAction(ActionCommand):
    def __init__(self, view):
        self.view = view

    async def execute(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.view.prepare_menu()
        await interaction.response.edit_message(content=None, view=self.view)


class SlotsModifyBetAction(ActionCommand):
    def __init__(self, view, amount):
        self.view = view
        self.amount = amount

    async def execute(self, button: discord.ui.Button, interaction: discord.Interaction):
        if self.view.bet_multiplier == 1 and self.amount == -1:
            await interaction.response.send_message("You can't bet less than $10!", ephemeral=True)
            return
        self.view.bet_multiplier += self.amount
        self.view.bet = None
        await self.view.prepare_slots()
        await interaction.response.edit_message(view=self.view)