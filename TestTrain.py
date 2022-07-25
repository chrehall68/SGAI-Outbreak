from QTrain import QTrain
from Board import Board
from constants import *


player_role = "Zombie"  # Valid options are "Government" and "Zombie"

GameBoard = Board((ROWS, COLUMNS), player_role)
qtrainer = QTrain(GameBoard)
GameBoard.populate()

qtrainer.train()