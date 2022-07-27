import numpy as np
import random as rd
import csv

episodes = 500
steps_per_game = 100

#Update qtable Values
learning_rate = 0.8  # Learning rate
discount_rate = 0.95  # Discounting rate
state_size = 36
action_size = 12

max_exploration_rate = 1
min_exploration_rate = .01
exploration_decay_rate = .001

actions = [
    "moveRight", "moveLeft", "moveUp", "moveDown", "healRight", "healLeft",
    "healUp", "healDown", "killRight", "killLeft", "killUp", "killDown"
]


class QTrain:
    def __init__(self, GameBoard):

        # self.qtable = np.zeros(shape=(state_size, action_size))
        self.readCSVFile()
        self.exploration_rate = 1
        self.GameBoard = GameBoard
        self.DoubleQ = True
        print(len(self.qtable))

    # TRAINING

    def updateCSVFile(self):
        with open("QTable.csv", 'w') as f:
            writer = csv.writer(f)
            writer.writerows(self.qtable)

    def readCSVFile(self):
        with open("QTable.csv", 'r') as f:
            tab = np.loadtxt(f, delimiter=',')
            self.qtable = tab

    def chooseMove(self, possible_states):
        DoubleQ = self.DoubleQ
        player_states = possible_states  # contains all the states with people on it
        if(len(player_states) == 0):
            return
        max_q_state = player_states[0]
        max_q_action = 0
        for curr_state in player_states:  # 0 to 35
            for q in curr_state.get_possible_player_actions(self.GameBoard):  # 0 to 5
                if self.qtable[curr_state.location][q] > max_q_action:
                    if (rd.random() > 0.9 or q in range(5,12) or not DoubleQ) and len(curr_state.get_possible_player_actions(self.GameBoard)) > 1:
                        max_q_state = curr_state
                        max_q_action = q
        
        state = max_q_state
        action = max_q_action
        
        coords = self.GameBoard.toCoord(state.location)
        action_str = actions[action]
        if actions[action] == "healRight" or actions[action] == "killRight":
            coords = [coords[0] + 1, coords[1]]
        elif actions[action] == "healLeft" or actions[action] == "killLeft":
            coords = [coords[0] - 1, coords[1]]
        elif actions[action] == "healUp" or actions[action] == "killUp":
            coords = [coords[0], coords[1] - 1]
        elif actions[action] == "healDown" or actions[action] == "killDown":
            coords = [coords[0], coords[1] + 1]
        if actions[action] == "healRight" or actions[action] == "healLeft" or actions[action] == "healUp" or actions[action] == "healDown":
            action_str = "heal"
        if actions[action] == "killRight" or actions[action] == "killLeft" or actions[action] == "killUp" or actions[action] == "killDown":
            action_str = "kill"
        #if rd.random() > 0.95:
        #   state = rd.choice(possible_states)
        #  action = rd.choice(state.get_possible_player_actions(self.GameBoard))
        # action_str = actions[action]
        #coords = self.GameBoard.toCoord(state.location)

        success, new_state_index = self.GameBoard.actionToFunction[
            action_str](coords)
        if action_str == "heal" or action_str=="kill":
                new_state_index = state.location
        if DoubleQ:
            wasBitten = True if state.person is not None and state.person.isZombie else False

            reward = self.assign_reward_realtime(success, action, wasBitten)
            try:
                self.qtable[state.location][action] = (1 - learning_rate) * self.qtable[
                    state.location][action] + learning_rate * (
                        reward +
                        discount_rate * np.max(self.qtable[new_state_index]))
            except IndexError:
                print("q_table can't update")
            self.updateCSVFile()

    def train(self):
        action_list = []
        for episode in range(episodes):
            self.GameBoard.resetBoard()
            self.GameBoard.populate()
            for step in range(steps_per_game):
                player_states = self.GameBoard.getPlayerStates()  # contains all the states with people on it
                if(len(player_states) == 0):
                    break
                
                state = rd.choice(player_states)
                poss_actions = state.get_possible_player_actions(self.GameBoard)
                while len(poss_actions) == 0:
                    state = rd.choice(player_states)
                    poss_actions = state.get_possible_player_actions(self.GameBoard)
                action = rd.choice(poss_actions)
                if rd.random() > self.exploration_rate:
                    max_q_state = player_states[0]
                    max_q_action = 0
                    for curr_state in player_states:  # 0 to 35
                        for q in curr_state.get_possible_player_actions(self.GameBoard):  # 0 to 5
                            if self.qtable[curr_state.location][q] > max_q_action:
                                max_q_state = curr_state
                                max_q_action = q
                    action = max_q_action
                    state = max_q_state
                coords = self.GameBoard.toCoord(state.location)
                action_str = actions[action]
                if actions[action] == "healRight" or actions[action] == "killRight":
                    coords = [coords[0] + 1, coords[1]]
                elif actions[action] == "healLeft" or actions[action] == "killLeft":
                    coords = [coords[0] - 1, coords[1]]
                elif actions[action] == "healUp" or actions[action] == "killUp":
                    coords = [coords[0], coords[1] - 1]
                elif actions[action] == "healDown" or actions[action] == "killDown":
                    coords = [coords[0], coords[1] + 1]
                if actions[action] == "healRight" or actions[action] == "healLeft" or actions[action] == "healUp" or actions[action] == "healDown":
                    action_str = "heal"
                if actions[action] == "killRight" or actions[action] == "killLeft" or actions[action] == "killUp" or actions[action] == "killDown":
                    action_str = "kill"
                if coords[0]>5:
                    coords[0] = 5
                if coords[0]<0:
                    coords[0] = 0
                if coords[1]>5:
                    coords[1]=5
                if coords[1]<0:
                    coords[1]=0
                    
                action_list.append(action_str)
                if len(action_list) > 4:
                    action_list.pop(0)
                success, new_state_index = self.GameBoard.actionToFunction[
                    action_str](coords)
                
                if action_str == "heal" or action_str=="kill":
                    new_state_index = state.location
                

                new_state = self.GameBoard.States[new_state_index]

                wasBitten = self.zombieMove()

                reward = self.assign_reward(success, action, step, wasBitten, action_list, self.GameBoard.getPlayerStates())

                self.qtable[state.location][action] = (1 - learning_rate) * self.qtable[
                    state.location][action] + learning_rate * (
                        reward +
                        discount_rate * np.max(self.qtable[new_state_index]))
                self.updateCSVFile()

                if self.check_win(step) == True:
                    if step>=99:
                        print("BOZO")
                    else:
                        print(f'win {episode} {self.exploration_rate} {step}')
                    break

            self.exploration_rate = min_exploration_rate + (
                max_exploration_rate - min_exploration_rate) * np.exp(
                    -exploration_decay_rate * episode)


    def zombieMove(self):
        optimum_state = self.GameBoard.heuristic_state()
        if optimum_state != False:
            move_coord = self.GameBoard.toCoord(optimum_state.location)

            action = self.GameBoard.heuristic_action(optimum_state)
            if action == "bite":
                prev_state = optimum_state
                optimum_state = optimum_state.get_nearest_person(self.GameBoard)[0]
                move_coord = self.GameBoard.toCoord(optimum_state.location)
                self.GameBoard.actionToFunction[action](
                    move_coord, prev_state.person.zombieStage)
                return True  # bitten
            else:
                # Implement the selected action
                self.GameBoard.actionToFunction[action](move_coord)
                return False  # no bite

    def assign_reward(self, success, action, step, wasBitten, actList, livingPeople):
        total_reward = 0
        if wasBitten == True:
            total_reward -= 500
        if success == False and action < 4:  # invalid move
            total_reward -= 1000
        if success == True and action < 4:  # successful move
            total_reward += -25
        if action in [4,5,6,7]:  # heal
            total_reward += 1000
        if action in [8,9,10,11]:  # kill
            total_reward -= 250
        if self.check_win(step):
            total_reward += 1000-step*2+len(livingPeople)*100
        if len(actList) is 4 and actList[2] is not actList[3] and actList[2:3] is actList[0:1]:
            total_reward -= 100
        return total_reward
    
    def assign_reward_realtime(self, success, action, wasBitten):
        total_reward = 0
        if wasBitten == True:
            total_reward -= 500
        if success == False and action < 4:  # invalid move
            total_reward -= 1000
        if success == True and action < 4:  # successful move
            total_reward += -25
        if action in [4,5,6,7]:  # heal
            total_reward += 1000
        if action in [8,9,10,11]:  # kill
            total_reward -= 250
        return total_reward

    def check_win(self, step):
        if self.GameBoard.num_zombies() == 0 or step >= 100:
            return True
        return False
