import pygame
from Board import Board
from Player import GovernmentPlayer, ZombiePlayer
import PygameFunctions as PF
import random as rd
from constants import *

SELF_PLAY = True  # whether or not a human will be playing
player_role = "Government"  # Valid options are "Government" and "Zombie"
# Create the game board
GameBoard = Board((ROWS, COLUMNS), player_role)
GameBoard.populate()

# Self play variables
alpha = 0.1
gamma = 0.6
epsilon = 0.1
epochs = 1000
epochs_ran = 0
Original_Board = GameBoard.clone(GameBoard.States, GameBoard.player_role)

# Temp
print(GameBoard.getSafeEdge())


# Initialize variables
running = True
take_action = []
playerMoved = False

enemy_player = None
if player_role == "Government":
    enemy_player = ZombiePlayer()
else:
    enemy_player = GovernmentPlayer()

if SELF_PLAY:
    PF.initScreen(GameBoard)

while running:
    P = PF.run(GameBoard)

    if SELF_PLAY:
        if not playerMoved:
            if not GameBoard.containsPerson(False):
                PF.display_lose_screen()
                running = False
                continue
            # Event Handling
            for event in P:
                if event.type == pygame.MOUSEBUTTONUP:
                    x, y = pygame.mouse.get_pos()
                    action = PF.get_action(GameBoard, x, y)
                    if action == "heal" or action == "bite":
                        # only allow healing by itself (prevents things like ['move', (4, 1), 'heal'])
                        if len(take_action) == 0:
                            take_action.append(action)
                    elif action == "reset move":
                        take_action = []
                    elif action is not None:
                        idx = GameBoard.toIndex(action)
                        # action is a coordinate
                        if idx < (GameBoard.rows * GameBoard.columns) and idx > -1:
                            if "move" not in take_action and len(take_action) == 0:
                                # make sure that the space is not an empty space or a space of the opposite team
                                # since cannot start a move from those invalid spaces
                                if (
                                    GameBoard.States[idx].person is not None
                                    and GameBoard.States[idx].person.isZombie
                                    == ROLE_TO_ROLE_BOOLEAN[player_role]
                                ):
                                    take_action.append("move")
                                else:
                                    continue

                            # don't allow duplicate cells
                            if action not in take_action:
                                take_action.append(action)
                if event.type == pygame.QUIT:
                    running = False

            PF.display_cur_move(take_action)

            # Action handling
            if len(take_action) > 1:
                if take_action[0] == "move":
                    if len(take_action) > 2:
                        directionToMove = PF.direction(take_action[1], take_action[2])
                        result = GameBoard.actionToFunction[directionToMove](
                            take_action[1]
                        )
                        if result[0] is not False:
                            playerMoved = True
                        take_action = []

                elif take_action[0] == "heal" or take_action[0] == "bite":
                    result = GameBoard.actionToFunction[take_action[0]](take_action[1])
                    if result[0] is not False:
                        playerMoved = True
                    take_action = []

        # Computer turn
        else:
            playerMoved = False
            take_action = []

            action, move_coord = enemy_player.get_move(GameBoard)

            if not action:
                running = False
                PF.display_win_screen()
                continue
            # Implement the selected action
            GameBoard.actionToFunction[action](move_coord)

            # update the board's states
            GameBoard.update()

        # Update the display
        pygame.display.update()
        pygame.time.wait(75)

    else:
        pass  # TODO
