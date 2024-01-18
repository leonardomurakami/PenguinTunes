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
                player=self.cassino_player,
                label="$10",
                action="bet_10",
                row=0,
            )
        )
        self.add_item(
            CassinoButton(
                style=discord.ButtonStyle.grey,
                player=self.cassino_player,
                label="$20",
                action="bet_20",
                row=0,
            )
        )
        self.add_item(
            CassinoButton(
                style=discord.ButtonStyle.grey,
                player=self.cassino_player,
                label="$30",
                action="bet_30",
                row=0,
            )
        )
        self.add_item(
            CassinoButton(
                style=discord.ButtonStyle.grey,
                player=self.cassino_player,
                label="$40",
                action="bet_40",
                row=0,
            )
        )
        self.add_item(
            CassinoButton(
                style=discord.ButtonStyle.grey,
                player=self.cassino_player,
                label="$50",
                action="bet_50",
                row=0,
            )
        )
        self.add_item(
            CassinoButton(
                style=discord.ButtonStyle.blurple,
                player=self.cassino_player,
                label="<<",
                action="back",
                row=1,
            )
        )
        self.add_item(
            CassinoButton(
                style=discord.ButtonStyle.red,
                player=self.cassino_player,
                label=f"{config.emoji.cassino.slots} Spin",
                action="spin",
                row=1,
            )
        )
        self.add_item(
            CassinoButton(
                style=discord.ButtonStyle.blurple,
                player=self.cassino_player,
                label=f"Prizes",
                action="prizes",
                row=1,
            )
        )
