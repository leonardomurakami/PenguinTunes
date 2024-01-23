from abc import ABC, abstractmethod
from io import BytesIO
import logging
from PIL import Image, ImageDraw, ImageFont
from modules.globals import config

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
        player.balance += prize
        player.money_won += max(prize, 0)
        player.money_lost += bet if prize > 0 else 0
        player.roulette_wins += prize if prize > 0 else 0

    async def spin(self, interaction: discord.Interaction, condition: bool, prize_modifier: int):
        if not await self.ensure_bet(interaction):
            return
        if not await self.ensure_minimum_balance(interaction, self.view.bet):
            return
        
        if condition:
            prize = self.view.bet*prize_modifier
        else:
            prize = -self.view.bet

        self.update_balance(prize, self.view.bet)
        self.view.bet = None

        content = self.display(prize, self.view.roulette.winning_number)
        await self.view.cassino_player.update(self.view.cassino_player.db_player)
        await self.view.prepare_roulette()
        await interaction.response.edit_message(content=content, view=self.view)

    def display(self, prize, number):
        if prize > 0:
            content = f"You won ${prize}!"
        elif prize < 0:
            content = f"You lost ${-prize}!"
        content += f"\nThe winning number was {number}!"
        return content

class RouletteBetAction(ActionCommand):
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


class RouletteReturnAction(ActionCommand):
    def __init__(self, view):
        self.view = view

    async def execute(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.view.prepare_menu()
        await interaction.response.edit_message(content=None, view=self.view)


class RouletteModifyBetAction(ActionCommand):
    def __init__(self, view, amount):
        self.view = view
        self.amount = amount

    async def execute(self, button: discord.ui.Button, interaction: discord.Interaction):
        if self.view.bet_multiplier == 1 and self.amount == -1:
            await interaction.response.send_message("You can't bet less than $10!", ephemeral=True)
            return
        self.view.bet_multiplier += self.amount
        self.view.bet = None
        await self.view.prepare_roulette()
        await interaction.response.edit_message(view=self.view)

    
class BetRedAction(ActionCommand):
    def __init__(self, view):
        self.view = view

    async def execute(self, button: discord.ui.Button, interaction: discord.Interaction):
        await self.spin(interaction, self.view.roulette.is_red, self.view.roulette.payout['red'])


class BetBlackAction(ActionCommand):
    def __init__(self, view):
        self.view = view

    async def execute(self, button: discord.ui.Button, interaction: discord.Interaction):
        await self.spin(interaction, self.view.roulette.is_black, self.view.roulette.payout['black'])


class BetEvenAction(ActionCommand):
    def __init__(self, view):
        self.view = view

    async def execute(self, button: discord.ui.Button, interaction: discord.Interaction):
        await self.spin(interaction, self.view.roulette.is_even, self.view.roulette.payout['even'])


class BetOddAction(ActionCommand):
    def __init__(self, view):
        self.view = view

    async def execute(self, button: discord.ui.Button, interaction: discord.Interaction):
        await self.spin(interaction, self.view.roulette.is_odd, self.view.roulette.payout['odd'])


class Bet1st12Action(ActionCommand):
    def __init__(self, view):
        self.view = view

    async def execute(self, button: discord.ui.Button, interaction: discord.Interaction):
        await self.spin(interaction, self.view.roulette.is_1st_12, self.view.roulette.payout['1st_12'])


class Bet2nd12Action(ActionCommand):
    def __init__(self, view):
        self.view = view

    async def execute(self, button: discord.ui.Button, interaction: discord.Interaction):
        await self.spin(interaction, self.view.roulette.is_2nd_12, self.view.roulette.payout['2nd_12'])


class Bet3rd12Action(ActionCommand):
    def __init__(self, view):
        self.view = view

    async def execute(self, button: discord.ui.Button, interaction: discord.Interaction): 
        await self.spin(interaction, self.view.roulette.is_3rd_12, self.view.roulette.payout['3rd_12'])


class Bet1to18Action(ActionCommand):
    def __init__(self, view):
        self.view = view
    
    async def execute(self, button: discord.ui.Button, interaction: discord.Interaction): 
        await self.spin(interaction, self.view.roulette.is_1_to_18, self.view.roulette.payout['1_to_18'])


class Bet19to36Action(ActionCommand):
    def __init__(self, view):
        self.view = view
    
    async def execute(self, button: discord.ui.Button, interaction: discord.Interaction): 
        await self.spin(interaction, self.view.roulette.is_19_to_36, self.view.roulette.payout['19_to_36'])


class Bet1stRowAction(ActionCommand):
    def __init__(self, view):
        self.view = view
    
    async def execute(self, button: discord.ui.Button, interaction: discord.Interaction): 
        await self.spin(interaction, self.view.roulette.is_first_row, self.view.roulette.payout['1st_row'])


class Bet2ndRowAction(ActionCommand):
    def __init__(self, view):
        self.view = view
    
    async def execute(self, button: discord.ui.Button, interaction: discord.Interaction): 
        await self.spin(interaction, self.view.roulette.is_second_row, self.view.roulette.payout['2nd_row'])


class Bet3rdRowAction(ActionCommand):
    def __init__(self, view):
        self.view = view
    
    async def execute(self, button: discord.ui.Button, interaction: discord.Interaction): 
        await self.spin(interaction, self.view.roulette.is_third_row, self.view.roulette.payout['3rd_row'])


class BetGreenAction(ActionCommand):
    def __init__(self, view):
        self.view = view
    
    async def execute(self, button: discord.ui.Button, interaction: discord.Interaction): 
        await self.spin(interaction, self.view.roulette.is_green, self.view.roulette.payout['green'])


class GetRouletteTable(ActionCommand):
    def __init__(self, view) -> None:
        self.view = view

    async def execute(self, button: discord.ui.Button, interaction: discord.Interaction):
        try:
            base_image = Image.open(config.fun.roulette_table)
            final_buffer = BytesIO()
            base_image.save(final_buffer, "PNG")
            final_buffer.seek(0)
            await interaction.response.send_message(file=discord.File(final_buffer, "roulette_table.png"), ephemeral=True)
        except Exception as e:
            logging.error(f"Failed to send image: {str(e)}")