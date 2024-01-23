import random

from modules.globals import config


class BlackjackDealer:
    def __init__(self):
        self.deck = self.create_deck()
        self.hand = []

    @staticmethod
    def create_deck():
        suits = [config.emoji.cassino.blackjack.hearts, config.emoji.cassino.blackjack.diamonds, config.emoji.cassino.blackjack.clubs, config.emoji.cassino.blackjack.spades]
        ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        return [{'suit': suit, 'rank': rank} for suit in suits for rank in ranks]*8

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
