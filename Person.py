import random as rd


class Person:
    def __init__(self, iz: bool):
        self.isZombie = iz
        self.wasCured = False

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
        chance = 1
        
        if self.wasCured:
            chance = 0.75

        if rd.random() < chance:
            self.isZombie = True


    def get_cured(self):
        self.isZombie = False
        self.wasCured = True

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
