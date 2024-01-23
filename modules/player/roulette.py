import random

class Roulette:
    def __init__(self):
        self.result = self.spin_wheel()
        self.colors = {
            "red": [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36],
            "black": [2, 4, 6, 8, 10, 11, 13, 15, 17, 20, 22, 24, 26, 28, 29, 31, 33, 35],
            "green": [0]
        }
        self.payout = {
            "red": 1,
            "black": 1,
            "green": 35,
            "1st_12": 2,
            "2nd_12": 2,
            "3rd_12": 2,
            "1_to_18": 2,
            "19_to_36": 2,
            "even": 2,
            "odd": 2,
            "1st_row": 3,
            "2nd_row": 3,
            "3rd_row": 3
        }

    def remove_player(self):
        self.player = None

    def spin_wheel(self):
        self.winning_number = random.randint(0, 36)

    def announce_winner(self):
        if self.winning_number is None:
            print("Please spin the wheel first.")
        else:
            if self.player.selected_number == self.winning_number:
                print("Congratulations! You are the winner.")
            else:
                print("Better luck next time.")
    
    @property
    def is_red(self):
        return self.winning_number in self.colors["red"]
    
    @property
    def is_black(self):
        return self.winning_number in self.colors["black"]
    
    @property
    def is_1st_12(self):
        return self.winning_number in range(1, 13)
    
    @property
    def is_2nd_12(self):
        return self.winning_number in range(13, 25)
    
    @property
    def is_3rd_12(self):
        return self.winning_number in range(25, 37)
    
    @property
    def is_1_to_18(self):
        return self.winning_number in range(1, 19)
    
    @property
    def is_19_to_36(self):
        return self.winning_number in range(19, 37)
    
    @property
    def is_even(self):
        return self.winning_number%2 == 0
    
    @property
    def is_odd(self):
        return self.winning_number%2 != 0
    
    @property
    def is_green(self):
        return self.winning_number in self.colors["green"]
    
    @property
    def is_first_row(self):
        return self.winning_number%3 == 0
    
    @property
    def is_second_row(self):
        return self.winning_number%3 == 1
    
    @property
    def is_third_row(self):
        return self.winning_number%3 == 2
    
    