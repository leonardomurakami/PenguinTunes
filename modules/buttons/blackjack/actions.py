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
        await self.view.cassino_player.refresh()
        if self.view.cassino_player.db_player.balance < required_balance:
            await interaction.response.send_message("You don't have enough money for this action!", ephemeral=True)
            return False
        return True
    
    async def subtract_bet(self):
        await self.view.cassino_player.refresh()
        self.view.cassino_player.db_player.balance -= self.view.bet
        self.view.cassino_player.db_player.money_lost += self.view.bet
        await self.view.cassino_player.update(self.view.cassino_player.db_player)

    async def finalize_game(self, interaction: discord.Interaction):
        # Determine the outcome
        result_content, win, tie = "", False, False
        if self.view.cassino_player.bust:
            result_content = "\nYou bust! You lost!"
            win, tie = False, False
        elif self.view.blackjack_dealer.bust:
            result_content = "\nThe dealer busts! You won!"
            win, tie = True, False
        elif self.view.blackjack_dealer.hand_value > self.view.cassino_player.hand_value:
            result_content = "\nThe dealer wins! You lost!"
            win, tie = False, False
        elif self.view.blackjack_dealer.hand_value < self.view.cassino_player.hand_value:
            result_content = "\nYou win!"
            win, tie = True, False
        else:
            result_content = "\nIt's a tie!"
            win, tie = False, True

        # Update the player's balance and stats
        bet = self.view.bet
        await self.view.cassino_player.refresh()
        if win:
            result_content += f"\nYou won ${bet}!"
            prize = bet * 2
            self.view.cassino_player.db_player.balance += prize
            self.view.cassino_player.db_player.money_won += bet
            self.view.cassino_player.db_player.blackjack_wins += 1
        elif tie:
            result_content += f"\nYou get your bet back!"
            prize = bet
            self.view.cassino_player.db_player.balance += prize
        else:
            result_content += f"\nYou lost ${bet}!"
            prize = 0
            self.view.cassino_player.db_player.balance += prize
            self.view.cassino_player.db_player.money_lost += bet

        # Update the database with the new player stats
        await self.view.cassino_player.update(self.view.cassino_player.db_player)

        # Send the result message
        result_content += f" Your new balance is ${self.view.cassino_player.db_player.balance}"

        self.enable_bet_buttons()
        self.enable_start_button()
        self.disable_play_buttons()

        self.view.bet = None

        return result_content

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

        await self.subtract_bet()
        await interaction.response.edit_message(content=content, view=self.view)


class HitAction(ActionCommand):
    def __init__(self, view):
        self.view = view

    async def execute(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.view.blackjack_dealer.hit(self.view.cassino_player)
        content = self.display()
        if self.view.cassino_player.bust:
            content += await self.finalize_game(interaction)
        await interaction.response.edit_message(content=content, view=self.view)


class StandAction(ActionCommand):
    def __init__(self, view: discord.ui.View):
        self.view = view

    async def execute(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.view.blackjack_dealer.play()
        content = self.display(force_display=True)
        content += await self.finalize_game(interaction)
        await interaction.response.edit_message(content=content, view=self.view)

class DoubleAction(ActionCommand):
    def __init__(self, view: discord.ui.View):
        self.view = view

    async def execute(self, button: discord.ui.Button, interaction: discord.Interaction):
        if not await self.ensure_minimum_balance(interaction, self.view.bet * 2):
            return
        
        await self.subtract_bet()
        self.view.bet *= 2
        self.view.blackjack_dealer.hit(self.view.cassino_player)
        self.view.blackjack_dealer.play()
        content = self.display(force_display=True)
        content += await self.finalize_game(interaction)
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