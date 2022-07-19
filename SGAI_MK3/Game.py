"""
Purpose of this file is to replace pygameFunctions.py and all the mess in main.py 
"""

from threading import Thread
from typing import List, Optional, Tuple
from Board import Board
from State import State
from Person import Person
from FrontEnd import FrontEnd
import pygame
from constants import *
import random as rd


class Game:
    # use none if training an agent
    metadata = {"render_modes": ["human", "none"]}

    def __init__(
        self,
        render_mode: str = "human",
        board_dimensions: Tuple[int, int] = (ROWS, COLUMNS),
        player_role: str = "Government",
    ):
        self.render_mode = render_mode
        self.board = Board(board_dimensions, player_role)
        self.board.populate()
        self.player_role = player_role
        self.done = False

        self.frontEnd = None
        if self.render_mode == "human":
            self.frontEnd = FrontEnd(
                board_dimensions[0],
                board_dimensions[1],
            )
            self.user_actions = []

        self.running = False
        self.is_player_turn = True

    def infinirender(self):
        while self.running and not self.done:
            self.render()

    def start(self):
        self.running = True

        if self.render_mode == "human":
            mythread = Thread(target=self.infinirender)
            mythread.start()

        while not self.done and self.running:
            self.step()
        mythread.join()

        if self.done:
            if self.won:
                self.frontEnd.display_win_screen()
            else:
                self.frontEnd.display_lose_screen()

    def render(self):
        assert self.render_mode == "human", "must be in render_mode 'human'"
        self.frontEnd.render(self.board, self.user_actions)

    def step(self, action=None):
        if self.is_player_turn:
            if action == None and self.render_mode == "human":
                self.process_user_action(self.frontEnd.handle_user_input())

                # Action handling
                if len(self.user_actions) > 1:
                    if self.user_actions[0] == "move":
                        if len(self.user_actions) > 2:
                            directionToMove = Board.direction(
                                self.user_actions[1], self.user_actions[2]
                            )
                            result = self.board.actionToFunction[directionToMove](
                                self.user_actions[1]
                            )
                            if result[0] is not False:
                                self.is_player_turn = False
                            self.user_actions = []

                    elif self.user_actions[0] == "heal":
                        result = self.board.heal(self.user_actions[1])
                        if result[0] is not False:
                            self.is_player_turn = False
                        self.user_actions = []
        else:  # take random computer move
            # Make a list of all possible actions that the computer can take
            possible_actions = [
                ACTION_SPACE[i]
                for i in range(6)
                if (i != 4 and self.player_role == "Government")
                or (i != 5 and self.player_role == "Zombie")
            ]
            possible_move_coords = []
            while len(possible_move_coords) == 0 and len(possible_actions) != 0:
                action = possible_actions.pop(rd.randint(0, len(possible_actions) - 1))
                possible_move_coords = self.board.get_possible_moves(
                    action, "Government" if self.player_role == "Zombie" else "Zombie"
                )

            # no valid moves, player wins
            if len(possible_actions) == 0 and len(possible_move_coords) == 0:
                self.done = True
                return

            # Select the destination coordinates
            move_coord = rd.choice(possible_move_coords)

            # Implement the selected action
            self.board.actionToFunction[action](move_coord)
            self.is_player_turn = True

        if self.board.over:
            self.done = True
            self.won = False
            if self.board.won:
                self.won = True

    def process_user_action(self, user_action: List):
        if len(user_action) == 0 or user_action[0] is None:
            return
        if user_action[0] is False:
            self.running = False  # user pressed the close button
            return
        # process the input
        for action in user_action:
            if action == "reset move":
                self.user_actions = []
            elif type(action) == str:
                if len(self.user_actions) == 0:
                    self.user_actions.append(action)
            else:
                # action is a coordinate
                idx = self.board.toIndex(action)
                if idx < (self.board.rows * self.board.columns) and idx > -1:
                    if "move" not in self.user_actions and len(self.user_actions) == 0:
                        # make sure that the space is not an empty space or a space of the opposite team
                        # since cannot start a move from those invalid spaces
                        if (
                            self.board.States[idx].person is not None
                            and self.board.States[idx].person.isZombie
                            == ROLE_TO_ROLE_BOOLEAN[self.player_role]
                        ):
                            self.user_actions.append("move")
                        else:
                            continue

                    # don't allow duplicate cells
                    if action not in self.user_actions:
                        self.user_actions.append(action)
