import random
import discord

from modules.globals import config
from modules.orm.database import Cassino, PersistentValues
from modules.utils._database_utils import get_session


class CassinoPlayer:
    def __init__(self, member: discord.Member) -> None:
        self.member: discord.Member = member
        self.db_player: Cassino | None = None

    @classmethod
    async def create(cls, member: discord.Member):
        self = CassinoPlayer(member)
        await self.initialize()
        return self

    async def initialize(self):
        async with get_session() as session:
            player = await session.get(Cassino, int(self.member.id))
            if not player:
                player = Cassino(id=self.member.id, balance=1000)
                session.add(player)
                await session.commit()
                await session.refresh(player)
            self.db_player = player
    
    async def update(self, player):
        async with get_session() as session:
            session.add(player)
            await session.commit()
            await session.refresh(player)


class BlackjackPlayer(CassinoPlayer):
    def __init__(self, member: discord.Member) -> None:
        super().__init__(member)
        self.hand = []

    def add_to_hand(self, card):
        self.hand.append(card)

    @property
    def hand_value(self) -> int:
        value = 0
        ace_count = 0

        for card in self.hand:
            rank = card['rank']
            if rank in ['J', 'Q', 'K']:
                value += 10
            elif rank == 'A':
                ace_count += 1
                value += 11
            else:
                value += int(rank)

        while value > 21 and ace_count:
            value -= 10
            ace_count -= 1

        return value

    @property
    def bust(self) -> bool:
        """
        Property that returns if the player has busted.
        """
        return self.hand_value > 21