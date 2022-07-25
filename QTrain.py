import numpy as np
import random as rd
import csv

episodes = 1000
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

        self.qtable = np.zeros(shape=(state_size, action_size))
        self.exploration_rate = 1
        self.GameBoard = GameBoard

    # TRAINING

    def updateCSVFile(self):
        with open("QTable.csv", 'w') as f:
            writer = csv.writer(f)
            writer.writerows(self.qtable)

    def readCSVFile(self):
        with open("QTable.csv", 'r') as f:
            tab = np.loadtxt(f, delimeter=',')
            self.qtable = tab

    def chooseMove(self, possible_states):
        player_states = possible_states  # contains all the states with people on it
        max_q_state = player_states[0]
        max_q_action = 0
        for curr_state in player_states:  # 0 to 35
            for q in range(curr_state.get_possible_player_actions()):  # 0 to 5
                if curr_state.get_possible_player_actions()[q] > max_q_state:
                    max_q_state = curr_state.get_possible_player_actions()
                    max_q_action = q
        action = max_q_action
        state = max_q_state
        coords = self.GameBoard.toCoord(state.location)
        if actions[action] == "healRight" or actions[action] == "killRight":
            coords = [coords[0] + 1, coords[1]]
        elif actions[action] == "healLeft" or actions[action] == "killLeft":
            coords = [coords[0] - 1, coords[1]]
        elif actions[action] == "healUp" or actions[action] == "killUp":
            coords = [coords[0], coords[1] + 1]
        elif actions[action] == "healDown" or actions[action] == "killDown":
            coords = [coords[0], coords[1] - 1]
        success, new_state_index = self.GameBoard.actionToFunction[
            actions[action]](coords)

    def train(self):
        for episode in range(episodes):

            for step in range(steps_per_game):
                player_states = []  # contains all the states with people on it
                action = rd.randint(0, 11)
                state = rd.choice(player_states)
                if rd.random() > self.exploration_rate:
                    max_q_state = player_states[0]
                    max_q_action = 0
                    for curr_state in player_states:  # 0 to 35
                        for q in range(curr_state):  # 0 to 5
                            if curr_state[q] > max_q_state:
                                max_q_state = curr_state
                                max_q_action = q
                    action = max_q_action
                    state = max_q_state
                coords = self.GameBoard.toCoord(state.location)
                if actions[action] == "healRight" or actions[action] == "killRight":
                    coords = [coords[0] + 1, coords[1]]
                elif actions[action] == "healLeft" or actions[action] == "killLeft":
                    coords = [coords[0] - 1, coords[1]]
                elif actions[action] == "healUp" or actions[action] == "killUp":
                    coords = [coords[0], coords[1] + 1]
                elif actions[action] == "healDown" or actions[action] == "killDown":
                    coords = [coords[0], coords[1] - 1]
                success, new_state_index = self.GameBoard.actionToFunction[
                    actions[action]](coords)
                new_state = self.GameBoard.States[new_state_index]

                wasBitten = self.zombieMove()

                reward = self.assign_reward(success, action, step, wasBitten)

                self.qtable[state, action] = (1 - learning_rate) * self.qtable[
                    state, action] + learning_rate * (
                        reward +
                        discount_rate * np.max(self.qtable[new_state, :]))
                self.updateCSVFile()

            if self.check_win() == True:
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

    def assign_reward(self, success, action, step, wasBitten):
        total_reward = 0
        if wasBitten == True:
            total_reward -= 10
        if success == False and action < 4:  # invalid move
            total_reward -= 1000
        if success == True and action < 4:  # successful move
            total_reward += 0
        if action == 4:  # heal
            total_reward += 10
        if action == 5:  # kill
            total_reward += 10
        if self.check_win(step):
            total_reward += 750
        return total_reward

    def check_win(self, step):
        if self.GameBoard.num_zombies() == 0 or step >= 100:
            return True
        return False
