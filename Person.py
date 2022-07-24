import random as rd
import constants

class Person:
    def __init__(self, iz: bool):
        self.isZombie = iz
        self.wasCured = False
        self.zombieStage = 0 # stage 0 = human
        self.numMovesSinceTransformation = 0
        # stage 1 = intermed 1
        # stage 2 = intermed 2
        # stage 3 = full zombie

    def clone(self):
        ret = Person(self.isZombie)
        ret.wasCured = self.wasCured
        return ret

    def get_bitten(self):
        """
        Decides whether a person becomes a zombie after getting bitten
        The chance of bite infection is:
        - 100% for a person who has never been vaccinated or cured
        - 75% for a person who has been vaccinated or cured but not both
        - 50% for a person who has been vaccinated and cured
        - 0% for a person who is currently vaccinated
        """
        # chance = 1
        
        # if self.wasCured:
        #     chance = 0.75

        # if rd.random() < chance:
        self.zombieStage = 1
        self.isZombie = True

    def updateMovesSinceTransformation(self):
        if self.isZombie == True:
            self.numMovesSinceTransformation+=1
            if self.zombieStage==1:
                if self.numMovesSinceTransformation>=constants.NUM_MOVES_UNTIL_STAGE_2:
                    self.zombieStage=2
                    self.numMovesSinceTransformation=0
            elif self.zombieStage==2:
                if self.numMovesSinceTransformation>=constants.NUM_MOVES_UNTIL_STAGE_3:
                    self.zombieStage=3
                    self.numMovesSinceTransformation=0


    def get_cured(self):
        threshold = constants.CURE_SUCCESS_RATES[self.zombieStage]
        randNum = rd.random()

        if randNum < threshold:
            self.isZombie = False
            self.wasCured = True
            self.zombieStage = 0
            self.numMovesSinceTransformation = 0
            return True
        return False
        

    def kill_me (self):
        pass

    def update(self):
        return True

    def __str__(self) -> str:
        return f"Person who is a zombie? {self.isZombie}"

    def __repr__(self) -> str:
        return str(self)

    def __eq__(self, __o: object) -> bool:
        if type(__o) == Person:
            return (
                self.isZombie == __o.isZombie
                and self.wasCured == __o.wasCured
            )
        return False
