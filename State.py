from typing import Tuple
from Person import Person
import math


class State:
    def __init__(self, p: Person, i) -> None:
        self.person = p
        self.location = i
        pass

    def distance(self, GameBoard, other_location: int):
        first_coord = GameBoard.toCoord(self.location)
        second_coord = GameBoard.toCoord(other_location)
        a = second_coord[0] - first_coord[0]
        b = second_coord[1] - first_coord[1]
        a = a * a
        b = b * b
        return math.sqrt(a + b)

    def nearest_zombie(self, GameBoard):
        smallest_dist = 100
        for state in GameBoard.States:
            if state.person != None:
                if state.person.isZombie:
                    d = self.distance(GameBoard, state.location)
                    if d < smallest_dist:
                        smallest_dist = d
        return smallest_dist

    def evaluate(self, action: str, GameBoard):
        reward = 0
        reward += self.nearest_zombie(GameBoard) - 3
        if action == "heal":
            reward += 5
        elif action == "bite" and self.person.isZombie:
            chance = 0
            if self.person.wasCured:
                chance = 0.25
            reward = reward + int(5 * (2 + chance))
        return reward

    def get_adj_states(self, GameBoard):
        adj_states = []
        for state in GameBoard.States:
            self_coords = GameBoard.toCoord(self.location)
            other_coords = GameBoard.toCoord(state.location)
            if other_coords[0] == self_coords[0] + 1 and other_coords[1] == self_coords[1]:
                adj_states.append(state)
            elif other_coords[0] == self_coords[0] - 1 and other_coords[1] == self_coords[1]:
                adj_states.append(state)
            elif other_coords[1] == self_coords[1] + 1 and other_coords[0] == self_coords[0]:
                adj_states.append(state)
            elif other_coords[1] == self_coords[1] - 1 and other_coords[0] == self_coords[0]:
                adj_states.append(state)
        return adj_states

    def get_direction_to(self, other_state, GameBoard):
        self_coords = GameBoard.toCoord(self.location)
        other_coords = GameBoard.toCoord(other_state.location)
        
        dir = "On Same State"

        upCoords = GameBoard.toIndex((self_coords[0], self_coords[1]-1))
        downCoords = GameBoard.toIndex((self_coords[0], self_coords[1]+1))
        rightCoords = GameBoard.toIndex((self_coords[0]+1, self_coords[1]))
        leftCoords = GameBoard.toIndex((self_coords[0]-1, self_coords[1]))

        print(other_state.distance(GameBoard, upCoords), other_state.distance(GameBoard, downCoords),other_state.distance(GameBoard, rightCoords),other_state.distance(GameBoard, leftCoords))

        min_coords = min(other_state.distance(GameBoard, upCoords), other_state.distance(GameBoard, downCoords),other_state.distance(GameBoard, rightCoords),other_state.distance(GameBoard, leftCoords))
        if min_coords == upCoords:
            dir="moveUp"
        elif min_coords == downCoords:
            dir="moveDown"
        elif min_coords == rightCoords:
            dir='moveRight'
        elif min_coords == leftCoords:
            dir="moveLeft"
        # if other_coords[0] == self_coords[0] + 1:
        #     dir = "moveRight"
        # elif other_coords[0] == self_coords[0] - 1:
        #     dir = "moveLeft"
        # elif other_coords[1] == self_coords[1] - 1:
        #     dir = "moveUp"
        # elif other_coords[1] == self_coords[1] + 1:
        #     dir = "moveDown"
        return dir

    def get_possible_moves(self, GameBoard):
        adj_states = self.get_adj_states(GameBoard)
        poss_acts = ["moveRight", "moveLeft", "moveUp", "moveDown"]

        for state in adj_states:
            if state.person != None:
                self_coords = GameBoard.toCoord(self.location)
                other_coords = GameBoard.toCoord(state.location)
                
                if other_coords[0] == self_coords[0] + 1:
                    poss_acts.remove("moveRight")
                elif other_coords[0] == self_coords[0] - 1:
                    poss_acts.remove("moveLeft")
                elif other_coords[1] == self_coords[1] - 1:
                    poss_acts.remove("moveUp")
                elif other_coords[1] == self_coords[1] + 1:
                    poss_acts.remove("moveDown")
        
        self_coords = GameBoard.toCoord(self.location)
        if self_coords[0] == 5 and "moveRight" in poss_acts:
            poss_acts.remove("moveRight")
        if self_coords[0] == 0 and "moveLeft" in poss_acts:
            poss_acts.remove("moveLeft")
        if self_coords[1] == 0 and "moveUp" in poss_acts:
            poss_acts.remove("moveUp")
        if self_coords[1] == 5 and "moveDown" in poss_acts:
            poss_acts.remove("moveDown")

        return poss_acts
            
            

    def get_nearest_person(self, GameBoard):
        people_states = []
        for state in GameBoard.States:
            if state.person != None and not state.person.isZombie:
                people_states.append(state)
        dist = 100
        nearest_person_state = None
        for person in people_states:
            if self.distance(GameBoard, person.location) < dist:
                dist = self.distance(GameBoard, person.location)
                nearest_person_state = person
        return [nearest_person_state, dist]


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
        if self.person is None:
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
        if self.person is None:
            return
        self.person.update()

    def get_possible_player_actions (self, GameBoard): # returns number value
        actions = [
    "moveRight", "moveLeft", "moveUp", "moveDown", "healRight", "healLeft",
    "healUp", "healDown", "killRight", "killLeft", "killUp", "killDown"
]
        act = []
        x, y = GameBoard.toCoord(self.location)
        adjStates = self.get_adj_states(GameBoard)
        if x<5 and GameBoard.States[GameBoard.toIndex((x+1, y))].person is None:
            act.append(0) # 0 = move right
        if x>0 and GameBoard.States[GameBoard.toIndex((x-1, y))].person is None:
            act.append(1) # 1 = move left
        if y<5 and GameBoard.States[GameBoard.toIndex((x, y+1))].person is None:
            act.append(3)
        if y>0 and GameBoard.States[GameBoard.toIndex((x, y-1))].person is None:
            act.append(2)
        if x<5 and GameBoard.States[GameBoard.toIndex((x+1, y))].person is not None and GameBoard.States[GameBoard.toIndex((x+1, y))].person.isZombie==True: # right
            act.append(4) # right
            act.append(8)
        if x>0 and GameBoard.States[GameBoard.toIndex((x-1, y))].person is not None and GameBoard.States[GameBoard.toIndex((x-1, y))].person.isZombie==True: # right
            act.append(5) # left
            act.append(9)
        if y<5 and GameBoard.States[GameBoard.toIndex((x, y+1))].person is not None and GameBoard.States[GameBoard.toIndex((x, y+1))].person.isZombie==True: # right
            act.append(7) # bottom
            act.append(11)
        if y>0 and GameBoard.States[GameBoard.toIndex((x, y-1))].person is not None and GameBoard.States[GameBoard.toIndex((x, y-1))].person.isZombie==True: # right
            act.append(6) # top
            act.append(10)
        return act
        
        
