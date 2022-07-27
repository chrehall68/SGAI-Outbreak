from constants import *
import random as rd

class Wall:
    def __init__(self):
        self.turnsLeft = rd.randrange(MIN_WALL_DURATION, MAX_WALL_DURATION + 1)

    def update(self):
        if self.turnsLeft == 0:
            return False
        else:
            self.turnsLeft = self.turnsLeft - 1
        return True