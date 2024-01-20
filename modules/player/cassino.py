import random
import discord

from tabulate import tabulate
from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from modules.globals import config
from modules.orm.database import Cassino, PersistentValues

#TODO: Introduce a increasing jackpot for the triple diamond. Take 5% from every buy-in and add it to the jackpot.
#TODO: Make a leaderboard for most wins and most money.

class CassinoPlayer:
    def __init__(self, member: discord.Member) -> None:
        self.member: discord.Member = member
        self.db_player: Cassino | None = None
        self.hand: list = []
        self.sessionmaker = sessionmaker(
            create_async_engine(
                f"{config.database.db_driver}://{config.database.connection_url}"
            ),
            class_=AsyncSession,
        )

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

    @classmethod
    async def create(cls, member: discord.Member):
        self = CassinoPlayer(member)
        await self.initialize()
        return self

    async def initialize(self):
        async with self.sessionmaker() as session:
            player = await session.get(Cassino, int(self.member.id))
            if not player:
                player = Cassino(id=self.member.id, balance=1000)
                session.add(player)
                await session.commit()
                await session.refresh(player)
            self.db_player = player
    
    async def update(self, player):
        async with self.sessionmaker() as session:
            session.add(player)
            await session.commit()
            await session.refresh(player)

    def add_to_hand(self, card):
        self.hand.append(card)


class SlotMachine:
    def __init__(self) -> None:
        self.sessionmaker = sessionmaker(
            create_async_engine(
                f"{config.database.db_driver}://{config.database.connection_url}"
            ),
            class_=AsyncSession,
        )
        self.full_prizes = {
            config.emoji.cassino.diamond: 100,
            config.emoji.cassino.cherry: 50,
            config.emoji.cassino.lemon: 25,
            config.emoji.cassino.orange: 10,
            config.emoji.cassino.apple: 8,
            config.emoji.cassino.grapes: 5,
            config.emoji.cassino.banana: 2,
        }
        self.two_of_a_kind_prizes = {
            config.emoji.cassino.diamond: 20,
            config.emoji.cassino.cherry: 15,
            config.emoji.cassino.lemon: 10,
            config.emoji.cassino.orange: 6,
            config.emoji.cassino.apple: 3,
        }
        self.one_of_a_kind_prizes = {
            config.emoji.cassino.diamond: 6,
            config.emoji.cassino.cherry: 2
        }
        self.probability_distribution = self.calculate_probabilities()

    def calculate_probabilities(self):
        adjustment_factor = config.fun.cassino_adjustment_factor
        total_weight = sum(1 / (prize * adjustment_factor) for prize in self.full_prizes.values())
        probabilities = {symbol: (1 / (prize * adjustment_factor)) / total_weight for symbol, prize in self.full_prizes.items()}
        return probabilities
    
    def spin(self):
        symbols, weights = zip(*self.probability_distribution.items())
        return random.choices(symbols, weights, k=3)
    
    async def calculate_prize(self, combination, bet_amount):
        """
        Calculate the prize based on the combination of symbols and the bet amount.
        :param combination: tuple of symbols
        :param bet_amount: the amount of bet placed
        :return: prize amount
        """
        if combination[0] == combination[1] == combination[2]:
            if combination[0] == config.emoji.cassino.diamond:
                jackpot = await self.get_jackpot()
            else:
                jackpot = 0
            multiplier = self.full_prizes.get(combination[0], 0)
            return bet_amount * multiplier + jackpot

        elif combination[0] == combination[1] or combination[0] == combination[2] or combination[1] == combination[2]:
            for symbol in combination:
                if combination.count(symbol) == 2:
                    multiplier = self.two_of_a_kind_prizes.get(symbol, 0)
                    return bet_amount * multiplier
            return 0
        
        else:
            for symbol in combination:
                if combination.count(symbol) == 1 and symbol in self.one_of_a_kind_prizes:
                    multiplier = self.one_of_a_kind_prizes.get(symbol, 0)
                    return bet_amount * multiplier
            await self.add_jackpot(bet_amount * (1-config.fun.house_retain)) #add 90% of the bet amount to the jackpot
            return 0
        
    def display_prizes(self):
        table_data = [
            ['Full Prizes', '', ''],
            *[[symbol*3, f"{prize}x", ''] for symbol, prize in self.full_prizes.items()],
            ['', '', ''],  # Empty row for spacing
            ['Two of a Kind Prizes', '', ''],
            *[[symbol*2, f"{prize}x", ''] for symbol, prize in self.two_of_a_kind_prizes.items()],
            ['', '', ''],  # Empty row for spacing
            ['One of a Kind Prizes', '', ''],
            *[[symbol, f"{prize}x", ''] for symbol, prize in self.one_of_a_kind_prizes.items()],
        ]
        return tabulate(table_data, tablefmt="plain")
    
    async def get_jackpot(self):
        async with self.sessionmaker() as session:
            jackpot = await session.get(PersistentValues, "jackpot")
            if not jackpot:
                jackpot = PersistentValues(name="jackpot", value="0")
                session.add(jackpot)
                await session.commit()
                await session.refresh(jackpot)
            return jackpot.value
        
    async def add_jackpot(self, value: int):
        async with self.sessionmaker() as session:
            jackpot = await session.get(PersistentValues, "jackpot")
            if not jackpot:
                jackpot = PersistentValues(name="jackpot", value="0")
                session.add(jackpot)
                await session.commit()
                await session.refresh(jackpot)
            jackpot.value += value
            await session.commit()
            await session.refresh(jackpot)
    
    async def reset_jackpot(self):
        async with self.sessionmaker() as session:
            jackpot = await session.get(PersistentValues, "jackpot")
            if not jackpot:
                jackpot = PersistentValues(name="jackpot", value="0")
                session.add(jackpot)
                await session.commit()
                await session.refresh(jackpot)
            jackpot.value = 0
            await session.commit()
            await session.refresh(jackpot)


