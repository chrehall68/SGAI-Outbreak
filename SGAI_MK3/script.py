# %% [markdown]
# # SGAI models (DQN)

# %% [markdown]
# This notebook is based off of the pytorch tutorial [here](https://pytorch.org/tutorials/intermediate/reinforcement_q_learning.html). It is intended to both create and train models for Courtney2-Outbreak. View on Colab [here](https://drive.google.com/file/d/1paNMxYQ6wVQ8c5bKJf-u3rHDcqgpKOB0/view?usp=sharing).

# %% [markdown]
# ### Setup

# %%
import pickle
import sys
import numpy as np
from collections import namedtuple, Counter
from queue import deque
import random
import math
from typing import List
from tqdm import tqdm  # used for progress meters
from time import sleep

sys.path.append("./")  # make sure that it is able to import Board

from Board import Board
from constants import *
from Player import ZombiePlayer, GovernmentPlayer


def main():

    import tensorflow as tf
    import keras.layers as layers
    import keras.models as models
    import keras

    # %%
    DEVICE = "GPU"
    # tf.debugging.set_log_device_placement(True)
    devices = tf.config.list_physical_devices(DEVICE)
    if DEVICE == "GPU":
        tf.config.experimental.set_memory_growth(devices[0], True)

    # %% [markdown]
    # ### Training Environments

    # %%
    class ZombieEnvironment:
        ACTION_MAPPINGS = {
            0: "movebiteUp",
            1: "movebiteDown",
            2: "movebiteLeft",
            3: "movebiteRight",
        }
        ACTION_SPACE = tuple(range(len(ACTION_MAPPINGS)))
        SIZE = (6, 6)

        def __init__(
            self,
            max_timesteps: int = 300,
            have_enemy_player: bool = True,
            logdir: str = "",
            run_name="",
        ) -> None:
            self.max_timesteps = max_timesteps
            self.reset()
            self.total_timesteps = 0
            self.total_invalid_moves = 0
            self.writer = None
            if logdir != "" and run_name != "":
                self.writer = tf.summary.create_file_writer(f"{logdir}/{run_name}")
            self.have_enemy_player = have_enemy_player

        def reset(self):
            self.board = Board(ZombieEnvironment.SIZE, "Zombie")
            self.board.populate(num_zombies=1)
            self.enemyPlayer = GovernmentPlayer()
            self.done = False

            # coordinates of the first zombie
            self.agentPosition = self.board.indexOf(True)

            # useful for metrics
            self.max_number_of_zombies = 1
            self.episode_invalid_actions = 0
            self.episode_reward = 0
            self.episode_timesteps = 0

            return self._get_obs()

        def step(self, action: int):
            action_name = ZombieEnvironment.ACTION_MAPPINGS[action]

            # first, try to move
            valid, new_pos = self.board.actionToFunction["move" + action_name[8:]](
                self.board.toCoord(self.agentPosition)
            )
            if valid:
                self.agentPosition = new_pos
                action_name = "move"
            else:  # bite variation
                dest_coord = list(self.board.toCoord(self.agentPosition))
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

            won = None
            # do the opposing player's action if the action was valid.
            if valid:
                _action, coord = self.enemyPlayer.get_move(self.board)
                if not _action:
                    self.done = True
                    won = True
                else:
                    if self.have_enemy_player:
                        self.board.actionToFunction[_action](coord)
                self.board.update()

            # see if the game is over
            if not self.board.States[
                self.agentPosition
            ].person.isZombie:  # zombie was cured
                self.done = True
                won = False
            if not self.board.is_move_possible_at(
                self.agentPosition
            ):  # no move possible
                self.done = True
            if self.episode_timesteps > self.max_timesteps:
                self.done = True
            if not valid:
                self.done = True

            # get obs, reward, done, info
            obs, reward, done, info = (
                self._get_obs(),
                self._get_reward(action_name, valid, won),
                self._get_done(),
                self._get_info(),
            )

            # update the metrics
            self.episode_reward += reward
            if not valid:
                self.episode_invalid_actions += 1
                self.total_invalid_moves += 1
            self.episode_timesteps += 1
            self.max_number_of_zombies = max(
                self.board.num_zombies(), self.max_number_of_zombies
            )
            self.total_timesteps += 1

            # write the metrics
            if self.writer is not None:
                with self.writer.as_default():
                    tf.summary.scalar(
                        "train/invalid_action_rate",
                        self.total_invalid_moves / self.total_timesteps,
                        step=self.total_timesteps,
                    )
                    tf.summary.scalar(
                        "train/cur_reward", reward, step=self.total_timesteps
                    )

            # return the obs, reward, done, info
            return obs, reward, done, info

        def _get_info(self):
            return {}

        def _get_done(self):
            return self.done

        def _get_reward(self, action_name: str, was_valid: bool, won: bool):
            """
            Gonna try to return reward between [-1, 1]
            """
            if not was_valid:
                return -1
            if won is True:
                return 1
            if won is False:
                return -0.1
            if "bite" in action_name:
                return 0.9
            return -0.01  # this is the case where it was move

        def _get_obs(self):
            """
            Is based off the assumption that 5 is not in the returned board.
            Uses 5 as the key for current position.
            """
            AGENT_POSITION_CONSTANT = 5
            ret = self.board.get_board()
            ret[self.agentPosition] = AGENT_POSITION_CONSTANT

            # normalize observation to be be centered at 0
            ret = np.array(ret, dtype=np.float32)
            ret /= np.float32(AGENT_POSITION_CONSTANT)
            ret -= np.float32(0.5)
            return ret

        def render(self):
            import PygameFunctions as PF
            import pygame

            PF.run(self.board)
            pygame.display.update()

        def init_render(self):
            import PygameFunctions as PF
            import pygame

            PF.initScreen(self.board)
            pygame.display.update()

        def close(self):
            import pygame

            pygame.quit()

        def write_run_metrics(self):
            if self.writer is not None:
                with self.writer.as_default():
                    tf.summary.scalar(
                        "episode/num_invalid_actions_per_ep",
                        self.episode_invalid_actions,
                        step=self.total_timesteps,
                    )
                    tf.summary.scalar(
                        "episode/episode_length",
                        self.episode_timesteps,
                        step=self.total_timesteps,
                    )
                    tf.summary.scalar(
                        "episode/episode_total_reward",
                        self.episode_reward,
                        step=self.total_timesteps,
                    )
                    tf.summary.scalar(
                        "episode/mean_reward",
                        self.episode_reward / self.episode_timesteps,
                        step=self.total_timesteps,
                    )
                    tf.summary.scalar(
                        "episode/percent_invalid_per_ep",
                        self.episode_invalid_actions / self.episode_timesteps,
                        step=self.total_timesteps,
                    )

    # %%
    # test to make sure that the observation is what we want.
    test_env = ZombieEnvironment()
    test_env.reset()

    # %% [markdown]
    # ### Make models

    # %%
    ZOMBIE_OUTPUT_SIZE = len(ZombieEnvironment.ACTION_SPACE)
    INPUT_SHAPE = (ROWS * COLUMNS,)

    # %%
    def make_zombie_model():
        """
        makes the model that will be used for zombies
        The output of the model will be the predicted q value
        for being in a certain state.
        """
        model = models.Sequential()
        model.add(layers.InputLayer(INPUT_SHAPE))
        model.add(layers.Flatten())
        model.add(layers.Dense(36 * 256, activation="tanh"))
        model.add(layers.Dense(ZOMBIE_OUTPUT_SIZE))  # the q values for each action
        model.add(layers.LeakyReLU())
        return model

    # %%
    with tf.device(DEVICE):
        zombie_policy = make_zombie_model()
        zombie_target = make_zombie_model()

    # %%
    zombie_policy.load_weights("zombie_policy_weights")
    zombie_target.load_weights("zombie_policy_weights")

    # %% [markdown]
    # ### DQN utilities

    # %%
    # this acts as a class; useful in the training
    Transition = namedtuple("Transition", ("state", "action", "next_state", "reward"))

    class ReplayMemory(object):
        def __init__(self, capacity):
            self.memory = deque([], maxlen=capacity)

        def push(self, *args):
            """Save a transition"""
            self.memory.append(Transition(*args))

        def sample(self, batch_size):
            return random.sample(self.memory, batch_size)

        def __len__(self):
            return len(self.memory)

    # %% [markdown]
    # ### Optimizers and Loss

    # %%
    with tf.device(DEVICE):
        optimizer = keras.optimizers.Adam(0.3)
        loss = keras.losses.Huber()

    # %% [markdown]
    # ### Training loop

    # %%
    BATCH_SIZE = 256
    GAMMA = 0.999
    EPSILON_MAX = 0.9  # exploration rate maximum
    EPSILON_MIN = 0.05  # exploration rate minimum
    EPS_DECAY = 1000  # decay rate, in steps
    TARGET_UPDATE = 500  # how many episodes before the target is updated

    BUFFER_CAPACITY = 10000
    memory = ReplayMemory(BUFFER_CAPACITY)

    # %%
    def select_zombie_action(state, steps_done: int = -1, writer=None):
        """
        If no steps are provided, assuming not going to do
        random exploration
        """
        sample = random.random()
        eps_threshold = 0
        if steps_done != -1:
            eps_threshold = EPSILON_MIN + (EPSILON_MAX - EPSILON_MIN) * math.exp(
                -1.0 * steps_done / EPS_DECAY
            )
        if writer is not None:
            with writer.as_default():
                tf.summary.scalar("exploration rate", eps_threshold, step=steps_done)
        if sample > eps_threshold:
            # Pick the action with the largest expected reward.
            temp = zombie_policy(state, training=False)
            numpy = temp.numpy().flatten()
            if writer is not None:
                with writer.as_default():
                    for idx, name in ZombieEnvironment.ACTION_MAPPINGS.items():
                        tf.summary.scalar(f"q_vals/{name}", numpy[idx], step=steps_done)
            return tf.constant([tuple(numpy).index(max(numpy))], dtype=tf.int32)
        else:
            return tf.constant([random.randrange(ZOMBIE_OUTPUT_SIZE)], dtype=tf.int32)

    # %%
    @tf.function(reduce_retracing=True)
    def train_on_batch(
        state_batch: tf.Tensor,
        action_batch: tf.Tensor,
        reward_batch: tf.Tensor,
        non_final_next_states: tf.Tensor,
        non_final_mask: tf.Tensor,
    ):
        with tf.GradientTape() as policy_tape:
            # Compute Q(s_t, a) - the model computes Q(s_t), then we select the
            # columns of actions taken. These are the actions which would've been taken
            # for each batch state according to policy_net
            action_batch = tf.expand_dims(action_batch, 1)
            state_action_values = tf.gather_nd(
                zombie_policy(state_batch, training=True), action_batch, 1
            )

            # Compute V(s_{t+1}) for all next states.
            # Expected values of actions for non_final_next_states are computed based
            # on the "older" target_net; selecting their best reward with max(1)[0].
            # This is merged based on the mask, such that we'll have either the expected
            # state value or 0 in case the state was final.
            next_state_values = tf.scatter_nd(
                tf.expand_dims(non_final_mask, 1),
                tf.reduce_max(zombie_target(non_final_next_states, training=False), 1),
                tf.constant([BATCH_SIZE]),
            )

            # Compute the expected Q values
            expected_state_action_values = (next_state_values * GAMMA) + reward_batch

            # compute loss (mean squared error)
            assert state_action_values.shape == expected_state_action_values.shape
            _loss = loss(state_action_values, expected_state_action_values)

        # Optimize the model
        policy_gradient = policy_tape.gradient(_loss, zombie_policy.trainable_variables)

        # apply gradient
        optimizer.apply_gradients(
            zip(policy_gradient, zombie_policy.trainable_variables)
        )

        # return the loss
        return _loss

    # %%
    @tf.function(reduce_retracing=True)
    def train_on_batch_v2(
        state_batch: tf.Tensor,
        action_batch: tf.Tensor,
        reward_batch: tf.Tensor,
        non_final_next_states: tf.Tensor,
        non_final_mask: tf.Tensor,
    ):
        with tf.GradientTape() as policy_tape:
            # Compute Q(s_t, a) - the model computes Q(s_t), then we select the
            # columns of actions taken. These are the actions which would've been taken
            # for each batch state according to policy_net
            action_batch = tf.expand_dims(action_batch, 1)
            state_action_values = tf.gather_nd(
                zombie_policy(state_batch, training=True), action_batch, 1
            )
            state_action_values = tf.expand_dims(
                state_action_values, 1
            )  # should give us (batch_size, 1) instead of (batch_size,)

            # Compute V(s_{t+1}) for all next states.
            # Expected values of actions for non_final_next_states are computed based
            # on the "older" target_net; selecting their best reward with max(1)[0].
            # This is merged based on the mask, such that we'll have either the expected
            # state value or 0 in case the state was final.
            next_state_values = tf.scatter_nd(
                tf.expand_dims(non_final_mask, 1),
                tf.reduce_max(zombie_target(non_final_next_states, training=False), 1),
                tf.constant([BATCH_SIZE]),
            )

            # reshape next_state values and reward batch to be (batch_size, 1) instead of (batch_size)
            next_state_values = tf.expand_dims(next_state_values, 1)
            reward_batch = tf.expand_dims(reward_batch, 1)

            # Compute the expected Q values
            expected_state_action_values = (next_state_values * GAMMA) + reward_batch

            # compute loss (mean squared error)
            assert (
                state_action_values.shape == expected_state_action_values.shape
                and state_action_values.shape == (BATCH_SIZE, 1)
            )
            _loss = loss(state_action_values, expected_state_action_values)

        # Optimize the model
        policy_gradient = policy_tape.gradient(_loss, zombie_policy.trainable_variables)

        # apply gradient
        optimizer.apply_gradients(
            zip(policy_gradient, zombie_policy.trainable_variables)
        )

        # return the loss
        return _loss

    # %%
    def train(num_timesteps, max_timesteps=200, render=False, logdir="", run_name=""):
        env = ZombieEnvironment(
            max_timesteps, logdir=logdir, run_name=run_name, have_enemy_player=True
        )
        if render:
            env.init_render()

        while env.total_timesteps < num_timesteps:
            # Initialize the environment and state
            prev_obs = env.reset()
            done = False
            while not done:
                if render:
                    env.render()

                # Select and perform an action
                action = select_zombie_action(
                    tf.constant([prev_obs]), env.total_timesteps, env.writer
                )
                action = action.numpy()[0]  # "flatten" the tensor and take the item
                new_obs, reward, done, _ = env.step(action)
                # reward = tf.constant([reward])

                # Observe new state
                if not done:
                    next_state = new_obs
                else:
                    next_state = None

                # Store the transition in memory
                memory.push(prev_obs, action, next_state, reward)

                # Move to the next state
                prev_obs = next_state

                # Perform one step of the optimization (on the policy network)
                if len(memory) >= BATCH_SIZE:
                    # Transpose the batch (see https://stackoverflow.com/a/19343/3343043 for
                    # detailed explanation). This converts batch-array of Transitions
                    # to Transition of batch-arrays.
                    batch = Transition(*zip(*memory.sample(BATCH_SIZE)))

                    # compute the states that aren't terminal states
                    non_final_mask = tf.constant(
                        tuple(
                            idx
                            for state, idx in zip(
                                batch.next_state, range(len(batch.next_state))
                            )
                            if state is not None
                        ),
                    )
                    non_final_next_states = tf.cast(
                        tuple(state for state in batch.next_state if state is not None),
                        dtype=tf.float32,
                    )

                    loss = train_on_batch_v2(
                        tf.cast(batch.state, dtype=tf.float32),
                        tf.cast(batch.action, dtype=tf.int32),
                        tf.cast(batch.reward, dtype=tf.float32),
                        non_final_next_states,
                        non_final_mask,
                    )
                    with env.writer.as_default():
                        tf.summary.scalar(
                            "train/loss",
                            float(loss.numpy().item()),
                            step=env.total_timesteps,
                        )

            env.write_run_metrics()

            # Update the target network, copying all weights and biases in DQN
            if env.total_timesteps % TARGET_UPDATE == 0:
                zombie_policy.save_weights("zombie_policy_weights")
                zombie_target.load_weights("./zombie_policy_weights")
        # env.close()
        zombie_policy.save_weights("zombie_policy_weights")

    # %% [markdown]
    # ### Start Training!

    # %%
    file = open("run_num.p", "rb")
    RUN_NUMBER = pickle.load(file)["run_num"]
    file.close()

    # %%
    for i in range(5):
        train(
            7000,
            25,
            render=False,
            logdir="zombieEnvironmentv2",
            run_name=f"run{RUN_NUMBER}",
        )
        RUN_NUMBER += 1

    file = open("run_num.p", "wb")
    pickle.dump({"run_num": RUN_NUMBER}, file)
    file.close()
