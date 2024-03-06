import discord

from modules.globals import config

from modules.buttons.cassino import CassinoSelect
from modules.player.player import BlackjackPlayer, CassinoPlayer, VideoPokerPlayer
from modules.player.blackjack import BlackjackDealer
from modules.player.video_poker import VideoPokerDealer
from modules.player.roulette import Roulette
from modules.player.slots import SlotMachine

from modules.buttons.slots.buttons import SlotButton
from modules.buttons.slots.actions import *

from modules.buttons.blackjack.buttons import BlackjackButton
from modules.buttons.blackjack.actions import *

from modules.buttons.roulette.buttons import RouletteButton
from modules.buttons.roulette.actions import *

from modules.buttons.video_poker.buttons import VideoPokerButton
from modules.buttons.video_poker.actions import *

from modules.buttons.dig_trash.buttons import DigTrashButton
from modules.buttons.dig_trash.actions import *


class CassinoView(discord.ui.View):
    def __init__(self, *, member: discord.Member, timeout: float = 180):
        super().__init__(timeout=timeout)
        self.member = member
        self.cassino_player: CassinoPlayer | BlackjackDealer = None
        self.bet: int = None
        
        self.slot_machine: SlotMachine = None
        self.bet_multiplier: int = 1
        self.blackjack_dealer: BlackjackDealer = None
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
        return self.bet

    async def prepare_dig_trash(self):
        self.cassino_player = await CassinoPlayer.create(self.member)
        self.clear_items()
        self.add_item(
            DigTrashButton(
                style=discord.ButtonStyle.blurple,
                label="<<",
                action=DigTrashReturnAction(self),
                row=0,
            )
        )
        self.add_item(
            DigTrashButton(
                style=discord.ButtonStyle.grey,
                label="Search Trash",
                action=DigTrashAction(self),
                row=0,
            )
        )

    async def prepare_blackjack(self):
        self.blackjack_dealer = BlackjackDealer()
        self.cassino_player = await BlackjackPlayer.create(self.member)

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

    async def prepare_roulette(self):
        self.roulette = Roulette()
        self.cassino_player = await CassinoPlayer.create(self.member)

        self.clear_items()
        self.add_item(
            RouletteButton(
                style=discord.ButtonStyle.grey,
                label="$1" + "0"*self.bet_multiplier,
                action=RouletteBetAction(self, 1*(10**self.bet_multiplier)),
                row=0,
            )
        )
        self.add_item(
            RouletteButton(
                style=discord.ButtonStyle.grey,
                label="$2" + "0"*self.bet_multiplier,
                action=RouletteBetAction(self, 2*(10**self.bet_multiplier)),
                row=0,
            )
        )
        self.add_item(
            RouletteButton(
                style=discord.ButtonStyle.grey,
                label="$3" + "0"*self.bet_multiplier,
                action=RouletteBetAction(self, 3*(10**self.bet_multiplier)),
                row=0,
            )
        )
        self.add_item(
            RouletteButton(
                style=discord.ButtonStyle.grey,
                label="$4" + "0"*self.bet_multiplier,
                action=RouletteBetAction(self, 4*(10**self.bet_multiplier)),
                row=0,
            )
        )
        self.add_item(
            RouletteButton(
                style=discord.ButtonStyle.grey,
                label="$5" + "0"*self.bet_multiplier,
                action=RouletteBetAction(self, 5*(10**self.bet_multiplier)),
                row=0,
            )
        )
        self.add_item(
            RouletteButton(
                style=discord.ButtonStyle.blurple,
                label="1 to 18",
                action=Bet1to18Action(self),
                row=1,
            )
        )
        self.add_item(
            RouletteButton(
                style=discord.ButtonStyle.blurple,
                label="Red",
                action=BetRedAction(self),
                row=1,
            )
        )
        self.add_item(
            RouletteButton(
                style=discord.ButtonStyle.blurple,
                label="Green",
                action=BetGreenAction(self),
                row=1,
            )
        )
        self.add_item(
            RouletteButton(
                style=discord.ButtonStyle.blurple,
                label="Black",
                action=BetBlackAction(self),
                row=1,
            )
        )
        self.add_item(
            RouletteButton(
                style=discord.ButtonStyle.blurple,
                label="19 to 36",
                action=Bet19to36Action(self),
                row=1,
            )
        )
        self.add_item(
            RouletteButton(
                style=discord.ButtonStyle.blurple,
                label="Even",
                action=BetEvenAction(self),
                row=2,
            )
        )
        self.add_item(
            RouletteButton(
                style=discord.ButtonStyle.blurple,
                label="1st 12",
                action=Bet1st12Action(self),
                row=2,
            )
        )
        self.add_item(
            RouletteButton(
                style=discord.ButtonStyle.blurple,
                label="2nd 12",
                action=Bet2nd12Action(self),
                row=2,
            )
        )
        self.add_item(
            RouletteButton(
                style=discord.ButtonStyle.blurple,
                label="3rd 12",
                action=Bet3rd12Action(self),
                row=2,
            )
        )
        self.add_item(
            RouletteButton(
                style=discord.ButtonStyle.blurple,
                label="Odd",
                action=BetOddAction(self),
                row=2,
            )
        )
        self.add_item(
            RouletteButton(
                style=discord.ButtonStyle.blurple,
                label="1st Row",
                action=Bet1stRowAction(self),
                row=3,
            )
        )
        self.add_item(
            RouletteButton(
                style=discord.ButtonStyle.blurple,
                label="2nd Row",
                action=Bet2ndRowAction(self),
                row=3,
            )
        )
        self.add_item(
            RouletteButton(
                style=discord.ButtonStyle.blurple,
                label="3rd Row",
                action=Bet3rdRowAction(self),
                row=3,
            )
        )
        self.add_item(
            RouletteButton(
                style=discord.ButtonStyle.grey,
                label="<<",
                action=RouletteReturnAction(self),
                row=4,
            )
        )
        self.add_item(
            RouletteButton(
                style=discord.ButtonStyle.grey,
                label=f"/10",
                action=RouletteModifyBetAction(self, -1),
                row=4,
            )
        )
        self.add_item(
            RouletteButton(
                style=discord.ButtonStyle.grey,
                label=f"x10",
                action=RouletteModifyBetAction(self, 1),
                row=4,
            )
        )
        self.add_item(
            RouletteButton(
                style=discord.ButtonStyle.grey,
                label=f"Help",
                action=GetRouletteTable(self),
                row=4,
            )
        )

    async def prepare_video_poker(self):
        self.dealer = VideoPokerDealer()
        self.cassino_player = await VideoPokerPlayer.create(self.member, self.dealer)
        self.clear_items()

        self.add_item(
            VideoPokerButton(
                style=discord.ButtonStyle.grey,
                label="$1" + "0"*self.bet_multiplier,
                action=VideoPokerBetAction(self, 1*(10**self.bet_multiplier)),
                row=0,
            )
        )
        self.add_item(
            VideoPokerButton(
                style=discord.ButtonStyle.grey,
                label="$2" + "0"*self.bet_multiplier,
                action=VideoPokerBetAction(self, 2*(10**self.bet_multiplier)),
                row=0,
            )
        )
        self.add_item(
            VideoPokerButton(
                style=discord.ButtonStyle.grey,
                label="$3" + "0"*self.bet_multiplier,
                action=VideoPokerBetAction(self, 3*(10**self.bet_multiplier)),
                row=0,
            )
        )
        self.add_item(
            VideoPokerButton(
                style=discord.ButtonStyle.grey,
                label="$4" + "0"*self.bet_multiplier,
                action=VideoPokerBetAction(self, 4*(10**self.bet_multiplier)),
                row=0,
            )
        )
        self.add_item(
            VideoPokerButton(
                style=discord.ButtonStyle.grey,
                label="$5" + "0"*self.bet_multiplier,
                action=VideoPokerBetAction(self, 5*(10**self.bet_multiplier)),
                row=0,
            )
        )
        self.add_item(
            VideoPokerButton(
                style=discord.ButtonStyle.green,
                label=config.emoji.cassino.video_poker.unlock,
                action=LockCardAction(self, 0),
                disabled=True,
                row=1,
            )
        )
        self.add_item(
            VideoPokerButton(
                style=discord.ButtonStyle.green,
                label=config.emoji.cassino.video_poker.unlock,
                action=LockCardAction(self, 1),
                disabled=True,
                row=1,
            )
        )
        self.add_item(
            VideoPokerButton(
                style=discord.ButtonStyle.green,
                label=config.emoji.cassino.video_poker.unlock,
                action=LockCardAction(self, 2),
                disabled=True,
                row=1,
            )
        )
        self.add_item(
            VideoPokerButton(
                style=discord.ButtonStyle.green,
                label=config.emoji.cassino.video_poker.unlock,
                action=LockCardAction(self, 3),
                disabled=True,
                row=1,
            )
        )
        self.add_item(
            VideoPokerButton(
                style=discord.ButtonStyle.green,
                label=config.emoji.cassino.video_poker.unlock,
                action=LockCardAction(self, 4),
                disabled=True,
                row=1,
            )
        )
        self.add_item(
            VideoPokerButton(
                style=discord.ButtonStyle.blurple,
                label="<<",
                action=VideoPokerReturnAction(self),
                row=2,
            )
        )
        self.add_item(
            VideoPokerButton(
                style=discord.ButtonStyle.blurple,
                label="Start",
                action=VideoPokerStartAction(self),
                row=2,
            )
        )
        self.add_item(
            VideoPokerButton(
                style=discord.ButtonStyle.blurple,
                label="Draw",
                action=RedrawAction(self),
                disabled=True,
                row=2,
            
            )
        )
        self.add_item(
            VideoPokerButton(
                style=discord.ButtonStyle.blurple,
                label=f"/10",
                action=VideoPokerModifyBetAction(self, -1),
                row=2,
            )
        )
        self.add_item(
            VideoPokerButton(
                style=discord.ButtonStyle.blurple,
                label=f"x10",
                action=VideoPokerModifyBetAction(self, 1),
                row=2,
            )
        )
        self.add_item(
            VideoPokerButton(
                style=discord.ButtonStyle.blurple,
                label=f"Help",
                action=DisplayHandsAction(self),
                row=3,
            )
        )