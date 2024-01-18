import discord

from modules.buttons.cassino import CassinoButton, CassinoSelect
from modules.buttons.music import MusicButton
from modules.globals import config
from modules.player.cassino import CassinoPlayer, SlotMachine


class CassinoView(discord.ui.View):
    def __init__(self, *, member: discord.Member, timeout: float | None = 180):
        super().__init__(timeout=timeout)
        self.member = member
        self.cassino_player: CassinoPlayer | None = None
        
        self.slot_machine: SlotMachine | None = None
        self.bet_multiplier: int = 1
        self.blackjack = None
        self.roulette = None
        self.prepare_menu()

    def prepare_menu(self):
        self.clear_items()
        self.add_item(
            CassinoSelect()
        )

    async def prepare_slots(self):
        self.slot_machine = SlotMachine()
        self.cassino_player = await CassinoPlayer.create(self.member)

        self.clear_items()
        self.add_item(
            CassinoButton(
                style=discord.ButtonStyle.green,
                label="$1" + "0"*self.bet_multiplier,
                action="bet_1" + "0"*self.bet_multiplier,
                row=0,
            )
        )
        self.add_item(
            CassinoButton(
                style=discord.ButtonStyle.grey,
                label="$2" + "0"*self.bet_multiplier,
                action="bet_2" + "0"*self.bet_multiplier,
                row=0,
            )
        )
        self.add_item(
            CassinoButton(
                style=discord.ButtonStyle.grey,
                label="$3" + "0"*self.bet_multiplier,
                action="bet_3" + "0"*self.bet_multiplier,
                row=0,
            )
        )
        self.add_item(
            CassinoButton(
                style=discord.ButtonStyle.grey,
                label="$4" + "0"*self.bet_multiplier,
                action="bet_4" + "0"*self.bet_multiplier,
                row=0,
            )
        )
        self.add_item(
            CassinoButton(
                style=discord.ButtonStyle.grey,
                label="$5" + "0"*self.bet_multiplier,
                action="bet_5" + "0"*self.bet_multiplier,
                row=0,
            )
        )
        self.add_item(
            CassinoButton(
                style=discord.ButtonStyle.blurple,
                label="<<",
                action="back",
                row=1,
            )
        )
        self.add_item(
            CassinoButton(
                style=discord.ButtonStyle.red,
                label=f"{config.emoji.cassino.slots} Spin",
                action="spin",
                row=1,
            )
        )
        self.add_item(
            CassinoButton(
                style=discord.ButtonStyle.blurple,
                label=f"Prizes",
                action="prizes",
                row=1,
            )
        )
        self.add_item(
            CassinoButton(
                style=discord.ButtonStyle.blurple,
                label=f"/10",
                action="decrease_bet",
                row=1,
            )
        )
        self.add_item(
            CassinoButton(
                style=discord.ButtonStyle.blurple,
                label=f"x10",
                action="increase_bet",
                row=1,
            )
        )
