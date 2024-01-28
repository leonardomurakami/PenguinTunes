import random
import discord

from collections import Counter
from modules.globals import config
from modules.orm.database import Cassino, PersistentValues
from modules.player.video_poker import VideoPokerDealer
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

    @classmethod
    async def create(cls, member: discord.Member):
        self = BlackjackPlayer(member)
        await self.initialize()
        return self

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
    

class VideoPokerPlayer(CassinoPlayer):
    def __init__(self, member: discord.Member, dealer: VideoPokerDealer) -> None:
        super().__init__(member)
        self.dealer = dealer
        self.hand = self.start_hand()
        self.hand_locks = [False, False, False, False, False]

    def start_hand(self):
        return self.dealer.deal(5)
    
    def redraw(self):
        for i in range(5):
            if not self.hand_locks[i]:
                self.hand[i] = self.dealer.deal_card()
                
    @classmethod
    async def create(cls, member: discord.Member, dealer: VideoPokerDealer):
        self = VideoPokerPlayer(member, dealer)
        await self.initialize()
        return self

    @property
    def hand_evaluation(self) -> str:
        """
        Evaluate the player's hand and return the ranking as a string.
        """
        # Implement hand evaluation logic here
        return self.evaluate_hand(self.hand)

    def calculate_winnings(self, bet_amount):
        payouts = {
            "Royal Flush": 800,
            "Straight Flush": 50,
            "Four of a Kind": 25,
            "Full House": 9,
            "Flush": 6,
            "Straight": 4,
            "Three of a Kind": 3,
            "Two Pair": 2,
            "Jacks or Better": 1,
            "High Card": 0,
        }
        hand_rank = self.hand_evaluation

        return bet_amount * payouts.get(hand_rank, 0)
        
    def evaluate_hand(self, hand):
        ranks = [card['rank'] for card in hand]
        suits = [card['suit'] for card in hand]
        
        rank_counter = Counter(ranks)
        suit_counter = Counter(suits)
        
        is_flush = len(suit_counter) == 1
        is_straight = False
        sorted_ranks = sorted([int(card) if card.isdigit() else {'J': 11, 'Q': 12, 'K': 13, 'A': 14}[card] for card in ranks])
        
        # Check for straight
        if len(rank_counter) == 5 and sorted_ranks[-1] - sorted_ranks[0] == 4:
            is_straight = True
        elif sorted_ranks == [2, 3, 4, 5, 14]:  # Handle special case: A-2-3-4-5
            is_straight = True
            sorted_ranks = [1, 2, 3, 4, 5]  # Adjusted ranking for A-2-3-4-5 straight

        # Check for Royal Flush
        if is_straight and is_flush and sorted_ranks[-1] == 14:
            return "Royal Flush"

        # Check for Straight Flush
        if is_straight and is_flush:
            return "Straight Flush"

        # Check for Four of a Kind
        if 4 in rank_counter.values():
            return "Four of a Kind"

        # Check for Full House
        if 3 in rank_counter.values() and 2 in rank_counter.values():
            return "Full House"

        # Check for Flush
        if is_flush:
            return "Flush"

        # Check for Straight
        if is_straight:
            return "Straight"

        # Check for Three of a Kind
        if 3 in rank_counter.values():
            return "Three of a Kind"

        # Check for Two Pair
        if list(rank_counter.values()).count(2) == 2:
            return "Two Pair"

        # Check for One Pair
        if 2 in rank_counter.values():
            pairs = [rank for rank, count in rank_counter.items() if count == 2]
            face_cards = {'J', 'Q', 'K', 'A'}
            if any(pair in face_cards or pair.isdigit() and int(pair) >= 11 for pair in pairs):
                return "Jacks or Better"
            return "One Pair"

        # High Card
        high_card_rank = max(sorted_ranks)
        high_card = [rank for rank in rank_counter.keys() if rank_counter[rank] == 1 and (int(rank) if rank.isdigit() else {'J': 11, 'Q': 12, 'K': 13, 'A': 14}[rank]) == high_card_rank][0]
        return f"High Card: {high_card}"


    def display_hand(self):
        return " ".join([f"[{card['rank']} {card['suit']}]" for card in self.hand])