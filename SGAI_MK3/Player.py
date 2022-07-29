from abc import abstractmethod
from typing import Dict, Tuple, List, Union

import numpy as np
from Board import Board
from constants import *
import random as rd


class Player:
    """
    Base class for a player, takes
    random actions
    """

    def __init__(self, player_name, verbose=False) -> None:
        self.player_name = player_name
        self.verbose = verbose

    def get_all_possible_actions(
        self, board: Board
    ) -> Dict[str, List[Tuple[int, int]]]:
        possible_actions = [
            ACTION_SPACE[i]
            for i in range(len(ACTION_SPACE))
            if (i != 5 and self.player_name == "Government")
            or (i != 4 and self.player_name == "Zombie")
        ]
        ret = {}
        for action in possible_actions:
            ret[action] = board.get_possible_moves(
                action, "Zombie" if self.player_name == "Zombie" else "Government"
            )
        return ret

    def get_move(self, board: Board) -> Tuple[str, Tuple[int, int]]:
        # Make a list of all possible actions that the computer can take
        possible_actions = [
            ACTION_SPACE[i]
            for i in range(len(ACTION_SPACE))
            if (i != 5 and self.player_name == "Government")
            or (i != 4 and self.player_name == "Zombie")
        ]
        possible_move_coords = []
        while len(possible_move_coords) == 0 and len(possible_actions) != 0:
            if self.verbose:
                print("possible actions are", possible_actions)
            action = possible_actions.pop(rd.randint(0, len(possible_actions) - 1))
            possible_move_coords = board.get_possible_moves(
                action, "Zombie" if self.player_name == "Zombie" else "Government"
            )

        # no valid moves, player wins
        if len(possible_actions) == 0 and len(possible_move_coords) == 0:
            if self.verbose:
                print("no possible moves for the computer")
                if self.player_name == "Zombie":
                    print(
                        f"The government ended with {board.resources.resources} resources"
                    )
                    print(
                        f"The price of vaccination was {board.resources.costs['vaccinate']} and the price of curing was {board.resources.costs['cure']}"
                    )
            return False, None

        # Select the destination coordinates
        move_coord = rd.choice(possible_move_coords)
        if self.verbose:
            print(f"choosing to go with {action} at {move_coord}")
        return (action, move_coord)


class GovernmentPlayer(Player):
    """
    Plays as the government
    """

    def __init__(self, verbose=False) -> None:
        super().__init__("Government", verbose)


class ZombiePlayer(Player):
    """
    Plays as the zombies
    """

    def __init__(self, verbose=False) -> None:
        super().__init__("Zombie", verbose)


