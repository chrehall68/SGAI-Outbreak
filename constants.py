# Constants
ROWS = 6
COLUMNS = 6
ACTION_SPACE = ["moveUp", "moveDown", "moveLeft", "moveRight", "heal", "bite"]

# Player role variables
ROLE_TO_ROLE_NUM = {"Government": 1, "Zombie": -1}
ROLE_TO_ROLE_BOOLEAN = {"Government": False, "Zombie": True}

# Pygame constants
BACKGROUND = "#DDC2A1"
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
CELL_COLOR = (233, 222, 188)
LINE_WIDTH = 5
IMAGE_ASSETS = [
    "person_normal.png",
    "person_vax.png",
    "person_zombie.png",
    "zombie_stage_1.png",
    "zombie_stage_2.png"
]
GAME_WINDOW_DIMENSIONS = (1200, 800)
RESET_MOVE_COORDS = (800, 600)
RESET_MOVE_DIMS = (200, 50)
CURE_BITE_COORDS = (950, 200)
KILL_COORDS = (750, 200)
CURE_BITE_DIMS = (200, 200)
CELL_DIMENSIONS = (100, 100)  # number of pixels (x, y) for each cell
CUR_MOVE_COORDS = (800, 400)
MARGIN = 150  # Number of pixels to offset grid to the top-left side
SCORE_DIMS = (200,100)
SCORE_COORDS = (950, 650)
LAST_MOVE_COORDS = (800, 725)
CURRENT_SCORE = 0
SCORE_VALUES = { # TEMPORARY VALUES
    "heal":100,
    "kill":100,
    "move":0
}
TIME_BETWEEN_ZOMBIE_MOVE = 1000 # ms

CURE_SUCCESS_RATES = [1, .75, .5, .25] # these are temporary values

NUM_MOVES_UNTIL_STAGE_2 = 2
NUM_MOVES_UNTIL_STAGE_3 = 3

STAGE_2_BITE_RATE = .5
STAGE_3_BITE_RATE = 1

HEART_SELECTED = False
SKULL_SELECTED = False