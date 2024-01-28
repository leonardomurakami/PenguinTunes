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

    def update_player_stats(self, win=False, tie=False):
        if win:
            self.view.cassino_player.db_player.balance += self.view.bet*2
            self.view.cassino_player.db_player.money_won += self.view.bet*2
            self.view.cassino_player.db_player.blackjack_wins += self.view.bet*2
        elif tie:
            self.view.cassino_player.db_player.balance += self.view.bet

    def disable_play_buttons(self):
        for item in self.view.children:
            if isinstance(item, discord.ui.Button) and (
                isinstance(item.action, HitAction) or 
                isinstance(item.action, StandAction) or 
                isinstance(item.action, DoubleAction)
            ):
                item.disabled = True
    
    def enable_play_buttons(self):
        for item in self.view.children:
            if isinstance(item, discord.ui.Button) and (
                isinstance(item.action, HitAction) or 
                isinstance(item.action, StandAction) or 
                isinstance(item.action, DoubleAction)
            ):
                item.disabled = False

    def disable_bet_buttons(self):
        for item in self.view.children:
            if isinstance(item, discord.ui.Button) and isinstance(item.action, BlackjackBetAction):
                item.disabled = True

    def enable_bet_buttons(self):
        for item in self.view.children:
            if isinstance(item, discord.ui.Button) and isinstance(item.action, BlackjackBetAction):
                item.disabled = False

    def disable_start_button(self):
        for item in self.view.children:
            if isinstance(item, discord.ui.Button) and isinstance(item.action, StartAction):
                item.disabled = True
    
    def enable_start_button(self):
        for item in self.view.children:
            if isinstance(item, discord.ui.Button) and isinstance(item.action, StartAction):
                item.disabled = False

    def display(self, force_display=False):
        # Display only the current state of hands
        content = f"Your hand: {self.view.blackjack_dealer.display(self.view.cassino_player.hand, dealer=False, force_display=force_display)} => {self.view.cassino_player.hand_value}\n"
        content += f"Dealer's Hand: {self.view.blackjack_dealer.display(self.view.blackjack_dealer.hand, dealer=True, force_display=force_display)}"
        return content

    def determine_winner(self):
        # Generate only the result-related content
        result_content = ""
        if self.view.blackjack_dealer.bust:
            result_content += "\nThe dealer busts!"
            result_content += f"\nYou won ${self.view.bet}!"
            self.update_player_stats(win=True)
        elif self.view.blackjack_dealer.hand_value > self.view.cassino_player.hand_value:
            result_content += "\nThe dealer wins!"
            result_content += f"\nYou lost ${self.view.bet}!"
        elif self.view.blackjack_dealer.hand_value < self.view.cassino_player.hand_value:
            result_content += "\nYou win!"
            result_content += f"\nYou won ${self.view.bet}!"
            self.update_player_stats(win=True)
        else:
            result_content += "\nIt's a tie!"
            result_content += f"\nYou get your ${self.view.bet} back!"
            self.update_player_stats(tie=True)
        result_content += f"\n Your new balance is ${self.view.cassino_player.db_player.balance}"
        return result_content
    

class StartAction(ActionCommand):
    def __init__(self, view):
        self.view = view

    async def execute(self, button: discord.ui.Button, interaction: discord.Interaction):
        if not await self.ensure_bet(interaction):
            return
        
        if not await self.ensure_minimum_balance(interaction, self.view.bet):
            return
        
        await self.view.prepare_blackjack()

        self.view.cassino_player.add_to_hand(self.view.blackjack_dealer.deal_card())
        self.view.cassino_player.add_to_hand(self.view.blackjack_dealer.deal_card())
        
        self.view.blackjack_dealer.add_to_hand(self.view.blackjack_dealer.deal_card())
        self.view.blackjack_dealer.add_to_hand(self.view.blackjack_dealer.deal_card())
        
        content = self.display()
        
        self.enable_play_buttons()
        self.disable_start_button()
        self.disable_bet_buttons()

        self.view.cassino_player.db_player.balance -= self.view.bet
        self.view.cassino_player.db_player.money_lost += self.view.bet
        
        await self.view.cassino_player.update(self.view.cassino_player.db_player)
        await interaction.response.edit_message(content=content, view=self.view)


class HitAction(ActionCommand):
    def __init__(self, view):
        self.view = view

    async def execute(self, button:discord.ui.Button, interaction: discord.Interaction):
        self.view.blackjack_dealer.hit(self.view.cassino_player)
        content = self.display()
        if self.view.cassino_player.bust:
            content += "\nYou bust!"
            content += f"\nYou lost ${self.view.bet}!"
            
            self.update_player_stats()
            
            self.enable_bet_buttons()
            self.enable_start_button()
            self.disable_play_buttons()
        await interaction.response.edit_message(content=content, view=self.view)


class StandAction(ActionCommand):
    def __init__(self, view: discord.ui.View):
        self.view = view

    async def execute(self, button: discord.ui.Button, interaction: discord.Interaction):
        plays = self.view.blackjack_dealer.play()
        content = self.display(force_display=True)
        content += f"\n{plays}"

        content += self.determine_winner()
        
        self.enable_bet_buttons()
        self.enable_start_button()
        self.disable_play_buttons()
        
        await self.view.cassino_player.update(self.view.cassino_player.db_player)
        await interaction.response.edit_message(content=content, view=self.view)


class DoubleAction(ActionCommand):
    def __init__(self, view: discord.ui.View):
        self.view = view

    async def execute(self, button: discord.ui.Button, interaction: discord.Interaction):
        if not await self.ensure_minimum_balance(interaction, self.view.bet):
            return
        
        self.view.bet *= 2
        self.view.cassino_player.db_player.balance -= self.view.bet
        self.view.cassino_player.db_player.money_lost += self.view.bet

        self.view.blackjack_dealer.hit(self.view.cassino_player)
        plays = self.view.blackjack_dealer.play()

        content = self.display(force_display=True)
        content += f"\n{plays}"
        content += self.determine_winner()

        self.disable_play_buttons()
        self.enable_bet_buttons()
        self.enable_start_button()

        self.view.bet //= 2 #return bet to before double

        await self.view.cassino_player.update(self.view.cassino_player.db_player)
        await interaction.response.edit_message(content=content, view=self.view)


class BlackjackBetAction(ActionCommand):
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
            if isinstance(item, discord.ui.Button) and item.style == discord.ButtonStyle.green and isinstance(item.action, BlackjackBetAction):
                item.style = discord.ButtonStyle.grey
        button.style = style


class BlackjackReturnAction(ActionCommand):
    def __init__(self, view):
        self.view = view

    async def execute(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.view.prepare_menu()
        await interaction.response.edit_message(content=None, view=self.view)


class BlackjackModifyBetAction(ActionCommand):
    def __init__(self, view, amount):
        self.view = view
        self.amount = amount

    async def execute(self, button: discord.ui.Button, interaction: discord.Interaction):
        if self.view.bet_multiplier == 1 and self.amount == -1:
            await interaction.response.send_message("You can't bet less than $10!", ephemeral=True)
            return
        self.view.bet_multiplier += self.amount
        self.view.bet = None
        await self.view.prepare_blackjack()
        await interaction.response.edit_message(view=self.view)