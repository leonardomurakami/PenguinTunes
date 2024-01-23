import discord

from modules.globals import config

from modules.buttons.cassino import CassinoSelect
from modules.player.cassino import BlackjackDealer, CassinoPlayer, SlotMachine

from modules.buttons.slots.buttons import SlotButton
from modules.buttons.slots.actions import *

from modules.buttons.blackjack.buttons import BlackjackButton
from modules.buttons.blackjack.actions import *


class CassinoView(discord.ui.View):
    def __init__(self, *, member: discord.Member, timeout: float | None = 180):
        super().__init__(timeout=timeout)
        self.member = member
        self.cassino_player: CassinoPlayer | None = None
        self.bet: int = None
        
        self.slot_machine: SlotMachine | None = None
        self.bet_multiplier: int = 1
        self.blackjack_dealer: BlackjackDealer | None = None
        self.roulette = None
        self.prepare_menu()

    def prepare_menu(self):
        self.clear_items()
        self.add_item(
            CassinoSelect()
        )

    def set_bet(self, bet: int):
        self.bet = bet
    
    def get_bet(self):
        return self.cassino_player.bet

    async def prepare_blackjack(self):
        self.blackjack_dealer = BlackjackDealer()
        self.cassino_player = await CassinoPlayer.create(self.member)

        self.clear_items()
        self.add_item(
            BlackjackButton(
                style=discord.ButtonStyle.grey,
                label="$1" + "0"*self.bet_multiplier,
                action=BlackjackBetAction(self, 1*(10**self.bet_multiplier)),
                row=0,
            )
        )
        self.add_item(
            BlackjackButton(
                style=discord.ButtonStyle.grey,
                label="$2" + "0"*self.bet_multiplier,
                action=BlackjackBetAction(self, 2*(10**self.bet_multiplier)),
                row=0,
            )
        )
        self.add_item(
            BlackjackButton(
                style=discord.ButtonStyle.grey,
                label="$3" + "0"*self.bet_multiplier,
                action=BlackjackBetAction(self, 3*(10**self.bet_multiplier)),
                row=0,
            )
        )
        self.add_item(
            BlackjackButton(
                style=discord.ButtonStyle.grey,
                label="$4" + "0"*self.bet_multiplier,
                action=BlackjackBetAction(self, 4*(10**self.bet_multiplier)),
                row=0,
            )
        )
        self.add_item(
            BlackjackButton(
                style=discord.ButtonStyle.grey,
                label="$5" + "0"*self.bet_multiplier,
                action=BlackjackBetAction(self, 5*(10**self.bet_multiplier)),
                row=0,
            )
        )
        self.add_item(
            BlackjackButton(
                style=discord.ButtonStyle.red,
                disabled=True,
                label="Stand",
                action=StandAction(self),
                row=1,
            )
        )
        self.add_item(
            BlackjackButton(
                style=discord.ButtonStyle.blurple,
                disabled=True,
                label="Double",
                action=DoubleAction(self),
                row=1,
            )
        )
        self.add_item(
            BlackjackButton(
                style=discord.ButtonStyle.green,
                disabled=True,
                label="Hit",
                action=HitAction(self),
                row=1,
            )
        )
        self.add_item(
            BlackjackButton(
                style=discord.ButtonStyle.blurple,
                label="<<",
                action=BlackjackReturnAction(self),
                row=2,
            )
        )
        self.add_item(
            BlackjackButton(
                style=discord.ButtonStyle.blurple,
                label="Start",
                action=StartAction(self),
                row=2,
            )
        )
        self.add_item(
            BlackjackButton(
                style=discord.ButtonStyle.blurple,
                label=f"/10",
                action=BlackjackModifyBetAction(self, -1),
                row=2,
            )
        )
        self.add_item(
            BlackjackButton(
                style=discord.ButtonStyle.blurple,
                label=f"x10",
                action=BlackjackModifyBetAction(self, 1),
                row=2,
            )
        )

    async def prepare_slots(self):
        self.slot_machine = SlotMachine()
        self.cassino_player = await CassinoPlayer.create(self.member)

        self.clear_items()
        self.add_item(
            SlotButton(
                style=discord.ButtonStyle.grey,
                label="$1" + "0"*self.bet_multiplier,
                action=SlotsBetAction(self, 1*(10**self.bet_multiplier)),
                row=0,
            )
        )
        self.add_item(
            SlotButton(
                style=discord.ButtonStyle.grey,
                label="$2" + "0"*self.bet_multiplier,
                action=SlotsBetAction(self, 2*(10**self.bet_multiplier)),
                row=0,
            )
        )
        self.add_item(
            SlotButton(
                style=discord.ButtonStyle.grey,
                label="$3" + "0"*self.bet_multiplier,
                action=SlotsBetAction(self, 3*(10**self.bet_multiplier)),
                row=0,
            )
        )
        self.add_item(
            SlotButton(
                style=discord.ButtonStyle.grey,
                label="$4" + "0"*self.bet_multiplier,
                action=SlotsBetAction(self, 4*(10**self.bet_multiplier)),
                row=0,
            )
        )
        self.add_item(
            SlotButton(
                style=discord.ButtonStyle.grey,
                label="$5" + "0"*self.bet_multiplier,
                action=SlotsBetAction(self, 5*(10**self.bet_multiplier)),
                row=0,
            )
        )
        self.add_item(
            SlotButton(
                style=discord.ButtonStyle.blurple,
                label="<<",
                action=SlotsReturnAction(self),
                row=1,
            )
        )
        self.add_item(
            SlotButton(
                style=discord.ButtonStyle.blurple,
                label=f"Prizes",
                action=DisplayPrizesAction(self),
                row=1,
            )
        )
        self.add_item(
            SlotButton(
                style=discord.ButtonStyle.red,
                label=f"{config.emoji.cassino.slots} Spin",
                action=SpinAction(self),
                row=1,
            )
        )
        self.add_item(
            SlotButton(
                style=discord.ButtonStyle.blurple,
                label=f"/10",
                action=SlotsModifyBetAction(self, -1),
                row=1,
            )
        )
        self.add_item(
            SlotButton(
                style=discord.ButtonStyle.blurple,
                label=f"x10",
                action=SlotsModifyBetAction(self, 1),
                row=1,
            )
        )