class GovernmentAIPlayer(GovernmentPlayer):
    """
    Will be a smarter version of the Human Player
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


class MiniMaxPlayer(Player):
    def __init__(self, player_name, verbose=False, lookahead: int = 3) -> None:
        super().__init__(player_name, verbose)
        self.lookahead = 3

    @abstractmethod
    def _get_value(self, board: Board) -> float:
        raise NotImplementedError(
            "_get_value must be implemented in a subclass of MinimaxPlayer"
        )

    def _minimax_val(
        self,
        board: Board,
        self_turn: bool,
        depth: int,
        alpha: Union[float, int],
        beta: Union[float, int],
    ) -> int:
        """
        Returns the highest value possible from a state
        If depth is 0, returns the board's current value.
        If not self turn, returns the least possible value possible from the board
        @param alpha - the best case found so far for the maximizing player (highest reachable val)
        @param beta - the best case found so far for the minimizing player (lowest reachable val)
        """
        if depth == 0:
            return self._get_value(board)

        mappings = (self if self_turn else self.enemyPlayer).get_all_possible_actions(
            board
        )
        ret = float("-inf" if self_turn else "inf")
        for action, lst in mappings.items():
            for coord in lst:
                clone = board.clone(board.States.copy(), board.player_role)
                clone.actionToFunction[action](coord)
                value = self._minimax_val(clone, not self_turn, depth - 1, alpha, beta)
                if self_turn:
                    ret = max(ret, value)
                    alpha = max(alpha, ret)

                    # alpha beta pruning
                    if beta <= alpha:
                        return ret
                else:
                    ret = min(value, ret)
                    beta = min(beta, ret)

                    # alpha beta pruning
                    if alpha <= beta:
                        return ret

        return ret

    def get_moves(self, board: Board) -> Dict[str, List[Tuple[int, int]]]:
        mappings = self.get_all_possible_actions(board)
        max_val = float("-inf")
        action_coordlists = {}
        for action, lst in mappings.items():
            for coord in lst:
                clone = board.clone(board.States.copy(), board.player_role)
                clone.actionToFunction[action](coord)
                val = self._minimax_val(
                    clone, False, self.lookahead - 1, float("-inf"), float("inf")
                )
                if val > max_val:
                    action_coordlists.clear()
                    max_val = val
                    action_coordlists[action] = [coord]
                if val == max_val:
                    if action not in action_coordlists:
                        action_coordlists[action] = [coord]
                    else:
                        action_coordlists[action].append(coord)
        return action_coordlists


class GovernmentMinimaxPlayer(MiniMaxPlayer):
    """
    Government player, minimaxed
    """

    def __init__(self, lookahead: int = 3) -> None:
        """
        Initializes a GovernmentMinimaxPlayer
        @param lookahead How far to look ahead
        """
        super().__init__("Government", lookahead=lookahead)
        self.enemyPlayer = ZombiePlayer()

    def _get_value(self, board: Board) -> int:
        """
        Returns how valuable a board is.
        Rewards based on # of people on the board
        """
        zombie_count = 0
        zombie_x = 0
        zombie_y = 0

        people_count = 0
        people_x = 0
        people_y = 0
        for idx in range(len(board.States)):
            state = board.States[idx]
            if state.person is not None:
                x, y = board.toCoord(idx)
                if state.person.isZombie:
                    zombie_x += x
                    zombie_y += y
                    zombie_count += 1
                else:
                    people_x += x
                    people_y += y
                    people_count += 1

        if people_count != 0 and zombie_count != 0:
            people_x /= people_count
            people_y /= people_count
            zombie_x /= zombie_count
            zombie_y /= zombie_count
            return people_count + 0.75 * (
                1 + np.sqrt((people_x - zombie_x) ** 2 + (people_y - zombie_y) ** 2)
            )

        return people_count

    def get_move(self, board: Board) -> Tuple[str, Tuple[int, int]]:
        action_coordlists = self.get_moves(board)

        if len(action_coordlists) == 0:
            return None, (-1, -1)

        if "cure" in action_coordlists:
            action = "cure"
        elif "vaccinate" in action_coordlists:
            action = "vaccinate"
        else:
            action = rd.choice(tuple(action_coordlists.keys()))
        return action, rd.choice(action_coordlists[action])


class ZombieMinimaxPlayer(MiniMaxPlayer):
    """
    Zombie player, minimaxed
    """

    def __init__(self, lookahead: int = 3) -> None:
        """
        Initializes a ZombieMinimaxPlayer
        @param lookahead How far to look ahead
        """
        super().__init__("Zombie", lookahead=lookahead)
        self.enemyPlayer = GovernmentPlayer()

    def _get_value(self, board: Board) -> int:
        """
        Returns how valuable a board is.
        Rewards based on # of zombies on the board
        and distance between people centroid and zombie centroid
        """
        zombie_count = 0
        zombie_x = 0
        zombie_y = 0

        people_count = 0
        people_x = 0
        people_y = 0
        for idx in range(len(board.States)):
            state = board.States[idx]
            if state.person is not None:
                x, y = board.toCoord(idx)
                if state.person.isZombie:
                    zombie_x += x
                    zombie_y += y
                    zombie_count += 1
                else:
                    people_x += x
                    people_y += y
                    people_count += 1

        if people_count != 0 and zombie_count != 0:
            people_x /= people_count
            people_y /= people_count
            zombie_x /= zombie_count
            zombie_y /= zombie_count
            return zombie_count + 0.75 / (
                1 + np.sqrt((people_x - zombie_x) ** 2 + (people_y - zombie_y) ** 2)
            )
        return zombie_count

    def get_move(self, board: Board) -> Tuple[str, Tuple[int, int]]:
        action_coordlists = self.get_moves(board)

        if len(action_coordlists) == 0:
            return None, (-1, -1)

        if "bite" in action_coordlists:
            action = "bite"
        else:
            action = rd.choice(tuple(action_coordlists.keys()))
        return action, rd.choice(action_coordlists[action])
