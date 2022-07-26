from Resources import Resources
from State import State
import random as rd
from Person import Person
from typing import List, Tuple
from constants import *
import random


class Board:
    def __init__(
        self,
        dimensions: Tuple[int, int],
        player_role: str,
    ):
        self.rows = dimensions[0]
        self.columns = dimensions[1]
        self.player_role = player_role
        self.player_num = ROLE_TO_ROLE_NUM[player_role]
        self.safeEdge = random.choice(
            [
                [0, 1, 2, 3, 4, 5],
                [0, 6, 12, 18, 24, 30],
                [5, 11, 17, 23, 29, 35],
                [30, 31, 32, 33, 34, 35],
            ]
        )
        self.population = 0
        self.States = [State(None, s) for s in range(dimensions[0] * dimensions[1])]

        self.actionToFunction = {
            "moveUp": self.moveUp,
            "moveDown": self.moveDown,
            "moveLeft": self.moveLeft,
            "moveRight": self.moveRight,
            "heal": self.heal,
            "bite": self.bite,
        }
        self.resources = Resources(4)

    def getSafeEdge(self):
        return self.safeEdge

    def count_people(self, isZombie: bool) -> int:
        ret = 0
        for state in self.States:
            if state.person is not None and state.person.isZombie == isZombie:
                ret += 1
        return ret

    def num_zombies(self) -> int:
        return self.count_people(True)

    def num_people(self) -> int:
        return self.count_people(False)

    def containsPerson(self, isZombie: bool):
        for state in self.States:
            if state.person is not None and state.person.isZombie == isZombie:
                return True
        return False

    def coordsOf(self, isZombie: bool):
        """
        Returns the coordinates of the first occurrence of a
        person whose isZombie == isZombie. On failure, returns (-1, -1)
        """
        for idx in range(len(self.States)):
            state = self.States[idx]
            if state.person is not None and state.person.isZombie == isZombie:
                return self.toCoord(idx)
        return -1, -1

    def get_possible_moves(self, action: str, role: str):
        """
        Get the coordinates of people (or zombies) that are able
        to make the specified move.
        @param action - the action to return possibilities for (options are 'bite', 'moveUp', 'moveDown','moveLeft', 'moveRight', and 'heal')
        @param role - either 'Zombie' or 'Government'; helps decide whether an action
        is valid and which people/zombies it applies to
        """
        poss = []
        B = self.clone(self.States, role)

        if role == "Zombie":
            if not self.containsPerson(True):
                return poss
            for idx in range(len(self.States)):
                state = self.States[idx]
                if state.person is not None:
                    changed_states = False

                    if (
                        action == "bite"
                        and not state.person.isZombie
                        and self.isAdjacentTo(self.toCoord(idx), True)
                    ):
                        # if the current space isn't a zombie and it is adjacent
                        # a space that is a zombie
                        poss.append(B.toCoord(idx))
                        changed_states = True
                    elif (
                        action != "bite"
                        and state.person.isZombie
                        and B.actionToFunction[action](B.toCoord(idx))[0]
                    ):
                        poss.append(B.toCoord(idx))
                        changed_states = True

                    if changed_states:
                        # reset the states
                        B.States = [
                            self.States[i].clone()
                            if self.States[i] != B.States[i]
                            else B.States[i]
                            for i in range(len(self.States))
                        ]

        elif role == "Government":
            if not self.containsPerson(False):
                return poss
            for idx in range(len(self.States)):
                state = self.States[idx]
                if state.person is not None:
                    changed_states = False
                    if (
                        action == "heal"
                        and (
                            state.person.isZombie
                            or (
                                not state.person.isVaccinated
                                and idx in self.getSafeEdge()
                            )
                        )
                        and (
                            (state.person.isZombie and B.resources.spendOn("cure"))
                            or (
                                not state.person.isVaccinated
                                and B.resources.spendOn("vaccinate")
                            )
                        )
                    ):
                        poss.append(B.toCoord(idx))
                        changed_states = True
                    elif (
                        action != "heal"
                        and not state.person.isZombie
                        and B.actionToFunction[action](B.toCoord(idx))[0]
                    ):
                        poss.append(B.toCoord(idx))
                        changed_states = True

                    if changed_states:
                        # reset the states
                        B.States = [
                            self.States[i].clone()
                            if self.States[i] != B.States[i]
                            else B.States[i]
                            for i in range(len(self.States))
                        ]
                        B.resources = self.resources.clone()
        return poss

    def toCoord(self, i: int):
        return (int(i % self.columns), int(i / self.rows))

    def toIndex(self, coordinates: Tuple[int, int]):
        return int(coordinates[1] * self.columns) + int(coordinates[0])

    def isValidCoordinate(self, coordinates: Tuple[int, int]):
        return (
            coordinates[1] < self.rows
            and coordinates[1] >= 0
            and coordinates[0] < self.columns
            and coordinates[0] >= 0
        )

    def clone(self, L: List[State], role: str):
        NB = Board(
            (self.rows, self.columns),
            self.player_role,
        )
        NB.States = [state.clone() for state in L]
        NB.player_role = role
        NB.resources = self.resources.clone()
        return NB

    def isAdjacentTo(self, coord: Tuple[int, int], is_zombie: bool) -> bool:
        ret = False
        vals = [
            (coord[0], coord[1] + 1),
            (coord[0], coord[1] - 1),
            (coord[0] + 1, coord[1]),
            (coord[0] - 1, coord[1]),
        ]
        for coord in vals:
            if (
                self.isValidCoordinate(coord)
                and self.States[self.toIndex(coord)].person is not None
                and self.States[self.toIndex(coord)].person.isZombie == is_zombie
            ):
                ret = True
                break

        return ret

    def move(
        self, from_coords: Tuple[int, int], new_coords: Tuple[int, int]
    ) -> Tuple[bool, int]:
        """
        Check if the move is valid.
        If valid, then implement the move and return [True, destination_idx]
        If invalid, then return [False, None]
        If the space is currently occupied, then return [False, destination_idx]
        """
        # Get the start and destination index (1D)
        start_idx = self.toIndex(from_coords)
        destination_idx = self.toIndex(new_coords)

        # Check if the new coordinates are valid
        if not self.isValidCoordinate(new_coords):
            return [False, destination_idx]

        # Check if the destination is currently occupied
        if self.States[destination_idx].person is None:
            self.States[destination_idx].person = self.States[start_idx].person
            self.States[start_idx].person = None
            return [True, destination_idx]
        return [False, destination_idx]

    def moveUp(self, coords: Tuple[int, int]) -> Tuple[bool, int]:
        new_coords = (coords[0], coords[1] - 1)
        return self.move(coords, new_coords)

    def moveDown(self, coords: Tuple[int, int]) -> Tuple[bool, int]:
        new_coords = (coords[0], coords[1] + 1)
        return self.move(coords, new_coords)

    def moveLeft(self, coords: Tuple[int, int]) -> Tuple[bool, int]:
        new_coords = (coords[0] - 1, coords[1])
        return self.move(coords, new_coords)

    def moveRight(self, coords: Tuple[int, int]) -> Tuple[bool, int]:
        new_coords = (coords[0] + 1, coords[1])
        return self.move(coords, new_coords)

    def bite(self, coords: Tuple[int, int]) -> Tuple[bool, int]:
        if not self.isValidCoordinate(coords):
            return [False, None]
        i = self.toIndex(coords)
        if (
            self.States[i].person is None
            or self.States[i].person.isZombie
            or not self.isAdjacentTo(coords, True)
        ):
            return [False, None]
        self.States[i].person.get_bitten()
        return [True, i]

    def heal(self, coords: Tuple[int, int]) -> Tuple[bool, int]:
        """
        Cures or vaccinates the person at the stated coordinates.
        If there is a zombie there, the person will be cured.
        If there is a person there, the person will be vaccinated
        If no person is selected, then return [False, None]
        if a person is vaccinated, then return [True, index]
        """
        i = self.toIndex(coords)
        if self.States[i].person is None:
            return [False, None]
        p = self.States[i].person

        if p.isZombie:
            if self.isAdjacentTo(coords, False):  # zombie only cured if adjacent
                if self.resources.spendOn("cure"):
                    # 80% chance of getting cured (for now, # can be changed)
                    chance = 0.8
                    if rd.random() < chance:
                        p.get_cured()
                    else:
                        print("Cure Failed")
                        return [False, None]
                else:
                    return [False, None]
            else:
                return [False, None]
        else:
            if i in self.getSafeEdge():
                if self.resources.spendOn("vaccinate"):
                    p.get_vaccinated()
                else:
                    return [False, i]
            else:
                return [False, i]
        return [True, i]

    def populate(self, num_people=-1, num_zombies=4):
        """
        Populate the board
        @param num_people The number of people to make.
        If set to -1 (default), makes a random number of people
        between 7 and self.rows*self.columns/3. Note that the number of
        people is the number of people BEFORE infection
        @param num_zombies The number of zombies to make; defaults to 4
        """
        # make people
        total = num_people
        if total == -1:
            total = rd.randint(7, ((self.rows * self.columns) / 3))
        poss = []
        for x in range(len(self.States)):
            r = rd.randint(0, 100)
            if r < 60 and self.population < total:
                p = Person(False)
                self.States[x].person = p
                self.population = self.population + 1
                poss.append(x)
            else:
                self.States[x].person = None

        # make zombies
        used = []
        for x in range(num_zombies):
            s = rd.randint(0, len(poss) - 1)
            while s in used:
                s = rd.randint(0, len(poss) - 1)
            self.States[poss[s]].person.isZombie = True
            used.append(s)

    def update(self):
        """
        Update each of the states;
        This method should be called at the end of each round
        (after player and computer have each gone once)
        """
        for state in self.States:
            state.update()

        self.resources.update(self.num_people())

    def personAtIdx(self, idx: int):
        return self.States[idx].person

    def get_board(self):
        s = []
        for i in range(len(self.States)):
            state = self.States[i]
            # if state.wall != None:
            #    s.append(4)
            if state.person is not None:
                if state.person.isZombie:
                    s.append(2)
                else:
                    s.append(1)
            else:
                s.append(0)
        for i in self.getSafeEdge():
            if s[i] == 0:
                s[i] = 3
        return s
