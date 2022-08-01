# Constants
ROWS = 6
COLUMNS = 6
ACTION_SPACE = [
    "moveUp",
    "moveDown",
    "moveLeft",
    "moveRight",
    "cure",
    "vaccinate",
    "wall",
    "bite",
]

# Player role variables
ROLE_TO_ROLE_NUM = {"Government": 1, "Zombie": -1}
ROLE_TO_ROLE_BOOLEAN = {"Government": False, "Zombie": True}

# Pygame constants
BACKGROUND = "#DDC2A1"
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
TELEMETRY_RED = (255, 0, 127)
CELL_COLOR = (218, 221, 161)  # old: (233, 222, 188)
VAX_COLOR = (102, 255, 0)
CELL_BORDER = 2
IMAGE_ASSETS = [
    "person_normal.png",
    "person_vax.png",
    "person_zombie.png",
]
GAME_WINDOW_DIMENSIONS = (1200, 800)
RESET_MOVE_COORDS = (50, 550)
RESET_MOVE_DIMS = (200, 50)

IMG_RED = (255, 131, 119)  # for when you don't have enough resources
IMG_GREEN = (162, 255, 119)  # for when a move is selected
CURE_BITE_COORDS = (50, 200)
CURE_BITE_DIMS = (75, 75)
VAX_COORDS = (125, 200)
VAX_DIMS = (75, 75)
CELL_DIMENSIONS = (100, 100)  # number of pixels (x, y) for each cell
CUR_MOVE_COORDS = (50, 300)
TELEMETRY_COORDS = (50, 700)  # telemetry: feedback stuff ex) cure failed, etc.

MARGIN = 150  # Number of pixels to offset grid to the top-left side
LEFT_MARGIN = 300
TOP_MARGIN = 150

WALL_BUTTON_DIMS = (75, 75)
WALL_BUTTON_COORDS = (200, 200)

COIN_DIMS = (50, 50)
COIN_BALANCE_COORDS = (1125, 25)

MIN_WALL_DURATION = 1
MAX_WALL_DURATION = 3

PERSON_SIZE = (35, 60)
