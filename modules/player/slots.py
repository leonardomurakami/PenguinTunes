import random

from tabulate import tabulate

from modules.globals import config
from modules.orm.database import PersistentValues
from modules.utils._database_utils import get_session


class SlotMachine:
    def __init__(self) -> None:
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
        async with get_session() as session:
            jackpot = await session.get(PersistentValues, "jackpot")
            if not jackpot:
                jackpot = PersistentValues(name="jackpot", value="0")
                session.add(jackpot)
                await session.commit()
                await session.refresh(jackpot)
            return jackpot.value
        
    async def add_jackpot(self, value: int):
        async with get_session() as session:
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
        async with get_session() as session:
            jackpot = await session.get(PersistentValues, "jackpot")
            if not jackpot:
                jackpot = PersistentValues(name="jackpot", value="0")
                session.add(jackpot)
                await session.commit()
                await session.refresh(jackpot)
            jackpot.value = 0
            await session.commit()
            await session.refresh(jackpot)

