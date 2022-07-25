# file for dqn??

# import torch
# import torch.nn as nn
import tensorflow  # tensorflow is installed
import keras.layers as layers
import keras.models as models

from constants import ACTION_SPACE, COLUMNS, ROWS

OUTPUT_SIZE = len(ACTION_SPACE)
INPUT_SHAPE = (ROWS * COLUMNS, 1)


def make_zombie_model():
    model = models.Sequential()
    model.add(layers.InputLayer(INPUT_SHAPE))
    model.add(layers.Dense(64))
    model.add(layers.LeakyReLU())
    model.add(layers.Dense(128))  # 120 is arbitrary number
    model.add(layers.LeakyReLU())
    model.add(layers.Dense(OUTPUT_SIZE))
    return model


model = make_zombie_model()
print(model.summary())

model_optimizer = model


@tensorflow.function
def train_step(state, reward):
    pass


# device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# if torch.cuda.is_available():
#     print("GPU is available")
#     device = torch.device("cuda")
# #Comment out the following 3 lines if you do not use the nightly build of PyTorch
# if torch.has_mps():
#     print("MPS is available")
#     device = torch.device("mps")
# else:
#     print("GPU/MPS is not available")
#     device = torch.device("cpu")

# """
# This is a multi agent environment; each agent will be each person on the board
# The rewards are designed for training a single agent of that type

# Training process
# Set board up w/

# Board [0 for empty, 1 for person, 2 for zombie, 3 for wall, 4 for safe zone, 5 for position]
# [
#     [0 0 0 1 0]
#     [0 0 0 5 0]
# ]


# ACTION SPACE - 5 if zombie, 6 if person (heal, wall)

# Reward to be given
# Zombie - [Walking -1, biting give it 10 points, walking into wall/off board -1000 points, losing -1000 points, winning 1000 points]

# Gov - [healing - 10, running into wall - -1000, losing - -1000, winning 1000, becoming_zombie - -100]

# """
# class DQN(nn.Module):
#     def __init__(self, outputs:int,input_size:int):
#         super(DQN, self).__init__()
#         """self.conv1 = nn.Conv2d(3, 16, kernel_size=5, stride=2)
#         self.bn1 = nn.BatchNorm2d(16)
#         self.conv2 = nn.Conv2d(16, 32, kernel_size=5, stride=2)
#         self.bn2 = nn.BatchNorm2d(32)
#         self.conv3 = nn.Conv2d(32, 32, kernel_size=5, stride=2)
#         self.bn3 = nn.BatchNorm2d(32)

#         # Number of Linear input connections depends on output of conv2d layers
#         # and therefore the input image size, so compute it.
#         def conv2d_size_out(size, kernel_size=5, stride=2):
#             return (size - (kernel_size - 1) - 1) // stride + 1

#         convw = conv2d_size_out(conv2d_size_out(conv2d_size_out(w)))
#         convh = conv2d_size_out(conv2d_size_out(conv2d_size_out(h)))
#         linear_input_size = convw * convh * 32
#         self.head = nn.Linear(linear_input_size, outputs)
#         """
#         self.layers = [
#             nn.Flatten(),
#             nn.Linear(input_size*100),

#         ]

#     # Called with either one element to determine next action, or a batch
#     # during optimization. Returns tensor([[left0exp,right0exp]...]).
#     def forward(self, x):
#         x = x.to(device)
#         """x = F.relu(self.bn1(self.conv1(x)))
#         x = F.relu(self.bn2(self.conv2(x)))
#         x = F.relu(self.bn3(self.conv3(x)))
#         return self.head(x.view(x.size(0), -1))"""
