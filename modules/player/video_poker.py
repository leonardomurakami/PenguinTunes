import random

from modules.globals import config


class VideoPokerDealer:
    def __init__(self):
        self.deck = self.create_deck()

    @staticmethod
    def create_deck():
        suits = [config.emoji.cassino.blackjack.hearts, config.emoji.cassino.blackjack.diamonds, config.emoji.cassino.blackjack.clubs, config.emoji.cassino.blackjack.spades]
        ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        return [{'suit': suit, 'rank': rank} for suit in suits for rank in ranks]

    def shuffle_deck(self):
        random.shuffle(self.deck)

    def deal_card(self):
        if not self.deck:
            self.deck = self.create_deck()
            self.shuffle_deck()
        return self.deck.pop(random.randrange(len(self.deck)))
    
    def deal(self, n):
        return [self.deal_card() for _ in range(n) if self.deck]

    def reset_deck(self) -> None:
        self.deck = self.create_deck()