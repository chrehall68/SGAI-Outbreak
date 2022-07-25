from typing import Tuple
from Board import Board
from constants import *
import random as rd


class Player:
    """
    Base class for a player, takes
    random actions
    """

    def __init__(self, player_name) -> None:
        self.player_name = player_name

    def get_move(self, board: Board) -> Tuple[str, Tuple[int, int]]:
        # Make a list of all possible actions that the computer can take
        possible_actions = [
            ACTION_SPACE[i]
            for i in range(6)
            if (i != 4 and self.player_name == "Government")
            or (i != 5 and self.player_name == "Zombie")
        ]
        possible_move_coords = []
        while len(possible_move_coords) == 0 and len(possible_actions) != 0:
            print("possible actions are", possible_actions)
            action = possible_actions.pop(rd.randint(0, len(possible_actions) - 1))
            possible_move_coords = board.get_possible_moves(
                action, "Government" if self.player_name == "Zombie" else "Zombie"
            )

        # no valid moves, player wins
        if len(possible_actions) == 0 and len(possible_move_coords) == 0:
            print("no possible moves for the computer")
            if self.player_name == "Zombie":
                print(
                    f"The government ended with {board.resources.resources} resources"
                )
                print(
                    f"The price of vaccination was {board.resources.costs['vaccinate']} and the price of curing was {board.resources.costs['cure']}"
                )
            return False

        # Select the destination coordinates
        move_coord = rd.choice(possible_move_coords)
        print(f"choosing to go with {action} at {move_coord}")
        return (action, move_coord)


class GovernmentPlayer(Player):
    """
    Plays as the government
    """

    def __init__(self) -> None:
        super().__init__("Government")


class ZombiePlayer(Player):
    """
    Plays as the zombies
    """

    def __init__(self) -> None:
        super().__init__("Zombie")


class GovernmentAIPlayer(GovernmentPlayer):
    """
    Will be a smarter vwersion of the Human Player
    """

    def __init__(self) -> None:
        super().__init__()

    def get_move(self, board: Board) -> Tuple[str, Tuple[int, int]]:
        raise NotImplementedError("TODO")


class ZombieAIPlayer(ZombiePlayer):
    """
    Will be a smarter version of the Zombie Player
    """

    def __init__(self) -> None:
        super().__init__()

    def get_move(self, board: Board) -> Tuple[str, Tuple[int, int]]:
        raise NotImplementedError("TODO")
