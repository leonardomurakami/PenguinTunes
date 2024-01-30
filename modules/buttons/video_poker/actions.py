import logging
import discord

from abc import ABC, abstractmethod
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from modules.globals import config


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
        await self.view.cassino_player.refresh()
        if self.view.cassino_player.db_player.balance < required_balance:
            await interaction.response.send_message("You don't have enough money for this action!", ephemeral=True)
            return False
        return True

    async def update_balance(self, prize, bet):
        await self.view.cassino_player.refresh()
        player = self.view.cassino_player.db_player
        player.balance += (prize - bet)
        player.money_won += max(prize, 0)
        player.money_lost += bet
        if prize > 0:
            player.video_poker_wins += prize
        await self.view.cassino_player.update(player)

    def disable_bet_buttons(self):
        for item in self.view.children:
            if isinstance(item, discord.ui.Button) and isinstance(item.action, VideoPokerBetAction):
                item.disabled = True

    def enable_bet_buttons(self):
        for item in self.view.children:
            if isinstance(item, discord.ui.Button) and isinstance(item.action, VideoPokerBetAction):
                item.disabled = False

    def disable_start_button(self):
        for item in self.view.children:
            if isinstance(item, discord.ui.Button) and isinstance(item.action, VideoPokerStartAction):
                item.disabled = True
    
    def enable_start_button(self):
        for item in self.view.children:
            if isinstance(item, discord.ui.Button) and isinstance(item.action, VideoPokerStartAction):
                item.disabled = False

    def enable_lock_buttons(self):
        for item in self.view.children:
            if isinstance(item, discord.ui.Button) and isinstance(item.action, LockCardAction):
                item.disabled = False

    def disable_lock_buttons(self):
        for item in self.view.children:
            if isinstance(item, discord.ui.Button) and isinstance(item.action, LockCardAction):
                item.disabled = False

    def enable_redraw_button(self):
        for item in self.view.children:
            if isinstance(item, discord.ui.Button) and isinstance(item.action, RedrawAction):
                item.disabled = False
    
    def disable_redraw_button(self):
        for item in self.view.children:
            if isinstance(item, discord.ui.Button) and isinstance(item.action, RedrawAction):
                item.disabled = True

class VideoPokerBetAction(ActionCommand):
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
            if isinstance(item, discord.ui.Button) and item.style == discord.ButtonStyle.green and isinstance(item.action, VideoPokerBetAction):
                item.style = discord.ButtonStyle.grey
        button.style = style

class VideoPokerStartAction(ActionCommand):
    def __init__(self, view):
        self.view = view

    async def execute(self, button: discord.ui.Button, interaction: discord.Interaction):
        if not await self.ensure_bet(interaction):
            return
        
        self.disable_bet_buttons()
        self.disable_start_button()
        self.enable_lock_buttons()
        self.enable_redraw_button()

        content = f"Your initial hand is: {self.view.cassino_player.display_hand()}"

        await self.update_balance(prize=0, bet=self.view.bet)
        await interaction.response.edit_message(content=content, view=self.view)

class VideoPokerReturnAction(ActionCommand):
    def __init__(self, view):
        self.view = view

    async def execute(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.view.prepare_menu()
        await interaction.response.edit_message(content=None, view=self.view)


class VideoPokerModifyBetAction(ActionCommand):
    def __init__(self, view, amount):
        self.view = view
        self.amount = amount

    async def execute(self, button: discord.ui.Button, interaction: discord.Interaction):
        if self.view.bet_multiplier == 1 and self.amount == -1:
            await interaction.response.send_message("You can't bet less than $10!", ephemeral=True)
            return
        self.view.bet_multiplier += self.amount
        self.view.bet = None
        await self.view.prepare_video_poker()
        await interaction.response.edit_message(view=self.view)

class DisplayHandsAction(ActionCommand):
    def __init__(self, view):
        self.view = view

    async def execute(self, button: discord.ui.Button, interaction: discord.Interaction):
        try:
            base_image = Image.open(config.fun.poker_table)
            final_buffer = BytesIO()
            base_image.save(final_buffer, "PNG")
            final_buffer.seek(0)
            await interaction.response.send_message(file=discord.File(final_buffer, "poker_table.png"), ephemeral=True)
        except Exception as e:
            logging.error(f"Failed to send image: {str(e)}")

class LockCardAction(ActionCommand):
    def __init__(self, view, card_index):
        self.view = view
        self.card_index = card_index

    async def execute(self, button: discord.ui.Button, interaction: discord.Interaction):
        if not await self.ensure_bet(interaction):
            return

        self.view.cassino_player.hand_locks[self.card_index] = not self.view.cassino_player.hand_locks[self.card_index]
        self.bet_change_style(button)
        
        await interaction.response.edit_message(content=interaction.message.content, view=self.view)

    def bet_change_style(self, button: discord.ui.Button):
        if button.style == discord.ButtonStyle.green:
            button.style = discord.ButtonStyle.red
            button.label = config.emoji.cassino.video_poker.lock
        else:
            button.style = discord.ButtonStyle.green
            button.label = config.emoji.cassino.video_poker.unlock

class RedrawAction(ActionCommand):
    def __init__(self, view):
        self.view = view

    async def execute(self, button: discord.ui.Button, interaction: discord.Interaction):
        if not await self.ensure_bet(interaction):
            return
        
        self.disable_redraw_button()
        self.disable_lock_buttons()
        self.enable_bet_buttons()
        self.enable_start_button()

        self.view.cassino_player.redraw()
        prize = self.view.cassino_player.calculate_winnings(self.view.bet)

        await self.update_balance(prize, 0)

        content = f"Your final hand is: {self.view.cassino_player.display_hand()}"
        content += f"\n You have a {self.view.cassino_player.hand_evaluation}!"
        if prize > 0:
            content += f"\n You won ${prize}!"
        else:
            content += f"\n You lost ${self.view.bet}!"
        content += f"\n Your new balance is ${self.view.cassino_player.db_player.balance}"

        self.view.bet = None
        await self.view.prepare_video_poker()
        await interaction.response.edit_message(content=content, view=self.view)
