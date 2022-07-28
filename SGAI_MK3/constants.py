# Constants
ROWS = 6
COLUMNS = 6
ACTION_SPACE = ["moveUp", "moveDown", "moveLeft", "moveRight", "heal", "bite", "wall"]

# Player role variables
ROLE_TO_ROLE_NUM = {"Government": 1, "Zombie": -1}
ROLE_TO_ROLE_BOOLEAN = {"Government": False, "Zombie": True}

# Pygame constants
BACKGROUND = "#DDC2A1"
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
CELL_COLOR = (233, 222, 188)
VAX_COLOR = (102, 255, 0)
CELL_BORDER = 2
IMAGE_ASSETS = [
    "person_normal.png",
    "person_vax.png",
    "person_zombie.png",
]
GAME_WINDOW_DIMENSIONS = (1200, 800)
RESET_MOVE_COORDS = (800, 600)
RESET_MOVE_DIMS = (200, 50)
CURE_BITE_COORDS = (950, 200)
CURE_BITE_DIMS = (200, 200)
CELL_DIMENSIONS = (100, 100)  # number of pixels (x, y) for each cell
CUR_MOVE_COORDS = (800, 400)
TELEMETRY_COORDS = (800, 200) # telemetry: feedback stuff ex) cure failed, etc.
MARGIN = 150  # Number of pixels to offset grid to the top-left side

WALL_BUTTON_DIMS = (200, 50)
WALL_BUTTON_COORDS = (800, 525)

MIN_WALL_DURATION = 1
MAX_WALL_DURATION = 3

PERSON_SIZE = (35, 60)
