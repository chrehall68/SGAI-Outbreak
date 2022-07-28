from typing import Tuple
from Person import Person
import math


class State:
    def __init__(self, p: Person, i) -> None:
        self.person = p
        self.location = i
        self.wall = None
        pass

    def distance(self, GameBoard, other_location: int):
        first_coord = GameBoard.toCoord(self.location)
        second_coord = GameBoard.toCoord(other_location)
        a = second_coord[0] - first_coord[0]
        b = second_coord[1] - first_coord[1]
        a = a * a
        b = b * a
        return math.pow(int(a + b), 0.5)

    def nearest_zombie(self, GameBoard):
        smallest_dist = 100
        for state in GameBoard.States:
            if state.person != None:
                if state.person.isZombie:
                    d = self.distance(GameBoard, state.location)
                    if d < smallest_dist:
                        smallest_dist = d
        return smallest_dist

    # returns the number of moves a person/zombie would have to take to get to another person/zombie
    # "zombie" is for whether to look for the nearest zombie or person
    def nearest_person(self, GameBoard, zombie: bool):
        location = self.location
        dRow = [-1, 0, 1, 0]
        dCol = [0, 1, 0, -1]
        visited = [False for i in range(36)]
        toVisit = [[location, 0]] # current location, num moves to get there
        visited[location] = True
        while len(toVisit) > 0:
            loc, moves = toVisit.pop(0)
            visited[loc] = True
            for i in range(4):
                coords = list(GameBoard.toCoord(loc))
                coords[0] += dRow[i]
                coords[1] += dCol[i]
                newLoc = GameBoard.toIndex(coords)
                if GameBoard.isValidCoordinate(coords):
                    if visited[newLoc] == False:
                        visited[newLoc] = True
                        if (GameBoard.States[newLoc].person != None
                            and GameBoard.States[newLoc].person.isZombie == zombie
                        ):
                            return moves
                        if (GameBoard.States[newLoc].wall == None
                            and GameBoard.States[newLoc].person == None
                        ):
                            toVisit.append([newLoc, moves + 1])
        # no possible path
        return None

    def evaluate(self, action: str, GameBoard):
        reward = 0
        reward += self.nearest_zombie(GameBoard) - 3
        if action == "heal":
            reward += 5
        elif action == "bite" and self.person.isZombie:
            chance = 0
            if self.person.wasVaccinated != self.person.wasCured:
                chance = 0.25
            if self.person.wasVaccinated and self.person.wasCured:
                chance = 0.5
            reward = reward + int(5 * (2 + chance))
        return reward

    def adjacent(self, GameBoard):
        newCoord = GameBoard.toCoord(self.location)
        moves = [
            (newCoord[0], newCoord[1] - 1),
            (newCoord[0], newCoord[1] + 1),
            (newCoord[0] - 1, newCoord[1]),
            (newCoord[0] + 1, newCoord[1]),
        ]
        remove = []
        for i in range(4):
            move = moves[i]
            if (
                move[0] < 0
                or move[0] > GameBoard.columns
                or move[1] < 0
                or move[1] > GameBoard.rows
            ):
                remove.append(i)
        remove.reverse()
        for r in remove:
            moves.pop(r)
        return moves

    def clone(self):
        if self.wall is not None:
            s = State(None, self.location)
            s.wall = self.wall
            return s
        elif self.person is None:
            return State(self.person, self.location)
        return State(self.person.clone(), self.location)

    def __eq__(self, __o: object) -> bool:
        if type(__o) == State:
            return self.person == __o.person and self.location == __o.location
        return False

    def __ne__(self, __o: object) -> bool:
        return not self == __o

    def update(self):
        """
        If this has a person, update the person within.
        """
        if self.wall is not None:
            ret = self.wall.update()
            if not ret:
                self.wall = None
            return
        elif self.person is None:
            return
        self.person.update()
