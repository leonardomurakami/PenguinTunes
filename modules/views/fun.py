import discord

from modules.buttons.cassino import BlackjackButton, SlotButton, CassinoSelect
from modules.buttons.music import MusicButton
from modules.globals import config
from modules.player.cassino import BlackjackDealer, CassinoPlayer, SlotMachine


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
                action="bet_1" + "0"*self.bet_multiplier,
                row=0,
            )
        )
        self.add_item(
            BlackjackButton(
                style=discord.ButtonStyle.grey,
                label="$2" + "0"*self.bet_multiplier,
                action="bet_2" + "0"*self.bet_multiplier,
                row=0,
            )
        )
        self.add_item(
            BlackjackButton(
                style=discord.ButtonStyle.grey,
                label="$3" + "0"*self.bet_multiplier,
                action="bet_3" + "0"*self.bet_multiplier,
                row=0,
            )
        )
        self.add_item(
            BlackjackButton(
                style=discord.ButtonStyle.grey,
                label="$4" + "0"*self.bet_multiplier,
                action="bet_4" + "0"*self.bet_multiplier,
                row=0,
            )
        )
        self.add_item(
            BlackjackButton(
                style=discord.ButtonStyle.grey,
                label="$5" + "0"*self.bet_multiplier,
                action="bet_5" + "0"*self.bet_multiplier,
                row=0,
            )
        )
        self.add_item(
            BlackjackButton(
                style=discord.ButtonStyle.red,
                disabled=True,
                label="Stand",
                action="stand",
                row=1,
            )
        )
        self.add_item(
            BlackjackButton(
                style=discord.ButtonStyle.blurple,
                disabled=True,
                label="Double",
                action="double",
                row=1,
            )
        )
        self.add_item(
            BlackjackButton(
                style=discord.ButtonStyle.green,
                disabled=True,
                label="Hit",
                action="hit",
                row=1,
            )
        )
        self.add_item(
            BlackjackButton(
                style=discord.ButtonStyle.blurple,
                label="<<",
                action="back",
                row=2,
            )
        )
        self.add_item(
            BlackjackButton(
                style=discord.ButtonStyle.blurple,
                label="Start",
                action="start",
                row=2,
            )
        )
        self.add_item(
            BlackjackButton(
                style=discord.ButtonStyle.blurple,
                label=f"/10",
                action="decrease_bet",
                row=2,
            )
        )
        self.add_item(
            BlackjackButton(
                style=discord.ButtonStyle.blurple,
                label=f"x10",
                action="increase_bet",
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
                action="bet_1" + "0"*self.bet_multiplier,
                row=0,
            )
        )
        self.add_item(
            SlotButton(
                style=discord.ButtonStyle.grey,
                label="$2" + "0"*self.bet_multiplier,
                action="bet_2" + "0"*self.bet_multiplier,
                row=0,
            )
        )
        self.add_item(
            SlotButton(
                style=discord.ButtonStyle.grey,
                label="$3" + "0"*self.bet_multiplier,
                action="bet_3" + "0"*self.bet_multiplier,
                row=0,
            )
        )
        self.add_item(
            SlotButton(
                style=discord.ButtonStyle.grey,
                label="$4" + "0"*self.bet_multiplier,
                action="bet_4" + "0"*self.bet_multiplier,
                row=0,
            )
        )
        self.add_item(
            SlotButton(
                style=discord.ButtonStyle.grey,
                label="$5" + "0"*self.bet_multiplier,
                action="bet_5" + "0"*self.bet_multiplier,
                row=0,
            )
        )
        self.add_item(
            SlotButton(
                style=discord.ButtonStyle.blurple,
                label="<<",
                action="back",
                row=1,
            )
        )
        self.add_item(
            SlotButton(
                style=discord.ButtonStyle.blurple,
                label=f"Prizes",
                action="prizes",
                row=1,
            )
        )
        self.add_item(
            SlotButton(
                style=discord.ButtonStyle.red,
                label=f"{config.emoji.cassino.slots} Spin",
                action="spin",
                row=1,
            )
        )
        self.add_item(
            SlotButton(
                style=discord.ButtonStyle.blurple,
                label=f"/10",
                action="decrease_bet",
                row=1,
            )
        )
        self.add_item(
            SlotButton(
                style=discord.ButtonStyle.blurple,
                label=f"x10",
                action="increase_bet",
                row=1,
            )
        )
