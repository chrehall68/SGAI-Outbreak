from numpy import number
import pygame
from Board import Board
import PygameFunctions as PF
import random as rd
from constants import *
import constants
import time
import QTrain as qt

SELF_PLAY = True  # whether or not a human will be playing
player_role = "Zombie"  # Valid options are "Government" and "Zombie"
# Create the game board
GameBoard = Board((ROWS, COLUMNS), player_role)
qtrainer = qt.QTrain(GameBoard)
GameBoard.populate()



# Self play variables
alpha = 0.1
gamma = 0.6
epsilon = 0.1
epochs = 1000
epochs_ran = 0
Original_Board = GameBoard.clone(GameBoard.States, GameBoard.player_role)


# Initialize variables
running = True
take_action = []
playerMoved = False
justStarted = True
IS_PLAYER_TURN = 1
lose = False

while running:
    if constants.number_steps>=100 or lose:
        PF.display_win_screen()
        running = False
        continue
            
    P = PF.run(GameBoard)
    if SELF_PLAY:
        if not GameBoard.containsPerson(False):
            PF.display_lose_screen()
            running = False
            continue
        # Event Handling
        for event in P:
            if event.type == pygame.MOUSEBUTTONUP:
                x, y = pygame.mouse.get_pos()
                action = PF.get_action(GameBoard, x, y)
                
                if action == "heal" or action == "bite" or action == "kill":
                    # only allow healing by itself (prevents things like ['move', (4, 1), 'heal'])
                    if len(take_action) == 0:
                        take_action.append(action)
                    else:
                        take_action = []
                        take_action.append(action)
                    PF.display_curr_action(action)
                elif action == "reset move":
                    take_action = []
                    PF.reset_images()
                elif action == "try again":
                    GameBoard.resetBoard()
                    GameBoard.populate()
                elif action == "quit":
                    running = False
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
                            # prevent players from moving in invalid spaces
                            if take_action[0]=="move" and len(take_action)==2: 
                                curr_x, curr_y = take_action[1]
                                new_x, new_y = action
                                if (new_x==curr_x and curr_y==new_y+1) or (new_x==curr_x and curr_y==new_y-1) or (new_x==curr_x+1 and curr_y==new_y) or (new_x==curr_x-1 and curr_y==new_y):
                                    take_action.append(action)
                                else:
                                    PF.get_last_move('Government', None,None)
                                    take_action = []
                                    PF.reset_images()
                            else:
                                take_action.append(action)
            if event.type == pygame.QUIT:
                running = False

        PF.display_cur_move(take_action)

        # Action handling
        if player_role == "Zombie":
            time.sleep(.3)
            if len(GameBoard.getZombieStates()) == 0:
                PF.display_win_screen()
                running = False
                continue
            if constants.number_steps>=100:
                PF.display_win_screen()
                running = False
                continue
            constants.number_steps+=1

            qtrainer.chooseMove(GameBoard.getPlayerStates())
            GameBoard.updateMovesSinceTransformation()
            time.sleep(.3)

            optimum_state = GameBoard.heuristic_state()
            if optimum_state != False:
                move_coord = GameBoard.toCoord(optimum_state.location)
                
                action = GameBoard.heuristic_action(optimum_state)
                if action == "bite":
                    prev_state = optimum_state
                    optimum_state = optimum_state.get_nearest_person(GameBoard)[0]
                    move_coord = GameBoard.toCoord(optimum_state.location)
                    GameBoard.actionToFunction[action](move_coord, prev_state.person.zombieStage)
                else:
                    # Implement the selected action
                    GameBoard.actionToFunction[action](move_coord)
            
        else:
            if len(take_action) > 1:
                if take_action[0] == "move":
                    if len(take_action) > 2:
                        directionToMove = PF.direction(take_action[1], take_action[2])
                        result = GameBoard.actionToFunction[directionToMove](take_action[1])
                        
                        if result[0] is not False:
                            playerMoved = True
                            
                        PF.get_last_move('Government',take_action[0],None)
                        take_action = []
                        PF.reset_images()
                        GameBoard.updateMovesSinceTransformation()
                        continue

                elif take_action[0] == "heal" or take_action[0]=="kill":
                    if GameBoard.num_zombies() > 1 or not justStarted:
                        justStarted = False
                        result = GameBoard.actionToFunction[take_action[0]](take_action[1])
                        
                        print(result)
                        print(take_action[0])
                        if result[0] is not False:
                            playerMoved = True
                            
                        if (result[2] is not None):
                            PF.get_last_move('Government',take_action[0],result[2])
                        else:
                            PF.get_last_move('Government',None,None)
                        take_action = []
                        PF.reset_images()
                        GameBoard.updateMovesSinceTransformation()
                        continue
                    else:
                        take_action = []
                        PF.reset_images()

                elif take_action[0] == "bite":
                    result = GameBoard.actionToFunction[take_action[0]](take_action[1])
                    
                    if result[0] is not False:
                        playerMoved = True
                        
                    take_action = []
                    PF.reset_images()
                    continue

        # Computer turn
       
        if playerMoved:
            constants.number_steps+=1
            playerMoved = False
            take_action = []
            PF.reset_images()
            GameBoard.update() # UPDATE BOARD BEFORE ZOMBIE MOVE SO THE DELAY CAN HAPPEN
            
            
            
            pygame.display.update()
            
            # PF.run(GameBoard) # do this to update display

            time.sleep(1)
            # pygame.time.delay(TIME_BETWEEN_ZOMBIE_MOVE)
            

            # Make a list of all possible actions that the computer can take
            possible_actions = [
                ACTION_SPACE[i]
                for i in range(6)
                if (i != 4 and player_role == "Government")
                or (i != 5 and player_role == "Zombie")
            ]
            possible_move_coords = []
            while len(possible_move_coords) == 0 and len(possible_actions) != 0:
                action = possible_actions.pop(rd.randint(0, len(possible_actions) - 1))
                possible_move_coords = GameBoard.get_possible_moves(
                    action, "Government" if player_role == "Zombie" else "Zombie"
                )

            # no valid moves, player wins
            if len(possible_actions) == 0 and len(possible_move_coords) == 0:
                PF.display_win_screen()
                running = False
                continue

            # Select the destination coordinates
            move_coord = rd.choice(possible_move_coords)

            

            #Override Q-Choice with Heuristics if heuristic zombies is true
            HeuristicZombies = True
            if player_role == "Government":
                optimum_state = GameBoard.heuristic_state()
                if optimum_state != False:
                    move_coord = GameBoard.toCoord(optimum_state.location)
                    
                    action = GameBoard.heuristic_action(optimum_state)
                    if action == "bite":
                        prev_state = optimum_state
                        optimum_state = optimum_state.get_nearest_person(GameBoard)[0]
                        move_coord = GameBoard.toCoord(optimum_state.location)
                        result = GameBoard.actionToFunction[action](move_coord, prev_state.person.zombieStage)
                        
                        PF.get_last_move('Zombie','bite',result[2])
                        print(result)
                    else:
                        # Implement the selected action
                        GameBoard.actionToFunction[action](move_coord)
                        PF.get_last_move('Zombie','move',None)
            else:
                qtrainer.chooseMove(GameBoard.getPlayerStates())
            

            # update the board's states
            GameBoard.update()
            
            
            

        # Update the display
        pygame.display.update()

    else:
        if epochs_ran % 100 == 0:
            print("Board Reset!")
            GameBoard = Original_Board  # reset environment
        for event in P:
            i = 0
            r = rd.uniform(0.0, 1.0)
            st = rd.randint(0, len(GameBoard.States) - 1)
            state = GameBoard.QTable[st]

            if r < gamma:
                while GameBoard.States[st].person is None:
                    st = rd.randint(0, len(GameBoard.States) - 1)
            else:
                biggest = None
                for x in range(len(GameBoard.States)):
                    arr = GameBoard.QTable[x]
                    exp = sum(arr) / len(arr)
                    if biggest is None:
                        biggest = exp
                        i = x
                    elif biggest < exp and player_role == "Government":
                        biggest = exp
                        i = x
                    elif biggest > exp and player_role != "Government":
                        biggest = exp
                        i = x
                state = GameBoard.QTable[i]
            b = 0
            j = 0
            ind = 0
            for v in state:
                if v > b and player_role == "Government":
                    b = v
                    ind = j
                elif v < b and player_role != "Government":
                    b = v
                    ind = j
                j += 1
            action_to_take = ACTION_SPACE[ind]
            old_qval = b
            old_state = i

            # Update
            # Q(S, A) = Q(S, A) + alpha[R + gamma * max_a Q(S', A) - Q(S, A)]
            reward = GameBoard.act(old_state, action_to_take)
            ns = reward[1]
            NewStateAct = GameBoard.QGreedyat(ns)
            NS = GameBoard.QTable[ns][NewStateAct[0]]
            # GameBoard.QTable[i] = GameBoard.QTable[i] + alpha * (reward[0] + gamma * NS) - GameBoard.QTable[i]
            if GameBoard.num_zombies() == 0:
                print("winCase")

            take_action = []
            PF.reset_images()
            print("Enemy turn")
            ta = ""
            if player_role == "Government":
                r = rd.randint(0, 5)
                while r == 4:
                    r = rd.randint(0, 5)
                ta = ACTION_SPACE[r]
            else:
                r = rd.randint(3, 4)
                ta = ACTION_SPACE[r]
            poss = GameBoard.get_possible_moves(ta, "Zombie")

            if len(poss) > 0:
                r = rd.randint(0, len(poss) - 1)
                a = poss[r]
                GameBoard.actionToFunction[ta](a)
            if GameBoard.num_zombies() == GameBoard.population:
                print("loseCase")
            if event.type == pygame.QUIT:
                running = False
print(take_action)