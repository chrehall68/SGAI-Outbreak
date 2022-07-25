import random as rd


class Resources:
    # static variable since this should be easily accessible and changeable
    accumulationPerPerson = 1
    accumulationPerTurn = 0

    def __init__(self, starting_resources: int):
        self.resources = starting_resources
        self.costs = {"cure": rd.randint(5, 10), "vaccinate": rd.randint(5, 10), "wall": rd.randint(3,10)}

    def spendOn(self, item: str) -> bool:
        """
        Returns True on success (spent resources to buy the item),
        False on failure (failed to spend resources since there weren't enough)
        """
        assert item in self.costs
        if self.resources >= self.costs[item]:
            self.resources -= self.costs[item]
            return True
        return False

    def update(self, num_people: int) -> None:
        self.resources += num_people * Resources.accumulationPerPerson
        self.resources += Resources.accumulationPerTurn

    def clone(self):
        return Resources(self.resources)