class BlackjackDealer:
    def __init__(self):
        self.deck = self.create_deck()
        self.hand = []

    @staticmethod
    def create_deck():
        suits = [config.emoji.cassino.blackjack.hearts, config.emoji.cassino.blackjack.diamonds, config.emoji.cassino.blackjack.clubs, config.emoji.cassino.blackjack.spades]
        ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        return [{'suit': suit, 'rank': rank} for suit in suits for rank in ranks]

    @staticmethod
    def display(hand: list, dealer: bool, force_display: bool = False):
        if dealer and len(hand) == 2 and not force_display:
            return f"[{hand[0]['rank']}{hand[0]['suit']}] [?{hand[0]['suit']}]"
        return ' '.join([f"[{card['rank']}{card['suit']}]" for card in hand])

    def shuffle_deck(self):
        random.shuffle(self.deck)

    def deal_card(self):
        if not self.deck:
            self.deck = self.create_deck()
            self.shuffle_deck()
        return self.deck.pop(random.randrange(len(self.deck)))

    def add_to_hand(self, card):
        self.hand.append(card)

    def show_hand(self):
        return self.hand

    def reset_hand(self):
        self.hand = []

    @property
    def hand_value(self):
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

    def play(self) -> list:
        # The dealer must hit until the cards total 17 or more points.
        plays = ""
        while self.hand_value < 17:
            card = self.deal_card()
            plays += f"Dealer got {card['rank']}{card['suit']}\n"
            self.add_to_hand(card)
        return plays
    
    def deal_initial_hand(self) -> None:
        self.add_to_hand(self.deal_card())
        self.add_to_hand(self.deal_card())

    def reset_deck(self) -> None:
        self.deck = self.create_deck()

    def hit(self, player) -> None:
        player.add_to_hand(self.deal_card())       
