import random as rd
import stable_baselines3 as sb3
import numpy as np
import torch
import copy
import math

class Person:
    def __init__(self, iz: bool):
        self.isZombie = iz
        self.wasVaccinated = False
        self.turnsVaccinated = 0
        self.isVaccinated = False
        self.wasCured = False

    def clone(self):
        ret = Person(self.isZombie)
        ret.wasVaccinated = self.wasVaccinated
        ret.turnsVaccinated = self.turnsVaccinated
        ret.isVaccinated = self.isVaccinated
        ret.wasCured = self.wasCured
        return ret

    def get_bitten(self):
        """
        Decides whether a person becomes a zombie after getting bitten
        The chance of bite infection is:
        - 100% for a person who has never been vaccinated or cured
        - 75% for a person who has been vaccinated or cured but not both
        - 50% for a person who has been vaccinated and cured
        - 0% for a person who is currently vaccinated
        """
        chance = 1
        if self.isVaccinated:
            chance = 0
        elif self.wasVaccinated and self.wasCured:
            chance = 0.50
        elif self.wasVaccinated or self.wasCured:
            chance = 0.75

        if rd.random() < chance:
            self.isZombie = True

    def get_vaccinated(self):
        self.wasVaccinated = True
        self.isVaccinated = True
        self.turnsVaccinated = 1

    def get_cured(self):
        self.isZombie = False
        self.wasCured = True
        self.isVaccinated= True
        self.turnsVaccinated = 3

    def update(self):
        if self.isVaccinated:
            self.turnsVaccinated += 1
        if self.turnsVaccinated > 5:
            self.isVaccinated = False
            self.turnsVaccinated = 0

    def __str__(self) -> str:
        return f"Person who is a zombie? {self.isZombie}"

    def __repr__(self) -> str:
        return str(self)

    def __eq__(self, __o: object) -> bool:
        if type(__o) == Person:
            return (
                self.wasVaccinated == __o.wasVaccinated
                and self.turnsVaccinated == __o.turnsVaccinated
                and self.isVaccinated == __o.isVaccinated
                and self.isZombie == __o.isZombie
                and self.wasCured == __o.wasCured
            )
        return False

    def get_best_move(self, gameboard, position):
        if self.isZombie == False:
            return "Not avaliable", -100000000
        else:
            trained_model = sb3.PPO.load("./saved_zombie_models/ppov2.zip")
            obs = self._get_obs(position, gameboard)
            value = trained_model.policy.predict_values(torch.Tensor([obs]))
            action = trained_model.predict(obs)[0]
            ACTION_MAPPINGS = {
                0: "movebiteUp",
                1: "movebiteDown",
                2: "movebiteLeft",
                3: "movebiteRight",
            }
            a = self.process(gameboard, position, ACTION_MAPPINGS[action])
            if a is not None:
                action_name, pos = a
            else:
                action_name = "Not avaliable"
                value = -math.inf
                pos = -math.inf
            return action_name, pos, value
    
    def process(self, gameb, position, action_name):
        gameboard = copy.deepcopy(gameb)
        valid, new_pos = gameboard.actionToFunction["move" + action_name[8:]](
            self.board.toCoord(self.agentPosition)
        )
        if valid:
            action_name = "move" + action_name[8:]
            return action_name, new_pos
        else:  # bite variation
            dest_coord = list(gameboard.toCoord(position))
            if "Up" in action_name:
                dest_coord[1] -= 1
            elif "Down" in action_name:
                dest_coord[1] += 1
            elif "Right" in action_name:
                dest_coord[0] += 1
            else:
                dest_coord[0] -= 1
            valid, _ = self.board.actionToFunction["bite"](dest_coord)
            if valid:
                action_name = "bite"
                return action_name, dest_coord

    def _get_obs(self, position, gameboard):
        """
        Is based off the assumption that 5 is not in the returned board.
        Uses 5 as the key for current position.
        """
        AGENT_POSITION_CONSTANT = 5
        ret = gameboard.get_board()
        ret[position] = AGENT_POSITION_CONSTANT

        # normalize observation to be be centered at 0
        ret = np.array(ret, dtype=np.float32)
        ret /= np.float32(AGENT_POSITION_CONSTANT)
        ret -= np.float32(0.5)
        return ret  # (36, )
